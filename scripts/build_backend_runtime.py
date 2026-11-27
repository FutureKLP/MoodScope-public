"""Build from a fresh, CPU-only environment; never copy a developer venv.

Run with the clean environment's Python after installing backend requirements
(excluding pytest), CPU Torch/Torchaudio and the pinned PyInstaller builder.
Generated inventory, licenses, binaries and build evidence remain ignored/local.
"""
import hashlib
import argparse
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def exclude_test_assets(folder):
    """Hooks can collect upstream benchmark datasets; they are not app inputs."""
    folder=Path(folder).resolve()
    for path in folder.rglob('*'):
        relative=path.relative_to(folder)
        torch_test = relative.parts[:3] == ('_internal','torch','bin') and (
            path.name.startswith('test_') or path.name.endswith('Test') or path.name == 'script_module_v4.ptl')
        if path.is_file() and (torch_test or any(part in {'tests','test','__pycache__'} for part in relative.parts)):
            path.unlink()


def inventory():
    packages=[]
    for dist in metadata.distributions():
        name=dist.metadata['Name']
        if name.lower().startswith('nvidia-') or (name.lower() in {'torch','torchaudio'} and '+cu' in dist.version):
            raise RuntimeError('CPU-only builder required; CUDA distribution detected')
        licenses=[]
        for entry in dist.files or []:
            if any(word in entry.name.lower() for word in ['license','licence','copying','notice']):
                source=Path(dist.locate_file(entry))
                if source.is_file():licenses.append((str(entry),source))
        packages.append((dist,{'name':name,'version':dist.version,
            'license':dist.metadata.get('License-Expression') or dist.metadata.get('License'),
            'classifiers':[v for v in dist.metadata.get_all('Classifier',[]) if v.startswith('License')],
            'license_files':[name for name,_ in licenses]},licenses))
    return packages


def supplemental_licenses(packages, legal):
    """Copy reviewed, version-bound upstream texts; never fetch during a build."""
    source = ROOT / 'docs' / 'distribution-licenses'
    catalog = json.loads((source / 'provenance.json').read_text(encoding='utf8'))
    versions = {row['name'].lower().replace('_', '-'): row['version'] for _, row, _ in packages}
    included = []
    for item in catalog:
        if versions.get(item['package']) != item['version']:
            continue
        binaries = item.get('runtime_files')
        if binaries is not None:
            if sys.platform not in binaries:
                continue
            binary = binaries[sys.platform]
            runtime = legal.parent.resolve()
            binary_path = runtime / binary['path']
            if not binary_path.resolve().is_relative_to(runtime):
                raise ValueError('Invalid supplemental binary path')
            with binary_path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            if digest != binary['sha256']:
                raise ValueError('Supplemental binary checksum mismatch: ' + binary['path'])
        path = source / item['file']
        if not path.resolve().is_relative_to(source.resolve()):
            raise ValueError('Invalid supplemental license path')
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != item['sha256']:
            raise ValueError('Supplemental license checksum mismatch: ' + item['file'])
        destination = legal / item['package'] / ('upstream-' + path.name)
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(body)
        included.append(item)
    (legal / 'upstream-provenance.json').write_text(json.dumps(included, indent=2), encoding='utf8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work-name',default='runtime-build')
    parser.add_argument('--incremental',action='store_true',help='Reuse PyInstaller dependency analysis for local iteration')
    args=parser.parse_args()
    if not args.work_name.replace('-','').isalnum():raise ValueError('Invalid work directory name')
    if Path(sys.prefix).resolve() in {(ROOT/'.venv').resolve(),(ROOT/'.venv-modern').resolve()}:
        raise RuntimeError('Use a new dedicated builder, not a developer environment')
    work=ROOT/'.tools'/args.work_name;work.mkdir(parents=True,exist_ok=True)
    target=ROOT/'.tools'/'backend-runtime'
    if target.exists():raise RuntimeError('Output already exists; preserve/review it before rebuilding')
    packages=inventory()
    (work/'packages.json').write_text(json.dumps([row for _,row,_ in packages],indent=2),encoding='utf8')
    # Explicit collection is necessary for lazy model imports. No project data,
    # models, tests, .tools or entire source tree is passed as an input resource.
    command=[sys.executable,'-m','PyInstaller','--noconfirm','--onedir','--noupx',
        '--name','moodscope-backend','--distpath',str(work/'dist'),'--workpath',str(work/'build'),
        '--specpath',str(work),'--paths',str(ROOT)]
    if not args.incremental:command+=['--clean']
    for package in ['backend','uvicorn','transformers','librosa','soundfile','imageio_ffmpeg','faster_whisper','demucs','torchaudio']:
        command+=['--collect-all',package]
    command+=['--copy-metadata','torch','--copy-metadata','transformers','--copy-metadata','librosa',
        '--hidden-import','scripts.runtime','--hidden-import','scripts.service',str(ROOT/'scripts'/'packaged_backend.py')]
    subprocess.run(command,cwd=ROOT,check=True)
    shutil.copytree(work/'dist'/'moodscope-backend',target)
    exclude_test_assets(target)
    legal=target/'licenses';legal.mkdir()
    for _,row,files in packages:
        for index,(_,source) in enumerate(files):
            folder=legal/row['name'];folder.mkdir(exist_ok=True)
            shutil.copyfile(source,folder/(str(index)+'-'+source.name))
    supplemental_licenses(packages, legal)
    shutil.copyfile(work/'packages.json',target/'packages.json')
    shutil.copyfile(ROOT/'LICENSE',legal/'MoodScope-LICENSE.txt')
    python_license=Path(sys.base_prefix)/'LICENSE.txt'
    if python_license.is_file():shutil.copyfile(python_license,legal/'Python-LICENSE.txt')
    records=[]
    for path in sorted(target.rglob('*')):
        if path.is_file():
            with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
            records.append({'path':path.relative_to(target).as_posix(),'bytes':path.stat().st_size,'sha256':digest})
    (work/'runtime-manifest.json').write_text(json.dumps({'bytes':sum(p['bytes'] for p in records),'files':records},indent=2),encoding='utf8')
    print(json.dumps({'files':len(records),'bytes':sum(p['bytes'] for p in records)}))


if __name__=='__main__':main()
