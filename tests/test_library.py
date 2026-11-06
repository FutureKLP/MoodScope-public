import io
import importlib
import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient
from backend import library


@pytest.fixture
def state(tmp_path,monkeypatch):
    module=importlib.import_module('backend.app')
    monkeypatch.setattr(module,'DATA',tmp_path)
    with module.job_lock:module.jobs.clear()
    calls=[]
    monkeypatch.setattr(module.engines,'audio',lambda *a:calls.append(1) or [{'start':0,'end':1,'valence':.2,'scores':{}}])
    monkeypatch.setattr(module.engines,'lyrics',lambda *a:[])
    monkeypatch.setattr(module.engines,'device',lambda:'cpu')
    monkeypatch.setattr(module.insights,'acoustic_features',lambda y,sr:{'duration':len(y)/sr,'rms_mean':0.,'bpm':None})
    return module,TestClient(module.app),calls


def sample(seconds=1):
    buffer=io.BytesIO();sr=48000
    t=np.arange(sr*seconds)/sr
    audio=(.1*(1+.7*np.sin(2*np.pi*.7*t))*np.sin(2*np.pi*220*t)).astype('float32')
    sf.write(buffer,audio,sr,format='WAV')
    return buffer.getvalue()


def test_force_reanalysis_bypasses_full_and_audio_cache(state):
    module,client,calls=state
    track=client.post('/api/tracks',files={'file':('test.wav',sample())}).json()
    module.jobs['job']={'status':'running'}
    module.run_job('job',track['id'],module.AnalyzeRequest())
    module.run_job('job',track['id'],module.AnalyzeRequest())
    assert len(calls)==1
    assert client.get(f"/api/tracks/{track['id']}/analysis").json()['cached']
    module.run_job('job',track['id'],module.AnalyzeRequest(force=True))
    assert len(calls)==2


def test_cache_delete_removes_analysis_but_preserves_notes_and_audio(state):
    module,client,calls=state
    identity=client.post('/api/tracks',files={'file':('test.wav',sample())}).json()['id']
    module.jobs['job']={'status':'running'};module.run_job('job',identity,module.AnalyzeRequest())
    client.post(f'/api/tracks/{identity}/notes',json={'interpretation':'Keep this note'})
    result=client.post(f'/api/tracks/{identity}/cache/delete',json={})
    assert result.status_code==200,result.text
    assert result.json()['deleted_cache_entries']>=2
    assert client.get(f'/api/tracks/{identity}/analysis').status_code==404
    assert client.get(f'/api/tracks/{identity}/notes').json()['interpretation']=='Keep this note'
    assert client.get(f'/api/tracks/{identity}/audio').status_code==200
    module.run_job('job',identity,module.AnalyzeRequest())
    assert len(calls)==2


def test_reimport_recognizes_file_and_lists_only_one_track(state):
    module,client,_=state
    first=client.post('/api/tracks',files={'file':('one.wav',sample())}).json()
    second=client.post('/api/tracks',files={'file':('renamed.wav',sample())}).json()
    assert first['id']==second['id']
    assert second['cache_match']=='same-file'
    assert len(client.get('/api/library').json()['tracks'])==1


def test_metadata_match_requires_matching_recording(state,tmp_path):
    import mutagen
    module,client,_=state
    source=tmp_path/'source.flac'
    audio,sr=sf.read(io.BytesIO(sample(20)))
    sf.write(source,audio,sr)
    tags=mutagen.File(source);tags['artist']='Test Artist';tags['title']='Test Song';tags.save()
    first=client.post('/api/tracks',files={'file':('first.flac',source.read_bytes())}).json()
    tags=mutagen.File(source);tags['comment']='Different file tags';tags.save()
    second=client.post('/api/tracks',files={'file':('second.flac',source.read_bytes())}).json()
    assert first['id']!=second['id']
    assert second.get('reuse_source_id')==first['id'],second
    assert len(client.get('/api/library').json()['tracks'])==1
    sf.write(source,audio[::-1],sr)
    tags=mutagen.File(source);tags['artist']='Test Artist';tags['title']='Test Song';tags.save()
    other=client.post('/api/tracks',files={'file':('other.flac',source.read_bytes())}).json()
    assert not other.get('reuse_source_id')


def test_library_signature_rejects_silence_and_large_gain_changes(tmp_path):
    a=tmp_path/'a.wav';b=tmp_path/'b.wav'
    audio,sr=sf.read(io.BytesIO(sample(20)));sf.write(a,audio,sr);sf.write(b,audio*.3,sr)
    assert not library.same_recording(library.signature(a),library.signature(b))
    sf.write(b,np.zeros(48000*20),48000)
    assert library.signature(b) is None

def test_legacy_song_cache_and_stem_preferences_are_removed(state):
    import json
    module,client,_=state
    identity=client.post('/api/tracks',files={'file':('test.wav',sample())}).json()['id']
    removed=[f'interpretation-latest:{identity}:local:default:de',f'research-recording:{identity}:itunes:1',f'research-results:{identity}']
    with module.db() as conn:
        for key in removed+[f'stem-visibility:{identity}:htdemucs_auto']:
            conn.execute('INSERT INTO cache VALUES (?,?)',(key,json.dumps({'fixture':True})))
        module.own(conn,f'stem-visibility:{identity}:htdemucs_auto',identity)
        conn.execute('INSERT INTO cache VALUES (?,?)',('interpretation:legacy-hash',json.dumps({'fixture':True})))
        removed.append('interpretation:legacy-hash')
    response=client.post(f'/api/tracks/{identity}/cache/delete')
    assert response.json()['affected_ids']==[identity]
    with module.db() as conn:keys={r[0] for r in conn.execute('SELECT key FROM cache')}
    assert not keys.intersection(removed)
    assert f'stem-visibility:{identity}:htdemucs_auto' not in keys
    assert client.post(f'/api/tracks/{identity}/delete').status_code==200
    with module.db() as conn:assert not conn.execute('SELECT key FROM cache').fetchall()


@pytest.mark.parametrize('delete_song',[False,True])
def test_inflight_research_cannot_restore_deleted_cache(state,monkeypatch,delete_song):
    module,client,_=state
    identity=client.post('/api/tracks',files={'file':('test.wav',sample())}).json()['id']
    def search(*args):
        endpoint='delete' if delete_song else 'cache/delete'
        assert client.post(f'/api/tracks/{identity}/{endpoint}').status_code==200
        return {'candidates':[],'note':'Authored research fixture'}
    monkeypatch.setattr(module.research,'search',search)
    response=client.post(f'/api/tracks/{identity}/research',json={'artist':'Fixture','title':'Fixture','force':True})
    assert response.status_code==409,response.text
    with module.db() as conn:assert not conn.execute("SELECT key FROM cache WHERE key LIKE 'research-%'").fetchall()
