"""Install an official standalone downloader inside the project, with SHA256 verification."""
import hashlib
import os
from pathlib import Path
import platform
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def main():
    if platform.machine().lower() not in {'amd64','x86_64'}:
        raise SystemExit('Für diese Architektur yt-dlp manuell installieren; siehe offizielle yt-dlp-Dokumentation.')
    name='yt-dlp.exe' if os.name=='nt' else 'yt-dlp_linux'
    target=ROOT/'.tools'/'yt-dlp';target.mkdir(parents=True,exist_ok=True)
    base='https://github.com/yt-dlp/yt-dlp/releases/latest/download/'
    with urllib.request.urlopen(base+'SHA2-256SUMS',timeout=30) as response:
        checksums=response.read().decode()
    expected=next(line.split()[0] for line in checksums.splitlines() if line.split()[-1].lstrip('*')==name)
    temporary=target/(name+'.download')
    try:
        with urllib.request.urlopen(base+name,timeout=120) as response,temporary.open('wb') as output:
            while chunk:=response.read(1024*1024): output.write(chunk)
        digest=hashlib.sha256(temporary.read_bytes()).hexdigest()
        if digest!=expected: raise RuntimeError('Downloader-Prüfsumme stimmt nicht überein')
        temporary.replace(target/name)
        if os.name!='nt': (target/name).chmod(0o755)
        print('Projektlokales yt-dlp installiert; SHA256 stimmt mit dem offiziellen Release überein.')
    finally: temporary.unlink(missing_ok=True)


if __name__=='__main__':main()
