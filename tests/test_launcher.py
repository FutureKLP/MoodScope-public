import io
import pytest
from scripts import launch


@pytest.mark.parametrize('version',['0.1.0',None])
def test_running_old_backend_requires_restart(monkeypatch,version):
    import json
    monkeypatch.setattr(launch,'urlopen',lambda *a,**k:io.BytesIO(json.dumps({'status':'ok','version':version}).encode()))
    with pytest.raises(RuntimeError,match='älteres Backend'):
        launch.ready()


def test_current_backend_can_be_reused(monkeypatch):
    monkeypatch.setattr(launch,'urlopen',lambda *a,**k:io.BytesIO(__import__('json').dumps({'status':'ok','version':'0.3.0','api_revision':16,'runtime_id':launch.environment_id()}).encode()))
    assert launch.ready()


def test_backend_from_other_environment_is_not_silently_reused(monkeypatch):
    import json
    monkeypatch.setattr(launch,'urlopen',lambda *a,**k:io.BytesIO(json.dumps({'status':'ok','version':'0.3.0','api_revision':16,'runtime_id':'other'}).encode()))
    with pytest.raises(RuntimeError,match='anderen Python-Umgebung'):launch.ready()


def test_modern_environment_is_selected_only_after_validation(tmp_path):
    from scripts.runtime import preferred_python
    import sys
    relative='Scripts/python.exe' if sys.platform=='win32' else 'bin/python'
    modern=tmp_path/'.venv-modern'/relative;modern.parent.mkdir(parents=True);modern.touch()
    assert preferred_python(tmp_path)==tmp_path/'.venv'/relative
    (tmp_path/'.venv-modern/.moodscope-validated').write_text('validated')
    assert preferred_python(tmp_path)==modern


def test_legacy_launcher_delegates_to_validated_project_interpreter(tmp_path,monkeypatch):
    import sys
    relative='Scripts/python.exe' if sys.platform=='win32' else 'bin/python'
    modern=tmp_path/'.venv-modern'/relative;modern.parent.mkdir(parents=True);modern.touch()
    (tmp_path/'.venv-modern/.moodscope-validated').write_text('validated')
    monkeypatch.setattr(launch,'ROOT',tmp_path)
    monkeypatch.setattr(launch.sys,'executable',str(tmp_path/'.venv'/relative))
    calls=[];monkeypatch.setattr(launch.subprocess,'call',lambda args,**kw:(calls.append((args,kw)) or 0))
    with pytest.raises(SystemExit) as stopped:launch.main()
    assert stopped.value.code==0 and calls[0][0][0]==str(modern)
    assert calls[0][1]['cwd']==tmp_path


def test_native_restart_reselects_newest_binary_and_rechecks_service(monkeypatch,tmp_path):
    import subprocess
    selected=iter([tmp_path/'first',tmp_path/'second']);calls=[];before=[]
    monkeypatch.setattr(launch,'latest_binary',lambda:next(selected))
    codes=iter([75,0])
    monkeypatch.setattr(launch.subprocess,'run',lambda command,**kw:(calls.append(command) or subprocess.CompletedProcess(command,next(codes))))
    launch.run_desktop(lambda:before.append(True))
    assert calls==[[str(tmp_path/'first')],[str(tmp_path/'second')]] and len(before)==2


def test_restart_selects_a_versioned_build_beside_a_running_executable(tmp_path,monkeypatch):
    import os
    from scripts import launch
    monkeypatch.setattr(launch,'ROOT',tmp_path)
    root=tmp_path/'src-tauri'/'target'/'v03'/'release';root.mkdir(parents=True)
    suffix='.exe' if os.name=='nt' else ''
    original=root/('moodscope'+suffix);original.write_bytes(b'authored placeholder');os.utime(original,(1000,1000))
    fresh=root/('moodscope-build-20300101'+suffix);fresh.write_bytes(b'authored replacement');os.utime(fresh,(2000,2000))
    assert launch.latest_binary()==fresh


def test_service_reaps_resistant_owned_children(monkeypatch):
    from scripts import service
    import psutil
    calls=[]
    class Child:
        def terminate(self):calls.append('terminate')
        def kill(self):calls.append('kill')
    child=Child()
    class Parent:
        def children(self,recursive):
            assert recursive
            return [child]
    def wait(children,timeout):
        calls.append(('wait',tuple(children)))
        return ([],[child]) if len(calls)==2 else ([child],[])
    monkeypatch.setattr(psutil,'wait_procs',wait)
    service.stop_children(Parent())
    assert calls==['terminate',('wait',(child,)),'kill',('wait',(child,))]


def test_worker_exit_always_cleans_model_children(monkeypatch):
    from scripts import service
    import uvicorn,importlib
    app=importlib.import_module('backend.app')
    monkeypatch.setattr(app,'SYSTEM_CONTROL',None)
    cleaned=[]
    monkeypatch.setattr(service,'stop_children',lambda:cleaned.append(True))
    class Server:
        def __init__(self,*args):pass
        def run(self):raise RuntimeError('authored server failure')
    monkeypatch.setattr(uvicorn,'Server',Server)
    with pytest.raises(RuntimeError,match='server failure'):service.worker(12345)
    assert cleaned==[True]


def test_direct_launcher_resolves_cleanup_without_project_on_import_path(tmp_path):
    import subprocess,sys
    scripts=__import__('pathlib').Path(launch.__file__).parent
    result=subprocess.run([sys.executable,'-I','-c',
        'import sys; sys.path.insert(0,sys.argv[1]); import launch; assert callable(launch.stop_children)',
        str(scripts)],cwd=tmp_path,capture_output=True,timeout=10)
    assert result.returncode==0
