"""Cached Demucs source separation. No promise of individual singer isolation."""
import json
import math
import hashlib
import threading
from pathlib import Path
import numpy as np
import soundfile as sf

MODELS={'htdemucs','htdemucs_6s','htdemucs_ft','htdemucs_auto'}
LABELS={'vocals':'Gesang / Stimmen','drums':'Schlagzeug','bass':'Bass','other':'Übrige Instrumente','guitar':'Gitarre','piano':'Klavier'}


def folder(data,identity,model):
    if model not in MODELS:raise ValueError('Nicht unterstütztes Trennmodell')
    return Path(data)/'stems'/identity/model


def status(data,identity,model):
    root=folder(data,identity,model)
    try:
        info=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
        if not all((root/(s+'.wav')).is_file() for s in info['sources']):raise ValueError()
        if 'activity' not in info:
            energy={}
            for source in info['sources']:
                squared=0.;count=0
                with sf.SoundFile(root/(source+'.wav')) as audio:
                    for block in audio.blocks(blocksize=65536,dtype='float32'):
                        squared+=float(np.square(block,dtype='float64').sum());count+=block.size
                energy[source]=squared/max(1,count)
            total=sum(energy.values())
            info['activity']={s:float(v/max(1e-12,total)) for s,v in energy.items()}
            info['audible_sources']=[s for s in info['sources'] if info['activity'][s]>=.005]
            (root/'manifest.json').write_text(json.dumps(info),encoding='utf-8')
        return {**info,'ready':True,'cached':True}
    except (OSError,ValueError,KeyError):
        return {'ready':False,'model':model,'sources':[]}


def separate(data,identity,model_name,engine,progress):
    cached=status(data,identity,model_name)
    if cached['ready']:return cached
    try:
        from .demucs_models import load_model
        from demucs.apply import apply_model
    except ImportError:
        raise RuntimeError('Quellentrennung fehlt. Projektlokal: python -m pip install -r backend/requirements-separation.txt') from None
    import torch
    from . import catalog
    catalog.unload_models(engine)
    torch.hub.set_dir(str(catalog.ROOT/'models'/'demucs'))
    progress('Lade lokales Demucs-Modell; beim ersten Mal Modelldownload',5)
    actual_model='htdemucs_ft' if model_name=='htdemucs_auto' else model_name
    model=load_model(actual_model,progress).to(engine.device()).eval()
    y,sr=sf.read(Path(data)/(identity+'.wav'),dtype='float32',always_2d=True)
    import librosa
    y=librosa.resample(y.T,orig_sr=sr,target_sr=model.samplerate)
    mixture=torch.from_numpy(y).to(engine.device())
    reference=mixture.mean(0);mean=reference.mean();std=reference.std()
    std=std.clamp(min=1e-6)
    adaptive=model_name=='htdemucs_auto'
    plan=adaptive_plan(y,model.samplerate) if adaptive else {'shifts':0,'overlap':.25}
    try:
        progress('Trenne Gesang und Instrumentgruppen lokal; das kann mehrere Minuten dauern',15)
        with torch.inference_mode():
            stems=apply_model(model,((mixture-mean)/std)[None],device=engine.device(),
                shifts=plan['shifts'],split=True,overlap=plan['overlap'],progress=False,num_workers=0)[0]
        stems=(stems*std+mean/len(model.sources)).cpu().numpy()
        progress('Prüfe getrennte Spuren und Rekonstruktion',90)
        error_before=float(np.sqrt(np.mean((y-stems.sum(axis=0))**2)))
        if adaptive:
            energy=np.mean(stems**2,axis=(1,2));weights=energy/max(1e-12,float(energy.sum()))
            stems+=weights[:,None,None]*(y-stems.sum(axis=0))[None]
        if not np.isfinite(stems).all():raise RuntimeError('Quellentrennung lieferte ungültige Audiodaten.')
        root=folder(data,identity,model_name);root.mkdir(parents=True,exist_ok=True)
        for source,audio in zip(model.sources,stems):sf.write(root/(source+'.wav'),audio.T,model.samplerate,subtype='FLOAT')
        info={'sources':list(model.sources),'model':model_name,'sample_rate':model.samplerate,
            'actual_model':actual_model,'processing':plan,'reconstruction_rms_before':error_before,
            'reconstruction_rms_after':float(np.sqrt(np.mean((y-stems.sum(axis=0))**2))),
            'duration':stems.shape[-1]/model.samplerate,'cached':False,'ready':True,
            'note':'Geschätzte Quellen mit möglichen Artefakten und Übersprechen. Gesang umfasst alle Stimmen; einzelne Sänger werden nicht getrennt. Gitarre/Klavier im 6-Spur-Modell sind experimentell.'}
        (root/'manifest.json').write_text(json.dumps(info),encoding='utf-8')
        return {**status(data,identity,model_name),'cached':False}
    finally:
        del model,mixture
        import gc
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()


