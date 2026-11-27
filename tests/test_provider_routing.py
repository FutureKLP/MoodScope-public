"""Recipient consent, immutable job targets and restart persistence, without inference."""
import importlib
import json
import os
import subprocess
import sys

import httpx
import pytest
from fastapi.testclient import TestClient
from backend import cloud, providers, provider_routing as routing


@pytest.fixture(autouse=True)
def isolated_session(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    monkeypatch.setattr(providers, '_keys', {})
    monkeypatch.setattr(providers, '_audio_profile', None)
    cloud.configure('', False)
    yield
    cloud.configure('', False)


def audio_profile(data, **changes):
    return providers.save(data, {
        'name': 'Authored audio', 'protocol': 'openai',
        'base_url': 'https://first.example/v1', 'model': 'audio-fixture',
        'api_key': 'fixture-session-value', 'audio_input': True,
        'audio_usage_confirmed': True, **changes,
    })


@pytest.mark.parametrize('persist_routes', [False, True])
@pytest.mark.parametrize('change', [
    {'base_url': 'https://second.example/v1'}, {'model': 'other-fixture'},
    {'audio_usage_confirmed': False},
])
def test_prepared_changes_revoke_consent_even_without_routes_file(tmp_path, persist_routes, change):
    p = audio_profile(tmp_path)
    providers.activate_audio(tmp_path, p['id'])
    if persist_routes: routing.save(tmp_path, dict.fromkeys(routing.TASKS, 'prepared'))
    before = routing.status(tmp_path)['version']
    routing.check_consent(tmp_path, before)
    with pytest.raises(ValueError): routing.check_consent(tmp_path, None)
    providers.save(tmp_path, {**p, **change})
    if change.get('audio_usage_confirmed', True): providers.activate_audio(tmp_path, p['id'])
    assert routing.status(tmp_path)['version'] != before
    with pytest.raises(ValueError): routing.check_consent(tmp_path, before)


def test_override_profile_and_key_rotation_have_distinct_consent_identity(tmp_path):
    p = audio_profile(tmp_path)
    before = routing.status(tmp_path)['version']
    providers.save(tmp_path, {**p, 'api_key': 'fixture-rotated-value'})
    assert routing.status(tmp_path)['version'] == before
    assert 'fixture-' not in json.dumps(routing.status(tmp_path))
    providers.save(tmp_path, {**p, 'base_url': 'https://second.example/v1'})
    with pytest.raises(ValueError): routing.check_consent(tmp_path, before)
    assert providers.session_key(tmp_path, p['id']) == ''


@pytest.mark.parametrize('task', routing.TASKS)
@pytest.mark.parametrize('target', ['local', 'prepared', 'profile'])
def test_each_task_uses_only_its_explicit_target(tmp_path, task, target):
    p = audio_profile(tmp_path)
    providers.activate_audio(tmp_path, p['id'])
    routing.save(tmp_path, {**dict.fromkeys(routing.TASKS, 'local'), task: p['id'] if target == 'profile' else target})
    calls = []
    def local(): calls.append('local'); return 'local'
    def remote(): calls.append(cloud.settings()['profile_id']); return 'remote'
    assert routing.execute(tmp_path, task, 'cloud', local, remote) == ('local' if target == 'local' else 'remote')
    assert len(calls) == 1
    assert routing.execute(tmp_path, task, 'local', local, remote) == 'local'


@pytest.mark.parametrize('task', routing.TASKS)
def test_missing_profiles_and_required_keys_fail_without_fallback(tmp_path, task):
    p = audio_profile(tmp_path, base_url='https://api.openai.com/v1', api_key='')
    routing.save(tmp_path, dict.fromkeys(routing.TASKS, p['id']))
    with pytest.raises(ValueError, match='Key'): routing.preflight(tmp_path, task, 'cloud')
    providers.remove(tmp_path, p['id'])
    with pytest.raises(ValueError, match='vorhanden'): routing.preflight(tmp_path, task, 'cloud')
    assert routing.preflight(tmp_path, task, 'local') == 'local'


@pytest.mark.parametrize('target', ['prepared', 'profile'])
def test_admitted_job_keeps_recipient_key_cache_and_model_snapshot(tmp_path, monkeypatch, target):
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path)
    monkeypatch.setattr(app, 'jobs', {})
    monkeypatch.setattr(app, 'cancel_events', {})
    submitted = []
    monkeypatch.setattr(app.executor, 'submit', lambda *args: submitted.append(args))
    p = audio_profile(tmp_path)
    providers.activate_audio(tmp_path, p['id'])
    routing.save(tmp_path, dict.fromkeys(routing.TASKS, p['id'] if target == 'profile' else target))
    before = routing.status(tmp_path)['version']; version = cloud.version()
    seen = []
    def post(url, **kwargs):
        seen.append((url, kwargs['headers']['Authorization']))
        return httpx.Response(200, json={'choices': [{'finish_reason': 'stop', 'message': {'content': '{"ok":true}'}}]})
    monkeypatch.setattr(cloud.provider_http, 'post', post)
    def worker(job_id):
        assert routing.status(tmp_path)['version'] == before
        assert cloud.version() == version
        assert routing.model(tmp_path, 'audio', 'cloud', 'local-fixture') == p['model']
        routing.execute(tmp_path, 'audio', 'cloud', lambda: pytest.fail('Unexpected fallback'), cloud.request_json, 'Authored input', {})
        # Explicit interpretation overrides use the same admitted profile/key set.
        assert providers.session_key(tmp_path, p['id']) == 'fixture-session-value'
        app.jobs[job_id].update(status='done', result={})
    app.start_job('analysis', worker)
    providers.save(tmp_path, {**p, 'base_url': 'https://second.example/v1', 'model': 'changed', 'api_key': 'fixture-new-value'})
    providers.activate_audio(tmp_path, p['id'])
    routing.save(tmp_path, dict.fromkeys(routing.TASKS, 'local'))
    fn, *args = submitted.pop(); fn(*args)
    assert seen == [('https://first.example/v1/chat/completions', 'Bearer fixture-session-value')]
    assert next(iter(app.jobs.values()))['status'] == 'done'
    assert routing.status(tmp_path)['version'] != before


