"""Offline Music2Emo context comparison using explicitly supplied upstream code.

No model downloads, app imports, active-model changes or database writes.
The source directory must be an inspected Music2Emotion checkout. Its MIT
license stays with the isolated runtime copy. Model terms apply separately.
"""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time
from scripts.audio_evaluation import digest, load_manifest, output_directory


def checked_result(value):
    """Preserve raw regression and independent tags, never invent six-way scores."""
    result={}
    for name in ('valence','arousal'):
        raw=value[name]
        if isinstance(raw,bool) or not isinstance(raw,(int,float)) or not math.isfinite(raw):
            raise ValueError('Nonfinite or missing regression output')
        result[name+'_raw']=float(raw)
        result[name]=max(-1.,min(1.,(raw-5)/4)) if name=='valence' else max(0.,min(1.,(raw-1)/8))
    result['outside_training_scale']=any(not 1<=result[name+'_raw']<=9 for name in ('valence','arousal'))
    tags=value.get('tag_scores',{})
    if not isinstance(tags,dict) or not tags or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in tags.values()):
        raise ValueError('Expected finite independent tag scores')
    result['tags']=dict(tags)
    return result


def segment_ranges(samples,sample_rate):
    """Do not give a subsecond decoder tail the weight of a 30-second segment."""
    if samples<=0 or sample_rate<=0:raise ValueError('Nonempty audio required')
    size=30*sample_rate
    spans=[(start,min(samples,start+size)) for start in range(0,samples,size)]
    if len(spans)>1 and spans[-1][1]-spans[-1][0]<sample_rate:
        spans[-2]=(spans[-2][0],spans[-1][1]);spans.pop()
    return spans


def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('Upstream source changed; review adaptation before running')
    return text.replace(old,new,1)


def prepare_runtime(source,destination,correct_key_mode=False):
    """Copy only inference source; all upstream scratch writes stay in a new run."""
    for folder in ('utils','model','inference'):
        shutil.copytree(source/folder,destination/folder,
                        ignore=shutil.ignore_patterns('__pycache__','*.pt','*.ckpt','*.mp3','*.wav'))
    shutil.copy2(source/'LICENSE',destination/'LICENSE')
    code=(source/'music2emo.py').read_text(encoding='utf8')
    for line in ('from omegaconf import DictConfig','import hydra','from hydra.utils import to_absolute_path','import gradio as gr'):
        code=replace_once(code,line,'# Unused training/web import omitted for isolated inference.')
    code=replace_once(code,'weights_only=False','weights_only=True')
    code=replace_once(code,'checkpoint = torch.load(model_file, map_location=self.device)',
                      'checkpoint = torch.load(model_file, map_location=self.device, weights_only=True)')
    code=replace_once(code,"model_file = './inference/data/btc_model_large_voca.pt'",
                      "model_file = os.environ['MOODSCOPE_BTC_WEIGHTS']")
    code=replace_once(code,'"predicted_moods": predicted_moods',
                      '"predicted_moods": predicted_moods, "tag_scores": dict(zip(mood_list, probs.squeeze().tolist()))')
    if correct_key_mode:
        code=replace_once(code,'mode = key_signature.split()[-1]','mode = key_type')
    (destination/'music2emo.py').write_text(code,encoding='utf8')
    head=destination/'model/linear_mt_attn_ck.py'
    head.write_text(replace_once(head.read_text(encoding='utf8'),'import pytorch_lightning as pl',
                    '# Unused training import omitted.'),encoding='utf8')
    mert=destination/'utils/mert.py'
    mert.write_text(replace_once(mert.read_text(encoding='utf8'),
                    'torch.stack(model_outputs.hidden_states).squeeze()[1:, :, :]',
                    'torch.stack(model_outputs.hidden_states).squeeze(1)[1:, :, :]'),encoding='utf8')


