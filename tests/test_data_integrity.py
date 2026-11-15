"""Synthetic library faults; no user media, model downloads or inference."""
import importlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading

import numpy as np
import pytest
import soundfile as sf
from backend import cancellation, storage, separation
from test_api import client, wav_bytes
from test_library import state


def imported(client):
    return client.post('/api/tracks', files={'file': ('authored.wav', wav_bytes())}).json()['id']


@pytest.mark.parametrize('committed', [False, True])
def test_process_exit_recovers_quarantine_from_database_commit_state(client, committed):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    audio = app.DATA / (identity + '.wav')
    before = audio.read_bytes()
    client.post(f'/api/tracks/{identity}/notes', json={'interpretation': 'Authored note'})
    stems = app.DATA / 'stems' / identity
    stems.mkdir(parents=True)
    (stems / 'fixture').write_bytes(b'authored stem fixture')
    # Abrupt exit bypasses Python finally blocks and closes an uncommitted DB.
    code = '''
import os, sqlite3, sys
from pathlib import Path
from backend import storage
data=Path(sys.argv[1]); identity=sys.argv[2]
quarantine=storage.quarantine_files(data,[identity])
conn=sqlite3.connect(data/'cache.sqlite3')
conn.execute('DELETE FROM cache')
conn.execute('DELETE FROM tracks WHERE id=?',(identity,))
storage.mark_deleted(conn,quarantine)
if sys.argv[3]=='True':conn.commit()
os._exit(91)
'''
    result = subprocess.run([sys.executable, '-c', code, str(app.DATA), identity, str(committed)], cwd=Path(__file__).resolve().parents[1])
    assert result.returncode == 91
    app.store.recovered_data.discard(app.DATA.resolve())
    with app.db() as conn:
        assert bool(conn.execute('SELECT 1 FROM tracks').fetchone()) is not committed
    if committed:
        assert not audio.exists() and not stems.exists()
    else:
        assert audio.read_bytes() == before and (stems / 'fixture').read_bytes() == b'authored stem fixture'
        assert client.get(f'/api/tracks/{identity}/notes').json()['interpretation'] == 'Authored note'
    assert not list(app.DATA.glob('delete-*'))


