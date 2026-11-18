"""Synthetic Phase-2A fixtures and read-only evidence, separate from music quality.

Native import must be verified through the desktop UI. Authored caches are installed
in advance solely to prevent automatic inference; they are not model results.
"""
import argparse
import hashlib
import json
import math
import sqlite3
import struct
import wave

from scripts import windows_desktop_testing as desktop


def identity(path):
    digest = hashlib.sha256(b'moodscope-stereo-decoder-v2')
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def prepare():
    area = desktop.prepare()
    area, marker = desktop.workspace(area)
    sources = area / 'sources'
    sources.mkdir()
    planned = []
    for frequency in (440, 660):
        path = sources / f'synthetic-{frequency}hz-0-60s.wav'
        with wave.open(str(path), 'wb') as audio:
            audio.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
            block = b''.join(struct.pack('<hh', *([int(2500 * math.sin(2 * math.pi * frequency * n / 48000))] * 2)) for n in range(48000))
            for _ in range(60):
                audio.writeframesraw(block)
        planned.append(identity(path))
    (sources / 'synthetic-timestamps.lrc').write_text(
        '[00:00.00]Synthetic zero\n[00:10.25]Synthetic fractional\n[00:25.00]Synthetic middle\n[00:45.00]Synthetic final\n', encoding='utf-8')
    (sources / 'synthetic-damaged.wav').write_bytes(b'RIFF deliberately damaged synthetic input')
    from backend import app, expression_compare
    with app.db() as conn:
        for track_id in planned:
            points = [{'start': n, 'end': n + 10, 'valence': (n / 50) * 2 - 1,
                       'arousal': .2, 'tags': {}, 'scores': {}, 'confidence': .5} for n in range(0, 60, 10)]
            lyrics = [{'start': n, 'end': end, 'text': text, 'valence': 0, 'arousal': 0, 'tags': {}, 'scores': {}}
                      for n, end, text in [(0, 10.25, 'Synthetic zero'), (10.25, 25, 'Synthetic fractional'),
                                            (25, 45, 'Synthetic middle'), (45, 60, 'Synthetic final')]]
            analysis = {'audio': points, 'lyrics': lyrics, 'split': None, 'warnings': ['Authored synthetic acceptance fixture; no inference'],
                        'device': 'fixture', 'method': 'synthetic-desktop-fixture', 'models': {},
                        'source_lyrics': (sources / 'synthetic-timestamps.lrc').read_text()}
            comparison = {'rows': points, 'method': expression_compare.METHOD,
                          'model_basis': expression_compare.fingerprint(), 'track_id': track_id, 'synthetic_fixture': True}
            for key, value in [(f'latest:{track_id}:local', analysis), (f'expression-comparison:{track_id}', comparison)]:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)', (key, json.dumps(value)))
                conn.execute('INSERT OR REPLACE INTO cache_owner VALUES (?,?)', (key, track_id))
    marker.update(phase='2A', planned_track_ids=planned, library_track_ids=[marker['track_id']],
                  sources=desktop.files(sources), protected_music=desktop.files(desktop.ROOT / 'for test only music files'))
    (area / 'workspace.json').write_text(json.dumps(marker, indent=2))
    print('PHASE2A_AREA=' + str(area), flush=True)


def snapshot(area, label, baseline=None):
    area, marker = desktop.workspace(area)
    if marker.get('phase') != '2A':
        raise ValueError('Requires a Phase-2A workspace')
    desktop.snapshot(area, label)
    with sqlite3.connect(f'file:{(area / "data/cache.sqlite3").as_posix()}?mode=ro', uri=True) as conn:
        tables = {name: [list(row) for row in conn.execute(f'SELECT * FROM {name} ORDER BY 1')]
                  for name in ('tracks', 'cache', 'cache_owner')}
        ids = [row[0] for row in tables['tracks']]
        orphans = conn.execute('SELECT track_id FROM cache_owner WHERE track_id NOT IN (SELECT id FROM tracks)').fetchall()
    result = {'tables': tables, 'track_ids': ids, 'orphan_cache_owners': orphans,
              'managed_audio': {p.name: desktop.digest(p) for p in (area / 'data').glob('*.wav')},
              'sources_unchanged': desktop.files(area / 'sources') == marker['sources'],
              'original_music_unchanged': desktop.files(desktop.ROOT / 'for test only music files') == marker['protected_music']}
    if baseline:
        before = json.loads((area / 'evidence' / (baseline + '-library.json')).read_text())
        result['library_unchanged'] = all(result[key] == before[key] for key in ('tables', 'managed_audio'))
    (area / 'evidence' / (label + '-library.json')).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ('tables', 'managed_audio')}, indent=2))
    assert result['sources_unchanged'] and result['original_music_unchanged']
    if baseline:
        assert result['library_unchanged'], 'Library changed across restart'
    # Only the recorded synthetic identities can be accepted by the next launch.
    if not set(ids) <= {marker['track_id'], *marker['planned_track_ids']}:
        raise ValueError('Unexpected track in synthetic library')
    marker['library_track_ids'] = ids
    (area / 'workspace.json').write_text(json.dumps(marker, indent=2))


def seed(area):
    """Fixture setup only, explicitly not evidence of a native import."""
    import httpx
    area, marker = desktop.workspace(area)
    if marker.get('phase') != '2A' or desktop.files(area / 'sources') != marker['sources']:
        raise ValueError('Requires unchanged Phase-2A sources')
    with httpx.Client(base_url='http://127.0.0.1:8765', trust_env=False, timeout=30) as client:
        response = client.get('/api/library')
        response.raise_for_status()
        if sorted(t['id'] for t in response.json()['tracks']) != sorted(marker['library_track_ids']):
            raise ValueError('Unexpected service library; refusing fixture setup')
        for path in sorted((area / 'sources').glob('synthetic-*hz-0-60s.wav')):
            with path.open('rb') as stream:
                response = client.post('/api/tracks', files={'file': (path.name, stream, 'audio/wav')})
            response.raise_for_status()
            if response.json()['id'] != identity(path):
                raise ValueError('Unexpected imported fixture identity')
    print('FIXTURE_SETUP_ONLY: two synthetic tracks imported through HTTP, not native UI')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'snapshot', 'seed'])
    parser.add_argument('--area')
    parser.add_argument('--label', default='snapshot')
    parser.add_argument('--baseline')
    args = parser.parse_args()
    for label in (args.label, args.baseline):
        if label is not None and (not label or not all(c.isascii() and (c.isalnum() or c in '-_') for c in label)):
            parser.error('Evidence labels must be plain names')
    if args.action == 'prepare':
        prepare()
    else:
        if not args.area:
            parser.error('--area is required')
        if args.action == 'seed':
            seed(args.area)
        else:
            snapshot(args.area, args.label, args.baseline)


if __name__ == '__main__':
    main()