def adaptive_plan(audio,sr):
    """Choose bounded inference effort from measured transient contrast, not catalogue guesses."""
    sample=audio[...,:min(audio.shape[-1],sr*30)]
    rms=float(np.sqrt(np.mean(sample**2)))
    crest=float(np.max(np.abs(sample))/max(1e-8,rms))
    return {'shifts':2 if crest>5 else 1,'overlap':.5,'crest_ratio':crest,
            'method':'fine-tuned ensemble, measured crest-based shift averaging, energy-weighted mixture consistency',
            'limitation':'Reconstruction consistency does not measure source isolation quality.'}


_mix_lock=threading.RLock()


def mix(data,identity,model,sources,gains=None):
    # Concurrent media requests must not write the same temporary WAV at once.
    with _mix_lock:return _mix(data,identity,model,sources,gains)


def _mix(data,identity,model,sources,gains):
    info=status(data,identity,model)
    if not info['ready'] or not sources or len(sources)>6 or len(set(sources))!=len(sources) or any(s not in info['sources'] for s in sources):
        raise ValueError('Keine gültigen getrennten Quellen gewählt')
    weights=[1.]*len(sources) if gains is None else gains
    if len(weights)!=len(sources) or any(not math.isfinite(v) or not 0<=v<=1 for v in weights):raise ValueError('Spurpegel müssen zwischen 0 und 1 liegen.')
    chosen=sorted(zip(sources,weights))
    root=folder(data,identity,model)
    if len(chosen)==1 and chosen[0][1]==1:return root/(chosen[0][0]+'.wav')
    fingerprint=hashlib.sha256(('peak-safe-v3:'+json.dumps(chosen)).encode()).hexdigest()[:24]
    destination=root/('mix-'+fingerprint+'.wav')
    if destination.exists():return destination
    handles=[sf.SoundFile(root/(s+'.wav')) for s,_ in chosen]
    temporary=destination.with_suffix('.tmp.wav')
    normalized=destination.with_suffix('.normalized.tmp.wav')
    try:
        peak=0.
        with sf.SoundFile(temporary,'w',samplerate=info['sample_rate'],channels=2,subtype='FLOAT') as output:
            while True:
                blocks=[h.read(65536,dtype='float32',always_2d=True)*gain for h,(_,gain) in zip(handles,chosen)]
                if not len(blocks[0]):break
                mixture=sum(blocks);peak=max(peak,float(np.max(np.abs(mixture))))
                output.write(mixture)
        if peak>1:
            with sf.SoundFile(temporary) as source,sf.SoundFile(normalized,'w',samplerate=info['sample_rate'],channels=2,subtype='FLOAT') as output:
                for block in source.blocks(blocksize=65536,dtype='float32'):output.write(block/peak)
            normalized.replace(temporary)
        temporary.replace(destination)
    finally:
        for handle in handles:handle.close()
        for leftover in [temporary,normalized]:
            if leftover.exists():leftover.unlink()
    return destination
