import numpy as np
import pytest
from backend.insights import acoustic_features,audio_evidence,validate_text_interpretation


def test_silence_does_not_invent_bpm():
    features=acoustic_features(np.zeros(22050,dtype='float32'),22050)
    assert features['bpm'] is None


def test_audio_explanation_only_uses_supplied_measurements():
    text=audio_evidence({'audio':[{'start':0,'end':5,'valence':-.5,'scores':{'sadness':.8,'joy':.2}}],
                         'features':{'bpm':120.,'brightness_hz':1800.}},2)
    assert '-0.50' in text and '120.0 BPM' in text and '1800 Hz' in text
    assert 'beweisen aber keine Ursache' in text
    assert audio_evidence({'audio':[]})=='Keine Audioanalyse für diese Stelle vorhanden.'


def test_text_only_model_claiming_it_heard_audio_is_rejected():
    with pytest.raises(RuntimeError):validate_text_interpretation('Ich höre einen traurigen Song.')
    validate_text_interpretation('Die Wörter können Verlust und Hoffnung ausdrücken. Diese Lesart ist unsicher.')
