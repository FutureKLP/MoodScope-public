import json
import sqlite3

import pytest

from scripts import windows_desktop_testing as desktop


def test_desktop_cpu_is_explicit_even_when_parent_requests_gpu(tmp_path, monkeypatch):
    monkeypatch.setenv('MOODSCOPE_DEVICE', 'cuda:0')
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', '0')
    environment = desktop.environment(tmp_path)
    assert environment['MOODSCOPE_DEVICE'] == 'cpu'
    assert environment['CUDA_VISIBLE_DEVICES'] == '-1'
    assert environment['HF_HUB_OFFLINE'] == environment['TRANSFORMERS_OFFLINE'] == '1'
    assert environment['MOODSCOPE_DATA'] == str(tmp_path / 'data')
    assert environment['WEBVIEW2_USER_DATA_FOLDER'] == str(tmp_path / 'webview')


def make_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(desktop, 'ROOT', tmp_path)
    area = tmp_path / '.tools' / 'desktop-fixture'
    for name in ('data', 'exports', 'webview', 'evidence'):
        (area / name).mkdir(parents=True)
    source = area / 'synthetic-440hz-0-2s.wav'
    source.write_bytes(b'fixture source')
    (area / 'exports' / 'existing.wav').write_bytes(b'fixture destination')
    with sqlite3.connect(area / 'data' / 'cache.sqlite3') as conn:
        conn.execute('CREATE TABLE fixture (value TEXT)')
    marker = {'kind': desktop.MARKER, 'source_hash': desktop.digest(source),
              'production_databases': {}, 'exports': desktop.files(area / 'exports')}
    (area / 'workspace.json').write_text(json.dumps(marker))
    return area


def test_desktop_workspace_refuses_production_and_unknown_marker(tmp_path, monkeypatch):
    area = make_workspace(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match='dedicated directory'):
        desktop.workspace(tmp_path / 'data')
    (area / 'workspace.json').write_text(json.dumps({'kind': 'other'}))
    with pytest.raises(ValueError, match='synthetic desktop'):
        desktop.workspace(area)


def test_cancel_snapshot_detects_new_files_and_preserves_failure_evidence(tmp_path, monkeypatch):
    area = make_workspace(tmp_path, monkeypatch)
    desktop.snapshot(area, 'before')
    desktop.snapshot(area, 'unchanged', 'before')
    (area / 'exports' / 'unexpected.wav').write_bytes(b'unexpected export')
    with pytest.raises(AssertionError, match='Export directory changed'):
        desktop.snapshot(area, 'failed', 'before')
    evidence = json.loads((area / 'evidence' / 'failed.json').read_text())
    assert not evidence['exports_unchanged']
    assert evidence['sqlite_integrity'] == 'ok'


def test_cancel_snapshot_detects_overwritten_existing_destination(tmp_path, monkeypatch):
    area = make_workspace(tmp_path, monkeypatch)
    desktop.snapshot(area, 'before')
    (area / 'exports' / 'existing.wav').write_bytes(b'changed destination')
    with pytest.raises(AssertionError, match='Export directory changed'):
        desktop.snapshot(area, 'failed', 'before')


def test_snapshot_detects_changes_to_protected_database(tmp_path, monkeypatch):
    area = make_workspace(tmp_path, monkeypatch)
    (tmp_path / 'data').mkdir()
    protected = tmp_path / 'data' / 'cache.sqlite3'
    protected.write_bytes(b'protected fixture')
    with pytest.raises(AssertionError):
        desktop.snapshot(area, 'protected-change')
    assert protected.read_bytes() == b'protected fixture'
    assert not json.loads((area / 'evidence' / 'protected-change.json').read_text())['production_databases_unchanged']
