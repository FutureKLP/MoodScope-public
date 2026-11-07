import numpy as np
import soundfile as sf
from backend import focus


def test_manual_focus_filters_real_audio_and_keeps_original_timeline(tmp_path):
    sr=16000;t=np.arange(sr*2)/sr
    source=np.stack([.2*np.sin(2*np.pi*220*t),.2*np.sin(2*np.pi*2200*t)],axis=1).astype('float32')
    original=tmp_path/'song.wav';sf.write(original,source,sr,subtype='FLOAT')
    options={'source':'original','model':'htdemucs','stereo':'left','start':.5,'end':1.5,'low_hz':80,'high_hz':600,'gain_db':0}
    key=focus.render(tmp_path,'song',options)
    filtered,rate=sf.read(tmp_path/'stems/song/focus'/(key+'.wav'))
    assert rate==sr and filtered.shape==source.shape
    assert np.max(np.abs(filtered[:sr//2]))==0 and np.max(np.abs(filtered[int(1.5*sr):]))==0
    assert np.allclose(filtered[:,0],filtered[:,1])
    assert np.sqrt(np.mean(filtered[sr//2:sr]**2))>.1
    assert focus.render(tmp_path,'song',options)==key
    assert np.allclose(sf.read(original)[0],source)

def test_manual_focus_accepts_mono_sources_and_outputs_dual_mono(tmp_path):
    sr=16000;t=np.arange(sr)/sr
    sf.write(tmp_path/'mono.wav',.2*np.sin(2*np.pi*220*t),sr)
    options={'source':'original','model':'htdemucs','stereo':'stereo','start':0,'end':None,'low_hz':80,'high_hz':1000,'gain_db':0}
    key=focus.render(tmp_path,'mono',options)
    rendered,rate=sf.read(tmp_path/'stems/mono/focus'/(key+'.wav'))
    assert rate==sr and rendered.shape==(sr,2)
    assert np.allclose(rendered[:,0],rendered[:,1])
    assert np.sqrt(np.mean(rendered**2))>.1
