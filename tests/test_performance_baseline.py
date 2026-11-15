"""Safety contracts for opt-in benchmarks; no actual model inference in pytest."""
import hashlib
from pathlib import Path
import subprocess
import sys

from scripts.performance_baseline import fixture


def test_generated_fixture_is_deterministic_and_preserves_other_files(tmp_path):
    original = tmp_path/'original.wav'
    original.write_bytes(b'original fixture')
    before = hashlib.sha256(original.read_bytes()).hexdigest()
    first = tmp_path/'first.wav'
    second = tmp_path/'second.wav'
    assert fixture(first, .1) == fixture(second, .1)
    assert first.read_bytes() == second.read_bytes()
    assert hashlib.sha256(original.read_bytes()).hexdigest() == before


def test_benchmark_rejects_output_outside_ignored_tools(tmp_path):
    import uuid
    destination = Path(__file__).resolve().parents[1]/('benchmark-forbidden-'+uuid.uuid4().hex)
    run = subprocess.run([sys.executable, '-m', 'scripts.performance_baseline',
                          '--output', str(destination), '--tasks', 'clap'],
                         capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=15)
    assert run.returncode != 0
    assert not destination.exists()


def test_benchmark_refuses_existing_output_without_touching_it():
    import tempfile
    root = Path(__file__).resolve().parents[1]
    (root/'.tools').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='benchmark-safety-', dir=root/'.tools') as directory:
        sentinel = Path(directory)/'sentinel.txt'
        sentinel.write_text('keep')
        run = subprocess.run([sys.executable, '-m', 'scripts.performance_baseline',
                              '--output', directory, '--tasks', 'clap'],
                             capture_output=True, cwd=root, timeout=15)
        assert run.returncode != 0
        assert b'FileExistsError' in run.stderr
        assert sentinel.read_text() == 'keep'
        assert not (Path(directory)/'synthetic.wav').exists()
