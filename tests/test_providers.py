import json
from types import SimpleNamespace
import pytest
from backend import providers


@pytest.mark.parametrize('value',['https://example.com/v1?token=value','http://example.com/v1','http://169.254.169.254/v1','http://[::ffff:169.254.169.254]/v1','file:///tmp/model','https://'+':'.join(['user','password'])+chr(64)+'example.com'])
def test_invalid_model_server_endpoints(value,monkeypatch):
    monkeypatch.setattr(providers.socket,'getaddrinfo',lambda *a,**k:[(2,1,6,'',('8.8.8.8',80))])
    with pytest.raises(ValueError):providers.endpoint(value)


@pytest.mark.parametrize('protocol',['openai','anthropic'])
def test_server_adapter_and_memory_only_keys(tmp_path,monkeypatch,protocol):
    profile=providers.save(tmp_path,{'name':'Test server','protocol':protocol,'base_url':'http://127.0.0.1:11434/v1','model':'test-model','api_key':'fixture-key'})
    assert 'fixture-key' not in (tmp_path/'providers.json').read_text()
    def post(url,headers,json,**kwargs):
        assert json['model']=='test-model'
        assert 'Text evidence' in json['messages'][0]['content']
        if protocol=='anthropic':
            assert url.endswith('/messages') and headers['x-api-key']=='fixture-key'
            value={'content':[{'type':'text','text':'Eine vorsichtige Deutung des vorliegenden Textes.'}],'stop_reason':'end_turn'}
        else:
            assert url.endswith('/chat/completions') and headers['Authorization']=='Bearer fixture-key'
            assert 'max_tokens' in json
            value={'choices':[{'message':{'content':'Eine vorsichtige Deutung des vorliegenden Textes.'},'finish_reason':'stop'}]}
        return SimpleNamespace(status_code=200,json=lambda:value)
    monkeypatch.setattr(providers.httpx,'post',post)
    assert providers.generate(tmp_path,profile['id'],'Text evidence')['text']
    providers.remove(tmp_path,profile['id'])
    assert providers.status(tmp_path)['profiles']==[]


def test_provider_errors_never_echo_response_body(tmp_path,monkeypatch):
    profile=providers.save(tmp_path,{'name':'Test','protocol':'openai','base_url':'https://api.openai.com/v1','model':'test','api_key':'fixture-key'})
    monkeypatch.setattr(providers.httpx,'post',lambda *a,**k:SimpleNamespace(status_code=401,text='PRIVATE RESPONSE'))
    with pytest.raises(RuntimeError,match='HTTP 401') as error:providers.generate(tmp_path,profile['id'],'test')
    assert 'PRIVATE' not in str(error.value)


def test_gemini_profile_uses_native_api_and_removal_clears_audio_key(tmp_path,monkeypatch):
    from backend import cloud
    p=providers.save(tmp_path,{'name':'Gemini fixture','protocol':'gemini','base_url':'https://generativelanguage.googleapis.com/v1beta',
        'model':'gemini-test','api_key':'fixture-key','free_project_confirmed':True})
    monkeypatch.setattr(cloud,'MODEL','gemini-test')
    def post(url,headers,json,**kwargs):
        assert url.endswith('/models/gemini-test:generateContent')
        assert headers['x-goog-api-key']=='fixture-key'
        return SimpleNamespace(status_code=200,json=lambda:{'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'Eine vorsichtige vollständige Testdeutung.'}]}}]})
    monkeypatch.setattr(providers.httpx,'post',post)
    assert providers.generate(tmp_path,p['id'],'Authored text')['text']
    providers.activate_audio(tmp_path,p['id'])
    assert cloud.settings()['configured']
    providers.remove(tmp_path,p['id'])
    assert not cloud.settings()['configured']


@pytest.mark.parametrize('protocol,url',[('anthropic','https://api.anthropic.com/v1'),('openai','https://api.deepseek.com')])
def test_text_only_profiles_cannot_be_activated_as_audio(tmp_path,protocol,url):
    with pytest.raises(ValueError):providers.save(tmp_path,{'name':'Fixture','protocol':protocol,'base_url':url,'model':'text-fixture','audio_input':True})


def test_audio_profile_requires_explicit_capability_and_terms_and_edit_deactivates(tmp_path):
    from backend import cloud
    request={'name':'Local audio fixture','protocol':'openai','base_url':'http://127.0.0.1:11434/v1','model':'audio-fixture','api_key':''}
    p=providers.save(tmp_path,request)
    with pytest.raises(ValueError):providers.activate_audio(tmp_path,p['id'])
    p=providers.save(tmp_path,{**request,'id':p['id'],'audio_input':True})
    with pytest.raises(ValueError):providers.activate_audio(tmp_path,p['id'])
    p=providers.save(tmp_path,{**request,'id':p['id'],'audio_input':True,'audio_usage_confirmed':True})
    providers.activate_audio(tmp_path,p['id']);assert cloud.credential()==''
    assert cloud.settings()['profile_id']==p['id']
    providers.save(tmp_path,{**request,'id':p['id'],'model':'changed-model','audio_input':True,'audio_usage_confirmed':True})
    with pytest.raises(cloud.CloudError):cloud.credential()
    providers.remove(tmp_path,p['id'])


@pytest.mark.parametrize('addresses,accepted',[(['192.168.1.20'],True),(['192.168.1.20','8.8.8.8'],False),(['169.254.169.254'],False)])
def test_http_home_server_names_require_private_resolved_addresses(monkeypatch,addresses,accepted):
    monkeypatch.setattr(providers.socket,'getaddrinfo',lambda *a,**k:[(2,1,6,'',(ip,11434)) for ip in addresses])
    if accepted:assert providers.endpoint('http://authored-server.local:11434/v1')=='http://authored-server.local:11434/v1'
    else:
        with pytest.raises(ValueError):providers.endpoint('http://authored-server.local:11434/v1')


def test_home_server_connection_model_discovery_and_generation_without_key(tmp_path):
    from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
    import threading
    calls=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def send(self,value):
            raw=json.dumps(value).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            calls.append(('GET',self.path));assert not self.headers.get('Authorization')
            self.send({'data':[{'id':'authored-home-model'}]})
        def do_POST(self):
            calls.append(('POST',self.path));assert not self.headers.get('Authorization')
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));assert body['model']=='authored-home-model'
            self.send({'choices':[{'finish_reason':'stop','message':{'content':'A cautious reading of the authored text.'}}]})
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        base=f'http://127.0.0.1:{server.server_port}/v1'
        result=providers.discover_models(base);assert result=={'models':['authored-home-model'],'generated':False}
        profile=providers.save(tmp_path,{'name':'Home fixture','protocol':'openai','base_url':base,'model':result['models'][0]})
        assert providers.generate(tmp_path,profile['id'],'Authored text')['text']
        assert calls==[('GET','/v1/models'),('POST','/v1/chat/completions')]
    finally:server.shutdown();server.server_close();thread.join(timeout=3)
