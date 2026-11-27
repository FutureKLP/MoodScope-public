import httpx
import pytest
from backend import providers

class Body(httpx.SyncByteStream):
    def __init__(self,chunks,error=None):self.chunks=chunks;self.reads=0;self.closed=False;self.error=error
    def __iter__(self):
        for chunk in self.chunks:
            self.reads+=1
            yield chunk
        if self.error:raise self.error
    def close(self):self.closed=True

@pytest.mark.parametrize('length',[None,'1','invalid'])
def test_model_metadata_stops_oversize_receive(monkeypatch,length):
    body=Body([b' '*65536]*64)
    headers={} if length is None else {'content-length':length}
    with httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,headers=headers,stream=body))) as client:
        monkeypatch.setattr(providers.httpx,'stream',client.stream)
        monkeypatch.setattr(providers.httpx,'get',client.get)
        with pytest.raises(ValueError,match='gültige kompatible Modellliste'):
            providers.discover_models('http://127.0.0.1:11434/v1')
    assert body.closed
    assert body.reads<=31

def test_model_metadata_rejects_declared_oversize_before_body(monkeypatch):
    body=Body([b' '*65536]*64)
    with httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,headers={'content-length':'4000000'},stream=body))) as client:
        monkeypatch.setattr(providers.httpx,'stream',client.stream)
        monkeypatch.setattr(providers.httpx,'get',client.get)
        with pytest.raises(ValueError):providers.discover_models('http://127.0.0.1:11434/v1')
    assert body.closed and body.reads==0

@pytest.mark.parametrize('status,error',[(200,None),(503,None),(200,httpx.ReadTimeout('PRIVATE FIXTURE'))])
def test_model_metadata_closes_regular_error_and_interrupted_responses(monkeypatch,status,error):
    body=Body([b'{"data":[',b'{"id":"fixture-model"}]}'],error)
    with httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(status,stream=body))) as client:
        monkeypatch.setattr(providers.httpx,'stream',client.stream)
        monkeypatch.setattr(providers.httpx,'get',client.get)
        if status==200 and error is None:
            assert providers.discover_models('http://127.0.0.1:11434/v1')['models']==['fixture-model']
        else:
            with pytest.raises(ValueError) as result:providers.discover_models('http://127.0.0.1:11434/v1')
            assert 'PRIVATE FIXTURE' not in str(result.value)
    assert body.closed
    if status!=200:assert body.reads==0


@pytest.mark.parametrize('payload,expected',[(b'{"choices":[{"finish_reason":"stop","message":{"content":"A cautious interpretation of authored text."}}]}',True),(b' '*2_000_001,False)])
def test_text_generation_uses_same_receive_budget(monkeypatch,payload,expected):
    body=Body([payload[i:i+65536] for i in range(0,len(payload),65536)])
    def handler(request):
        assert request.method=='POST'
        assert request.headers['accept-encoding']=='identity'
        return httpx.Response(200,stream=body)
    profile={'base_url':'http://127.0.0.1:11434/v1','protocol':'openai','model':'fixture','name':'Fixture'}
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        monkeypatch.setattr(providers.httpx,'stream',client.stream)
        if expected:assert providers.generate_snapshot(profile,'','Authored text')['text'].startswith('A cautious')
        else:
            with pytest.raises(RuntimeError,match='gültige Textantwort'):providers.generate_snapshot(profile,'','Authored text')
    assert body.closed and body.reads<=31

def test_metadata_rejects_unrequested_compression_without_reading(monkeypatch):
    body=Body([b'compressed fixture'])
    with httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,headers={'content-encoding':'gzip'},stream=body))) as client:
        monkeypatch.setattr(providers.httpx,'stream',client.stream)
        with pytest.raises(ValueError):providers.discover_models('http://127.0.0.1:11434/v1')
    assert body.closed and body.reads==0
