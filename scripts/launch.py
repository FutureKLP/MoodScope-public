"""Start the project-local native app and own only the backend process we create."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]


def ready():
    try:
        with urlopen('http://127.0.0.1:8765/api/health',timeout=2) as response:
            return json.load(response).get('status')=='ok'
    except (OSError,ValueError):
        return False


def main():
    os.chdir(ROOT)
    binary='moodscope.exe' if os.name=='nt' else 'moodscope'
    candidates=[ROOT/'src-tauri'/'target'/'v02'/'release'/binary,ROOT/'src-tauri'/'target'/'release'/binary]
    exe=next((p for p in candidates if p.exists()),candidates[0])
    if not exe.exists():
        raise SystemExit('Native App fehlt. Zuerst: npm run tauri build -- --no-bundle')
    backend=None
    (ROOT/'data').mkdir(exist_ok=True)
    with (ROOT/'data'/'backend.log').open('a',encoding='utf-8') as log:
        try:
            if not ready():
                backend=subprocess.Popen([sys.executable,'-m','uvicorn','backend.app:app','--host','127.0.0.1','--port','8765'],
                    cwd=ROOT,stdout=log,stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                for _ in range(60):
                    if ready(): break
                    if backend.poll() is not None: raise RuntimeError('Backend beendet. Siehe data/backend.log')
                    time.sleep(.5)
                else: raise RuntimeError('Backend startet nicht. Siehe data/backend.log')
            subprocess.run([str(exe)],cwd=ROOT,check=True)
        finally:
            if backend:
                backend.terminate()
                try: backend.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    backend.kill();backend.wait()


if __name__=='__main__':
    main()
