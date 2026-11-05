"""Opt-in integration check: downloads weights, runs real CUDA/CPU model inference."""
import json
import numpy as np
from backend.models import engines
from backend.core import biggest_split


if __name__ == '__main__':
    sr = 48000
    # Synthetic calibration signal, explicitly NOT a song or emotion fixture.
    t = np.arange(sr * 2) / sr
    y = (.1 * np.sin(2 * np.pi * 440 * t)).astype('float32')
    progress = lambda msg, percent: print(percent, msg, flush=True)
    audio = engines.audio(y, sr, progress)
    lyrics = engines.lyrics([{'start':0.,'end':2.,'text':'I feel joyful and happy today.'}], progress)
    result = {'device':engines.device(),'audio':audio,'lyrics':lyrics,'split':biggest_split(audio,lyrics)}
    print(json.dumps(result, indent=2))
    from pathlib import Path
    Path('data').mkdir(exist_ok=True)
    Path('data/model-smoke.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
