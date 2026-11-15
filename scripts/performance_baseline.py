"""Offline performance probes on generated audio, never the user's library.

Run as a module. Results, audio and scratch files must stay in an ignored .tools
directory. Each model runs in a separate process; no weights are downloaded.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def fixture(path, seconds):
    import numpy as np
    import soundfile as sf
    sr = 48000
    t = np.arange(round(sr*seconds), dtype=np.float64)/sr
    # Deterministic tones and amplitude modulation; no speech or emotion labels.
    left = .12*np.sin(2*np.pi*220*t)*(1+.25*np.sin(2*np.pi*2*t))
    right = .08*np.sin(2*np.pi*330*t)+.02*np.sin(2*np.pi*880*t)
    sf.write(path, np.stack([left, right], axis=1), sr, subtype='PCM_16')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(name, fn, rows):
    import psutil
    import torch
    gpu = torch.cuda.is_available()
    if gpu:
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    process = psutil.Process()
    before = process.cpu_times()
    start = time.perf_counter()
    value = fn()
    if gpu:
        torch.cuda.synchronize()
    elapsed = time.perf_counter()-start
    after = process.cpu_times()
    row = {'name': name, 'seconds': elapsed,
           'process_cpu_seconds': after.user+after.system-before.user-before.system,
           'rss_after_mib': process.memory_info().rss/2**20}
    if gpu:
        row.update(cuda_peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20,
                   cuda_peak_reserved_mib=torch.cuda.max_memory_reserved()/2**20)
    rows.append(row)
    return value


def worker(args):
    # Set before importing any application module. Ignore the user's model/device
    # settings while reusing only installed weight files in the shared model cache.
    area = Path(args.output).resolve()
    data = area/'data'
    data.mkdir(exist_ok=True)
    os.environ.update(MOODSCOPE_DATA=str(data), HF_HOME=str(ROOT/'models'),
                      HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', USE_TF='0',
                      USE_FLAX='0', MOODSCOPE_DEVICE=args.device,
                      MOODSCOPE_WHISPER_DEVICE='cpu')
    # Deny network in this worker, including accidental model download paths.
    import socket
    def denied(*a, **k):
        raise RuntimeError('Network disabled in performance worker')
    socket.socket.connect = denied
    import torch
    import soundfile as sf
    from backend.models import Engines
    engine = Engines()
    engine.data = data
    audio = area/'synthetic.wav'
    rows = []
    progress = lambda *a: None
    from unittest.mock import patch
    if args.worker == 'clap':
        from transformers import ClapModel, ClapProcessor
        for cls, label in [(ClapProcessor, 'clap_processor_load'), (ClapModel, 'clap_weight_load_cpu')]:
            original = cls.from_pretrained
            def loader(*a, _fn=original, _label=label, **k):
                return measure(_label, lambda: _fn(*a, **k), rows)
            setattr(cls, 'from_pretrained', loader)
        y, sr = sf.read(audio, dtype='float32', always_2d=True)
        y = y.mean(axis=1)
        measure('clap_first_total', lambda: engine.audio(y, sr, progress), rows)
        for _ in range(args.repeat):
            measure('clap_resident_inference', lambda: engine.audio(y, sr, progress), rows)
        # Real application job and exact repeat: verify cached flag and forbid
        # inference on the hit. The first job reuses the already resident model.
        import backend.app as app
        app.engines = engine
        track = app.import_path(audio, 'Synthetic benchmark.wav')
        request = app.AnalyzeRequest(whisper=False)
        def job():
            app.jobs['benchmark'] = {'status': 'running'}
            app.run_job('benchmark', track['id'], request)
            result = app.jobs['benchmark']
            if result['status'] != 'done':
                raise RuntimeError('Benchmark analysis job failed')
            return result['result']
        acoustic = app.insights.acoustic_features
        def features(*a, **k):
            return measure('acoustic_features_first', lambda: acoustic(*a, **k), rows)
        with patch.object(app.insights, 'acoustic_features', features):
            measure('analysis_job_resident_uncached', job, rows)
        for _ in range(args.repeat):
            measure('acoustic_features_warm', lambda: acoustic(y, sr), rows)
        with patch.object(engine, 'audio', side_effect=AssertionError('Cache executed inference')):
            for _ in range(args.repeat):
                if not measure('analysis_job_cache_hit', job, rows)['cached']:
                    raise AssertionError('Expected cache hit')
    elif args.worker == 'whisper':
        import faster_whisper
        original = faster_whisper.WhisperModel
        def load(*a, **k):
            k['local_files_only'] = True
            return measure('whisper_base_load_cpu_int8', lambda: original(*a, **k), rows)
        with patch.object(faster_whisper, 'WhisperModel', load):
            for _ in range(args.repeat):
                # The app deliberately reloads Whisper on each invocation.
                measure('whisper_base_total_cpu_int8', lambda: engine.transcribe(audio, progress, language='en'), rows)
    elif args.worker == 'demucs':
        from backend import demucs_models, separation
        original = demucs_models.load_model
        def existing(url, destination, expected):
            if not Path(destination).is_file():
                raise RuntimeError('Demucs weights absent; download disabled')
        def load(*a, **k):
            return measure('demucs_htdemucs_weight_load_cpu', lambda: original(*a, **k), rows)
        # Separate distinct generated copies to measure uncached invocations;
        # cached status calls are separately labelled and validated.
        import shutil
        with patch.object(demucs_models, 'fetch_checkpoint', existing), patch.object(demucs_models, 'load_model', load):
            for i in range(args.repeat):
                identity = 'synthetic-'+str(i)
                shutil.copyfile(audio, data/(identity+'.wav'))
                measure('demucs_htdemucs_total', lambda: separation.separate(data, identity, 'htdemucs', engine, progress), rows)
                if not measure('demucs_cache_hit', lambda: separation.separate(data, identity, 'htdemucs', engine, progress), rows)['cached']:
                    raise AssertionError('Expected stem cache')
    elif args.worker == 'music2emo':
        from backend import expression_compare
        if not expression_compare.ready():
            raise RuntimeError('Music2Emo not installed')
        # Includes verified weights, new worker, load, contexts, IO and teardown.
        # Child uses the existing compatibility runtime selected by the app.
        original = subprocess.Popen
        class TimedProcess(original):
            def __init__(self, command, *a, **k):
                self.performance_file = None
                if 'scripts.music2emo_curve' in command:
                    command = [*command, '--timings']
                    self.performance_file = Path(command[command.index('--output')+1])/'performance.json'
                super().__init__(command, *a, **k)
            def poll(self):
                code = super().poll()
                if code == 0 and self.performance_file and self.performance_file.exists():
                    value = json.loads(self.performance_file.read_text(encoding='utf8'))
                    rows.extend(value['rows'])
                    rows.append({'name':'music2emo_worker_metadata','seconds':0,
                                 **{key:v for key,v in value.items() if key!='rows'}})
                    self.performance_file = None
                return code
        with patch.object(subprocess, 'Popen', TimedProcess):
            for _ in range(args.repeat):
                measure('music2emo_application_worker_total', lambda: expression_compare.analyse(audio, data, args.device, progress), rows)
    (area/(args.worker+'.json')).write_text(json.dumps({'rows': rows,
        'runtime':{'python':platform.python_version(),'torch':torch.__version__,
                   'torch_threads':torch.get_num_threads(),'device':args.device,
                   'whisper_device':'cpu' if args.worker=='whisper' else None}}, indent=2), encoding='utf8')


def supervise(command, area, label, timeout):
    import psutil
    log = (area/(label+'.log')).open('wb')
    start = time.perf_counter()
    process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=log,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    root = psutil.Process(process.pid)
    samples = []
    resources = []
    previous_cpu = {}
    previous_time = start
    psutil.cpu_percent()
    timed_out = False
    try:
        while process.poll() is None:
            try:
                family = [root]+root.children(recursive=True)
                current = time.perf_counter()
                rss = 0
                cpu_delta = 0
                current_cpu = {}
                for member in family:
                    try:
                        rss += member.memory_info().rss/2**20
                        cpu = member.cpu_times()
                        total = cpu.user+cpu.system
                        if member.pid in previous_cpu:
                            cpu_delta += max(0, total-previous_cpu[member.pid])
                        current_cpu[member.pid] = total
                    except psutil.Error:
                        pass
                resources.append({'elapsed_s': current-start, 'tree_rss_mib': rss,
                    'tree_cpu_one_core_percent': cpu_delta/max(.001,current-previous_time)*100,
                    'system_cpu_percent': psutil.cpu_percent(),
                    'system_ram_used_mib': psutil.virtual_memory().used/2**20})
                previous_cpu = current_cpu
                previous_time = current
                samples.append(rss)
            except psutil.Error:
                pass
            if time.perf_counter()-start > timeout:
                timed_out = True
                break
            time.sleep(.2)
    finally:
        if process.poll() is None:
            try:
                family = root.children(recursive=True)
                for child in reversed(family):
                    try: child.terminate()
                    except psutil.Error: pass
            except psutil.Error:
                pass
            process.terminate()
        process.wait(timeout=15)
        log.close()
    result = {'status': 'timeout' if timed_out else 'passed' if process.returncode == 0 else 'failed',
              'process_wall_seconds': time.perf_counter()-start,
              'sample_interval_seconds': .2, 'sampled_tree_rss_peak_mib': max(samples, default=0),
              'resource_samples': resources}
    report = area/(label+'.json')
    if result['status']=='passed' and report.exists():
        result.update(json.loads(report.read_text(encoding='utf8')))
    return result


def startup(area, repeat):
    """Process creation to HTTP health, including first actual device probe."""
    import httpx
    import psutil
    import socket
    rows = []
    for i in range(repeat):
        data = area/('startup-'+str(i))
        data.mkdir()
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        env = {**os.environ, 'MOODSCOPE_DATA': str(data), 'HF_HUB_OFFLINE': '1',
               'TRANSFORMERS_OFFLINE': '1', 'MOODSCOPE_DEVICE': 'auto'}
        with (area/('startup-'+str(i)+'.log')).open('wb') as log:
            start = time.perf_counter()
            process = subprocess.Popen([sys.executable, '-m', 'scripts.service', '--port', str(port)],
                                       cwd=ROOT, env=env, stdout=log, stderr=log,
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            try:
                with httpx.Client(base_url=f'http://127.0.0.1:{port}', trust_env=False, timeout=2) as client:
                    while time.perf_counter()-start < 90:
                        if process.poll() is not None:
                            raise RuntimeError('Benchmark service exited')
                        try:
                            response = client.get('/api/health')
                            if response.is_success:
                                break
                        except httpx.HTTPError:
                            pass
                        time.sleep(.05)
                    else:
                        raise TimeoutError('Service readiness')
                    rows.append({'name': 'supervisor_to_health', 'seconds': time.perf_counter()-start})
                    for _ in range(5):
                        t = time.perf_counter()
                        client.get('/api/health').raise_for_status()
                        rows.append({'name': 'health_warm_http', 'seconds': time.perf_counter()-t})
            finally:
                root = psutil.Process(process.pid)
                for child in root.children(recursive=True):
                    try: child.terminate()
                    except psutil.Error: pass
                process.terminate()
                process.wait(timeout=15)
    return {'status': 'passed', 'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--seconds', type=float, default=12)
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--device', choices=['cpu', 'cuda:0'], default='cuda:0')
    parser.add_argument('--tasks', nargs='+', choices=['startup', 'clap', 'music2emo', 'whisper', 'demucs'],
                        default=['startup', 'clap', 'music2emo', 'whisper', 'demucs'])
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--worker', choices=['clap', 'music2emo', 'whisper', 'demucs'])
    args = parser.parse_args()
    area = Path(args.output).resolve()
    if not area.is_relative_to(ROOT/'.tools') or not 0 < args.seconds <= 60 or not 1 <= args.repeat <= 10:
        parser.error('Use a fresh .tools output directory, 0 < seconds <= 60, and 1..10 repeats')
    if args.worker:
        worker(args)
        return
    area.mkdir(parents=True, exist_ok=False)
    import psutil
    packages = {}
    for name in ['torch', 'transformers', 'faster-whisper', 'demucs', 'psutil', 'numpy', 'soundfile']:
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
    report = {'schema': 1, 'platform': platform.platform(), 'cpu': platform.processor(),
              'logical_cpus': psutil.cpu_count(), 'ram_gib': psutil.virtual_memory().total/2**30,
              'python': platform.python_version(), 'packages': packages,
              'seconds_audio': args.seconds, 'repeat': args.repeat, 'device': args.device,
              'fixture_sha256': fixture(area/'synthetic.wav', args.seconds),
              'fixture': 'PCM16 stereo 48 kHz deterministic tones v1; not speech or music quality evidence',
              'results': {}}
    try:
        git = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['source_commit'] = git
        report['tracked_worktree_dirty'] = subprocess.run(['git','diff','--quiet','HEAD'],cwd=ROOT).returncode != 0
        report['harness_sha256'] = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                                    for name in ['scripts/performance_baseline.py','scripts/music2emo_curve.py']}
    except (OSError, subprocess.SubprocessError):
        report['source_commit'] = None
    # Whole-device values include desktop/other processes; never label as app-only.
    gpu_samples = []
    stop = threading.Event()
    def gpu_poll():
        while not stop.is_set():
            try:
                raw = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used',
                    '--format=csv,noheader,nounits'], timeout=3, text=True,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                gpu_samples.append({'elapsed_s': time.perf_counter()-gpu_start, 'devices': raw.strip().splitlines()})
            except (OSError, subprocess.SubprocessError):
                pass
            stop.wait(1)
    gpu_start = time.perf_counter()
    sampler = threading.Thread(target=gpu_poll, daemon=True)
    sampler.start()
    try:
        for task in args.tasks:
            print('Benchmark:', task, flush=True)
            if task == 'startup':
                result = startup(area, args.repeat)
            else:
                compatible = ROOT/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
                interpreter = compatible if task=='music2emo' and compatible.is_file() else Path(sys.executable)
                command = [str(interpreter), '-m', 'scripts.performance_baseline', '--worker', task,
                           '--output', str(area), '--seconds', str(args.seconds), '--repeat', str(args.repeat),
                           '--device', args.device]
                result = supervise(command, area, task, args.timeout)
            report['results'][task] = result
            (area/'report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
            print(task, result['status'], flush=True)
    finally:
        stop.set()
        sampler.join(timeout=4)
        report['whole_device_gpu_samples'] = gpu_samples
        (area/'report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    if any(result['status'] != 'passed' for result in report['results'].values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