def test_sqlite_delete_failure_rolls_back_audio_stems_notes_and_caches(client):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    audio = app.DATA / (identity + '.wav'); before = audio.read_bytes()
    client.post(f'/api/tracks/{identity}/notes', json={'interpretation': 'Keep this note'})
    with app.db() as conn:
        conn.execute("CREATE TRIGGER fail_delete BEFORE DELETE ON tracks BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
        snapshot = conn.execute('SELECT * FROM cache ORDER BY key').fetchall()
    assert client.post(f'/api/tracks/{identity}/delete').status_code == 409
    assert audio.read_bytes() == before
    with app.db() as conn:
        assert conn.execute('SELECT * FROM cache ORDER BY key').fetchall() == snapshot
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'


def test_cancellation_rolls_back_all_writes_in_transaction(client):
    app = importlib.import_module('backend.app')
    event = threading.Event()
    with pytest.raises(cancellation.Cancelled), cancellation.scope(event):
        with app.db() as conn:
            conn.execute('INSERT INTO cache VALUES (?,?)', ('authored', '{}'))
            event.set()
    with app.db() as conn:assert not conn.execute('SELECT * FROM cache').fetchall()


def test_restore_conflict_preserves_both_versions_and_journal(client):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    original = app.DATA / (identity + '.wav'); before = original.read_bytes()
    quarantine = storage.quarantine_files(app.DATA, [identity])
    original.write_bytes(b'newer authored version')
    app.store.recovered_data.discard(app.DATA.resolve())
    with pytest.raises(RuntimeError, match='konflikt'):
        with app.db():pass
    assert original.read_bytes() == b'newer authored version'
    assert (quarantine / (identity + '.wav')).read_bytes() == before
    assert (quarantine / 'journal.json').is_file()


@pytest.mark.parametrize('fault', ['missing', 'moved', 'corrupt'])
def test_missing_or_corrupt_copy_keeps_notes_cache_and_can_be_reimported(client, fault):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    path = app.DATA / (identity + '.wav')
    before = path.read_bytes()
    if fault == 'missing':path.unlink()
    elif fault == 'moved':path.rename(app.DATA / 'moved-fixture.wav')
    else:path.write_bytes(b'damaged fixture')
    client.post(f'/api/tracks/{identity}/notes', json={'interpretation': 'Keep note'})
    with app.db() as conn:
        conn.execute('INSERT INTO cache VALUES (?,?)', (f'latest:{identity}:local', json.dumps({'audio': [], 'lyrics': [], 'track_id': identity})))
    response = client.get(f'/api/tracks/{identity}/audio', headers={'Accept-Language': 'en'})
    assert response.status_code == 409 and 'import' in response.json()['detail']
    assert client.get(f'/api/tracks/{identity}/analysis').status_code == 200
    assert imported(client) == identity
    assert path.read_bytes() == before
    assert client.get(f'/api/tracks/{identity}/notes').json()['interpretation'] == 'Keep note'
    if fault == 'corrupt':assert next(app.DATA.glob('*.damaged-*.wav')).read_bytes() == b'damaged fixture'


@pytest.mark.parametrize('fault', ['cycle', 'missing', 'invalid_metadata'])
def test_broken_saved_references_fail_without_mutating_rows(client, fault):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    with app.db() as conn:
        value = app.track(identity)
        value['reuse_source_id'] = identity if fault == 'cycle' else 'b' * 64
        raw = '{broken' if fault == 'invalid_metadata' else json.dumps(value)
        conn.execute('UPDATE tracks SET metadata=? WHERE id=?', (raw, identity))
    assert client.post(f'/api/tracks/{identity}/delete').status_code == 409
    with app.db() as conn:assert conn.execute('SELECT metadata FROM tracks').fetchone()[0] == raw
    assert (app.DATA / (identity + '.wav')).is_file()


def test_reimport_preserves_enriched_metadata_and_personal_notes(client, tmp_path):
    app = importlib.import_module('backend.app')
    source = tmp_path / 'source.wav';source.write_bytes(wav_bytes())
    before = source.read_bytes()
    first = app.import_path(source, 'authored.wav', {'artist': 'Authored Artist', 'title': 'Authored Title', 'album': 'Authored Album'})
    client.post(f"/api/tracks/{first['id']}/notes", json={'interpretation': 'Own note'})
    source.rename(tmp_path / 'renamed.wav')
    second = app.import_path(tmp_path / 'renamed.wav', 'renamed.wav')
    assert second['artist'] == first['artist'] and second['title'] == first['title']
    assert second['tags'] == first['tags'] and (tmp_path / 'renamed.wav').read_bytes() == before
    assert client.post(f"/api/tracks/{first['id']}/delete").status_code == 200
    assert (tmp_path / 'renamed.wav').read_bytes() == before


@pytest.mark.parametrize('raw', ['{broken', json.dumps({'track_id': 'b' * 64}), '[]'])
def test_invalid_saved_analysis_is_preserved_and_never_assigned_to_song(client, raw):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    key = f'latest:{identity}:local'
    with app.db() as conn:conn.execute('INSERT INTO cache VALUES (?,?)', (key, raw))
    assert client.get(f'/api/tracks/{identity}/analysis').status_code == 409
    with app.db() as conn:assert conn.execute('SELECT result FROM cache WHERE key=?', (key,)).fetchone()[0] == raw


def test_cache_delete_clears_legacy_music2emo_but_preserves_other_recording(client):
    app = importlib.import_module('backend.app')
    identity = imported(client)
    keys = [f'expression-comparison:{identity}', 'expression-comparison:' + 'b' * 64]
    with app.db() as conn:
        for key in keys:conn.execute('INSERT INTO cache VALUES (?,?)', (key, '{}'))
    assert client.post(f'/api/tracks/{identity}/cache/delete').status_code == 200
    with app.db() as conn:assert [r[0] for r in conn.execute('SELECT key FROM cache')] == [keys[1]]


@pytest.mark.parametrize('fault', ['corrupt', 'short', 'rate', 'channels', 'model', 'unknown', 'empty'])
def test_stem_manifest_never_advertises_incompatible_or_broken_files(tmp_path, fault):
    root = separation.folder(tmp_path, 'fixture', 'htdemucs');root.mkdir(parents=True)
    for name in ['vocals', 'drums']:sf.write(root / (name + '.wav'), np.zeros((480, 2)), 48000)
    info = {'sources': ['vocals', 'drums'], 'model': 'htdemucs', 'sample_rate': 48000, 'activity': {'vocals': 0, 'drums': 0}}
    if fault == 'corrupt':(root / 'drums.wav').write_bytes(b'broken')
    elif fault == 'short':sf.write(root / 'drums.wav', np.zeros((240, 2)), 48000)
    elif fault == 'rate':sf.write(root / 'drums.wav', np.zeros((480, 2)), 16000)
    elif fault == 'channels':sf.write(root / 'drums.wav', np.zeros((480,3)), 48000)
    elif fault == 'model':info['model'] = 'htdemucs_6s'
    elif fault == 'unknown':info['sources'] = ['../outside']
    else:info['sources'] = []
    raw = json.dumps(info);(root / 'manifest.json').write_text(raw)
    assert not separation.status(tmp_path, 'fixture', 'htdemucs')['ready']
    assert (root / 'manifest.json').read_text() == raw


def test_damaged_sqlite_is_never_replaced_with_empty_library(client):
    app = importlib.import_module('backend.app')
    path = app.DATA / 'cache.sqlite3';path.write_bytes(b'authored invalid SQLite')
    before = path.read_bytes()
    with pytest.raises(sqlite3.DatabaseError):
        with app.db():pass
    assert path.read_bytes() == before


def test_locked_cleanup_keeps_journal_and_retries_on_next_open(client, monkeypatch):
    app=importlib.import_module('backend.app');identity=imported(client)
    unlink=Path.unlink
    def locked(path,*args,**kwargs):
        if path.parent.name.startswith('delete-') and path.suffix=='.wav':raise PermissionError('authored lock')
        return unlink(path,*args,**kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path,'unlink',locked)
        response=client.post(f'/api/tracks/{identity}/delete')
    assert response.status_code==200 and response.json()['warning']
    assert next(app.DATA.glob('delete-*/journal.json')).is_file()
    app.store.recovered_data.discard(app.DATA.resolve())
    with app.db() as conn:assert not conn.execute('SELECT * FROM tracks').fetchall()
    assert not list(app.DATA.glob('delete-*'))


def test_reimport_after_committed_locked_deletion_is_not_rolled_back(client,monkeypatch):
    app=importlib.import_module('backend.app');identity=imported(client)
    with monkeypatch.context() as patch:
        patch.setattr(storage,'cleanup',lambda *args:(_ for _ in ()).throw(PermissionError('authored lock')))
        assert client.post(f'/api/tracks/{identity}/delete').status_code==200
    assert imported(client)==identity
    path=app.DATA/(identity+'.wav');before=path.read_bytes()
    app.store.recovered_data.discard(app.DATA.resolve())
    with app.db() as conn:assert conn.execute('SELECT id FROM tracks').fetchone()[0]==identity
    assert path.read_bytes()==before and not list(app.DATA.glob('delete-*'))


def test_clap_and_whisper_model_switches_keep_separate_caches_and_transcript_times(state,monkeypatch):
    app,client,audio_calls=state;identity=imported(client)
    config=app.catalog.configuration(app.DATA)
    monkeypatch.setattr(app.catalog,'configuration',lambda data:config)
    transcripts=[]
    def transcribe(*args):
        transcripts.append(config['active']['whisper'])
        return [{'start':.1,'end':.9,'text':'Authored words','uncertain':True,'word_confidence':.4}]
    monkeypatch.setattr(app.engines,'transcribe',transcribe)
    monkeypatch.setattr(app.engines,'lyrics',lambda lines,*args:[{**r,'valence':.2,'scores':{}} for r in lines])
    app.jobs['fixture']={'status':'running'}
    def run():
        app.run_job('fixture',identity,app.AnalyzeRequest(whisper=True))
        assert app.jobs['fixture']['status']=='done'
        result=app.jobs['fixture']['result']
        assert result['lyrics_source']=='whisper'
        assert result['lyrics'][0]=={'start':.1,'end':.9,'text':'Authored words','uncertain':True,'word_confidence':.4,'valence':.2,'scores':{}}
        return result
    first=run();assert run()['cached']
    config['active']['whisper']='whisper-small'
    run();assert len(audio_calls)==1 and transcripts==['whisper-base','whisper-small']
    config['active']['audio']='clap-fused'
    changed=run();assert len(audio_calls)==2 and changed['models']['audio']!=first['models']['audio']
    config['active']['audio']='clap';config['active']['whisper']='whisper-base'
    assert run()['cached'] and len(audio_calls)==2 and len(transcripts)==3


def test_long_focus_result_is_served_through_api_and_keeps_source(client,monkeypatch):
    app=importlib.import_module('backend.app')
    data=app.DATA/('authored-'*8);data.mkdir()
    monkeypatch.setattr(app,'DATA',data)
    identity=imported(client)
    source=data/(identity+'.wav');before=source.read_bytes()
    app.jobs['focus']={'status':'running'}
    app.run_focus('focus',identity,app.FocusRequest(source='original'))
    assert app.jobs['focus']['status']=='done'
    response=client.get(app.jobs['focus']['result']['url'])
    assert response.status_code==200 and response.content[:4]==b'RIFF'
    assert source.read_bytes()==before
