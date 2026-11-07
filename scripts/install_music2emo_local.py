"""Register an already reviewed/downloaded Music2Emo extension; no network access."""
import argparse
import json
from pathlib import Path
import shutil
from scripts.audio_evaluation import digest


def install(source,weights,dependencies):
    source=Path(source).resolve();weights=Path(weights).resolve();dependencies=Path(dependencies).resolve()
    provenance=json.loads((weights/'provenance.json').read_text(encoding='utf8'))
    for entry in provenance['files']:
        path=(weights/entry['file']).resolve()
        if not path.is_relative_to(weights) or digest(path)!=entry['sha256']:raise ValueError('Invalid weight provenance')
    target=weights/'source';packages=weights/'packages'
    if source.is_relative_to(target) or target.is_relative_to(source) or dependencies.is_relative_to(packages) or packages.is_relative_to(dependencies):
        raise ValueError('Use separate, non-nested source and installation folders')
    if not (source/'LICENSE').is_file() or not (dependencies/'music21/__init__.py').is_file():
        raise ValueError('Reviewed source and isolated dependencies required')
    target.mkdir(exist_ok=True)
    for folder in ('utils','model','inference'):
        shutil.copytree(source/folder,target/folder,dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__','*.pt','*.ckpt','*.mp3','*.wav'))
    for name in ('music2emo.py','LICENSE'):shutil.copy2(source/name,target/name)
    shutil.copytree(dependencies,packages,dirs_exist_ok=True)
    hashes={path.relative_to(target).as_posix():digest(path) for path in target.rglob('*') if path.is_file()}
    temporary=weights/'installation.tmp'
    temporary.write_text(json.dumps({'source_sha256':hashes,'upstream_commit':provenance['upstream_commit']},indent=2),encoding='utf8')
    temporary.replace(weights/'installation.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','weights','dependencies'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();install(args.source,args.weights,args.dependencies)
    print('Optional local Music2Emo extension registered; active model selection unchanged.')
