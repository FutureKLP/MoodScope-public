from contextlib import contextmanager
from pathlib import Path
import hashlib
import pytest
from backend.demucs_models import fetch_checkpoint


def test_checkpoint_hash_is_verified_and_failed_download_leaves_no_partial_file(tmp_path,monkeypatch):
    from backend import demucs_models
    data=b'authored model fixture';checksum=hashlib.sha256(data).hexdigest()[:8]
    class Response:
        def raise_for_status(self):pass
        def iter_bytes(self,*args):return iter([data])
    @contextmanager
    def stream(*args,**kwargs):
        assert kwargs['follow_redirects'] is False
        assert kwargs['timeout'].connect==10
        yield Response()
    monkeypatch.setattr(demucs_models.httpx,'stream',stream)
    target=tmp_path/'model.th';url='https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/12345678-'+checksum+'.th'
    fetch_checkpoint(url,target,checksum)
    assert target.read_bytes()==data
    with pytest.raises(RuntimeError,match='prüfsumme'):fetch_checkpoint(url,tmp_path/'bad.th','00000000')
    assert not (tmp_path/'bad.th').exists() and not list(tmp_path.glob('*.part'))
    with pytest.raises(ValueError):fetch_checkpoint('https://untrusted.invalid/model.th',tmp_path/'other.th',checksum)
