"""Offline production-engine gain test; no application database or downloads."""
import argparse
import json
import os
from pathlib import Path
from scripts.audio_evaluation import load_manifest, digest, output_directory


def run(manifest, output, model_directory, device='cpu'):
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    import soundfile as sf
    import librosa
    from transformers import ClapModel, ClapProcessor
    from backend.models import Engines, PIPELINE_VERSION
    cases=load_manifest(manifest)
    if any(c['split']!='diagnostic' for c in cases):
        raise ValueError('Diagnostic cases only; keep human holdout untouched')
    model_directory=Path(model_directory).resolve()
    if not model_directory.is_dir():raise ValueError('Existing local snapshot required')
    for case in cases:
        if case['start']+case['duration']>sf.info(case['source']).duration+1e-6:
            raise ValueError('Excerpt exceeds source duration')
    manifest_hash=digest(manifest)
    destination=output_directory(output)
    engine=Engines();engine.data=destination/'isolated-settings'
    engine.device=lambda purpose='audio':device
    engine.processor=ClapProcessor.from_pretrained(model_directory,local_files_only=True)
    engine.audio_model=ClapModel.from_pretrained(model_directory,local_files_only=True).to(device).eval()
    rows=[]
    for index,case in enumerate(cases):
        info=sf.info(case['source'])
        audio,sr=sf.read(case['source'],start=round(case['start']*info.samplerate),
                         frames=round(case['duration']*info.samplerate),dtype='float32',always_2d=True)
        audio=librosa.resample(audio.mean(axis=1),orig_sr=sr,target_sr=48000)
        original=engine.audio(audio,48000,lambda *args:None)
        attenuated=engine.audio(audio*10**(-12/20),48000,lambda *args:None)
        rows.append({'case_id':case['case_id'],'source_sha256':case['source_sha256'],
                     'original':original,'attenuated':attenuated})
        print(f'Cases completed: {index+1}/{len(cases)}',flush=True)
    for source,expected in {(c['source'],c['source_sha256']) for c in cases}:
        if digest(source)!=expected:raise RuntimeError('Source changed during evaluation')
    if digest(manifest)!=manifest_hash:raise RuntimeError('Manifest changed during evaluation')
    pairs=[(a,b) for row in rows for a,b in zip(row['original'],row['attenuated'])]
    summary={'cases':len(cases),'windows':len(pairs),
             'max_valence_gain_difference':max(abs(a['valence']-b['valence']) for a,b in pairs),
             'stable_winners':sum(max(a['scores'],key=a['scores'].get)==max(b['scores'],key=b['scores'].get) for a,b in pairs),
             'wording_disagreements':sum(not a['prompt_winners_agree'] for a,b in pairs),
             'semantic_accuracy_measured':False}
    report={'pipeline_version':PIPELINE_VERSION,'manifest_sha256':manifest_hash,
            'device':device,'model_snapshot':model_directory.name,'rows':rows,'summary':summary}
    (destination/'model-results.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf8')
    print(json.dumps(summary))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--model-directory',required=True)
    parser.add_argument('--device',choices=['cpu','cuda','cuda:0'],default='cpu')
    args=parser.parse_args()
    run(args.manifest,args.output,args.model_directory,args.device)
