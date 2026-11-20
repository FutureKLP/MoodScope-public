import hashlib
import json
import sqlite3

import pytest

from scripts import windows_library_testing as library
from backend.persistence import SQLiteStore
from test_windows_desktop_testing import make_workspace


def phase2_workspace(tmp_path, monkeypatch):
    area = make_workspace(tmp_path, monkeypatch)
    (area / 'sources').mkdir()
    (area / 'sources' / 'authored.txt').write_text('synthetic')
    marker = json.loads((area / 'workspace.json').read_text())
    marker.update(phase='2A', track_id='fixture', planned_track_ids=[],
                  sources=library.desktop.files(area / 'sources'), protected_music={})
    (area / 'workspace.json').write_text(json.dumps(marker))
    with SQLiteStore().transaction(area / 'data') as conn:
        conn.execute("INSERT INTO tracks VALUES ('fixture', '{}')")
    return area


def test_restart_snapshot_compares_rows_and_preserves_failure_evidence(tmp_path, monkeypatch):
    area = phase2_workspace(tmp_path, monkeypatch)
    library.snapshot(area, 'before')
    library.snapshot(area, 'same', 'before')
    with sqlite3.connect(area / 'data/cache.sqlite3') as conn:
        conn.execute("UPDATE tracks SET metadata = 'changed'")
    with pytest.raises(AssertionError, match='Library changed'):
        library.snapshot(area, 'changed', 'before')
    evidence = json.loads((area / 'evidence/changed-library.json').read_text())
    assert not evidence['library_unchanged']


def test_snapshot_detects_modified_fixture_sources(tmp_path, monkeypatch):
    area = phase2_workspace(tmp_path, monkeypatch)
    (area / 'sources/authored.txt').write_text('modified')
    with pytest.raises(AssertionError):
        library.snapshot(area, 'changed')
    assert not json.loads((area / 'evidence/changed-library.json').read_text())['sources_unchanged']


def test_identity_matches_decoder_namespace(tmp_path):
    path = tmp_path / 'fixture'
    path.write_bytes(b'authored fixture')
    assert library.identity(path) == hashlib.sha256(b'moodscope-stereo-decoder-v2authored fixture').hexdigest()
