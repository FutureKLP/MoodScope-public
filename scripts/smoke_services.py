"""Opt-in live service and real Whisper check. Downloads the Whisper base model."""
import json
from pathlib import Path
import httpx
import numpy as np
import soundfile as sf
from backend.models import engines


if __name__=='__main__':
    output={}
    response=httpx.get('https://lrclib.net/api/get',params={'artist_name':'Rick Astley',
                       'track_name':'Never Gonna Give You Up'},timeout=30)
    output['lrclib']={'status':response.status_code,
                      'has_synced_lyrics':bool(response.json().get('syncedLyrics'))}
    Path('data').mkdir(exist_ok=True)
    path=Path('data/whisper-silence.wav')
    sf.write(path,np.zeros(16000*3,dtype='float32'),16000)
    lines=engines.transcribe(path,lambda msg,p:print(p,msg,flush=True))
    output['whisper']={'input':'3 seconds of silence, not a singing accuracy test','segments':lines}
    print(json.dumps(output,indent=2))
    Path('data/service-smoke.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
