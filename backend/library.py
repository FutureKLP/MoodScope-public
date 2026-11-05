"""Conservative metadata matching, verified against aligned acoustic signatures."""
import json
import unicodedata
import numpy as np
import soundfile as sf


def normalized(text):
    return ' '.join(unicodedata.normalize('NFKC',str(text)).casefold().split())


def signature(path):
    audio,sr=sf.read(path,dtype='float32')
    if audio.ndim==2:audio=audio.mean(axis=1)
    duration=len(audio)/sr
    if duration<15 or float(np.max(np.abs(audio)))<1e-5:return None
    vectors=[];energy=[]
    edges=np.geomspace(40,min(18000,sr/2),25)
    frequencies=np.fft.rfftfreq(4096,1/sr)
    window=np.hanning(4096)
    for second in np.linspace(1,duration-1,min(120,int(duration)-2)):
        center=int(second*sr);start=max(0,center-2048)
        clip=audio[start:start+4096]
        if len(clip)<4096:clip=np.pad(clip,(0,4096-len(clip)))
        fft=np.abs(np.fft.rfft(clip*window))**2
        bands=np.array([np.log1p(fft[(frequencies>=a)&(frequencies<b)].sum()) for a,b in zip(edges[:-1],edges[1:])])
        bands/=max(float(np.linalg.norm(bands)),1e-8)
        vectors.append(bands.tolist());energy.append(float(np.sqrt(np.mean(clip**2))))
    return {'spectrum':vectors,'energy':energy}


def same_recording(first,second):
    if not first or not second:return False
    a=np.asarray(first['spectrum']);b=np.asarray(second['spectrum'])
    if a.shape!=b.shape:return False
    similarity=float(np.mean(np.sum(a*b,axis=1)))
    x=np.asarray(first['energy']);y=np.asarray(second['energy'])
    correlation=float(np.corrcoef(x,y)[0,1]) if min(float(x.std()),float(y.std()))>1e-7 else 0.
    gain=float(np.mean(y)/max(float(np.mean(x)),1e-8))
    return similarity>.995 and correlation>.995 and .9<gain<1.1


def find_metadata_match(conn,metadata,fingerprint):
    if not metadata.get('artist') or not metadata.get('title') or fingerprint is None:return None
    for identity,raw in conn.execute('SELECT id,metadata FROM tracks WHERE id<>?',(metadata['id'],)):
        candidate=json.loads(raw)
        if (normalized(candidate.get('artist',''))!=normalized(metadata['artist']) or
            normalized(candidate.get('title',''))!=normalized(metadata['title']) or
            abs(candidate['duration']-metadata['duration'])>.05):continue
        row=conn.execute('SELECT result FROM cache WHERE key=?',(f'fingerprint:{identity}',)).fetchone()
        if row and same_recording(fingerprint,json.loads(row[0])):return identity
    return None
