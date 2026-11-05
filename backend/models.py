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
PIPELINE_VERSION = f'clap-xlmemo-v2-lrc-gaps-window10-hop5:{AUDIO_REVISION}:{LYRIC_REVISION}'


class Engines:
    def __init__(self):
        self.audio_model = self.processor = self.lyric_pipe = None

    def device(self):
        import torch
        requested = os.environ.get('MOODSCOPE_DEVICE', 'auto')
        if requested == 'cpu':
            return 'cpu'
        if torch.cuda.is_available():
            try:
                # Probe an actual CUDA kernel, not merely driver presence.
                (torch.ones(4, device='cuda') * 2).sum().item()
                return 'cuda'
            except RuntimeError:
                if requested == 'cuda':
                    raise
        if requested == 'cuda':
            raise RuntimeError('CUDA requested but no usable GPU is available')
        return 'cpu'

    def audio(self, y, sr, progress):
        import numpy as np
        import torch
        import librosa
        from transformers import ClapModel, ClapProcessor
        device = self.device()
        if self.audio_model is None:
            progress('Lade CLAP-Musikmodell (erster Start: Download)', 10)
            self.processor = ClapProcessor.from_pretrained(AUDIO_MODEL, revision=AUDIO_REVISION)
            self.audio_model = ClapModel.from_pretrained(AUDIO_MODEL, revision=AUDIO_REVISION).to(device).eval()
        prompts = ['This music sounds joyful, happy and uplifting.',
                   'This music sounds peaceful, warm and content.',
                   'This music sounds sad, melancholic and sorrowful.',
                   'This music sounds angry, tense and aggressive.']
        values = torch.tensor([1., .5, -1., -.7], device=device)
        duration = len(y) / sr
        result = []
        # One 10-second window every 5 seconds; final window is clipped to track end.
        for start in np.arange(0, duration, 5):
            end = min(duration, start + 10)
            clip = y[int(start * sr):int(end * sr)]
            inputs = self.processor(text=prompts, audio=clip, sampling_rate=sr,
                                    return_tensors='pt', padding=True).to(device)
            with torch.inference_mode():
                scores = self.audio_model(**inputs).logits_per_audio.softmax(dim=-1)[0]
            rms = float(np.sqrt(np.mean(clip ** 2)))
            result.append({'start': float(start), 'end': float(end),
                           'valence': float((scores * values).sum().cpu()),
                           'scores': dict(zip(['joy','calm','sadness','anger'], scores.cpu().tolist())),
                           'rms': rms})
            progress('Analysiere musikalischen Ausdruck', 15 + int(50 * end / duration))
        return result

    def lyrics(self, lines, progress):
        from transformers import pipeline
        if not lines:
            return []
        if self.lyric_pipe is None:
            progress('Lade mehrsprachiges Text-Emotionsmodell', 70)
            self.lyric_pipe = pipeline('text-classification', model=LYRIC_MODEL, revision=LYRIC_REVISION,
                                       model_kwargs={'use_safetensors':False},
                                       device=0 if self.device() == 'cuda' else -1)
        results = self.lyric_pipe([l['text'] for l in lines], top_k=None,
                                 truncation=True, max_length=256, batch_size=8)
        output = []
        for line, prediction in zip(lines, results):
            scores = {p['label'].lower(): p['score'] for p in prediction}
            if not {'joy', 'sadness', 'anger', 'fear'}.issubset(scores):
                raise ValueError(f'Unexpected model labels: {list(scores)}')
            valence = scores['joy'] - scores['sadness'] - .7 * scores['anger'] - .7 * scores['fear']
            output.append({**line, 'valence': valence, 'scores': scores})
        return output

    def transcribe(self, path, progress):
        from faster_whisper import WhisperModel
        progress('Whisper: Transkribiere Gesang lokal', 5)
        # CPU default: CTranslate2 CUDA requires separate compatible cuDNN runtime.
        device = os.environ.get('MOODSCOPE_WHISPER_DEVICE', 'cpu')
        model = WhisperModel('base', device=device,
                             compute_type='float16' if device == 'cuda' else 'int8',
                             download_root=str(ROOT / 'models' / 'whisper'))
        segments, _ = model.transcribe(str(path), beam_size=5, vad_filter=True)
        return [{'start': s.start, 'end': s.end, 'text': s.text.strip()}
                for s in segments if s.text.strip()]


engines = Engines()
