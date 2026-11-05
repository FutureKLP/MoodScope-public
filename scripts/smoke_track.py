"""Run a user-selected local song through the running API; never upload audio externally."""
import argparse
import json
import time
from pathlib import Path
import httpx


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('path',type=Path)
    args=parser.parse_args()
    with httpx.Client(base_url='http://127.0.0.1:8765/api',timeout=180) as client:
        with args.path.open('rb') as file:
            response=client.post('/tracks',files={'file':(args.path.name,file)})
        response.raise_for_status()
        track=response.json()
        lyrics=''
        if track.get('artist') and track.get('title'):
            response=client.post(f"/tracks/{track['id']}/lyrics/search",json={'artist':track['artist'],'title':track['title']})
            response.raise_for_status()
            lyrics=response.json()['text']
        response=client.post(f"/tracks/{track['id']}/analyze",json={'lyrics':lyrics})
        response.raise_for_status()
        job_id=response.json()['job_id']
        previous=''
        deadline=time.monotonic()+1800
        while time.monotonic()<deadline:
            response=client.get(f'/jobs/{job_id}')
            response.raise_for_status()
            job=response.json()
            if job['message']!=previous:
                previous=job['message'];print(job.get('progress'),previous,flush=True)
            if job['status']=='error':
                raise RuntimeError(job['message'])
            if job['status']=='done':
                result=job['result']
                summary={'track':track,'audio_windows':len(result['audio']),
                         'lyric_lines':len(result['lyrics']),'device':result['device'],
                         'cached':result['cached'],'split':result['split'],'warnings':result['warnings']}
                print(json.dumps(summary,indent=2,ensure_ascii=False))
                Path('data/song-smoke.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
                break
            time.sleep(1)
        else:
            raise TimeoutError('Song analysis exceeded 30 minutes')
