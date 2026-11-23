from types import SimpleNamespace as Item
from backend.transcription import owned_segments
from backend.core import text_coverage


def test_overlap_assigns_each_word_to_one_time_window_and_retains_uncertainty():
    words=[Item(start=2,end=3,word=' First',probability=.4),Item(start=5,end=6,word=' next',probability=.7)]
    segment=Item(words=words,start=2,end=6,text=' First next',avg_logprob=-1.1,compression_ratio=1.,no_speech_prob=.1)
    first=owned_segments([segment],20,20,24,50)
    second=owned_segments([segment],20,24,48,50)
    assert first[0]['text']=='First' and second[0]['text']=='next'
    assert first[0]['uncertain'] and first[0]['start']==22 and second[0]['start']==25


def test_coverage_merges_overlaps_without_claiming_word_accuracy():
    report=text_coverage([{'start':0,'end':4,'text':'Own text'},{'start':3,'end':6,'text':'More words'}],20)
    assert report['covered_seconds']==6 and report['gaps']==[{'start':6,'end':20}]
    assert 'keine Wortgenauigkeit' in report['note']

def test_windows_cuda_directories_find_separately_installed_project_libraries(tmp_path,monkeypatch):
    from pathlib import PurePosixPath
    import importlib.metadata
    from backend.transcription import windows_cuda_directories
    entry=PurePosixPath('nvidia/cublas/bin/cublas64_12.dll')
    class Installed:
        files=[entry]
        def locate_file(self,value):return tmp_path/value
    monkeypatch.setattr(importlib.metadata,'distribution',lambda name:Installed())
    folders=windows_cuda_directories(tmp_path/'torch/lib')
    assert folders==[tmp_path/'torch/lib',tmp_path/'nvidia/cublas/bin']

def test_normalized_audio_decode_works_without_pyav_metadata_keyword(tmp_path):
    import numpy as np
    import soundfile as sf
    from backend.transcription import decode_audio
    path=tmp_path/'authored.wav';sr=48000
    mono=np.sin(2*np.pi*440*np.arange(sr)/sr).astype('float32')*.1
    sf.write(path,np.stack([mono,mono],axis=1),sr,subtype='FLOAT')
    decoded=decode_audio(path)
    assert decoded.shape==(16000,) and decoded.dtype==np.float32
    assert abs(np.fft.rfftfreq(len(decoded),1/16000)[np.argmax(abs(np.fft.rfft(decoded)))]-440)<1


def test_cancellation_stops_lazy_decoder_before_consuming_remaining_segments():
    import threading
    import pytest
    from backend import cancellation
    event=threading.Event();consumed=[]
    def segments():
        for index in range(3):
            consumed.append(index)
            if index==1:event.set()
            yield Item(words=[],start=index,end=index+1,text='Authored text',avg_logprob=0,compression_ratio=1)
    with pytest.raises(cancellation.Cancelled),cancellation.scope(event):
        owned_segments(segments(),0,0,3,3)
    assert consumed==[0,1]


def test_nonfinite_whisper_timestamps_are_rejected():
    import pytest
    with pytest.raises(ValueError,match='Zeitstempel'):
        owned_segments([Item(words=[],start=0,end=float('nan'))],0,0,3,3)


def test_decode_failure_still_releases_whisper_model(tmp_path,monkeypatch):
    import gc
    import weakref
    import pytest
    import faster_whisper
    from backend import transcription,catalog
    references=[]
    class Model:
        def __init__(self,*args,**kwargs):references.append(weakref.ref(self))
    monkeypatch.setattr(faster_whisper,'WhisperModel',Model)
    monkeypatch.setattr(transcription,'device_for',lambda engine:'cpu')
    monkeypatch.setattr(catalog,'unload_models',lambda engine:None)
    monkeypatch.setattr(catalog,'model_source',lambda *args:'fixture')
    def fail(*args,**kwargs):raise ValueError('Authored decode failure')
    monkeypatch.setattr(transcription,'decode_audio',fail)
    with pytest.raises(ValueError,match='decode failure'):
        transcription.transcribe(Item(data=tmp_path),tmp_path/'missing.wav',lambda *args:None)
    gc.collect()
    assert references and references[0]() is None


def test_missing_offline_whisper_weights_explain_installation_without_retry(tmp_path,monkeypatch):
    import pytest
    import faster_whisper
    from huggingface_hub.errors import LocalEntryNotFoundError
    from backend import transcription,catalog
    calls=[]
    def missing(*args,**kwargs):
        calls.append(kwargs)
        raise LocalEntryNotFoundError('Raw upstream offline cache error')
    monkeypatch.setattr(faster_whisper,'WhisperModel',missing)
    monkeypatch.setattr(transcription,'device_for',lambda engine:'cpu')
    monkeypatch.setattr(catalog,'unload_models',lambda engine:None)
    monkeypatch.setattr(catalog,'model_source',lambda *args:'fixture')
    with pytest.raises(ValueError,match='Whisper-Modellgewichte fehlen.*Modelle & API'):
        transcription.transcribe(Item(data=tmp_path),tmp_path/'unused.wav',lambda *args:None)
    assert len(calls)==1
