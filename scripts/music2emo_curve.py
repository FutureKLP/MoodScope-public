"""Isolated optional worker; called by the local service, never downloads models."""
import argparse
import json
import os
from pathlib import Path
from scripts.audio_evaluation import digest
from scripts.music2emo_evaluation import prepare_runtime,load_local_model,checked_result


def context_spans(duration,step=5,context=30):
    if duration<=0 or step<=0 or context<=0:raise ValueError('Positive durations required')
    from backend.core import analysis_grid
    for span in analysis_grid(duration,step):
        center=(span['start']+span['end'])/2
        start=max(0,min(duration-context,center-context/2))
        yield {**span,'context_start':start,'context_end':min(duration,start+context)}


def run(audio,weights,output,device):
    import soundfile as sf
    import torch
    source_hash=digest(audio)
    provenance=json.loads((weights/'provenance.json').read_text(encoding='utf8'))
    for entry in provenance['files']:
        path=(weights/entry['file']).resolve()
        if not path.is_relative_to(weights) or digest(path)!=entry['sha256']:raise ValueError('Model checksum mismatch')
    installation=json.loads((weights/'installation.json').read_text(encoding='utf8'))
    for name,expected in installation['source_sha256'].items():
        path=(weights/'source'/name).resolve()
        if not path.is_relative_to(weights/'source') or digest(path)!=expected:raise ValueError('Source checksum mismatch')
    runtime=output/'runtime';runtime.mkdir()
    prepare_runtime(weights/'source',runtime,correct_key_mode=True)
    model=load_local_model(weights,runtime,output,device,str(weights/'packages'))
    samples,sr=sf.read(audio,dtype='float32',always_2d=True);samples=samples.mean(axis=1)
    duration=len(samples)/sr;rows=[];spans=list(context_spans(duration))
    previous=Path.cwd();os.chdir(runtime)
    try:
        for span in spans:
            clip=samples[round(span['context_start']*sr):round(span['context_end']*sr)]
            sf.write('context.wav',clip,sr,subtype='FLOAT')
            with torch.inference_mode():prediction=checked_result(model.predict('context.wav'))
            rows.append({**span,**prediction})
            temporary=output/'progress.tmp';temporary.write_text(json.dumps({'done':len(rows),'total':len(spans)}))
            temporary.replace(output/'progress.json')
    finally:os.chdir(previous)
    if digest(audio)!=source_hash:raise RuntimeError('Source changed during analysis')
    result={'method':'music2emo-curve-v1','context_seconds':30,'grid_seconds':5,
            'experimental':True,'calibrated_for_timeline':False,'rows':rows}
    (output/'result.json').write_text(json.dumps(result,allow_nan=False),encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('audio','weights','output'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--device',default='cpu',choices=['cpu','cuda','cuda:0'])
    args=parser.parse_args()
    run(Path(args.audio).resolve(),Path(args.weights).resolve(),Path(args.output).resolve(),args.device)
