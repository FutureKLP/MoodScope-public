"""Real process leases and crash recovery, without music or model inference."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest
from backend import worker_workspace as work


def wait_for(check):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(.05)
    raise AssertionError('Isolated child did not reach expected state')


def test_success_exception_and_active_area(tmp_path):
    original = tmp_path / 'original.wav'
    original.write_bytes(b'source')
    for fail in (False, True):
        try:
            with work.workspace(tmp_path) as area:
                (area / 'runtime').mkdir()
                (area / 'runtime' / 'context.wav').write_bytes(b'fixture')
                assert work.recover(tmp_path) == [] and area.exists()
                if fail:
                    raise RuntimeError('cancelled')
        except RuntimeError:
            pass
        assert not area.exists()
    assert original.read_bytes() == b'source'


@pytest.mark.parametrize('marker', ['[]', 'null', '{"kind":"unknown"}', 'broken'])
def test_unknown_root_does_not_break_startup_or_delete_files(tmp_path, marker):
    base = tmp_path / work.ROOT_NAME; base.mkdir()
    (base / 'owner.json').write_text(marker)
    (base / 'preserve').write_bytes(b'unknown')
    assert work.recover(tmp_path) == []
    assert (base / 'preserve').read_bytes() == b'unknown'


def test_hard_service_stop_restart_and_active_worker(tmp_path, monkeypatch):
    # The parent holds its lease; a second real process holds the worker lease.
    code = '''
import sys,time
from pathlib import Path
from backend.worker_workspace import workspace
with workspace(Path(sys.argv[1])) as area:
    (Path(sys.argv[1])/'area.txt').write_text(str(area))
    time.sleep(120)
'''
    parent = subprocess.Popen([sys.executable, '-c', code, str(tmp_path)])
    worker = None
    try:
        wait_for(lambda: (tmp_path / 'area.txt').exists())
        area = Path((tmp_path / 'area.txt').read_text())
        child_code = '''
import sys,time
from pathlib import Path
from backend.worker_workspace import lease
area=Path(sys.argv[1])
with lease(area/'worker.lease'):
    (area/'ready').touch()
    time.sleep(120)
'''
        worker = subprocess.Popen([sys.executable, '-c', child_code, str(area)])
        wait_for(lambda: (area / 'ready').exists())
        parent.kill(); parent.wait(timeout=10)
        assert work.recover(tmp_path) == [] and area.exists()
        worker.kill(); worker.wait(timeout=10)
        # Exercise the actual service lifespan, not an explicit test cleanup.
        import importlib
        from fastapi.testclient import TestClient
        module = importlib.import_module('backend.app')
        monkeypatch.setattr(module, 'DATA', tmp_path)
        with TestClient(module.app):
            assert not area.exists()
        assert not area.exists() and work.recover(tmp_path) == []
    finally:
        for process in (worker, parent):
            if process is not None and process.poll() is None:
                process.kill(); process.wait(timeout=10)


@pytest.mark.parametrize('damage', ['marker', 'lease', 'owner', 'directory', 'hardlink'])
def test_ambiguous_or_linked_area_is_preserved(tmp_path, damage):
    with work.workspace(tmp_path) as area:
        if damage == 'marker': (area / 'owner.json').write_text('{}')
        elif damage == 'lease': (area / 'worker.lease').unlink()
        elif damage == 'owner':
            value = json.loads((area / 'owner.json').read_text()); value['owner'] = '0' * 32
            (area / 'owner.json').write_text(json.dumps(value))
        elif damage == 'directory':
            area = area.parent / 'unknown'; area.mkdir(); (area / 'keep').touch()
        elif damage == 'hardlink':
            source = tmp_path / 'source'; source.write_bytes(b'preserve')
            os.link(source, area / 'linked')
    assert area.exists()
    assert work.recover(tmp_path) == []


def test_guardian_exits_when_service_dies(tmp_path):
    code = '''
import sys,time,subprocess
from pathlib import Path
from backend.worker_workspace import workspace
with workspace(Path(sys.argv[1])) as area:
    child=subprocess.Popen([sys.executable,'-m','backend.expression_worker',str(area),'http.server','0','--bind','127.0.0.1'])
    (Path(sys.argv[1])/'child.txt').write_text(str(child.pid))
    time.sleep(120)
'''
    import psutil
    parent = subprocess.Popen([sys.executable, '-c', code, str(tmp_path)])
    child = None
    try:
        wait_for(lambda: (tmp_path / 'child.txt').exists())
        child = psutil.Process(int((tmp_path / 'child.txt').read_text()))
        time.sleep(.5)
        parent.kill(); parent.wait(timeout=10)
        def exited():
            try: return not child.is_running() or child.status() == psutil.STATUS_ZOMBIE
            except psutil.NoSuchProcess: return True
        wait_for(exited)
        assert work.recover(tmp_path)
    finally:
        if parent.poll() is None: parent.kill(); parent.wait(timeout=10)
        if child:
            try:
                if child.is_running() and child.status() != psutil.STATUS_ZOMBIE: child.kill()
            except psutil.NoSuchProcess: pass
