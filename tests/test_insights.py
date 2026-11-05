import numpy as np
import pytest
from backend.insights import acoustic_features,audio_evidence,validate_text_interpretation
from backend.insights import interpretation_context,interpretation
from backend.insights import checked_local_generation


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


def test_whole_song_is_distinct_from_instrumental_gap():
    analysis={'lyrics':[{'start':2,'end':4,'text':'Ich hoffe auf morgen.'}]}
    whole=interpretation_context(analysis,None)
    assert whole['scope']=='whole_song' and whole['has_text'] and not whole['instrumental_position']
    assert interpretation_context(analysis,1)['instrumental_position']
    assert interpretation_context({'source_lyrics':'Eigener Text ohne Zeitmarken'},None)['has_text']


def test_invented_long_quotation_is_rejected():
    with pytest.raises(RuntimeError,match='Textzitat'):
        validate_text_interpretation('Der Erzähler sagt "Wir reisen gemeinsam durch die Welt".','Ich gehe allein durch den Regen.')
    validate_text_interpretation('Die Wörter "allein durch den Regen" können Einsamkeit andeuten.','Ich gehe allein durch den Regen.')


def test_local_repair_keeps_evidence_checks_and_never_returns_rejected_answer():
    prompts=[]
    def generate(repair):
        prompts.append(repair)
        return {'text':'Der Text sagt "Wir reisen gemeinsam durch die Welt".' if repair is None else 'Die Aussage kann Einsamkeit ausdrücken; diese Lesart bleibt vorsichtig.'}
    value=checked_local_generation(generate,'Ich gehe allein durch den Regen.')
    assert value['validation_attempts']==2 and 'Wir reisen' not in value['text']
    assert prompts[0] is None and 'KEINE Zitate' in prompts[1]


def test_invalid_local_repair_is_also_rejected():
    with pytest.raises(RuntimeError):
        checked_local_generation(lambda repair:{'text':'Ich höre deutlich eine traurige Tonart.'},'Eigener Text')


def test_missing_lyrics_returns_actionable_result_without_loading_llm(tmp_path):
    result=interpretation(tmp_path,None,{'audio':[],'lyrics':[]},{})
    assert result['missing_lyrics'] and 'Texterkennung' in result['text']


def test_acoustic_sections_are_finite_and_time_bounded():
    features=acoustic_features(np.sin(2*np.pi*220*np.arange(22050*2)/22050).astype('float32')*.1,22050)
    assert features['sections'][0]['end']==2
    assert np.isfinite(features['dynamic_range_db'])
