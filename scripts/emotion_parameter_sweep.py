"""Offline diagnostic context sweep using installed weights and saved reference curves."""
import argparse
import json
import os
from pathlib import Path
from scripts.audio_evaluation import digest, output_directory
from scripts.music2emo_curve import context_spans, predict_spans, verify_installation
from scripts.music2emo_evaluation import prepare_runtime, load_local_model
from scripts.deam_timeline_evaluation import annotations, evaluate


def run(args):
    if not args.contexts or len(set(args.contexts)) != len(args.contexts):
        raise ValueError("Distinct context lengths required")
    import soundfile as sf
    import torch
    weights=Path(args.weights).resolve()
    verify_installation(weights)
    baseline=json.loads(Path(args.baseline).read_text(encoding='utf8'))['rows']
    selection=json.loads(Path(args.selection).read_text(encoding='utf8'))['tracks']
    known={str(row['track_id']):row for row in selection}
    audio_directory=Path(args.audio_directory).resolve()
    sources={}
    for row in baseline:
        identity=str(row['track_id'])
        if not identity.isdecimal() or identity not in known:
            raise ValueError('Expected selected numeric reference identity')
        source=audio_directory/(identity+'.mp3')
        if digest(source)!=known[identity]['sha256']:
            raise ValueError('Reference audio checksum mismatch')
        sources[identity]=source
    references={key:annotations(getattr(args,key)) for key in ('valence','arousal')}
    destination=output_directory(args.output)
    protocol={'diagnostic_only':True,'contexts':args.contexts,'grid_seconds':5,
              'baseline_sha256':digest(args.baseline),'selection_sha256':digest(args.selection),
              'annotation_sha256':{key:digest(getattr(args,key)) for key in references},
              'lag_seconds':0,'normalization':False,'correct_key_mode':True}
    (destination/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    runtime=destination/'runtime';runtime.mkdir()
    prepare_runtime(weights/'source',runtime,correct_key_mode=True)
    model=load_local_model(weights,runtime,destination,args.device,str(weights/'packages'))
    previous=Path.cwd();os.chdir(runtime)
    results={str(context):[] for context in args.contexts}
    try:
        for number,row in enumerate(baseline):
            identity=str(row['track_id']);source=sources[identity]
            samples,sr=sf.read(source,dtype='float32',always_2d=True);samples=samples.mean(axis=1)
            def predict(clip):
                sf.write('context.wav',clip,sr,subtype='FLOAT')
                with torch.inference_mode():return model.predict('context.wav')
            for context in args.contexts:
                curve=predict_spans(samples,sr,list(context_spans(len(samples)/sr,context=context)),predict,lambda *x:None)
                results[str(context)].append({**row,'music2emo_curve':curve})
                # Separate files preserve completed work if a later inference fails.
                target=destination/f'context-{context}.json'
                temporary=target.with_suffix('.tmp')
                temporary.write_text(json.dumps({'rows':results[str(context)]},allow_nan=False),encoding='utf8')
                temporary.replace(target)
                print(f'Track {number+1}/{len(baseline)}, context {context}s complete',flush=True)
            if digest(source)!=known[identity]['sha256']:raise RuntimeError('Source changed')
    finally:os.chdir(previous)
    scores={'baseline':evaluate(baseline,references)}
    scores.update({key:evaluate(rows,references) for key,rows in results.items()})
    (destination/'metrics.json').write_text(json.dumps(scores,indent=2,allow_nan=False),encoding='utf8')
    print('Diagnostic sweep complete',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('weights','baseline','selection','audio-directory','valence','arousal','output'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--contexts',nargs='+',type=int,choices=[5,10,15,20,30],default=[10,20])
    parser.add_argument('--device',choices=['cpu','cuda','cuda:0'],default='cpu')
    run(parser.parse_args())