@pytest.mark.parametrize('operation', ['analyze', 'details', 'interpret'])
def test_api_rejects_stale_and_missing_consent_versions(tmp_path, monkeypatch, operation):
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path)
    monkeypatch.setattr(app, 'jobs', {})
    monkeypatch.setattr(app, 'track', lambda identity: {'duration': 30})
    starts = []
    def start(*args):
        assert app.job_lock._is_owned()
        starts.append(args); return {'job_id': 'fixture'}
    monkeypatch.setattr(app, 'start_job', start)
    p = audio_profile(tmp_path); providers.activate_audio(tmp_path, p['id'])
    before = routing.status(tmp_path)['version']
    providers.save(tmp_path, {**p, 'base_url': 'https://second.example/v1'})
    providers.activate_audio(tmp_path, p['id'])
    with TestClient(app.app) as client:
        options = {'mode': 'cloud', 'upload_consent': True}
        if operation == 'interpret': options['provider_id'] = p['id']
        for version in [None, before]:
            assert client.post('/api/tracks/fixture/' + operation, json={**options, 'routing_version': version}).status_code == 422
        current = client.get('/api/provider-routes').json()['version']
        assert client.post('/api/tracks/fixture/' + operation, json={**options, 'routing_version': current}).status_code == 200
    assert len(starts) == 1


def test_profiles_routes_and_models_survive_fresh_process_but_keys_do_not(tmp_path):
    from backend import catalog
    p = audio_profile(tmp_path)
    routing.save(tmp_path, dict.fromkeys(routing.TASKS, p['id']))
    catalog.select(tmp_path, 'clap-fused')
    catalog.select(tmp_path, 'whisper-small')
    config = catalog.configuration(tmp_path)
    assert config['active']['audio'] == 'clap-fused'
    assert config['active']['whisper'] == 'whisper-small'
    before = routing.status(tmp_path)
    code = '''
import json,sys
from pathlib import Path
from backend import providers,provider_routing,cloud,catalog
data=Path(sys.argv[1]);p=providers.status(data)['profiles'][0]
print(json.dumps({'id':p['id'],'configured':p['configured'],'routes':provider_routing.assignments(data),'active':catalog.configuration(data)['active'],'audio_configured':cloud.settings()['configured'],'routing':provider_routing.status(data)}))
'''
    env = {k: v for k, v in os.environ.items() if k != 'GEMINI_API_KEY'}
    result = json.loads(subprocess.check_output([sys.executable, '-c', code, str(tmp_path)], env=env, text=True))
    after = result.pop('routing')
    assert before['cache_version'] == after['cache_version']
    assert before['version'] != after['version']
    assert result == {'id': p['id'], 'configured': False, 'routes': dict.fromkeys(routing.TASKS, p['id']), 'active': config['active'], 'audio_configured': False}
    assert 'fixture-session-value' not in ''.join(path.read_text() for path in tmp_path.glob('*.json'))


def test_mutations_stay_locked_and_running_jobs_reject_changes(tmp_path, monkeypatch):
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path); monkeypatch.setattr(app, 'jobs', {})
    original = providers.save
    def save(*args):
        assert app.job_lock._is_owned()
        return original(*args)
    monkeypatch.setattr(providers, 'save', save)
    with TestClient(app.app) as client:
        payload = {'name': 'Fixture', 'base_url': 'https://first.example/v1', 'model': 'fixture'}
        p = client.post('/api/providers', json=payload).json()
        app.jobs['fixture'] = {'status': 'running'}
        for path, body in [('/providers', payload), (f'/providers/{p["id"]}/remove', {}), (f'/providers/{p["id"]}/audio', {}), ('/settings/cloud', {}), ('/provider-routes', dict.fromkeys(routing.TASKS, 'local'))]:
            assert client.post('/api' + path, json=body).status_code == 409


