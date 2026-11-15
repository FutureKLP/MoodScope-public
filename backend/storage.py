"""Recoverable removal of managed copies; source paths never enter the journal."""
import json
import os
from pathlib import Path
import re
import shutil
import uuid


def long_path(path):
    path = Path(path).absolute()
    value = str(path)
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        value = '\\\\?\\UNC\\' + value[2:] if value.startswith('\\\\') else '\\\\?\\' + value
    return Path(value)


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf8') as stream:
            json.dump(value, stream, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def managed_path(data, *parts):
    root = Path(data).resolve()
    path = root.joinpath(*parts)
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise ValueError('Verwalteter Dateipfad verlässt den Datenordner.')
    return path


def song_paths(data, identities):
    if not identities or len(set(identities)) != len(identities) or any(
        not isinstance(i, str) or not re.fullmatch('[a-f0-9]{64}', i) for i in identities
    ):
        raise ValueError('Ungültige gespeicherte Song-ID; keine Dateien gelöscht.')
    return [(managed_path(data, i + '.wav'), i + '.wav') for i in identities] + [
        (managed_path(data, 'stems', i), i + '-stems') for i in identities]


def restore(data, quarantine, identities):
    for original, name in reversed(song_paths(data, identities)):
        temporary = managed_path(data, quarantine.name, name)
        if temporary.exists():
            if original.exists():
                raise RuntimeError('Wiederherstellungskonflikt; beide Dateistände bleiben erhalten.')
            original.parent.mkdir(parents=True, exist_ok=True)
            temporary.rename(original)


def cleanup(data, quarantine, identities):
    # Keep the recovery journal until every managed payload has been removed.
    # A locked stem must not turn a retryable operation into an unknown folder.
    for _, name in song_paths(data, identities):
        path = managed_path(data, quarantine.name, name)
        if path.is_dir():shutil.rmtree(path)
        else:path.unlink(missing_ok=True)
    (quarantine / 'journal.json').unlink()
    quarantine.rmdir()


def mark_deleted(conn, quarantine):
    conn.execute('INSERT OR REPLACE INTO cache_state VALUES (?,1)', ('delete:'+quarantine.name,))


def recover_deletions(data, conn):
    """Call once on opening a data directory, before serving library operations."""
    for quarantine in sorted(Path(data).glob('delete-*')):
        journal = quarantine / 'journal.json'
        # Older, unjournaled folders are preserved for manual inspection.
        if not journal.is_file():
            continue
        managed_path(data, quarantine.name)
        value = json.loads(journal.read_text(encoding='utf8'))
        identities = value['ids']
        paths = song_paths(data, identities)
        expected = {'journal.json'} | {name for _, name in paths}
        if value.get('version') not in {1,2} or any(p.name not in expected for p in quarantine.iterdir()):
            raise RuntimeError('Unbekannte Löschquarantäne; Dateien bleiben erhalten.')
        # A committed DB deletion is the authority for cleanup. An interrupted
        # move with intact DB rows is rolled back, never inferred as a deletion.
        marker='delete:'+quarantine.name
        committed=bool(conn.execute('SELECT 1 FROM cache_state WHERE name=?',(marker,)).fetchone())
        present = [bool(conn.execute('SELECT 1 FROM tracks WHERE id=?', (i,)).fetchone()) for i in identities]
        if committed:
            pass
        elif all(present):
            restore(data, quarantine, identities)
        elif any(present) or value['version']==2:
            raise RuntimeError('Unvollständiger Bibliotheksstand; Löschquarantäne bleibt erhalten.')
        try:
            cleanup(data, quarantine, identities)
            conn.execute('DELETE FROM cache_state WHERE name=?',(marker,))
        except OSError:
            # Locked leftovers can be retried on the next process start.
            continue


def quarantine_files(data, identities):
    paths = song_paths(data, identities)
    quarantine = managed_path(data, 'delete-' + uuid.uuid4().hex)
    quarantine.mkdir()
    atomic_json(quarantine / 'journal.json', {'version': 2, 'ids': identities})
    try:
        for source, name in paths:
            if source.exists():
                source.rename(quarantine / name)
    except Exception:
        restore(data, quarantine, identities)
        raise
    return quarantine
