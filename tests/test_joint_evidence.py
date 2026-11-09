import importlib
import json
import pytest
from backend.joint_evidence import timeline
from backend.expression_compare import project_analysis
from test_api import client,wav_bytes


def data():
    return {'audio':[{'start':0,'end':10,'valence':.8,'scores':{'joy':1}}],
            'lyrics':[{'start':0,'end':10,'valence':-.8,'text':'Authored sadness.'}], 'features':{}}


def test_opposing_modalities_do_not_become_a_falsely_neutral_fused_score():
    source=data();before=json.dumps(source)
    packet=timeline(source)
    assert packet['rows'][0]['relation']=='contrasting'
    assert packet['rows'][0]['lyric_valence']==-.8
    assert packet['fused_score'] is None and not packet['calibrated']
    assert json.dumps(source)==before


def test_uncertain_words_and_prompt_disagreement_block_strong_joint_reading():
    source=data();source['lyrics'][0]['uncertain']=True
    assert timeline(source)['rows'][0]['relation']=='uncertain_text'
    source=data();source['audio'][0].update(prompt_valence_min=-.5,prompt_valence_max=.6)
    assert timeline(source)['rows'][0]['relation']=='uncertain_audio'
    source['audio'][0].pop('prompt_valence_min');source['audio'][0].pop('prompt_valence_max')
    source['lyrics'][0]['end']=2
    assert timeline(source)['rows'][0]['relation']=='music_only'


def test_simultaneous_lyrics_cannot_inflate_coverage_or_hide_missing_text():
    source=data();source['lyrics']=[{'start':0,'end':3,'valence':.8}]*3
    row=timeline(source)['rows'][0]
    assert row['text_coverage']==pytest.approx(.3) and row['relation']=='music_only'


def test_whole_song_summary_preserves_a_brief_contradiction():
    from backend.joint_evidence import observations
    source={'audio':[{'start':i,'end':i+1,'valence':.8} for i in range(100)],
            'lyrics':[{'start':i,'end':i+1,'valence':-.8 if i==17 else .8} for i in range(100)]}
    selected=observations(source)
    assert len(selected)<=8 and any(row['start']==17 for row in selected)
    assert selected[0]['start']==0 and selected[-1]['end']==100


def test_direct_regression_keeps_lyrics_features_and_source_identity():
    source=data();projected=project_analysis(source,{'rows':[{'start':0,'end':10,'valence':.6,'arousal':.9}], 'model_basis':'authored'})
    assert projected['lyrics'] is source['lyrics'] and projected['features'] is source['features']
    assert projected['audio'][0]['scores']=={} and projected['expression_source']=='Music2Emo'
    assert source['audio'][0]['valence']==.8


def test_joint_text_is_rendered_from_actual_references_without_causal_energy_claims():
    from backend.music_evidence import packet
    from backend.joint_evidence import reading
    source=data();source['features']={'rms_mean':.1,'sections':[{'start':0,'end':10,'rms':.8,'bpm':160}]}
    evidence=packet(source)
    text=reading(evidence,'en')
    assert 'opposing valence directions' in text and 'does not establish irony' in text
    assert 'L1' in text and 'do not determine a feeling' in text
    assert '+18' not in text and 'positive energy' not in text


def test_api_and_interpretation_use_the_same_current_music_source(client,monkeypatch):
    from backend import expression_compare
    app=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    source=data();source['lyrics'][0].update(start=0,end=1);source['audio'][0]['end']=1
    monkeypatch.setattr(expression_compare,'fingerprint',lambda:'fixture-current')
    with app.db() as conn:
        conn.execute('INSERT INTO cache VALUES (?,?)',(f'latest:{identity}:local',json.dumps(source)))
        conn.execute('INSERT INTO cache VALUES (?,?)',(f'expression-comparison:{identity}',json.dumps({'rows':[{'start':0,'end':1,'valence':-.7,'arousal':.4}], 'model_basis':'fixture-current'})))
    url=f'/api/tracks/{identity}/combined-evidence'
    assert client.get(url).json()['rows'][0]['relation']=='contrasting'
    value=client.get(url+'?music_source=music2emo').json()
    assert value['audio_source']=='Music2Emo' and value['rows'][0]['relation']=='aligned'
    captured=[]
    monkeypatch.setattr(app.insights,'interpretation',lambda *args,**kwargs:(captured.append(args[2]) or {'text':'Authored cautious interpretation.'}))
    app.jobs['fixture']={'status':'running'}
    app.run_interpretation('fixture',identity,app.InterpretationRequest(include_music=True,music_source='music2emo'))
    assert app.jobs['fixture']['status']=='done' and captured[0]['expression_source']=='Music2Emo'
    saved=client.get(f'/api/tracks/{identity}/interpretation?include_music=true&music_source=music2emo').json()
    assert not saved['stale']
    monkeypatch.setattr(expression_compare,'fingerprint',lambda:'changed')
    assert client.get(url+'?music_source=music2emo').status_code==409
    assert client.get(f'/api/tracks/{identity}/interpretation?include_music=true&music_source=music2emo').json()['stale']
