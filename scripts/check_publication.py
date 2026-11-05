"""Inspect only Git-selected source; never print suspected secret values."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which('git.exe') or shutil.which('git')
ALLOWED_ROOTS = {'.github', '.githooks', 'backend', 'docs', 'scripts', 'src', 'src-tauri', 'tests'}
ALLOWED_TOP = {'.gitattributes', '.gitignore', 'README.md', 'Start-MoodScope.cmd',
               'index.html', 'package.json', 'package-lock.json', 'tsconfig.json', 'vite.config.ts'}
DENIED_PARTS = {'.git', '.venv', '.tools', 'node_modules', 'dist', 'data', 'models',
                '__pycache__', '.pytest_cache', 'target', 'gen', 'for test only music files'}
DENIED_EXTENSIONS = {'.mp3','.wav','.flac','.lrc','.mp4','.webm','.sqlite','.sqlite3','.db',
                     '.pem','.key','.p12','.pfx','.zip','.7z','.gz','.exe','.msi','.dll',
                     '.whl','.pt','.pth','.safetensors','.log'}
PATTERNS = {
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'GitHub token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'model hub token': re.compile(r'\bhf_[A-Za-z0-9]{25,}\b'),
    'service key': re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b'),
    'cloud access key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'credential URL': re.compile(r'https?://[^\s/@:]+:[^\s/@]+@'),
    'literal credential': re.compile(r'''(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[=:]\s*["'][A-Za-z0-9_./+\-=]{12,}["']'''),
    'personal Windows path': re.compile(r'(?i)[a-z]:[\\/]+Users[\\/]+[^\\/\s"\']+'),
    'personal Unix path': re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+/'),
    'email address': re.compile(r'\b(?!noreply@github\.com\b)[A-Za-z0-9._%+-]+@(?!users\.noreply\.github\.com\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
}


def git(*args):
    if not GIT:
        raise RuntimeError('Git is required for publication checks')
    return subprocess.check_output([GIT, *args], cwd=ROOT)


def path_problem(name):
    path=PurePosixPath(name)
    if any(part.lower() in DENIED_PARTS for part in path.parts): return 'excluded directory'
    if path.name.startswith('.env') and path.name != '.env.example': return 'environment file'
    if path.suffix.lower() in DENIED_EXTENSIONS: return 'excluded file type'
    if len(path.parts)==1 and name not in ALLOWED_TOP: return 'unapproved top-level file'
    if len(path.parts)>1 and path.parts[0] not in ALLOWED_ROOTS: return 'unapproved directory'
    return None


def content_problems(raw):
    try: text=raw.decode('utf-8')
    except UnicodeDecodeError: return ['unexpected binary data']
    text=text.replace('128x128@2x.png','128x128-scale2.png')
    problems=[label for label,pattern in PATTERNS.items() if pattern.search(text)]
    # Unicode pictographs and decorative UI glyph ranges, including variation selectors.
    if any(0x1F000<=ord(c)<=0x1FAFF or 0x2600<=ord(c)<=0x27BF
           or ord(c) in {0xFE0F,0x200D} for c in text):
        problems.append('emoji or decorative pictograph')
    return problems


def scan(ref=None):
    names=[name.decode('utf-8') for name in git('ls-files','--cached','-z').split(b'\0') if name]
    objects=[]
    if ref:
        for commit in git('rev-list',ref).decode().splitlines():
            for row in git('ls-tree','-rz',commit).split(b'\0'):
                if not row: continue
                info,name=row.split(b'\t',1)
                mode,kind,sha=info.decode().split()
                objects.append((name.decode('utf-8'),sha,kind))
        names=[name.decode('utf-8') for name in git('ls-tree','-rz','--name-only',ref).split(b'\0') if name]
    else:
        objects=[(name,None,'blob') for name in names]
    findings=[]
    visited=set()
    for name,sha,kind in objects:
        identity=(name,sha)
        if identity in visited: continue
        visited.add(identity)
        issue=path_problem(name)
        if issue:
            findings.append({'file':name,'reason':issue});continue
        if kind!='blob':
            findings.append({'file':name,'reason':'unexpected Git object type'});continue
        raw=git('cat-file','blob',sha) if sha else git('show',f':{name}')
        if name.startswith('src-tauri/icons/') and name.endswith(('.png','.ico')):
            # Only project-generated icon images are allowed binary assets.
            if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\0\0\1\0')):
                findings.append({'file':name,'reason':'invalid icon signature'})
            continue
        for issue in content_problems(raw): findings.append({'file':name,'reason':issue})
    if ref:
        authors=git('log',ref,'--format=%ae%n%ce').decode('utf-8')
        if any(email and not (email.endswith('@users.noreply.github.com') or email=='noreply@github.com')
               for email in authors.splitlines()):
            findings.append({'file':'Git commit metadata','reason':'non-noreply email'})
    return {'passed':not findings,'files_checked':len(names),
            'historical_versions_checked':len(visited) if ref else 0,'findings':findings}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--ref',help='Inspect a commit and its author metadata; default: staged files')
    args=parser.parse_args()
    result=scan(args.ref)
    print(json.dumps(result,indent=2))
    sys.exit(0 if result['passed'] else 1)
