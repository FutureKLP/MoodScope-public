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
    monkeypatch.setattr(launch,'urlopen',lambda *a,**k:io.BytesIO(b'{"status":"ok","version":"0.3.0","api_revision":5}'))
    assert launch.ready()
