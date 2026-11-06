"""Overlapping local speech decoding with time ownership and editable output."""
import os
from pathlib import Path
import numpy as np

_dll_handles=[]
_dll_directories=set()


def decode_audio(path,sampling_rate=16000):
    """Our inputs are normalised WAV/stem files; avoid incompatible PyAV keyword APIs."""
    import soundfile as sf
    import librosa
    audio,sr=sf.read(path,dtype='float32',always_2d=True)
    mono=audio.mean(axis=1)
    if sr!=sampling_rate:mono=librosa.resample(mono,orig_sr=sr,target_sr=sampling_rate)
    if not np.isfinite(mono).all():raise ValueError('Ungültige Audiodaten für Texterkennung')
    return np.ascontiguousarray(mono,dtype='float32')


def windows_cuda_directories(torch_folder):
    from importlib.metadata import distribution,PackageNotFoundError
    folders=[Path(torch_folder)]
    for package in ['nvidia-cublas-cu12','nvidia-cudnn-cu12','nvidia-cuda-nvrtc-cu12']:
        try:installed=distribution(package)
        except PackageNotFoundError:continue
        for entry in installed.files or []:
            if entry.suffix.lower()=='.dll':
                folder=Path(installed.locate_file(entry)).parent
                if folder not in folders:folders.append(folder)
    return folders


def device_for(engine):
    requested=os.environ.get('MOODSCOPE_WHISPER_DEVICE','auto')
    from . import runtime_devices
    chosen=requested if requested!='auto' else (runtime_devices.resolve(engine.data,'whisper') if hasattr(engine,'data') else engine.device())
    explicit=requested!='auto' or (hasattr(engine,'data') and runtime_devices.configuration(engine.data).get('whisper','auto')!='auto')
    if requested=='cpu' or (requested=='auto' and not chosen.startswith('cuda')):return 'cpu'
    if os.name=='nt':
        import torch
        folders=windows_cuda_directories(Path(torch.__file__).parent/'lib')
        available=all(any((folder/name).exists() for folder in folders) for name in ['cudnn64_9.dll','cublas64_12.dll'])
        if available:
            for folder in folders:
                if folder.is_dir() and str(folder) not in _dll_directories:
                    _dll_handles.append(os.add_dll_directory(str(folder)));_dll_directories.add(str(folder))
                    if str(folder) not in os.environ.get('PATH','').split(os.pathsep):os.environ['PATH']=str(folder)+os.pathsep+os.environ.get('PATH','')
            return 'cuda'
        if explicit:raise RuntimeError('Whisper-CUDA benötigt cuBLAS 12 und cuDNN 9 in der Projektumgebung.')
        return 'cpu'
    if explicit:return 'cuda'
    import ctypes.util
    return 'cuda' if ctypes.util.find_library('cudnn') else 'cpu'


def owned_segments(segments,window_start,owner_start,owner_end,duration):
    output=[]
    for segment in segments:
        words=[w for w in (segment.words or []) if owner_start<=window_start+(w.start+w.end)/2<owner_end]
        if words:
            start=max(owner_start,window_start+words[0].start);end=min(duration,owner_end,window_start+words[-1].end)
            text=''.join(w.word for w in words).strip()
            confidence=float(np.mean([w.probability for w in words]))
        elif not segment.words and owner_start<=window_start+(segment.start+segment.end)/2<owner_end:
            start=max(owner_start,window_start+segment.start);end=min(duration,owner_end,window_start+segment.end)
            text=segment.text.strip();confidence=None
        else:continue
        # Keep uncertain sung words visible for correction instead of silently dropping difficult rap.
        non_speech=getattr(segment,'no_speech_prob',0)>.85 and segment.avg_logprob<-1.2
        if text and end>start and not non_speech:
            output.append({'start':start,'end':end,'text':text,'word_confidence':confidence,
                'uncertain':segment.avg_logprob<-1 or segment.compression_ratio>2.4 or (confidence is not None and confidence<.55)})
    return output


def transcribe(engine,path,progress,quality='standard',language=None):
    from faster_whisper import WhisperModel
    from . import catalog,diagnostics
    device=device_for(engine)
    from .runtime_devices import resolve
    chosen=resolve(engine.data,'whisper') if device=='cuda' else 'cpu'
    device_index=int(chosen.split(':')[1]) if device=='cuda' and ':' in chosen else 0
    progress('Whisper: lokale Texterkennung auf '+('NVIDIA CUDA' if device=='cuda' else 'CPU'),5)
    catalog.unload_models(engine)
    model=WhisperModel(catalog.model_source(engine.data,'whisper'),device=device,device_index=device_index,
        compute_type='float16' if device=='cuda' else 'int8',download_root=str(catalog.ROOT/'models'/'whisper'))
    audio=decode_audio(str(path),sampling_rate=16000);duration=len(audio)/16000
    options={'beam_size':7 if quality=='precise' else 5,'vad_filter':False,
        'condition_on_previous_text':False,'word_timestamps':True,'language':language,
        'temperature':0.,'no_speech_threshold':.6}
    output=[]
    try:
        if quality=='precise':
            for start in np.arange(0,duration,24):
                left=max(0,float(start)-3);right=min(duration,float(start)+27)
                segments,_=model.transcribe(audio[int(left*16000):int(right*16000)],**options)
                output.extend(owned_segments(segments,left,float(start),min(duration,float(start)+24),duration))
                progress(f'Whisper: Abschnitt {int(start)}–{int(min(duration,start+24))} s von {int(duration)} s',min(60,5+55*right/max(1,duration)))
        else:
            segments,_=model.transcribe(audio,**options)
            output=owned_segments(segments,0,0,duration,duration)
        output.sort(key=lambda line:line['start'])
        for i in range(len(output)-1):output[i]['end']=min(output[i]['end'],output[i+1]['start'])
        output=[row for row in output if row['end']>row['start']]
        diagnostics.event(engine.data,'whisper',f'device={device} quality={quality} segments={len(output)} duration={duration:.1f}')
        return output
    finally:
        del model
        import gc,torch
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()
