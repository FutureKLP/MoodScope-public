import json
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from backend import separation


def test_source_mix_is_exact_and_cached_without_new_inference(tmp_path):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    sf.write(root/'vocals.wav',np.full((4800,2),.1),48000,subtype='FLOAT')
    sf.write(root/'drums.wav',np.full((4800,2),.2),48000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals','drums'],'sample_rate':48000,'model':'htdemucs'}))
    path=separation.mix(tmp_path,'test','htdemucs',['drums','vocals'])
    data,sr=sf.read(path)
    assert sr==48000 and np.allclose(data,.3)
    assert separation.mix(tmp_path,'test','htdemucs',['vocals','drums'])==path
    assert separation.mix(tmp_path,'test','htdemucs',['vocals'])==root/'vocals.wav'
    with pytest.raises(ValueError):separation.mix(tmp_path,'test','htdemucs',['../private'])


def test_incomplete_stems_are_never_reported_ready(tmp_path):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals']}))
    assert not separation.status(tmp_path,'test','htdemucs')['ready']


def test_empty_instrument_is_hidden_without_claiming_presence(tmp_path):
    root=separation.folder(tmp_path,'test','htdemucs_6s');root.mkdir(parents=True)
    sf.write(root/'vocals.wav',np.full((1000,2),.2),16000,subtype='FLOAT')
    sf.write(root/'piano.wav',np.zeros((1000,2)),16000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals','piano']}))
    info=separation.status(tmp_path,'test','htdemucs_6s')
    assert info['audible_sources']==['vocals'] and info['activity']['piano']==0

def test_source_gains_are_exact_order_independent_and_reject_unsafe_values(tmp_path):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    sf.write(root/'vocals.wav',np.full((480,2),.1),48000,subtype='FLOAT')
    sf.write(root/'drums.wav',np.full((480,2),.2),48000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals','drums'],'sample_rate':48000}))
    path=separation.mix(tmp_path,'test','htdemucs',['vocals','drums'],[1,.5])
    assert np.allclose(sf.read(path)[0],.2)
    assert separation.mix(tmp_path,'test','htdemucs',['drums','vocals'],[.5,1])==path
    assert np.allclose(sf.read(separation.mix(tmp_path,'test','htdemucs',['vocals'],[0]))[0],0)
    for gains in [[float('nan')],[float('inf')],[-1],[1.1],[]]:
        with pytest.raises(ValueError):separation.mix(tmp_path,'test','htdemucs',['vocals'],gains)

def test_peak_safe_mix_preserves_waveform_shape_instead_of_clipping(tmp_path):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    wave=np.array([[.8,.8],[.4,.4]],dtype='float32')
    for name in ['vocals','drums']:sf.write(root/(name+'.wav'),wave,48000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals','drums'],'sample_rate':48000}))
    output=sf.read(separation.mix(tmp_path,'test','htdemucs',['vocals','drums']))[0]
    assert np.allclose(output,[[1,1],[.5,.5]])


def test_mix_cache_tracks_replaced_stems_and_repairs_truncated_outputs(tmp_path):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    for name in ['vocals','drums']:sf.write(root/(name+'.wav'),np.full((480,2),.1),48000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals','drums'],'sample_rate':48000}))
    path=separation.mix(tmp_path,'test','htdemucs',['vocals','drums'])
    path.write_bytes(b'broken cached output')
    assert separation.mix(tmp_path,'test','htdemucs',['vocals','drums'])==path
    assert np.allclose(sf.read(path)[0],.2)
    sf.write(root/'drums.wav',np.full((480,2),.3),48000,subtype='FLOAT')
    new=separation.mix(tmp_path,'test','htdemucs',['vocals','drums'])
    assert new!=path and np.allclose(sf.read(new)[0],.4)
    (root/'drums.wav').unlink()
    assert not separation.status(tmp_path,'test','htdemucs')['ready']
    with pytest.raises(ValueError):separation.mix(tmp_path,'test','htdemucs',['vocals','drums'])


def test_open_failure_releases_previously_opened_stems(tmp_path,monkeypatch):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    for name in ['vocals','drums']:sf.write(root/(name+'.wav'),np.full((480,2),.1),48000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals','drums'],'sample_rate':48000,'activity':{}}))
    original=sf.SoundFile;opened=[]
    def fail_second(file,*args,**kwargs):
        if isinstance(file,Path):
            if file.name=='vocals.wav':raise OSError('fixture second decoder failure')
            handle=original(file,*args,**kwargs);opened.append(handle);return handle
        return original(file,*args,**kwargs)
    monkeypatch.setattr(sf,'SoundFile',fail_second)
    with pytest.raises(OSError):separation.mix(tmp_path,'test','htdemucs',['vocals','drums'])
    assert len(opened)==1 and opened[0].closed
    assert not list(root.glob('*.tmp.wav'))


@pytest.mark.parametrize('invalid',[np.nan,np.inf,-np.inf])
def test_solo_mix_rejects_nonfinite_samples_even_with_cached_activity(tmp_path,invalid):
    root=separation.folder(tmp_path,'test','htdemucs');root.mkdir(parents=True)
    samples=np.zeros((480,2),dtype='float32');samples[200,0]=invalid
    sf.write(root/'vocals.wav',samples,48000,subtype='FLOAT')
    (root/'manifest.json').write_text(json.dumps({'sources':['vocals'],'sample_rate':48000,'activity':{'vocals':1}}))
    with pytest.raises(ValueError,match='Ungültige Audiodaten'):
        separation.mix(tmp_path,'test','htdemucs',['vocals'])
