from pathlib import Path
from types import SimpleNamespace
import json
import pytest
from backend import links
credential_host=':'.join(['user','pass'])+chr(64)+'youtube.com'


@pytest.mark.parametrize('value',[
    'http://youtube.com/watch?v=BaW_jenozKc','https://youtube.com.evil.example/watch?v=BaW_jenozKc',
    'https://127.0.0.1/song','file:///etc/passwd','https://'+credential_host+'/watch?v=BaW_jenozKc',
    'https://youtube.com/watch?v=BaW_jenozKc&list=abc','https://soundcloud.com/artist/sets/list',
    'https://on.soundcloud.com/example','https://youtube.com:8443/watch?v=BaW_jenozKc',
])
def test_invalid_private_and_playlist_urls_are_rejected(value):
    with pytest.raises(ValueError):links.validate_url(value)


def test_supported_single_track_urls_are_canonicalized():
    assert links.validate_url('https://youtu.be/BaW_jenozKc?t=10')=='https://www.youtube.com/watch?v=BaW_jenozKc'
    assert links.validate_url('https://soundcloud.com/artist/track?utm_source=test')=='https://soundcloud.com/artist/track'


def test_downloader_uses_argument_array_and_does_not_load_user_config(tmp_path,monkeypatch):
    monkeypatch.setattr(links,'downloader',lambda:'downloader')
    def run(command,**kwargs):
        assert isinstance(command,list)
        assert '--ignore-config' in command and '--no-plugin-dirs' in command
        assert '--no-playlist' in command
        assert '--cookies-from-browser' not in command
        (tmp_path/'source.webm').write_bytes(b'test media')
        return SimpleNamespace(returncode=0,communicate=lambda **k:(json.dumps({'title':'Public test','artist':'Test'}).encode(),b''),poll=lambda:0)
    monkeypatch.setattr(links.subprocess,'Popen',run)
    source,metadata=links.download('https://youtu.be/BaW_jenozKc',tmp_path,lambda *a:None)
    assert source.name=='source.webm'
    assert metadata['source']=='YouTube'


def test_downloader_diagnostics_are_not_exposed(tmp_path,monkeypatch):
    monkeypatch.setattr(links,'downloader',lambda:'downloader')
    monkeypatch.setattr(links.subprocess,'Popen',lambda *a,**k:SimpleNamespace(returncode=1,communicate=lambda **kw:(b'',b'PRIVATE_DIAGNOSTIC'),poll=lambda:1))
    with pytest.raises(RuntimeError) as error:links.download('https://youtu.be/BaW_jenozKc',tmp_path,lambda *a:None)
    assert 'PRIVATE_DIAGNOSTIC' not in str(error.value)
