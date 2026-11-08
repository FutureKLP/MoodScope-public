"""Optional Music2Emo process, isolated from the active audio model and playback."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from . import cancellation

ROOT=Path(__file__).resolve().parents[1]
WEIGHTS=ROOT/'models/music2emo'
METHOD='music2emo-curve-v1'


def project_analysis(analysis,result):
    """Use the selected direct regressions without inventing six-way categories."""
    return {**analysis,'audio':[{**row,'scores':{}} for row in result['rows']],
            'expression_source':'Music2Emo','expression_model_basis':result.get('model_basis'),
            'expression_context_seconds':result.get('context_seconds',30)}


def ready():
    return all((WEIGHTS/name).is_file() for name in (
        'installation.json','provenance.json','J_all.ckpt','btc_model_large_voca.pt',
        'mert/pytorch_model.bin','source/music2emo.py','packages/music21/__init__.py'))


def fingerprint():
    if not ready():return None
    return hashlib.sha256(METHOD.encode()+(WEIGHTS/'installation.json').read_bytes()+(WEIGHTS/'provenance.json').read_bytes()).hexdigest()


def analyse(audio,data,device,progress):
    if not ready():raise RuntimeError('Music2Emo-Vergleich ist nicht lokal eingerichtet.')
    with tempfile.TemporaryDirectory(prefix='expression-',dir=data) as directory:
        output=Path(directory)
        with (output/'worker.log').open('wb') as log:
            # The optional research adapter is verified with the base environment;
            # the service may independently use the newer transcription runtime.
            base_python=ROOT/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
            interpreter=str(base_python) if base_python.is_file() else sys.executable
            process=subprocess.Popen([interpreter,'-m','scripts.music2emo_curve','--audio',str(audio),
                '--weights',str(WEIGHTS),'--output',str(output),'--device',device],cwd=ROOT,
                stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            started=time.monotonic()
            try:
                while process.poll() is None:
                    cancellation.check()
                    if time.monotonic()-started>1800:raise RuntimeError('Music2Emo-Vergleich hat das Zeitlimit erreicht.')
                    try:
                        state=json.loads((output/'progress.json').read_text())
                        progress('Vergleiche musikalischen Ausdruck mit Music2Emo',10+int(85*state['done']/state['total']))
                    except (OSError,ValueError,KeyError,ZeroDivisionError):pass
                    time.sleep(.25)
                cancellation.check()
                if process.returncode:raise RuntimeError('Music2Emo-Vergleich fehlgeschlagen; Installation oder Audio nicht kompatibel.')
                result=json.loads((output/'result.json').read_text(encoding='utf8'))
                if result.get('method')!=METHOD or not result.get('rows'):raise RuntimeError('Ungültiges Vergleichsergebnis.')
                return result
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:process.wait(timeout=5)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
