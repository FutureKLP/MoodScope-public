"""Manual time, stereo and frequency focus. This is filtering, not singer identity extraction."""
import hashlib
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt
from . import storage


def render(data,identity,options):
    data=storage.long_path(data);source=storage.managed_path(data,identity+'.wav') if options['source']=='original' else storage.managed_path(data,'stems',identity,options['model'],options['source']+'.wav')
    if not source.exists():raise ValueError('Zuerst die gewünschte Instrumentgruppe im Hörstudio trennen.')
    with source.open('rb') as stream:info=sf.info(stream)
    start=options['start'];end=options['end'] if options['end'] is not None else info.duration
    if not 0<=start<end<=info.duration+.1:raise ValueError('Zeitbereich liegt außerhalb des Songs.')
    low=options['low_hz'];high=min(options['high_hz'],info.samplerate/2-10)
    if high<=low+20:raise ValueError('Obergrenze muss mindestens 20 Hz über der Untergrenze liegen.')
    digest=hashlib.sha256((json.dumps(options,sort_keys=True)+str(source.stat().st_mtime_ns)).encode()).hexdigest()
    root=storage.managed_path(data,'stems',identity,'focus');root.mkdir(parents=True,exist_ok=True);target=root/(digest+'.wav')
    if target.exists():return digest
    sos=butter(4,[low,high],btype='bandpass',fs=info.samplerate,output='sos')
    state=np.zeros((len(sos),2,2))
    temp=target.with_suffix('.tmp.wav');offset=0
    try:
        with source.open('rb') as input_stream,temp.open('w+b') as output_stream,sf.SoundFile(input_stream) as audio,sf.SoundFile(output_stream,'w',format='WAV',samplerate=info.samplerate,channels=2,subtype='FLOAT') as output:
            while True:
                block=audio.read(65536,dtype='float32',always_2d=True)
                if not len(block):break
                if not np.isfinite(block).all():raise ValueError('Ungültige Audiodaten für manuellen Fokus.')
                if block.shape[1]==1:block=np.repeat(block,2,axis=1)
                if options['stereo']=='left':block=np.repeat(block[:,:1],2,axis=1)
                elif options['stereo']=='right':block=np.repeat(block[:,1:2],2,axis=1)
                elif options['stereo']=='center':block=np.repeat(block.mean(axis=1,keepdims=True),2,axis=1)
                elif options['stereo']=='sides':
                    side=(block[:,0]-block[:,1])*.5;block=np.stack([side,-side],axis=1)
                filtered,state=sosfilt(sos,block,axis=0,zi=state)
                times=(np.arange(len(block))+offset)/info.samplerate
                filtered[(times<start)|(times>=end)]=0
                output.write(np.clip(filtered*10**(options['gain_db']/20),-1,1));offset+=len(block)
        temp.replace(target)
    finally:temp.unlink(missing_ok=True)
    return digest
