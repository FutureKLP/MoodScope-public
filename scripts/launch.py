"""Start the project-local native app and own only the backend process we create."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

if __package__:
    from .runtime import preferred_python,environment_id
else:
    from runtime import preferred_python,environment_id

ROOT=Path(__file__).resolve().parents[1]


def latest_binary():
    binary='moodscope.exe' if os.name=='nt' else 'moodscope'
    candidates=[ROOT/'src-tauri'/'target'/version/'release'/binary for version in ['v03','v02']]
    candidates.append(ROOT/'src-tauri'/'target'/'release'/binary)
    return max((p for p in candidates if p.exists()),key=lambda p:p.stat().st_mtime,default=candidates[0])


def run_desktop(before_launch=None):
    while True:
        if before_launch:before_launch()
        result=subprocess.run([str(latest_binary())],cwd=ROOT)
        if result.returncode==75:continue
        result.check_returncode()
        return


def ready():
    try:
        with urlopen('http://127.0.0.1:8765/api/health',timeout=2) as response:
            state=json.load(response)
            if state.get('status')!='ok': return False
            if state.get('version')!='0.3.0' or state.get('api_revision')!=9:
                raise RuntimeError('Ein älteres Backend läuft auf Port 8765. Den bisherigen MoodScope-Dienst beenden und erneut starten.')
            if state.get('runtime_id')!=environment_id():
                raise RuntimeError('Ein MoodScope-Dienst aus einer anderen Python-Umgebung läuft. In der App Beenden wählen und den Projektstarter erneut öffnen.')
            return True
    except (OSError,ValueError):
        return False


def main():
    selected=preferred_python(ROOT)
    if selected.is_file() and selected.resolve()!=Path(sys.executable).resolve():
        raise SystemExit(subprocess.call([str(selected),str(Path(__file__).resolve())],cwd=ROOT))
    os.chdir(ROOT)
    exe=latest_binary()
    if not exe.exists():
        raise SystemExit('Native App fehlt. Zuerst: npm run tauri build -- --no-bundle')
    backend=None
    (ROOT/'data').mkdir(exist_ok=True)
    with (ROOT/'data'/'backend.log').open('a',encoding='utf-8') as log:
        def ensure_backend():
            nonlocal backend
            if not ready():
                backend=subprocess.Popen([sys.executable,'-m','scripts.service','--port','8765'],
                    cwd=ROOT,stdout=log,stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                for _ in range(60):
                    if ready(): break
                    if backend.poll() is not None: raise RuntimeError('Backend beendet. Siehe data/backend.log')
                    time.sleep(.5)
                else: raise RuntimeError('Backend startet nicht. Siehe data/backend.log')
        try:
            run_desktop(ensure_backend)
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
