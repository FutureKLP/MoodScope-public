import json
import pytest
from test_api import client
from backend.music_evidence import packet
from backend.harmony import evidence
from backend.insights import interpretation,validate_music_references,checked_local_generation


def analysis():
    return {'audio':[{'start':0,'end':2,'valence':-.5,'scores':{'anger':.6}},
                     {'start':2,'end':5,'valence':.5,'scores':{'joy':.6}}],
            'lyrics':[{'start':0,'end':5,'text':'A short authored observation about an uncertain future.'}],
            'features':{'duration':5,'rms_mean':.1,'sections':[{'start':0,'end':5,'rms':.2,'bpm':120}],
                'harmony':{'key':{'tonic':'C','mode':'major','similarity':.8,'margin':.1},
                           'key_regions':[{'start':0,'end':5,'key':None}], 'chords':[]}}}


def test_music_evidence_is_duration_weighted_and_preserves_unknown_local_key():
    data=analysis();value=packet(data)
    assert value['observations'][0]['value']['valence']==pytest.approx(.1)
    local=packet(data,1)
    assert not any('tonic' in r['value'] for r in local['observations'])
    assert local['observations'][1]['value']['relative_to_song_db']==pytest.approx(6.0206)
    assert local['observations'][1]['end']==5  # Source feature window, not an invented two-second measurement.
    assert 'independent emotional tension' in local['unmeasured']


def test_position_uses_actual_local_key_and_correct_time_scope():
    data=analysis();key={'tonic':'A','mode':'minor','similarity':.7,'margin':.04,'alternatives':[]}
    data['features']['harmony']['key_regions'][0]['key']=key
    value=packet(data,3)
    found=next(row for row in value['observations'] if row['source']=='harmony')
    assert found['value']['tonic']=='A' and found['start']==0 and found['end']==5
    assert 'A Moll' in evidence(data['features'],3)
    assert 'C Dur' not in evidence(data['features'],3)
    assert 'Globale' in evidence(data['features'])


def test_chord_examples_span_selection_and_expose_missing_coverage():
    data=analysis();data['features']['duration']=30
    data['features']['harmony']['chords']=[{'start':i,'end':i+.5,'label':f'candidate_{i}','margin':.03} for i in range(30)]
    value=packet(data);chords=next(row['value'] for row in value['observations'] if 'sequence_examples' in row['value'])
    assert chords['coverage']==.5
    assert len(chords['sequence_examples'])<=8
    assert chords['sequence_examples'][-1]['label']=='candidate_29'
    assert 'candidate_29' in evidence(data['features'])


def test_personal_notes_and_instrument_guesses_never_enter_packet():
    data=analysis();data.update(notes='private authored note',instruments=[{'instrument':'unconfirmed instrument'}])
    serialized=json.dumps(packet(data))
    assert 'private authored note' not in serialized and 'unconfirmed instrument' not in serialized


def test_whole_song_reports_energy_development_instead_of_zero_against_itself():
    data=analysis();data['features']['sections']=[{'start':0,'end':2,'rms':.1},{'start':2,'end':5,'rms':.2}]
    value=packet(data)
    energy=next(row['value'] for row in value['observations'] if 'energy_range_db' in row['value'])
    assert energy['peak_start']==2 and energy['trough_start']==0
    assert energy['energy_range_db']==pytest.approx(6.0206)
    assert 'relative_to_song_db' not in energy


def test_interpretation_prompt_does_not_use_unvalidated_category_ranking_as_lyric_evidence():
    from backend.music_evidence import prompt_rows
    rows=prompt_rows(packet(analysis()),'en')
    assert 'relative_descriptions' not in json.dumps(rows)
    assert 'category ranking has not been validated' in rows[0]['observation']


def test_grounded_prompt_reaches_provider_without_weakening_text_guards(tmp_path,monkeypatch):
    from backend import providers
    prompts=[]
    monkeypatch.setattr(providers,'generate',lambda *args:(prompts.append(args[-1]) or {'text':'The words may suggest uncertainty.'}))
    result=interpretation(tmp_path,None,analysis(),{},provider_id='fixture',language='en',include_music=True)
    assert result['music_evidence']['version']=='music-observations-v2-joint'
    assert 'Measured energy development' not in prompts[0]
    assert result['combination_method']=='referenced-joint-v1' and result['generated_music_claims'] is False
    assert 'M' in result['text']
    assert result['music_evidence']['observations'][0]['id']=='M1'


def test_text_model_cannot_invent_a_music_reference_in_joint_mode(tmp_path,monkeypatch):
    from backend import providers
    monkeypatch.setattr(providers,'generate',lambda *args:{'text':'The supplied observation M99 proves a particular musical feeling.'})
    with pytest.raises(RuntimeError,match='Musikreferenzen'):
        interpretation(tmp_path,None,analysis(),{},provider_id='fixture',language='en',include_music=True)


def test_music_references_are_checked_on_both_attempts():
    with pytest.raises(RuntimeError):validate_music_references('A possible comparison M99.',{'M1'})
    with pytest.raises(RuntimeError):validate_music_references('No observation reference here.',{'M1'})
    validate_music_references('A possible comparison M1.',{'M1'})
    attempts=[]
    def generate(repair):
        attempts.append(repair)
        return {'text':'A cautious comparison referring to '+('M99' if repair is None else 'M1')+'.'}
    result=checked_local_generation(generate,'Authored observation.',language='en',music_references={'M1'})
    assert result['validation_attempts']==2
    with pytest.raises(RuntimeError):checked_local_generation(lambda repair:{'text':'I hear a piano in the track M1.'},'',music_references={'M1'})


def test_local_language_switch_is_rejected_instead_of_saved_as_german():
    answer='A partly authored answer with '+chr(0x4E00)+' an unsupported language switch M1.'
    with pytest.raises(RuntimeError,match='Ausgabesprache'):
        checked_local_generation(lambda repair:{'text':answer},'',music_references={'M1'})


def test_music_and_text_caches_are_separate_and_both_deleted(client,monkeypatch):
    import importlib
    from test_api import wav_bytes
    module=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    with module.db() as conn:conn.execute('INSERT INTO cache VALUES (?,?)',(f'latest:{identity}:local',json.dumps(analysis())))
    calls=[]
    def generate(*args,**kwargs):
        calls.append(kwargs.get('include_music',False))
        return {'text':'A cautious authored comparison M1.','time':args[4],'model':'fixture'}
    monkeypatch.setattr(module.insights,'interpretation',generate)
    module.jobs['test']={'status':'running'}
    module.run_interpretation('test',identity,module.InterpretationRequest())
    module.run_interpretation('test',identity,module.InterpretationRequest(include_music=True))
    module.run_interpretation('test',identity,module.InterpretationRequest(include_music=True))
    assert calls==[False,True]
    assert client.get(f'/api/tracks/{identity}/interpretation').json()['interpretation_kind']=='lyrics'
    assert client.get(f'/api/tracks/{identity}/interpretation?include_music=true').json()['interpretation_kind']=='music_text_v1'
    client.post(f'/api/tracks/{identity}/cache/delete')
    assert client.get(f'/api/tracks/{identity}/interpretation?include_music=true').status_code==404
