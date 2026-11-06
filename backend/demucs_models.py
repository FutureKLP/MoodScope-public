"""Download only the packaged Demucs checkpoints, with hash checks and time limits."""
import hashlib
from pathlib import Path
import re
import time
import uuid
import httpx


def fetch_checkpoint(url,destination,expected_hash):
    if not re.fullmatch(r'https://dl\.fbaipublicfiles\.com/demucs/[A-Za-z0-9_/-]+/[a-f0-9]{8}-[a-f0-9]{8}\.th',url):
        raise ValueError('Nicht unterstützte Modellquelle')
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():return
    temporary=destination.with_name(destination.name+'.'+uuid.uuid4().hex+'.part')
    digest=hashlib.sha256();total=0;deadline=time.monotonic()+120
    try:
        with httpx.stream('GET',url,timeout=httpx.Timeout(30,connect=10),follow_redirects=False) as response:
            response.raise_for_status()
            with temporary.open('wb') as output:
                for block in response.iter_bytes(1024*1024):
                    from .cancellation import check
                    check()
                    total+=len(block)
                    if total>200*1024*1024 or time.monotonic()>deadline:raise RuntimeError('Modelldownload überschreitet Größen- oder Zeitlimit.')
                    digest.update(block);output.write(block)
        if not digest.hexdigest().startswith(expected_hash):raise RuntimeError('Modellprüfsumme stimmt nicht. Download verworfen.')
        temporary.replace(destination)
    finally:
        if temporary.exists():temporary.unlink()


def load_model(name,progress):
    import torch
    import yaml
    from demucs.pretrained import REMOTE_ROOT,_parse_remote_files
    from demucs.repo import check_checksum
    from demucs.states import load_model as construct_model
    from demucs.htdemucs import HTDemucs
    from demucs.apply import BagOfModels
    from fractions import Fraction
    import numpy as np
    if name not in {'htdemucs','htdemucs_6s','htdemucs_ft'}:raise ValueError('Nicht unterstütztes Trennmodell')
    bag=yaml.safe_load((REMOTE_ROOT/(name+'.yaml')).read_text())
    signatures=bag['models'];urls=_parse_remote_files(REMOTE_ROOT/'files.txt')
    if not 1<=len(signatures)<=4:raise ValueError('Unerwartetes Modellensemble')
    root=Path(torch.hub.get_dir())/'checkpoints'
    for index,signature in enumerate(signatures):
        url=urls[signature];filename=url.rsplit('/',1)[1];expected=filename.rsplit('-',1)[1].split('.')[0]
        progress('Lade offizielle Modellgewichte: '+str(index+1)+'/'+str(len(signatures)),5)
        fetch_checkpoint(url,root/filename,expected)
    allowed=[HTDemucs,Fraction,(np._core.multiarray.scalar,'numpy.core.multiarray.scalar'),np.dtype,
        type(np.dtype('float64')),type(np.dtype('float32'))]
    models=[]
    for signature in signatures:
        filename=urls[signature].rsplit('/',1)[1];path=root/filename
        check_checksum(path,filename.rsplit('-',1)[1].split('.')[0])
        # Keep weights_only enforced; allow only the types in the official HTDemucs packages.
        with torch.serialization.safe_globals(allowed):package=torch.load(path,map_location='cpu',weights_only=True)
        if not isinstance(package,dict) or package.get('klass') is not HTDemucs:raise ValueError('Unerwartete Modellklasse')
        models.append(construct_model(package))
    return BagOfModels(models,bag.get('weights'),bag.get('segment'))
