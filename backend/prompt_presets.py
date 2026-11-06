"""Local, bounded prompt presets. No executable templates or model code."""
import hashlib
import json
import os
import tempfile
import uuid
from pathlib import Path
from .audio_method import PROMPTS

DEFAULTS={
    'audio':'\n'.join(PROMPTS),
    'whole_de':'Deute den gesamten Text und seine Entwicklung vom Anfang zum Ende in fünf Absätzen.',
    'line_de':'Deute die ausgewählte Zeile im Zusammenhang des gesamten Textes in drei Absätzen.',
    'whole_en':'Interpret the entire supplied lyrics and their development from beginning to end in five paragraphs.',
    'line_en':'Interpret the selected line within the context of the entire supplied lyrics in three paragraphs.',
    'instruments':'\n'.join(['The music features acoustic guitar.','The music features electric guitar.','The music features bass guitar.','The music features a drum kit.','The music features piano.','The music features synthesizers.','The music features a string ensemble.','The music features brass instruments.','The music features singing vocals.']),
}

def read(data):
    path=Path(data)/'prompt-presets.json'
    if not path.exists():return {'active':{key:'default' for key in DEFAULTS},'presets':[]}
    return json.loads(path.read_text(encoding='utf8'))

def write(data,value):
    root=Path(data);root.mkdir(parents=True,exist_ok=True)
    name=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',dir=root,suffix='.tmp',delete=False) as output:
            name=output.name;json.dump(value,output,ensure_ascii=False)
        os.replace(name,root/'prompt-presets.json')
    finally:
        if name:Path(name).unlink(missing_ok=True)

def content(data,purpose):
    value=read(data);selected=value['active'].get(purpose,'default')
    return next((p['content'] for p in value['presets'] if p['id']==selected and p['purpose']==purpose),DEFAULTS[purpose])

def fingerprint(data,purposes):
    return hashlib.sha256(json.dumps([content(data,p) for p in purposes],ensure_ascii=False).encode()).hexdigest()

def status(data):
    return {**read(data),'defaults':DEFAULTS}

def change(data,action,purpose,preset_id=None,name='',text=''):
    if purpose not in DEFAULTS:raise ValueError('Unbekannter Prompt-Zweck.')
    value=read(data)
    if action=='save':
        text=text.strip();name=name.strip()
        if not name or len(name)>80 or not 10<=len(text)<=6000:raise ValueError('Vorlagenname und Prompt prüfen: 10 bis 6000 Zeichen.')
        if purpose in {'audio','instruments'}:
            lines=[line.strip() for line in text.splitlines()]
            if len(lines)!=(12 if purpose=='audio' else 9) or any(not 10<=len(line)<=400 for line in lines):raise ValueError('Anzahl und Länge der Klangbeschreibungen prüfen.')
            text='\n'.join(lines)
        existing=next((p for p in value['presets'] if p['id']==preset_id and p['purpose']==purpose),None)
        if preset_id and not existing:raise ValueError('Vorlage nicht gefunden.')
        if existing:existing.update(name=name,content=text)
        else:
            if len(value['presets'])>=60:raise ValueError('Maximal 60 eigene Prompt-Vorlagen.')
            value['presets'].append({'id':uuid.uuid4().hex,'purpose':purpose,'name':name,'content':text})
    elif action=='select':
        if preset_id!='default' and not any(p['id']==preset_id and p['purpose']==purpose for p in value['presets']):raise ValueError('Vorlage nicht gefunden.')
        value['active'][purpose]=preset_id
    elif action=='delete':
        if not any(p['id']==preset_id and p['purpose']==purpose for p in value['presets']):raise ValueError('Vorlage nicht gefunden.')
        value['presets']=[p for p in value['presets'] if p['id']!=preset_id]
        if value['active'].get(purpose)==preset_id:value['active'][purpose]='default'
    else:raise ValueError('Unbekannte Vorlagenaktion.')
    write(data,value);return status(data)
