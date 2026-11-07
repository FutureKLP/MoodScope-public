import numpy as np
import pytest
from backend.audio_method import prepare_emotion_audio, prompt_diagnostics, describe_current
from backend.models import PIPELINE_VERSION


def test_gain_invariance_and_original_dynamics():
    t=np.arange(48000)/48000
    source=(.2*np.sin(2*np.pi*220*t)*(1+t)).astype('float32')
    original=source.copy()
    prepared,info=prepare_emotion_audio(source)
    quiet,_=prepare_emotion_audio(source*10**(-12/20))
    np.testing.assert_allclose(prepared,quiet,atol=1e-7)
    np.testing.assert_array_equal(source,original)
    assert info['rms']==pytest.approx(np.sqrt(np.mean(source.astype(float)**2)))
    assert np.sqrt(np.mean(prepared**2))==pytest.approx(.1)
    mask=np.abs(source)>.01
    assert np.std(prepared[mask]/source[mask])<1e-6


def test_peak_ceiling_silence_and_invalid_input():
    transient=np.zeros(10000,dtype='float32');transient[0]=1
    prepared,_=prepare_emotion_audio(transient)
    assert prepared.max()<=.990001
    assert not prepare_emotion_audio(np.zeros(100))[0].any()
    for bad in [[],[float('nan')],[float('inf')],np.ones((2,3))]:
        with pytest.raises(ValueError):prepare_emotion_audio(bad)


def test_wording_disagreement_survives_confident_individual_scores():
    pairs=np.zeros((6,2));pairs[0,0]=20;pairs[2,1]=20
    result=prompt_diagnostics(pairs)
    assert not result['prompt_winners_agree']
    assert result['prompt_valence_min']<-.99 and result['prompt_valence_max']>.99
    result=prompt_diagnostics(np.repeat(pairs[:,:1],2,axis=1))
    assert result['prompt_winners_agree']
    assert result['prompt_valence_min']==result['prompt_valence_max']


def test_new_method_has_no_acoustic_offsets_and_separate_cache_version():
    method=describe_current('authored',5)
    assert PIPELINE_VERSION.startswith(method['id'])
    assert not method['features_used_in_valence']
    assert method['temporal_filter'] is None
    assert not method['calibrated']


def test_production_engine_uses_control_and_retains_original_measurement(monkeypatch,tmp_path):
    import torch
    from types import SimpleNamespace
    from backend.models import Engines
    class Inputs(dict):
        def to(self,device):return self
    captured=[]
    def processor(**kwargs):
        captured.append(kwargs['audio'].copy())
        return Inputs()
    engine=Engines();engine.data=tmp_path;engine.processor=processor
    engine.audio_model=lambda **kwargs:SimpleNamespace(logits_per_audio=torch.arange(12.).reshape(1,12))
    monkeypatch.setattr(engine,'device',lambda:'cpu')
    audio=np.full(48000,.25,dtype='float32')
    row=engine.audio(audio,48000,lambda *args:None)[0]
    assert np.max(captured[0])==pytest.approx(.1)
    assert row['rms']==.25 and np.all(audio==.25)
    assert 'prompt_winners_agree' in row and 'musical_adjustment' not in row
    assert row['context_end']==1 and row['end']==1
