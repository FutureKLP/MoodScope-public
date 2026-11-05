import json
from types import SimpleNamespace
import pytest
from backend import providers


@pytest.mark.parametrize('value',['https://example.com/v1?token=value','http://example.com/v1','http://169.254.169.254/v1','file:///tmp/model','https://'+':'.join(['user','password'])+chr(64)+'example.com'])
def test_invalid_model_server_endpoints(value):
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
