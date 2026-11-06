import json
import threading
import pytest
from backend import custom_models,catalog,cancellation


@pytest.mark.parametrize('url',['http://huggingface.co/a/b','https://evil.example/a/b','https://huggingface.co/a/b/file.safetensors','https://huggingface.co/a/b?token=private','https://huggingface.co/../b'])
def test_custom_model_rejects_untrusted_or_incomplete_links(url):
    with pytest.raises(ValueError):custom_models.repository(url)


def test_custom_model_requires_matching_architecture_and_labels():
    custom_models.validate_config('audio',{'model_type':'clap'})
    with pytest.raises(ValueError):custom_models.validate_config('audio',{'model_type':'llama'})
    with pytest.raises(ValueError):custom_models.validate_config('lyrics',{'model_type':'roberta','id2label':{'0':'positive'}})
    with pytest.raises(ValueError):custom_models.validate_config('interpretation',{'model_type':'qwen2','auto_map':{'x':'remote.code'}})


def custom_entry(data):
    key='custom-'+'a'*20
    custom_models.save(data,{key:{'repo':'example/model','revision':'b'*40,'purpose':'audio','custom':True,'name':'Authored model'}})
    return key


def test_custom_selection_requires_download_and_delete_removes_owned_files(tmp_path,monkeypatch):
    monkeypatch.setattr(catalog,'ROOT',tmp_path)
    key=custom_entry(tmp_path/'data')
    with pytest.raises(ValueError):catalog.select(tmp_path/'data',key)
    weights=tmp_path/'models/managed'/key;weights.mkdir(parents=True);(weights/'model.safetensors').write_bytes(b'authored fixture')
    catalog.save(tmp_path/'data',{'active':{},'installed':{key:str(weights)}})
    catalog.select(tmp_path/'data',key)
    assert catalog.configuration(tmp_path/'data')['active']['audio']==key
    result=catalog.remove(tmp_path/'data',key)
    assert not weights.exists() and key not in custom_models.entries(tmp_path/'data')
    assert result['active']['audio']=='clap'


def test_model_delete_refuses_external_paths(tmp_path,monkeypatch):
    root=tmp_path/'project';root.mkdir();monkeypatch.setattr(catalog,'ROOT',root)
    outside=tmp_path/'outside';outside.mkdir();sentinel=outside/'keep';sentinel.touch()
    catalog.save(root/'data',{'active':{},'installed':{'clap':str(outside)}})
    with pytest.raises(ValueError):catalog.remove(root/'data','clap')
    assert sentinel.exists()


def test_cancelled_download_is_not_registered_as_installed(tmp_path,monkeypatch):
    import huggingface_hub
    monkeypatch.setattr(catalog,'ROOT',tmp_path)
    def abort(*a,**kw):raise cancellation.Cancelled()
    monkeypatch.setattr(huggingface_hub,'snapshot_download',abort)
    with pytest.raises(cancellation.Cancelled):catalog.download(tmp_path/'data','clap',lambda *a:None)
    state=catalog.configuration(tmp_path/'data')
    assert 'clap' in state['incomplete'] and 'clap' not in state['installed']


def test_cancellation_capture_reaches_download_threads_without_leaking_scope():
    event=threading.Event();observed=[]
    with cancellation.scope(event):
        checkpoint=cancellation.capture()
        def worker():
            event.set()
            try:checkpoint()
            except cancellation.Cancelled:observed.append(True)
        thread=threading.Thread(target=worker);thread.start();thread.join()
        event.clear()
    assert observed==[True]
    cancellation.check()

def test_whisper_reuses_shared_model_manager_snapshot_offline(tmp_path,monkeypatch):
    import huggingface_hub
    monkeypatch.setattr(catalog,'ROOT',tmp_path)
    snapshot=tmp_path/'models/hub/snapshot';snapshot.mkdir(parents=True)
    (snapshot/'model.bin').write_bytes(b'fixture');(snapshot/'config.json').write_text('{}')
    monkeypatch.setattr(huggingface_hub,'try_to_load_from_cache',lambda *a,**k:str(snapshot/'model.bin'))
    assert catalog.model_source(tmp_path/'data','whisper')==str(snapshot)
