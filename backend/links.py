"""Bounded single-track import from supported public platform URLs."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.parse import parse_qs, urlsplit, urlunsplit

ROOT=Path(__file__).resolve().parents[1]


def validate_url(value):
    try:
        parsed=urlsplit(value.strip())
        if parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in {None,443}:
            raise ValueError()
        host=(parsed.hostname or '').lower()
        if host in {'youtube.com','www.youtube.com','m.youtube.com','music.youtube.com'}:
            query=parse_qs(parsed.query)
            if 'list' in query: raise ValueError()
            if parsed.path=='/watch': identity=query.get('v',[''])[0]
            elif parsed.path.startswith(('/shorts/','/embed/')): identity=parsed.path.split('/')[2]
            else: raise ValueError()
            if not re.fullmatch(r'[A-Za-z0-9_-]{11}',identity): raise ValueError()
            return 'https://www.youtube.com/watch?v='+identity
        if host=='youtu.be':
            identity=parsed.path.strip('/')
            if not re.fullmatch(r'[A-Za-z0-9_-]{11}',identity) or 'list' in parse_qs(parsed.query): raise ValueError()
            return 'https://www.youtube.com/watch?v='+identity
        if host in {'soundcloud.com','www.soundcloud.com','m.soundcloud.com'}:
            parts=parsed.path.strip('/').split('/')
            if len(parts)!=2 or any(not re.fullmatch(r'[A-Za-z0-9_-]+',p) for p in parts) or parts[0] in {'sets','discover','you'}:
                raise ValueError()
            return urlunsplit(('https','soundcloud.com','/'+ '/'.join(parts),'',''))
    except (ValueError,IndexError):
        pass
    raise ValueError('Bitte einen einzelnen HTTPS-Songlink von YouTube oder SoundCloud einfügen; Playlists und Kurzlinks von SoundCloud werden nicht unterstützt.')


def downloader():
    local=ROOT/'.tools'/'yt-dlp'/('yt-dlp.exe' if os.name=='nt' else 'yt-dlp_linux')
    binary=local if local.exists() else shutil.which('yt-dlp')
    if not binary: raise RuntimeError('Linkimport benötigt yt-dlp. Einmal python scripts/setup_links.py ausführen.')
    return str(binary)


def download(value,directory,progress):
    url=validate_url(value)
    target=Path(directory)
    command=[downloader(),'--ignore-config','--no-plugin-dirs','--no-playlist','--no-progress',
             '--no-warnings','--no-cache-dir','--max-filesize','250M','--socket-timeout','20',
             '--retries','1','--fragment-retries','1','--match-filters','!is_live & duration <= 1800',
             '--format','bestaudio/best','--output',str(target/'source.%(ext)s'),
             '--dump-single-json','--no-simulate']
    node=ROOT/'.tools'/'node-v22.16.0-win-x64'/'node.exe'
    node_path=str(node) if node.exists() else shutil.which('node')
    if node_path: command+=['--js-runtimes','node:'+node_path]
    command+=['--',url]
    progress('Lade öffentlichen Songlink; keine Browser-Cookies oder Anmeldungen',5)
    try:
        result=subprocess.run(command,capture_output=True,timeout=240,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    except subprocess.TimeoutExpired:
        raise RuntimeError('Linkimport hat das Zeitlimit überschritten. Lokale Datei importieren oder später erneut versuchen.') from None
    if result.returncode:
        # Do not expose downloader diagnostics, local paths, cookies or signed CDN URLs.
        raise RuntimeError('Plattform hat den Download abgelehnt oder der Song ist nicht öffentlich verfügbar. Keine Login-, DRM- oder Zugriffssperren werden umgangen.')
    try:
        metadata=json.loads(result.stdout)
        files=list(target.glob('source.*'))
        files=[p for p in files if p.suffix not in {'.part','.ytdl','.json'}]
        if len(files)!=1 or files[0].stat().st_size>250*1024*1024: raise ValueError()
        return files[0],{'title':str(metadata.get('track') or metadata.get('title') or 'Linkimport')[:200],
                         'artist':str(metadata.get('artist') or '')[:200],
                         'source':'YouTube' if 'youtube.com/' in url else 'SoundCloud'}
    except (ValueError,TypeError,OSError):
        raise RuntimeError('Link lieferte keine einzelne unterstützte Audiodatei.') from None