def run(args):
    source=Path(args.source_directory).resolve();weights=Path(args.weights_directory).resolve()
    cases=load_manifest(args.manifest)
    if any(c['split']!='diagnostic' for c in cases):raise ValueError('Diagnostic manifest required; do not tune on holdout')
    manifest_hash=digest(args.manifest)
    provenance=json.loads((weights/'provenance.json').read_text(encoding='utf8'))
    for entry in provenance['files']:
        path=(weights/entry['file']).resolve()
        if not path.is_relative_to(weights) or digest(path)!=entry['sha256']:
            raise ValueError('Model provenance check failed')
    destination=output_directory(args.output);runtime=destination/'runtime';runtime.mkdir()
    prepare_runtime(source,runtime,args.correct_key_mode)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',USE_TF='0',
                      HF_MODULES_CACHE=str(destination/'module-cache'),
                      MOODSCOPE_BTC_WEIGHTS=str(weights/'btc_model_large_voca.pt'))
    sys.path.insert(0,str(runtime))
    if args.dependency_directory:sys.path.insert(0,str(Path(args.dependency_directory).resolve()))
    import numpy as np
    import torch
    import soundfile as sf
    from transformers import AutoModel,Wav2Vec2FeatureExtractor
    import music2emo
    from utils.mert import FeatureExtractorMERT
    torch.set_num_threads(4)
    torch.serialization.add_safe_globals([(np._core.multiarray.scalar,'numpy.core.multiarray.scalar'),
                                           np.dtype,type(np.dtype(np.float32)),type(np.dtype(np.float64))])
    def local_init(self,model_name=None,device=None,sr=24000):
        self.device=args.device
        self.model=AutoModel.from_pretrained(weights/'mert',trust_remote_code=True,
                    local_files_only=True,attn_implementation='eager').to(self.device).eval()
        self.processor=Wav2Vec2FeatureExtractor.from_pretrained(weights/'mert',local_files_only=True)
    FeatureExtractorMERT.__init__=local_init
    def load_audio(path):
        audio,sr=sf.read(path,dtype='float32',always_2d=True)
        return torch.from_numpy(audio.T.copy()),sr
    music2emo.torchaudio.load=load_audio
    music2emo.split_audio=lambda waveform,sr:[waveform[start:end] for start,end in segment_ranges(len(waveform),sr)]
    previous=Path.cwd();os.chdir(runtime)
    try:
        model=music2emo.Music2emo(model_weights=str(weights/'J_all.ckpt'))
        model.device=args.device;model.music2emo_model.to(args.device)
        rows=[]
        for case in cases:
            info=sf.info(case['source'])
            if case['start']+case['duration']>info.duration+1e-6:raise ValueError('Context exceeds source duration')
            audio,sr=sf.read(case['source'],start=round(case['start']*info.samplerate),
                             frames=round(case['duration']*info.samplerate),dtype='float32')
            sf.write('context.wav',audio,sr,subtype='FLOAT')
            started=time.perf_counter()
            with torch.inference_mode():result=checked_result(model.predict('context.wav'))
            rows.append({'case_id':case['case_id'],'context_start':case['start'],
                         'context_end':case['start']+case['duration'],'source_sha256':case['source_sha256'],
                         'seconds':time.perf_counter()-started,**result})
            if digest(case['source'])!=case['source_sha256']:raise RuntimeError('Source changed during evaluation')
            print(f'Contexts completed: {len(rows)}/{len(cases)}',flush=True)
    finally:os.chdir(previous)
    if digest(args.manifest)!=manifest_hash:raise RuntimeError('Manifest changed during evaluation')
    report={'method':'music2emo-context-diagnostic-v2','correct_key_mode':args.correct_key_mode,'manifest_sha256':manifest_hash,
            'provenance':provenance,'device':args.device,'rows':rows,'calibrated_for_timeline':False}
    (destination/'model-results.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','output','source-directory','weights-directory'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--dependency-directory')
    parser.add_argument('--correct-key-mode',action='store_true',help='Compare corrected major/minor input against upstream behavior')
    parser.add_argument('--device',choices=['cpu','cuda','cuda:0'],default='cpu')
    run(parser.parse_args())
