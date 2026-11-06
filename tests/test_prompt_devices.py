import importlib
import json
import pytest
from test_api import client,wav_bytes
from backend import prompt_presets as prompts,runtime_devices as devices

def test_prompt_presets_are_local_scoped_and_reset_preserves_variants(tmp_path):
    before=prompts.fingerprint(tmp_path,['audio'])
    content=prompts.DEFAULTS['audio'].replace('joyful','cheerful')
    saved=prompts.change(tmp_path,'save','audio',name='Authored variant',text=content)
    identity=saved['presets'][0]['id']
    assert prompts.fingerprint(tmp_path,['audio'])==before
    prompts.change(tmp_path,'select','audio',identity)
    assert prompts.content(tmp_path,'audio')==content and prompts.fingerprint(tmp_path,['audio'])!=before
    assert prompts.content(tmp_path,'whole_en')==prompts.DEFAULTS['whole_en']
    prompts.change(tmp_path,'select','audio','default')
    assert prompts.fingerprint(tmp_path,['audio'])==before and len(prompts.status(tmp_path)['presets'])==1
    with pytest.raises(ValueError):prompts.change(tmp_path,'save','audio',name='Wrong lines',text='Only one authored description.')
    with pytest.raises(ValueError):prompts.change(tmp_path,'select','whole_en',identity)
    prompts.change(tmp_path,'delete','audio',identity)
    assert not prompts.status(tmp_path)['presets']

def test_prompt_selection_changes_interpretation_cache_and_marks_saved_result_stale(client,monkeypatch):
    module=importlib.import_module('backend.app');identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    with module.db() as conn:conn.execute('INSERT INTO cache VALUES (?,?)',(f'latest:{identity}:local',json.dumps({'audio':[],'lyrics':[]})))
    calls=[]
    monkeypatch.setattr(module.insights,'interpretation',lambda *args:(calls.append(1) or {'text':'An authored reading based on supplied text.','time':None,'model':'fixture'}))
    module.jobs['read']={'status':'running'};module.run_interpretation('read',identity,module.InterpretationRequest())
    saved=client.post('/api/prompts',json={'action':'save','purpose':'whole_de','name':'Authored task','content':'Beschreibe vorsichtig die Entwicklung und alternative Lesarten.'}).json()
    assert client.post('/api/prompts',json={'action':'select','purpose':'whole_de','preset_id':saved['presets'][0]['id']}).status_code==200
    assert client.get(f'/api/tracks/{identity}/interpretation').json()['stale']
    module.run_interpretation('read',identity,module.InterpretationRequest())
    assert len(calls)==2
    assert client.post('/api/tracks/'+identity+'/cache/delete').status_code==200
    assert client.get('/api/prompts').json()['presets']

def test_device_preferences_validate_available_hardware_and_do_not_overwrite_cache(client,monkeypatch,tmp_path):
    monkeypatch.setattr(devices,'available',lambda:[{'id':'auto','name':'Automatic'},{'id':'cpu','name':'CPU'},{'id':'cuda:1','name':'Authored GPU'}])
    selection={p:'cpu' for p in devices.PURPOSES};selection['interpretation']='cuda:1'
    assert client.post('/api/devices',json=selection).status_code==200
    assert client.get('/api/devices').json()['active']['interpretation']=='cuda:1'
    selection['lyrics']='cuda:9';assert client.post('/api/devices',json=selection).status_code==422
    module=importlib.import_module('backend.app');module.jobs['busy']={'status':'running'}
    selection['lyrics']='cpu';assert client.post('/api/devices',json=selection).status_code==409
    assert client.post('/api/prompts',json={'action':'select','purpose':'audio','preset_id':'default'}).status_code==409

def test_custom_interpretation_instruction_reaches_provider_with_fixed_grounding_rules(tmp_path,monkeypatch):
    from backend import insights,providers
    value=prompts.change(tmp_path,'save','whole_en',name='Authored style',text='Use concise numbered observations and compare two possible readings.')
    prompts.change(tmp_path,'select','whole_en',value['presets'][0]['id']);seen=[]
    monkeypatch.setattr(providers,'generate',lambda *args:(seen.append(args[-1]) or {'text':'The supplied words may express cautious hope for the future.'}))
    insights.interpretation(tmp_path,None,{'lyrics':[{'start':0,'end':2,'text':'I hope for tomorrow.'}],'audio':[]},{},provider_id='authored',language='en')
    assert 'concise numbered' in seen[0] and 'cannot hear audio' in seen[0] and 'Write every paragraph in English' in seen[0]

def test_method_records_the_actual_custom_audio_descriptions(tmp_path):
    from backend.audio_method import describe_musical
    text=prompts.DEFAULTS['audio'].replace('joyful','cheerful')
    value=prompts.change(tmp_path,'save','audio',name='Authored comparison',text=text);prompts.change(tmp_path,'select','audio',value['presets'][0]['id'])
    assert describe_musical('authored',2,tmp_path)['labels'][0]['prompts']==text.splitlines()[:2]
