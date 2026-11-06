"""Validated local Torch device preferences, separate from server profiles."""
import json
import os
from pathlib import Path

PURPOSES=('audio','lyrics','whisper','interpretation','separation')

def available():
    import torch
    result=[{'id':'auto','name':'Automatisch'},{'id':'cpu','name':'CPU'}]
    if torch.cuda.is_available():
        for index in range(torch.cuda.device_count()):
            prop=torch.cuda.get_device_properties(index)
            result.append({'id':f'cuda:{index}','name':prop.name,'vram_gb':round(prop.total_memory/1024**3,1)})
    return result

def configuration(data):
    path=Path(data)/'devices.json'
    return json.loads(path.read_text(encoding='utf8')) if path.exists() else {p:'auto' for p in PURPOSES}

def save(data,choices):
    if set(choices)!=set(PURPOSES) or any(v not in {d['id'] for d in available()} for v in choices.values()):raise ValueError('Nur verfügbare Rechengeräte auswählen.')
    import tempfile
    root=Path(data);root.mkdir(parents=True,exist_ok=True);name=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',dir=root,suffix='.tmp',delete=False) as file:
            name=file.name;json.dump(choices,file)
        os.replace(name,root/'devices.json')
    finally:
        if name:Path(name).unlink(missing_ok=True)
    return choices

def resolve(data,purpose):
    chosen=configuration(data).get(purpose,'auto')
    # Explicit launch configuration remains available for unattended CPU operation.
    chosen=os.environ.get('MOODSCOPE_DEVICE',chosen) if os.environ.get('MOODSCOPE_DEVICE','auto')!='auto' else chosen
    import torch
    if chosen=='auto':
        if torch.cuda.is_available():
            try:
                (torch.ones(1,device='cuda')*2).sum().item()
                return 'cuda'
            except RuntimeError:pass
        return 'cpu'
    if chosen=='cuda':chosen='cuda:0'
    if chosen!='cpu' and chosen not in {d['id'] for d in available()}:raise RuntimeError('Gespeichertes Rechengerät fehlt. Unter Modelle & API erneut auswählen.')
    return chosen
