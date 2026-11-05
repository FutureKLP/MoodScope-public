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
            state=json.load(response)
            if state.get('status')!='ok': return False
            if state.get('version')!='0.3.0' or state.get('api_revision')!=3:
                raise RuntimeError('Ein älteres Backend läuft auf Port 8765. Den bisherigen MoodScope-Dienst beenden und erneut starten.')
            return True
    except (OSError,ValueError):
        return False


def main():
    os.chdir(ROOT)
    binary='moodscope.exe' if os.name=='nt' else 'moodscope'
    candidates=[ROOT/'src-tauri'/'target'/'v03'/'release'/binary,ROOT/'src-tauri'/'target'/'v02'/'release'/binary,ROOT/'src-tauri'/'target'/'release'/binary]
    exe=max((p for p in candidates if p.exists()),key=lambda p:p.stat().st_mtime,default=candidates[0])
    if not exe.exists():
        raise SystemExit('Native App fehlt. Zuerst: npm run tauri build -- --no-bundle')
    backend=None
    (ROOT/'data').mkdir(exist_ok=True)
    with (ROOT/'data'/'backend.log').open('a',encoding='utf-8') as log:
        try:
            if not ready():
                backend=subprocess.Popen([sys.executable,'-m','scripts.service','--port','8765'],
                    cwd=ROOT,stdout=log,stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                for _ in range(60):
                    if ready(): break
                    if backend.poll() is not None: raise RuntimeError('Backend beendet. Siehe data/backend.log')
                    time.sleep(.5)
                else: raise RuntimeError('Backend startet nicht. Siehe data/backend.log')
            subprocess.run([str(exe)],cwd=ROOT,check=True)
        finally:
            if backend and backend.poll() is None:
                import psutil
                process=psutil.Process(backend.pid)
                descendants=process.children(recursive=True)
                for child in reversed(descendants):
                    try:child.terminate()
                    except psutil.Error:pass
                if backend.poll() is None:backend.terminate()
                try: backend.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    backend.kill();backend.wait()


if __name__=='__main__':
    main()