@pytest.mark.parametrize('protocol', ['openai', 'anthropic', 'gemini'])
def test_text_protocols_are_not_promoted_to_unconfirmed_audio(tmp_path, protocol):
    base = 'https://generativelanguage.googleapis.com/v1beta' if protocol == 'gemini' else 'https://first.example/v1'
    p = providers.save(tmp_path, {'name': 'Authored text', 'protocol': protocol, 'base_url': base, 'model': 'fixture', 'api_key': 'fixture-session-value'})
    routing.save(tmp_path, {**dict.fromkeys(routing.TASKS, 'local'), 'lyrics': p['id'], 'interpretation': p['id']})
    assert routing.preflight(tmp_path, 'lyrics', 'cloud') == p['id']
    assert routing.preflight(tmp_path, 'interpretation', 'cloud') == p['id']
    if protocol == 'gemini':
        routing.save(tmp_path, dict.fromkeys(routing.TASKS, p['id']))
        with pytest.raises(ValueError, match='Gratisprojekt'): routing.preflight(tmp_path, 'audio', 'cloud')
    else:
        with pytest.raises(ValueError): routing.save(tmp_path, dict.fromkeys(routing.TASKS, p['id']))


def test_local_jobs_remain_available_with_corrupt_server_assignments(tmp_path, monkeypatch):
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path); monkeypatch.setattr(app, 'jobs', {})
    monkeypatch.setattr(app, 'cancel_events', {})
    (tmp_path / 'provider_routes.json').write_text('broken')
    submitted = []; monkeypatch.setattr(app.executor, 'submit', lambda *args: submitted.append(args))
    app.start_job('analysis', lambda *args: None, 'fixture', app.AnalyzeRequest(mode='local'))
    assert len(submitted) == 1


def test_cancelled_api_response_cannot_enter_analysis_cache(tmp_path, monkeypatch):
    import threading
    import numpy as np
    import soundfile as sf
    from backend import cancellation
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path); monkeypatch.setattr(app, 'jobs', {'fixture': {'status': 'running'}})
    monkeypatch.setattr(app, 'track', lambda identity: {'duration': 1})
    monkeypatch.setattr(app, 'canonical', lambda identity: identity)
    p = audio_profile(tmp_path); providers.activate_audio(tmp_path, p['id'])
    sf.write(tmp_path / 'fixture.wav', np.zeros(16000), 16000)
    event = threading.Event()
    monkeypatch.setattr(app.insights, 'acoustic_features', lambda *args: {})
    def remote(*args): event.set(); return []
    monkeypatch.setattr(cloud, 'audio_mood', remote)
    with pytest.raises(cancellation.Cancelled), cancellation.scope(event):
        app.run_job('fixture', 'fixture', app.AnalyzeRequest(mode='cloud'))
    with app.db() as conn:
        assert conn.execute('SELECT COUNT(*) FROM cache').fetchone()[0] == 0


def test_locally_routed_interpretation_invalidates_cache_when_local_model_changes(tmp_path, monkeypatch):
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path); monkeypatch.setattr(app, 'jobs', {'fixture': {'status': 'running'}})
    monkeypatch.setattr(app, 'canonical', lambda identity: identity)
    monkeypatch.setattr(app, 'track', lambda identity: {'duration': 10})
    routing.save(tmp_path, dict.fromkeys(routing.TASKS, 'local'))
    analysis = {'audio': [], 'lyrics': []}
    with app.db() as conn:
        conn.execute('INSERT INTO cache VALUES (?,?)', ('latest:fixture:cloud', json.dumps(analysis)))
    model = ['first-local-fixture']
    monkeypatch.setattr(app.catalog, 'configuration', lambda data: {'active': {'interpretation': model[0], 'audio': 'clap'}})
    calls = []
    def interpret(*args):
        assert args[5] == 'local'
        calls.append(model[0]); return {'text': 'A cautious authored interpretation.', 'model': model[0], 'time': None}
    monkeypatch.setattr(app.insights, 'interpretation', interpret)
    request = app.InterpretationRequest(mode='cloud')
    app.run_interpretation('fixture', 'fixture', request)
    assert app.jobs['fixture']['status'] == 'done'
    model[0] = 'second-local-fixture'
    assert app.saved_interpretation('fixture', mode='cloud')['stale']
    app.run_interpretation('fixture', 'fixture', request)
    assert calls == ['first-local-fixture', 'second-local-fixture']
    assert app.jobs['fixture']['result']['model'] == model[0]


def test_consent_session_rotation_keeps_analysis_cache_identity(tmp_path, monkeypatch):
    app = importlib.import_module('backend.app')
    monkeypatch.setattr(app, 'DATA', tmp_path)
    p = audio_profile(tmp_path); providers.activate_audio(tmp_path, p['id'])
    before = routing.status(tmp_path); version = app.analysis_version('cloud', app.catalog.configuration(tmp_path)['active'])
    monkeypatch.setattr(routing, '_session', 'another-fixture-session')
    assert routing.status(tmp_path)['version'] != before['version']
    assert routing.status(tmp_path)['cache_version'] == before['cache_version']
    assert app.analysis_version('cloud', app.catalog.configuration(tmp_path)['active']) == version
    with pytest.raises(ValueError): routing.check_consent(tmp_path, before['version'])
