"""Real, local model inference. No synthetic emotional curves or heuristic fallback."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME', str(ROOT / 'models'))
os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('USE_FLAX', '0')
AUDIO_MODEL = 'laion/clap-htsat-unfused'
LYRIC_MODEL = 'MilaNLProc/xlm-emo-t'
AUDIO_REVISION = '8fa0f1c6d0433df6e97c127f64b2a1d6c0dcda8a'
LYRIC_REVISION = 'a6ee7c9fad08d60204e7ae437d41d392381496f0'
PIPELINE_VERSION = f'clap-musical-sequence-v6-harmony-v2-grid5-coverage50:{AUDIO_REVISION}:{LYRIC_REVISION}'


class Engines:
    def __init__(self):
        self.audio_model = self.processor = self.lyric_pipe = None
        self.data=ROOT/'data'

    def device(self,purpose='audio'):
        import torch
        from .runtime_devices import resolve
        requested = resolve(self.data,purpose)
        if requested == 'cpu':
            return 'cpu'
        if torch.cuda.is_available():
            try:
                # Probe an actual CUDA kernel, not merely driver presence.
                (torch.ones(4, device=requested) * 2).sum().item()
                return requested
            except RuntimeError:
                if requested.startswith('cuda'):
                    raise
        if requested.startswith('cuda'):
            raise RuntimeError('CUDA requested but no usable GPU is available')
        return 'cpu'

    def audio(self, y, sr, progress,step=5):
        import numpy as np
        import torch
        import librosa
        from transformers import ClapModel, ClapProcessor
        from . import catalog
        from .core import analysis_grid
        device = self.device()
        if self.audio_model is None:
            progress('Lade CLAP-Musikmodell (erster Start: Download)', 10)
            source=catalog.model_source(self.data,'audio')
            kwargs={'revision':AUDIO_REVISION} if source==AUDIO_MODEL else {}
            self.processor = ClapProcessor.from_pretrained(source,**kwargs)
            self.audio_model = ClapModel.from_pretrained(source,**kwargs).to(device).eval()
        from .audio_method import LABELS,VALENCE,AROUSAL
        from .prompt_presets import content
        prompts=content(self.data,'audio').splitlines()
        labels=list(LABELS)
        values=torch.tensor(VALENCE,device=device)
        arousal=torch.tensor(AROUSAL,device=device)
        duration = len(y) / sr
        result = []
        # Non-overlapping display bins, each estimated using centered 10-second context.
        for span in analysis_grid(duration,step):
            start,end=span['start'],span['end']
            center=(start+end)/2
            context_start=max(0.,center-5);context_end=min(duration,center+5)
            clip = y[int(context_start * sr):int(context_end * sr)]
            inputs = self.processor(text=prompts, audio=clip, sampling_rate=sr,
                                    return_tensors='pt', padding=True).to(device)
            with torch.inference_mode():
                logits=self.audio_model(**inputs).logits_per_audio[0].reshape(6,2).mean(dim=1)
                scores = logits.softmax(dim=-1)
                confidence=1-float((-(scores*scores.clamp_min(1e-8).log()).sum()/np.log(len(labels))).cpu())
            rms = float(np.sqrt(np.mean(clip ** 2)))
            result.append({'start': float(start), 'end': float(end),
                           'valence': float((scores * values).sum().cpu()),
                           'scores': dict(zip(labels, scores.cpu().tolist())),
                           'arousal':float((scores*arousal).sum().cpu()),
                           'confidence':max(0.,min(1.,confidence)),
                           'context_start':context_start,'context_end':context_end,
                           'rms': rms})
            progress('Analysiere musikalischen Ausdruck', 15 + int(50 * end / duration))
        return result

    def lyrics(self, lines, progress, context_weight=.3):
        from transformers import pipeline
        import math
        from . import catalog
        if not lines:
            return []
        if self.lyric_pipe is None:
            progress('Lade mehrsprachiges Text-Emotionsmodell', 70)
            source=catalog.model_source(self.data,'lyrics')
            kwargs={'revision':LYRIC_REVISION} if source==LYRIC_MODEL else {}
            self.lyric_pipe = pipeline('text-classification', model=source, **kwargs,
                                       model_kwargs={'use_safetensors':catalog.entries(self.data)[catalog.configuration(self.data)['active']['lyrics']].get('custom',False)},
                                       device=self.device('lyrics'))
        results = self.lyric_pipe([l['text'] for l in lines], top_k=None,
                                 truncation=True, max_length=256, batch_size=8)
        contexts=[]
        for i,line in enumerate(lines):
            previous=lines[i-1]['text'] if i and line['start']-lines[i-1]['end']<12 else ''
            following=lines[i+1]['text'] if i+1<len(lines) and lines[i+1]['start']-line['end']<12 else ''
            contexts.append(' '.join([previous,line['text'],following]).strip())
        contextual=self.lyric_pipe(contexts,top_k=None,truncation=True,max_length=384,batch_size=8) if context_weight else results
        output = []
        for line, prediction,context in zip(lines, results,contextual):
            isolated={p['label'].lower():p['score'] for p in prediction}
            surrounding={p['label'].lower():p['score'] for p in context}
            scores = {key:(1-context_weight)*value+context_weight*surrounding[key] for key,value in isolated.items()}
            if not {'joy', 'sadness', 'anger', 'fear'}.issubset(scores):
                raise ValueError(f'Unexpected model labels: {list(scores)}')
            valence = scores['joy'] - scores['sadness'] - .7 * scores['anger'] - .7 * scores['fear']
            confidence=1+sum(p*math.log(max(p,1e-8)) for p in scores.values())/math.log(4)
            output.append({**line, 'valence': valence, 'scores': scores,
                           'confidence':max(0.,min(1.,confidence)),
                           'arousal':scores['anger']+scores['fear']+.5*scores['joy'],
                           'context_weight':context_weight})
        return output

    def transcribe(self,path,progress,quality='standard',language=None):
        from .transcription import transcribe
        return transcribe(self,path,progress,quality,language)

    def instruments(self,y,sr,progress):
        import numpy as np
        import torch
        if self.audio_model is None:self.audio(y[:min(len(y),sr*10)],sr,progress)
        names=['akustische Gitarre','elektrische Gitarre','Bass','Schlagzeug','Klavier',
               'Synthesizer','Streicher','Bläser','Gesang']
        prompts=['The music features acoustic guitar.','The music features electric guitar.',
                 'The music features bass guitar.','The music features a drum kit.',
                 'The music features piano.','The music features synthesizers.',
                 'The music features a string ensemble.','The music features brass instruments.',
                 'The music features singing vocals.']
        from .prompt_presets import content
        prompts=content(self.data,'instruments').splitlines()
        estimates=[];duration=len(y)/sr;device=self.device()
        for fraction in [.2,.5,.8]:
            start=max(0.,duration*fraction-5)
            clip=y[int(start*sr):int(min(duration,start+10)*sr)]
            inputs=self.processor(text=prompts,audio=clip,sampling_rate=sr,return_tensors='pt',padding=True).to(device)
            with torch.inference_mode():
                scores=self.audio_model(**inputs).logits_per_audio.softmax(-1)[0].cpu().numpy()
            estimates.append(scores)
        relative=np.mean(estimates,axis=0)
        return sorted([{'instrument':name,'relative_similarity':float(value)} for name,value in zip(names,relative)],
                      key=lambda item:item['relative_similarity'],reverse=True)[:5]


engines = Engines()
