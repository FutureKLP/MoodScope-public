import json
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
