from backend.audio_method import describe,with_method,PROMPTS,VALENCE,LABELS
from test_api import client,wav_bytes

def test_method_records_actual_projection_and_never_attaches_clap_to_provider():
    method=describe('test model',2)
    assert len(PROMPTS)==12 and len(VALENCE)==len(LABELS)==6
    assert method['features_used_in_valence'] is False and method['calibrated'] is False
    assert method['labels'][2]['valence_weight']==-1
    legacy={'mode':'local','pipeline_version':'clap-ensemble-context-v4-features-grid5-coverage50:revision','models':{'audio':'test model'}}
    assert with_method(legacy)['audio_method']['recording']=='reconstructed'
    assert 'audio_method' not in with_method({'mode':'local','pipeline_version':'unknown'})
    assert with_method({'mode':'cloud'})['audio_method']['id']=='provider-audio'

def test_hidden_and_quiet_stems_have_persistent_explicit_restoration(client):
    identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    path=f'/api/tracks/{identity}/stems/visibility'
    assert client.post(path,json={'hidden':['vocals']}).json()['hidden_sources']==['vocals']
    assert client.post(path,json={'hidden':[],'shown':['vocals','piano']}).json()['shown_sources']==['vocals','piano']
    assert client.get(f'/api/tracks/{identity}/stems').json()['shown_sources']==['vocals','piano']
    assert client.post(path,json={'hidden':['vocals'],'shown':['vocals']}).status_code==422
    client.post(f'/api/tracks/{identity}/cache/delete',json={})
    assert client.get(f'/api/tracks/{identity}/stems').json()['shown_sources']==[]
