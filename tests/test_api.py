import importlib
import io
import wave
import subprocess
import json
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    module = importlib.import_module('backend.app')
    monkeypatch.setattr(module, 'DATA', tmp_path)
    with module.job_lock:module.jobs.clear()
    module.cloud.configure('',False)
    return TestClient(module.app)


def wav_bytes():
    buf=io.BytesIO()
    with wave.open(buf,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(48000)
        wav.writeframes(b'\0\0'*48000)
    return buf.getvalue()


def test_interpretation_is_restored_regenerated_and_deleted_with_cache(client,monkeypatch):
    module=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('test.wav',wav_bytes())}).json()['id']
    with module.db() as conn:
        conn.execute('INSERT INTO cache VALUES (?,?)',(f'latest:{identity}:local',json.dumps({'audio':[],'lyrics':[]})))
    calls=[]
    def interpret(*args):
        calls.append(1)
        return {'text':'Vorsichtige Testdeutung auf Basis vorhandener Textbelege.','time':None,'model':'fixture'}
    monkeypatch.setattr(module.insights,'interpretation',interpret)
    module.jobs['interpret']={'status':'running'}
    module.run_interpretation('interpret',identity,module.InterpretationRequest())
    assert module.jobs['interpret']['status']=='done'
    saved=client.get(f'/api/tracks/{identity}/interpretation').json()
    assert saved['cached'] and saved['text'].startswith('Vorsichtige')
    module.run_interpretation('interpret',identity,module.InterpretationRequest())
    assert len(calls)==1
    module.run_interpretation('interpret',identity,module.InterpretationRequest(force=True))
    assert len(calls)==2
    client.post(f'/api/tracks/{identity}/notes',json={'interpretation':'My own note'})
    assert client.post(f'/api/tracks/{identity}/cache/delete').status_code==200
    assert client.get(f'/api/tracks/{identity}/interpretation').status_code==404
    assert client.get(f'/api/tracks/{identity}/notes').json()['interpretation']=='My own note'


def test_external_text_provider_requires_explicit_consent(client):
    identity=client.post('/api/tracks',files={'file':('test.wav',wav_bytes())}).json()['id']
    profile=client.post('/api/providers',json={'name':'Local test','base_url':'http://127.0.0.1:11434/v1','model':'test','api_key':'fixture-key'}).json()
    assert 'api_key' not in profile
    response=client.post(f'/api/tracks/{identity}/interpret',json={'provider_id':profile['id']})
    assert response.status_code==422
    assert 'Zustimmung' in response.json()['detail']
    assert 'fixture-key' not in client.get('/api/providers').text


def test_research_requires_explicit_recording_choice_and_restores_it(client,monkeypatch):
    module=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('test.wav',wav_bytes())}).json()['id']
    recording='12345678-1234-1234-1234-123456789abc'
    monkeypatch.setattr(module.research,'search',lambda *a:{'candidates':[{'id':recording}],'source':'MusicBrainz'})
    monkeypatch.setattr(module.research,'details',lambda *a:{'title':'Public test','url':'https://musicbrainz.org/recording/'+recording,'credits':[]})
    assert client.post(f'/api/tracks/{identity}/research',json={'title':'Public test'}).status_code==200
    assert client.get(f'/api/tracks/{identity}/research').json() is None
    assert client.post(f'/api/tracks/{identity}/research/{recording}').status_code==200
    assert client.get(f'/api/tracks/{identity}/research').json()['title']=='Public test'


def test_failures_have_diagnostic_id_but_no_exception_payload(client,monkeypatch):
    module=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('test.wav',wav_bytes())}).json()['id']
    def fail(*a):raise RuntimeError('PRIVATE LYRICS')
    monkeypatch.setattr(module.insights,'acoustic_features',fail)
    module.jobs['details']={'status':'running'};module.run_details('details',identity)
    assert 'Fehler-ID:' in module.jobs['details']['message']
    report=client.get('/api/diagnostics').json()
    assert report['recent'] and 'PRIVATE LYRICS' not in json.dumps(report)


def test_import_real_audio_and_serve_normalized_file(client):
    response = client.post('/api/tracks',files={'file':('silence.wav',wav_bytes(),'audio/wav')})
    assert response.status_code == 200, response.text
    metadata = response.json()
    assert metadata['duration'] == pytest.approx(1)
    assert metadata['channels']==2
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


def test_personal_notes_persist_separately_from_analysis(client):
    metadata=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()
    route=f"/api/tracks/{metadata['id']}/notes"
    notes={'interpretation':'My own interpretation','personnel':'Manually verified','instruments':'piano','genre':'test','bpm':120}
    assert client.post(route,json=notes).status_code==200
    assert client.get(route).json()==notes
    assert client.post(route,json={**notes,'bpm':-1}).status_code==422


def test_keys_never_return_in_settings_or_validation_errors(client):
    key='test'+'key-'+'X'*25
    response=client.post('/api/settings/cloud',json={'api_key':key,'free_project_confirmed':True})
    assert response.status_code==200
    assert key not in response.text
    assert key not in client.get('/api/settings').text
    invalid=client.post('/api/settings/cloud',json={'api_key':key*100,'free_project_confirmed':True})
    assert invalid.status_code==422
    assert key not in invalid.text
    assert client.post('/api/settings/cloud',json={}).json()['configured'] is False


def test_cloud_mode_needs_key_and_upload_permission(client):
    identity=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()['id']
    route=f'/api/tracks/{identity}/analyze'
    assert client.post(route,json={'mode':'cloud'}).status_code==422
    assert client.post(route,json={'mode':'cloud','upload_consent':True}).status_code==422


def test_cloud_job_never_calls_local_models(client,monkeypatch):
    module=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()['id']
    def forbidden(*args):raise AssertionError('Local model must not run in cloud mode')
    monkeypatch.setattr(module.engines,'audio',forbidden)
    monkeypatch.setattr(module.engines,'lyrics',forbidden)
    monkeypatch.setattr(module.engines,'transcribe',forbidden)
    monkeypatch.setattr(module.engines,'device',forbidden)
    monkeypatch.setattr(module.cloud,'audio_mood',lambda *a:[{'start':0,'end':1,'valence':.2,'scores':{}}])
    monkeypatch.setattr(module.cloud,'lyric_mood',lambda *a:[])
    module.jobs['cloud']={'status':'running'}
    module.run_job('cloud',identity,module.AnalyzeRequest(mode='cloud',upload_consent=True,whisper=True))
    assert module.jobs['cloud']['status']=='done',module.jobs['cloud']
    assert module.jobs['cloud']['result']['device']=='API'


def test_model_catalog_rejects_arbitrary_models(client):
    result=client.get('/api/models')
    assert result.status_code==200
    assert len(result.json()['models'])>=5
    assert client.post('/api/models/download',json={'model_id':'untrusted/model'}).status_code==422
    assert client.post('/api/models/select',json={'model_id':'untrusted/model'}).status_code==422


def test_busy_jobs_are_not_lost(client):
    module=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('silence.wav',wav_bytes())}).json()['id']
    module.jobs['active']={'status':'running','message':'working'}
    assert client.post(f'/api/tracks/{identity}/analyze',json={}).status_code==409
    assert client.get('/api/jobs/active').json()['message']=='working'


def test_invalid_link_fails_before_downloader(client):
    assert client.post('/api/tracks/link',json={'url':'https://127.0.0.1/music'}).status_code==422
