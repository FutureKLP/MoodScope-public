import importlib
import io
import wave
import subprocess
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    module = importlib.import_module('backend.app')
    monkeypatch.setattr(module, 'DATA', tmp_path)
    return TestClient(module.app)


def wav_bytes():
    buf=io.BytesIO()
    with wave.open(buf,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(48000)
        wav.writeframes(b'\0\0'*48000)
    return buf.getvalue()


def test_import_real_audio_and_serve_normalized_file(client):
    response = client.post('/api/tracks',files={'file':('silence.wav',wav_bytes(),'audio/wav')})
    assert response.status_code == 200, response.text
    metadata = response.json()
    assert metadata['duration'] == pytest.approx(1)
    audio = client.get(f"/api/tracks/{metadata['id']}/audio")
    assert audio.status_code == 200
    assert audio.content[:4] == b'RIFF'
    assert client.get(f"/api/tracks/{metadata['id']}/audio",headers={'Range':'bytes=0-15'}).status_code == 206


def test_invalid_media_and_missing_track(client):
    assert client.post('/api/tracks',files={'file':('bad.txt',b'hello')}).status_code == 415
    assert client.post('/api/tracks',files={'file':('bad.mp3',b'hello')}).status_code == 422
    assert client.get('/api/tracks/missing/audio').status_code == 404


def test_local_origin_protection(client):
    assert client.post('/api/tracks',headers={'Origin':'https://evil.example'},files={'file':('a.wav',b'x')}).status_code == 403
    assert client.get('/api/jobs/anything',headers={'Host':'evil.example'}).status_code == 403


def test_cache_hit_skips_inference(client, monkeypatch):
    module = importlib.import_module('backend.app')
    metadata=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()
    calls=[]
    def audio(y,sr,progress):
        calls.append(1)
        return [{'start':0.,'end':1.,'valence':.2,'scores':{}}]
    monkeypatch.setattr(module.engines,'audio',audio)
    monkeypatch.setattr(module.engines,'lyrics',lambda lines,progress: [])
    monkeypatch.setattr(module.engines,'device',lambda: 'cpu')
    request=module.AnalyzeRequest()
    module.jobs['test']={'status':'running'}
    module.run_job('test',metadata['id'],request)
    assert module.jobs['test']['status']=='done', module.jobs['test']
    assert not module.jobs['test']['result']['cached']
    module.run_job('test',metadata['id'],request)
    assert module.jobs['test']['result']['cached']
    assert len(calls)==1


@pytest.mark.parametrize('extension', ['mp3','flac'])
def test_compressed_audio_formats(client, tmp_path, extension):
    import imageio_ffmpeg
    source = tmp_path/'source.wav'
    source.write_bytes(wav_bytes())
    output = tmp_path/f'source.{extension}'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-i',str(source),
                    '-metadata','artist=MoodScope Test','-metadata','title=Calibration',str(output)],check=True)
    response=client.post('/api/tracks',files={'file':(output.name,output.read_bytes())})
    assert response.status_code==200, response.text
    assert response.json()['duration']==pytest.approx(1,abs=.1)
    assert response.json()['artist']=='MoodScope Test'
    assert response.json()['title']=='Calibration'


def test_lyrics_search_cache_and_instrumental(client, monkeypatch):
    module = importlib.import_module('backend.app')
    metadata=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()
    calls=[]
    def get(*args,**kwargs):
        import httpx
        calls.append(1)
        return httpx.Response(200,json={'syncedLyrics':None,'plainLyrics':None,'instrumental':True},request=httpx.Request('GET',args[0]))
    monkeypatch.setattr(module.httpx,'get',get)
    route=f"/api/tracks/{metadata['id']}/lyrics/search"
    first=client.post(route,json={'artist':'Test','title':'Silence'})
    assert first.json()['instrumental'] is True
    second=client.post(route,json={'artist':'Test','title':'Silence'})
    assert second.json()['cached'] is True
    assert len(calls)==1


def test_analysis_error_is_visible(client, monkeypatch):
    module = importlib.import_module('backend.app')
    metadata=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()
    def fail(*args):
        raise RuntimeError('model unavailable')
    monkeypatch.setattr(module.engines,'audio',fail)
    module.jobs['failure']={'status':'running'}
    module.run_job('failure',metadata['id'],module.AnalyzeRequest())
    assert module.jobs['failure']['status']=='error'
    assert 'model unavailable' in module.jobs['failure']['message']
