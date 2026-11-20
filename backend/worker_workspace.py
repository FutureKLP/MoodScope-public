"""Owned Music2Emo scratch areas with OS leases; ambiguous areas are retained."""
from contextlib import contextmanager, ExitStack
import json
import os
from pathlib import Path
import stat
import uuid
from itertools import islice

ROOT_NAME = '.music2emo-workers-v1'


@contextmanager
def lease(path):
    # Never create a lease during recovery: missing metadata means unknown owner.
    with Path(path).open('r+b') as stream:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def safe(path):
    info = path.lstat()
    return not (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400)


def root(data):
    base = Path(data).resolve() / ROOT_NAME
    base.mkdir(exist_ok=True)
    if not safe(base):
        raise OSError('Worker root is a link')
    marker = base / 'owner.json'
    try:
        with marker.open('x', encoding='utf8') as stream:
            json.dump({'kind': ROOT_NAME, 'id': uuid.uuid4().hex}, stream)
    except FileExistsError:
        pass
    if not safe(marker):
        raise OSError('Worker root marker is a link')
    owner = json.loads(marker.read_text(encoding='utf8'))
    if not isinstance(owner, dict) or owner.get('kind') != ROOT_NAME or not isinstance(owner.get('id'), str) or len(owner['id']) != 32:
        raise ValueError('Unknown worker root')
    return base, owner['id']


def inventory(area):
    """Bounded preflight, then explicit unlink/rmdir; never follow reparse points."""
    files, directories = [], []
    pending = [(area, 0)]
    while pending:
        directory, depth = pending.pop()
        if depth > 12 or not safe(directory):
            raise ValueError('Unknown worker tree')
        directories.append(directory)
        for entry in directory.iterdir():
            info = entry.lstat()
            if not safe(entry) or getattr(info, 'st_nlink', 1) > 1 and stat.S_ISREG(info.st_mode):
                raise ValueError('Linked worker entry')
            if stat.S_ISDIR(info.st_mode):
                pending.append((entry, depth + 1))
            elif stat.S_ISREG(info.st_mode):
                files.append(entry)
            else:
                raise ValueError('Unknown worker entry')
            if len(files) + len(directories) + len(pending) > 4096:
                raise ValueError('Worker tree exceeds bound')
    return files, directories


def recover(data):
    removed = []
    try:
        base, owner = root(data)
        # Limit each pass; never inspect legacy expression-* directories.
        for area in islice(base.iterdir(), 1024):
            try:
                if not area.name.startswith('job-') or len(area.name) != 36 or not safe(area) or not area.is_dir():
                    continue
                for name in ('owner.json', 'parent.lease', 'worker.lease'):
                    if not safe(area / name):
                        raise ValueError('Unknown lease')
                metadata = json.loads((area / 'owner.json').read_text(encoding='utf8'))
                if metadata != {'kind': ROOT_NAME, 'owner': owner, 'job': area.name[4:]}:
                    continue
                with ExitStack() as stack:
                    stack.enter_context(lease(area / 'parent.lease'))
                    stack.enter_context(lease(area / 'worker.lease'))
                    files, directories = inventory(area)
                    # Windows needs lease handles closed before unlinking them.
                    for path in files:
                        if path.name not in {'parent.lease', 'worker.lease', 'owner.json'} or path.parent != area:
                            path.unlink()
                    for path in reversed(directories):
                        if path != area:
                            path.rmdir()
                # No new worker can begin: its parent lease must still be held.
                for name in ('worker.lease', 'parent.lease', 'owner.json'):
                    (area / name).unlink()
                area.rmdir()
                removed.append(area.name)
            except (OSError, ValueError, TypeError):
                continue
    except (OSError, ValueError, TypeError):
        pass
    return removed


@contextmanager
def workspace(data):
    recover(data)
    base, owner = root(data)
    identity = uuid.uuid4().hex
    area = base / ('job-' + identity)
    area.mkdir()
    for name in ('parent.lease', 'worker.lease'):
        (area / name).write_bytes(b'0')
    try:
        with lease(area / 'parent.lease'):
            (area / 'owner.json').write_text(json.dumps({'kind': ROOT_NAME, 'owner': owner, 'job': identity}), encoding='utf8')
            yield area
    finally:
        recover(data)
