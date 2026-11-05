import json
import pytest
from backend import language,insights
from test_api import client,wav_bytes

def test_translates_interface_fields_without_touching_user_data():
    data={'detail':'Song nicht gefunden','note':'Nicht unterstütztes Modell','title':'Song nicht gefunden','text':'Song nicht gefunden','tags':{'note':'Nicht unterstütztes Modell'},'warnings':['Keine synchronisierten Lyrics: Biggest Split ist nicht verfügbar.']}
    translated=language.response(data,'en')
    assert translated['detail']=='Song not found' and translated['note']=='Unsupported model'
    assert translated['title']==translated['text']=='Song nicht gefunden'
    assert translated['tags']==data['tags']
    assert translated['warnings'][0].startswith('No synchronised lyrics')

def test_english_errors_catalogue_and_validation_do_not_leak_input(client):
    response=client.get('/api/tracks/missing/notes',headers={'Accept-Language':'en-GB,en;q=0.9'})
    assert response.status_code==404 and response.json()['detail']=='Song not found'
    assert response.headers['Content-Language']=='en'
    models=client.get('/api/models',headers={'Accept-Language':'en'}).json()['models']
    assert all('keine' not in m['description'] for m in models)
    assert client.post('/api/providers',json={'api_key':'confidential-test-input'},headers={'Accept-Language':'en'}).status_code==422
    assert 'confidential-test-input' not in client.post('/api/providers',json={'api_key':'confidential-test-input'},headers={'Accept-Language':'en'}).text

def test_language_caches_are_separate_and_both_deleted(client,monkeypatch):
    from backend import app as module
    identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    with module.db() as conn:conn.execute('INSERT INTO cache VALUES (?,?)',(f'latest:{identity}:local',json.dumps({'audio':[],'lyrics':[]})))
    calls=[]
    def interpret(*args):
        calls.append(args[-1]);return {'text':'English interpretation of the authored lyrics.' if args[-1]=='en' else 'Deutsche Interpretation des selbst geschriebenen Textes.','time':None,'model':'fixture'}
    monkeypatch.setattr(module.insights,'interpretation',interpret)
    for locale in ['de','en','de']:
        module.jobs['locale-test']={'status':'running'}
        module.run_interpretation('locale-test',identity,module.InterpretationRequest(language=locale))
        assert module.jobs['locale-test']['status']=='done'
    assert calls==['de','en']
    assert client.get(f'/api/tracks/{identity}/interpretation?language=en').json()['text'].startswith('English')
    assert client.get(f'/api/tracks/{identity}/interpretation?language=de').json()['text'].startswith('Deutsche')
    own={'interpretation':'Song nicht gefunden'}
    client.post(f'/api/tracks/{identity}/notes',json=own,headers={'Accept-Language':'en'})
    assert client.get(f'/api/tracks/{identity}/notes',headers={'Accept-Language':'en'}).json()['interpretation']==own['interpretation']
    client.post(f'/api/tracks/{identity}/cache/delete',json={})
    for locale in ['de','en']:assert client.get(f'/api/tracks/{identity}/interpretation?language={locale}').status_code==404
    assert client.get(f'/api/tracks/{identity}/notes').json()['interpretation']==own['interpretation']

def test_server_prompt_and_audio_evidence_follow_output_language(tmp_path,monkeypatch):
    from backend import providers
    prompts=[]
    monkeypatch.setattr(providers,'generate',lambda *args:(prompts.append(args[-1]) or {'text':'The narrator expresses a possible hope for tomorrow, although this reading is uncertain.'}))
    data={'lyrics':[{'start':0,'end':4,'text':'Ich hoffe auf morgen.'}],'audio':[{'start':0,'end':4,'valence':.2,'scores':{'joy':.7}}],'features':{'bpm':120,'brightness_hz':1800}}
    result=insights.interpretation(tmp_path,None,data,{},provider_id='fixture',language='en')
    assert 'Write every paragraph in English' in prompts[0] and 'Ich hoffe auf morgen.' in prompts[0]
    assert '120.0 BPM' in result['audio_evidence'] and 'spectral centroid' in result['audio_evidence']
    assert insights.interpretation(tmp_path,None,{'lyrics':[],'audio':[]},{},language='en')['text'].startswith('No lyrics')
    with pytest.raises(RuntimeError):insights.validate_text_interpretation('I can hear a piano in a musical key.')

@pytest.mark.parametrize('origin',['https://untrusted.example','null','http://127.0.0.1.attacker.invalid'])
def test_untrusted_origin_cannot_write_profiles_even_with_language_header(client,origin):
    assert client.post('/api/providers',headers={'Origin':origin,'Accept-Language':'en'},json={}).status_code==403
