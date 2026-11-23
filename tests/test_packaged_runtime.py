import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import psutil
import pytest

from backend import paths, expression_compare
from scripts import packaged_backend


def test_frozen_paths_never_default_to_installation(monkeypatch,tmp_path):
    monkeypatch.setattr(sys,'frozen',True,raising=False)
    monkeypatch.delenv('MOODSCOPE_DATA',raising=False)
    monkeypatch.delenv('MOODSCOPE_MODELS',raising=False)
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path/'local'))
    monkeypatch.setenv('XDG_DATA_HOME',str(tmp_path/'xdg'))
    assert paths.data_dir().is_relative_to(tmp_path)
    assert paths.model_dir().is_relative_to(tmp_path)
    assert paths.data_dir()!=paths.model_dir()
    assert not paths.data_dir().exists()  # Selection itself performs no migration.


def test_explicit_paths_preserved(monkeypatch,tmp_path):
    monkeypatch.setenv('MOODSCOPE_DATA',str(tmp_path/'existing'))
    monkeypatch.setenv('MOODSCOPE_MODELS',str(tmp_path/'weights'))
    assert paths.data_dir()==tmp_path/'existing'
    assert paths.model_dir()==tmp_path/'weights'


def test_missing_compatibility_worker_is_not_available(monkeypatch,tmp_path):
    monkeypatch.setattr(sys,'frozen',True,raising=False)
    monkeypatch.setenv('MOODSCOPE_MUSIC2EMO_PYTHON',sys.executable)
    monkeypatch.setattr(expression_compare,'WEIGHTS',tmp_path)
    assert expression_compare.worker_python() is None
    assert not expression_compare.ready()


def test_loopback_conflict_preserves_existing_listener():
    with packaged_backend.bind_listener(0) as listener:
        port=listener.getsockname()[1]
        assert listener.getsockname()[0]=='127.0.0.1'
        with pytest.raises(OSError):packaged_backend.bind_listener(port)
        with socket.create_connection(('127.0.0.1',port),timeout=1):pass


@pytest.mark.skipif(os.name=='nt',reason='POSIX TIME_WAIT semantics')
def test_listener_can_rebind_after_accepted_connection_closes():
    listener=packaged_backend.bind_listener(0)
    port=listener.getsockname()[1]
    client=socket.create_connection(('127.0.0.1',port),timeout=1)
    connection,_=listener.accept()
    connection.close();client.close();listener.close()
    with packaged_backend.bind_listener(port):pass


def test_stop_reaps_owned_family_and_preserves_unrelated_process():
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],creationflags=flags)
    code='import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"]); print(p.pid,flush=True); time.sleep(60)'
    child=subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,text=True,creationflags=flags)
    try:
        descendant=psutil.Process(int(child.stdout.readline()))
        packaged_backend.stop(child)
        assert child.poll() is not None
        try:
            assert not descendant.is_running() or descendant.status()==psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            pass  # Reaping can finish between the two process observations.
        assert unrelated.poll() is None
    finally:
        if child.poll() is None:packaged_backend.stop(child)
        unrelated.terminate();unrelated.wait(10)
