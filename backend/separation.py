"""Cached Demucs source separation. No promise of individual singer isolation."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf

MODELS={'htdemucs','htdemucs_6s'}
LABELS={'vocals':'Gesang / Stimmen','drums':'Schlagzeug','bass':'Bass','other':'Übrige Instrumente','guitar':'Gitarre','piano':'Klavier'}


def folder(data,identity,model):
    if model not in MODELS:raise ValueError('Nicht unterstütztes Trennmodell')
    return Path(data)/'stems'/identity/model


def status(data,identity,model):
    root=folder(data,identity,model)
    try:
        info=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
        if not all((root/(s+'.wav')).is_file() for s in info['sources']):raise ValueError()
        return {**info,'ready':True,'cached':True}
    except (OSError,ValueError,KeyError):
        return {'ready':False,'model':model,'sources':[]}


def separate(data,identity,model_name,engine,progress):
    cached=status(data,identity,model_name)
    if cached['ready']:return cached
    try:
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
    except ImportError:
        raise RuntimeError('Quellentrennung fehlt. Projektlokal: python -m pip install -r backend/requirements-separation.txt') from None
    import torch
    from . import catalog
    catalog.unload_models(engine)
    torch.hub.set_dir(str(catalog.ROOT/'models'/'demucs'))
    progress('Lade lokales Demucs-Modell; beim ersten Mal Modelldownload',5)
    model=get_model(model_name).to(engine.device()).eval()
    y,sr=sf.read(Path(data)/(identity+'.wav'),dtype='float32',always_2d=True)
    import librosa
    y=librosa.resample(y.T,orig_sr=sr,target_sr=model.samplerate)
    mixture=torch.from_numpy(y).to(engine.device())
    reference=mixture.mean(0);mean=reference.mean();std=reference.std()
    std=std.clamp(min=1e-6)
    try:
        progress('Trenne Gesang und Instrumentgruppen lokal; das kann mehrere Minuten dauern',15)
        with torch.inference_mode():
            stems=apply_model(model,((mixture-mean)/std)[None],device=engine.device(),
                shifts=0,split=True,overlap=.25,progress=False,num_workers=0)[0]
        stems=(stems*std+mean/len(model.sources)).cpu().numpy()
        root=folder(data,identity,model_name);root.mkdir(parents=True,exist_ok=True)
        for source,audio in zip(model.sources,stems):sf.write(root/(source+'.wav'),audio.T,model.samplerate,subtype='FLOAT')
        info={'sources':list(model.sources),'model':model_name,'sample_rate':model.samplerate,
            'duration':stems.shape[-1]/model.samplerate,'cached':False,'ready':True,
            'note':'Geschätzte Quellen mit möglichen Artefakten und Übersprechen. Gesang umfasst alle Stimmen; einzelne Sänger werden nicht getrennt. Gitarre/Klavier im 6-Spur-Modell sind experimentell.'}
        (root/'manifest.json').write_text(json.dumps(info),encoding='utf-8')
        return info
    finally:
        del model,mixture
        import gc
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()


def mix(data,identity,model,sources):
    info=status(data,identity,model)
    chosen=sorted(set(sources))
    if not info['ready'] or not chosen or any(s not in info['sources'] for s in chosen):raise ValueError('Keine gültigen getrennten Quellen gewählt')
    root=folder(data,identity,model)
    if len(chosen)==1:return root/(chosen[0]+'.wav')
    destination=root/('mix-'+'-'.join(chosen)+'.wav')
    if destination.exists():return destination
    handles=[sf.SoundFile(root/(s+'.wav')) for s in chosen]
    temporary=destination.with_suffix('.tmp.wav')
    try:
        with sf.SoundFile(temporary,'w',samplerate=info['sample_rate'],channels=2,subtype='FLOAT') as output:
            while True:
                blocks=[h.read(65536,dtype='float32',always_2d=True) for h in handles]
                if not len(blocks[0]):break
                output.write(np.clip(sum(blocks),-1,1))
        temporary.replace(destination)
    finally:
        for handle in handles:handle.close()
    return destination
