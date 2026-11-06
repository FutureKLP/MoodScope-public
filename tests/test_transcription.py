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
