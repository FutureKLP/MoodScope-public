"""Local synthetic desktop acceptance workspace; never reuse a production service.

This prepares data and records evidence. Native inputs use Windows UI Automation
through the separately documented Computer Use driver, not HTTP dialog mocks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'moodscope-synthetic-desktop-v1'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def files(folder):
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def production_databases():
    return {p.name: digest(p) for p in (ROOT / 'data').glob('*')
            if p.is_file() and any(s in p.name for s in ('.sqlite', '.db'))}


def workspace(value):
    area = Path(value).resolve()
    if not area.is_relative_to((ROOT / '.tools').resolve()) or area.is_symlink():
        raise ValueError('Workspace must be a dedicated directory below .tools')
    marker = json.loads((area / 'workspace.json').read_text())
    if marker['kind'] != MARKER:
        raise ValueError('Not a synthetic desktop workspace')
    for name in ('data', 'exports', 'webview', 'evidence'):
        if not (area / name).resolve().is_relative_to(area):
            raise ValueError('Workspace contains an escaping path')
    return area, marker


def prepare():
    parent = ROOT / '.tools'
    parent.mkdir(exist_ok=True)
    area = Path(tempfile.mkdtemp(prefix='desktop-', dir=parent))
    for name in ('data', 'exports', 'webview', 'evidence'):
        (area / name).mkdir()
    os.environ['MOODSCOPE_DATA'] = str(area / 'data')
    # Import only after setting the isolated data root.
    from backend import app
    from fastapi.testclient import TestClient
    import math
    import struct
    source = area / 'synthetic-440hz-0-2s.wav'
    with wave.open(str(source), 'wb') as audio:
        audio.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
        audio.writeframes(b''.join(struct.pack('<hh', *([int(4000 * math.sin(2 * math.pi * 440 * n / 48000))] * 2)) for n in range(96000)))
    with TestClient(app.app) as client, source.open('rb') as stream:
        response = client.post('/api/tracks', files={'file': (source.name, stream, 'audio/wav')})
        response.raise_for_status()
        identity = response.json()['id']
    # Deliberately authored cached source: no Demucs or scientific analysis claim.
    import shutil
    stems = area / 'data' / 'stems' / identity / 'htdemucs_auto'
    stems.mkdir(parents=True)
    shutil.copyfile(source, stems / 'vocals.wav')
    (stems / 'manifest.json').write_text(json.dumps({'model': 'htdemucs_auto', 'sources': ['vocals'],
        'sample_rate': 48000, 'duration': 2, 'note': 'Synthetic export fixture; no source separation performed.'}))
    # Opening an uncached song normally starts local inference. Keep this export
    # acceptance independent of installed models and clearly label authored data.
    from backend import expression_compare
    analysis = {'audio': [], 'lyrics': [], 'split': None, 'warnings': ['Synthetic desktop export fixture'],
                'device': 'fixture', 'method': 'synthetic-desktop-fixture', 'models': {}, 'source_lyrics': ''}
    comparison = {'rows': [{'start': 0, 'end': 2, 'valence': 0, 'arousal': 0, 'tags': {}}],
                  'method': expression_compare.METHOD, 'model_basis': expression_compare.fingerprint(),
                  'track_id': identity, 'synthetic_fixture': True}
    with app.db() as conn:
        for key, value in [(f'latest:{identity}:local', analysis),
                           (f'expression-comparison:{identity}', comparison)]:
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)', (key, json.dumps(value)))
            conn.execute('INSERT OR REPLACE INTO cache_owner VALUES (?,?)', (key, identity))
    shutil.copyfile(source, area / 'exports' / 'existing.wav')
    marker = {'kind': MARKER, 'track_id': identity, 'source_hash': digest(source),
              'production_databases': production_databases(), 'exports': files(area / 'exports')}
    (area / 'workspace.json').write_text(json.dumps(marker, indent=2))
    print(area, flush=True)


def environment(area):
    return {**os.environ, 'MOODSCOPE_DATA': str(area / 'data'),
            'WEBVIEW2_USER_DATA_FOLDER': str(area / 'webview'),
            'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'CUDA_VISIBLE_DEVICES': ''}


def run(area, binary):
    import httpx
    import psutil
    # A pre-existing service must never be reused, even when its health is OK.
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 8765))
    binary = Path(binary).resolve()
    if not binary.is_relative_to((ROOT / 'src-tauri' / 'target').resolve()) or not binary.is_file():
        raise ValueError('Use an existing project-local native build')
    log = (area / 'evidence' / 'backend.log').open('ab')
    children = []
    try:
        server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', '8765'],
            cwd=ROOT, env=environment(area), stdout=log, stderr=log,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        children.append(server)
        with httpx.Client(trust_env=False, timeout=2) as client:
            deadline = time.monotonic() + 60
            while True:
                if server.poll() is not None:
                    raise RuntimeError('Isolated backend exited; see local backend.log')
                try:
                    health = client.get('http://127.0.0.1:8765/api/health')
                    if health.is_success:
                        library = client.get('http://127.0.0.1:8765/api/library')
                        library.raise_for_status()
                        tracks = library.json()['tracks']
                        _, marker = workspace(area)
                        if [t['id'] for t in tracks] != [marker['track_id']]:
                            raise RuntimeError('Unexpected backend library; refusing native launch')
                        break
                except httpx.TransportError:
                    pass
                if time.monotonic() >= deadline:
                    raise TimeoutError('Isolated backend readiness deadline exceeded')
                time.sleep(.2)
        while not (area / 'stop').exists():
            native = subprocess.Popen([str(binary)], cwd=ROOT, env=environment(area))
            children.append(native)
            (area / 'evidence' / 'processes.json').write_text(json.dumps({
                'backend': server.pid, 'native': native.pid, 'binary_sha256': digest(binary),
                'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}, indent=2))
            print('ISOLATED_NATIVE_READY', flush=True)
            while native.poll() is None and not (area / 'stop').exists() and not (area / 'restart').exists():
                if server.poll() is not None:
                    raise RuntimeError('Isolated backend exited during acceptance')
                time.sleep(.2)
            if (area / 'restart').exists():
                (area / 'restart').unlink()
                if native.poll() is None:
                    native.terminate()
                native.wait(timeout=10)
                continue
            break
    finally:
        for process in reversed(children):
            if process.poll() is not None:
                continue
            try:
                descendants = psutil.Process(process.pid).children(recursive=True)
                process.terminate()
                for child in descendants:
                    try: child.terminate()
                    except psutil.NoSuchProcess: pass
                _, alive = psutil.wait_procs(descendants, timeout=5)
                for child in alive: child.kill()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            except (psutil.NoSuchProcess, ProcessLookupError):
                pass
        log.close()
        print('ISOLATED_NATIVE_STOPPED', flush=True)


def snapshot(area, label, baseline=None):
    import psutil
    _, marker = workspace(area)
    result = {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'exports': files(area / 'exports'),
              'production_databases_unchanged': production_databases() == marker['production_databases'],
              'source_unchanged': digest(area / 'synthetic-440hz-0-2s.wav') == marker['source_hash']}
    with sqlite3.connect(f'file:{(area / "data" / "cache.sqlite3").as_posix()}?mode=ro', uri=True) as conn:
        result['sqlite_integrity'] = conn.execute('PRAGMA integrity_check').fetchone()[0]
    process_file = area / 'evidence' / 'processes.json'
    if process_file.exists():
        result['processes'] = []
        for role, pid in json.loads(process_file.read_text()).items():
            if role not in ('backend', 'native'): continue
            try:
                process = psutil.Process(pid)
                family = [process, *process.children(recursive=True)]
                result['processes'].append({'role': role, 'pid': pid, 'rss': process.memory_info().rss,
                    'children': len(family) - 1, 'family_rss': sum(p.memory_info().rss for p in family),
                    'handles': sum(p.num_handles() for p in family) if sys.platform == 'win32' else None})
            except psutil.NoSuchProcess: pass
    if baseline:
        before = json.loads((area / 'evidence' / (baseline + '.json')).read_text())
        result['exports_unchanged'] = result['exports'] == before['exports']
    (area / 'evidence' / (label + '.json')).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    assert result['production_databases_unchanged'] and result['source_unchanged']
    assert result['sqlite_integrity'] == 'ok'
    if baseline: assert result['exports_unchanged'], 'Export directory changed after cancel'


def geometry(area):
    """Read-only Win32 diagnostics, with no UI Automation or input injection."""
    if sys.platform != 'win32':
        raise RuntimeError('Window geometry diagnostics require Windows')
    import ctypes as c
    from ctypes import wintypes as w
    import platform
    user = c.WinDLL('user32', use_last_error=True)
    process = json.loads((area / 'evidence' / 'processes.json').read_text())
    user.GetForegroundWindow.restype = w.HWND
    user.GetWindow.argtypes = [w.HWND, w.UINT]
    user.GetWindow.restype = w.HWND
    user.GetWindowRect.argtypes = [w.HWND, c.POINTER(w.RECT)]
    user.GetClientRect.argtypes = [w.HWND, c.POINTER(w.RECT)]
    user.GetWindowThreadProcessId.argtypes = [w.HWND, c.POINTER(w.DWORD)]
    user.GetDpiForWindow.argtypes = [w.HWND]
    user.GetDpiForWindow.restype = w.UINT
    user.IsWindowVisible.argtypes = [w.HWND]
    user.IsIconic.argtypes = [w.HWND]
    user.GetWindowTextW.argtypes = [w.HWND, w.LPWSTR, c.c_int]
    user.GetClassNameW.argtypes = [w.HWND, w.LPWSTR, c.c_int]
    callback_type = c.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    user.EnumWindows.argtypes = [callback_type, w.LPARAM]
    foreground = user.GetForegroundWindow()
    windows = []

    def visit(handle, _):
        pid = w.DWORD()
        user.GetWindowThreadProcessId(handle, c.byref(pid))
        if pid.value != process['native']: return True
        title, kind = c.create_unicode_buffer(512), c.create_unicode_buffer(256)
        user.GetWindowTextW(handle, title, 512)
        user.GetClassNameW(handle, kind, 256)
        rect, client = w.RECT(), w.RECT()
        user.GetWindowRect(handle, c.byref(rect))
        user.GetClientRect(handle, c.byref(client))
        windows.append({'handle': handle, 'pid': pid.value, 'title': title.value, 'class': kind.value,
            'owner': user.GetWindow(handle, 4), 'visible': bool(user.IsWindowVisible(handle)),
            'minimized': bool(user.IsIconic(handle)), 'foreground': handle == foreground,
            'dpi': user.GetDpiForWindow(handle), 'window_rect': [rect.left, rect.top, rect.right, rect.bottom],
            'client_rect': [client.left, client.top, client.right, client.bottom]})
        return True

    user.EnumWindows(callback_type(visit), 0)
    result = {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'windows_version': platform.version(), 'windows': windows}
    (area / 'evidence' / ('geometry-' + str(time.time_ns()) + '.json')).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


def validate(area, filename):
    import numpy as np
    import soundfile as sf
    path = (area / 'exports' / filename).resolve()
    if path.parent != (area / 'exports').resolve() or path.suffix.lower() != '.wav':
        raise ValueError('Validate only a WAV directly inside the export workspace')
    header = path.read_bytes()[:12]
    samples, rate = sf.read(path, always_2d=True)
    peak = float(np.argmax(abs(np.fft.rfft(samples[:, 0]))) * rate / len(samples))
    result = {'sample_rate': rate, 'channels': samples.shape[1], 'frames': len(samples),
        'seconds': len(samples) / rate, 'bytes': path.stat().st_size,
        'riff_wave': header[:4] == b'RIFF' and header[8:] == b'WAVE',
        'riff_size_matches': int.from_bytes(header[4:8], 'little') + 8 == path.stat().st_size,
        'finite': bool(np.isfinite(samples).all()), 'peak_hz': peak,
        'source_equal': digest(path) == digest(area / 'synthetic-440hz-0-2s.wav')}
    (area / 'evidence' / ('wave-' + path.stem + '.json')).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    assert rate == 48000 and samples.shape == (96000, 2) and peak == 440
    assert all(result[key] for key in ('riff_wave', 'riff_size_matches', 'finite', 'source_equal'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'run', 'snapshot', 'geometry', 'validate'])
    parser.add_argument('--area')
    parser.add_argument('--binary', default=str(ROOT / 'src-tauri/target/v03/release/moodscope.exe'))
    parser.add_argument('--label', default='snapshot')
    parser.add_argument('--baseline')
    parser.add_argument('--filename')
    args = parser.parse_args()
    for label in (args.label, args.baseline):
        if label is not None and (not label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in label)):
            parser.error('Evidence labels must be plain names')
    if args.action == 'prepare':
        prepare()
    else:
        if not args.area: parser.error('--area is required')
        area, _ = workspace(args.area)
        if args.action == 'run': run(area, args.binary)
        elif args.action == 'geometry': geometry(area)
        elif args.action == 'validate':
            if not args.filename: parser.error('--filename is required')
            validate(area, args.filename)
        else: snapshot(area, args.label, args.baseline)


if __name__ == '__main__':
    main()
