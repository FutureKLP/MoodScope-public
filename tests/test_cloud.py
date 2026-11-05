import json
import math
import httpx
import numpy as np
import pytest
from backend import cloud


@pytest.fixture(autouse=True)
def reset_cloud(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    cloud.configure('',False)
    yield
    cloud.configure('',False)


def fake_key():return 'test'+'key-'+'X'*25


def test_key_requires_free_project_confirmation():
    cloud.configure(fake_key(),False)
    with pytest.raises(cloud.CloudError,match='Abrechnung'):cloud.credential()
    assert 'api_key' not in cloud.settings()


def test_rate_limit_error_never_echoes_provider_secrets(monkeypatch):
    cloud.configure(fake_key(),True)
    monkeypatch.setattr(cloud.httpx,'post',lambda *a,**k:httpx.Response(429,text=fake_key()))
    with pytest.raises(cloud.CloudError) as error:cloud.request_json('test',{'type':'object'})
    assert 'Kontingent' in str(error.value)
    assert fake_key() not in str(error.value)


def test_cloud_success_uses_header_not_url_and_requires_complete_output(monkeypatch):
    cloud.configure(fake_key(),True)
    def post(url,**kwargs):
        assert fake_key() not in url
        assert kwargs['headers']['x-goog-api-key']==fake_key()
        assert 'tools' not in kwargs['json']
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'{"answer":1}'}]}}]})
    monkeypatch.setattr(cloud.httpx,'post',post)
    assert cloud.request_json('test',{'type':'object'})=={'answer':1}
    monkeypatch.setattr(cloud.httpx,'post',lambda *a,**k:httpx.Response(200,json={'candidates':[{'finishReason':'MAX_TOKENS'}]}))
    with pytest.raises(cloud.CloudError):cloud.request_json('test',{'type':'object'})


@pytest.mark.parametrize('rows',[
    [],[{'id':0,'valence':2,'arousal':.5,'confidence':.5}],
    [{'id':0,'valence':float('nan'),'arousal':.5,'confidence':.5}],
    [{'id':1,'valence':0,'arousal':.5,'confidence':.5}],
    [{'id':0,'valence':0,'arousal':.5,'confidence':.5}]*2,
])
def test_invalid_or_missing_cloud_segments_are_rejected(rows):
    with pytest.raises(cloud.CloudError):cloud.validate_estimates({'estimates':rows},1)


def test_audio_and_lyric_requests_are_independent(monkeypatch):
    calls=[]
    def request(prompt,schema,audio=None):
        calls.append((prompt,audio))
        return {'estimates':[{'id':0,'valence':.1,'arousal':.2,'confidence':.3}]}
    monkeypatch.setattr(cloud,'request_json',request)
    monkeypatch.setattr(cloud,'encode_audio',lambda y,sr:b'FLAC')
    cloud.audio_mood(np.zeros(48000),48000,lambda *a:None)
    cloud.lyric_mood([{'start':0,'end':1,'text':'UNIQUE_TEST_WORDS'}],lambda *a:None)
    assert 'UNIQUE_TEST_WORDS' not in calls[0][0]
    assert calls[0][1]==b'FLAC'
    assert 'UNIQUE_TEST_WORDS' in calls[1][0]
    assert calls[1][1] is None


def test_oversized_audio_is_rejected_before_network():
    with pytest.raises(cloud.CloudError,match='10 Minuten'):cloud.encode_audio(np.zeros(601),1)
