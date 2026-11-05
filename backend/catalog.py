"""Curated, code-free model downloads and local selection."""
import gc
import json
import os
from pathlib import Path
import threading

ROOT=Path(__file__).resolve().parents[1]
CATALOG={
    'clap':{'repo':'laion/clap-htsat-unfused','purpose':'audio','name':'CLAP kompakt',
            'description':'Audio Mood und vermutete Instrumente. Allgemeines Audio/Text-Modell mit Musikprompts; keine objektive Emotionsmessung.',
            'download':'etwa 0,6-2 GB','memory':'etwa 3 GB VRAM'},
    'clap-fused':{'repo':'laion/clap-htsat-fused','purpose':'audio','name':'CLAP Fusion',
            'description':'Alternative CLAP-Variante für Audio Mood. Größerer Download; ein Genauigkeitsgewinn ist nicht garantiert.',
            'download':'etwa 0,6-2 GB','memory':'etwa 3 GB VRAM'},
    'xlm-emo':{'repo':'MilaNLProc/xlm-emo-t','purpose':'lyrics','name':'XLM-EMO mehrsprachig',
            'description':'Lyric Mood: Freude, Trauer, Angst und Ärger. Berücksichtigt zusätzlich benachbarte Textzeilen. Kein generatives Modell.',
            'download':'etwa 1,2 GB','memory':'etwa 2 GB VRAM'},
    'whisper-base':{'repo':'Systran/faster-whisper-base','purpose':'whisper','name':'Whisper Base',
            'description':'Lokale Transkription, wenn keine LRC-Lyrics verfügbar sind. Schnell; Gesangserkennung kann fehlerhaft sein.',
            'download':'etwa 150 MB','memory':'CPU-Standard'},
    'whisper-small':{'repo':'Systran/faster-whisper-small','purpose':'whisper','name':'Whisper Small',
            'description':'Größere Transkriptionsoption. Meist langsamer; höhere Wortgenauigkeit muss an deinen Songs geprüft werden.',
            'download':'etwa 500 MB','memory':'CPU-Standard'},
    'whisper-turbo':{'repo':'mobiuslabsgmbh/faster-whisper-large-v3-turbo','purpose':'whisper','name':'Whisper Large v3 Turbo',
            'description':'Stärkere mehrsprachige Texterkennung für schwierige Gesangsmischungen. GPU bevorzugt; auch dieses Modell kann Rap, Effekte und überlagerte Stimmen falsch erkennen.',
            'download':'etwa 1,6 GB','memory':'etwa 3-4 GB VRAM; CPU deutlich langsamer'},
    'qwen-small':{'repo':'Qwen/Qwen2.5-1.5B-Instruct','purpose':'interpretation','name':'Qwen 1.5B Interpretation',
            'description':'Lokale deutsche Song- und Zeilendeutung. Kleiner Einstieg; kann Kontext missverstehen oder Fakten erfinden. Aussagen prüfen.',
            'download':'etwa 3,1 GB','memory':'etwa 4 GB VRAM'},
    'qwen-medium':{'repo':'Qwen/Qwen2.5-3B-Instruct','purpose':'interpretation','name':'Qwen 3B Interpretation',
            'description':'Größere lokale Deutungsoption für die 12-GB-GPU. Emotionsmodelle werden vor der Generierung entladen. Eigene Qwen-Research-Lizenz; vor Weiterverwendung prüfen.',
            'download':'etwa 6,2 GB','memory':'etwa 7 GB VRAM'},
}
DEFAULTS={'audio':'clap','lyrics':'xlm-emo','whisper':'whisper-base','interpretation':'qwen-small'}
_lock=threading.Lock()


def config_path(data):return Path(data)/'model-settings.json'


def configuration(data):
    try:
        value=json.loads(config_path(data).read_text(encoding='utf-8'))
        active={k:v for k,v in value.get('active',{}).items() if v in CATALOG and CATALOG[v]['purpose']==k}
        installed={k:v for k,v in value.get('installed',{}).items() if k in CATALOG and Path(v).is_dir()}
        return {'active':{**DEFAULTS,**active},'installed':installed}
    except (OSError,ValueError,TypeError):return {'active':dict(DEFAULTS),'installed':{}}


def save(data,value):
    path=config_path(data);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2),encoding='utf-8');temporary.replace(path)


def select(data,key):
    if key not in CATALOG:raise ValueError('Nicht unterstütztes Modell')
    with _lock:
        value=configuration(data);value['active'][CATALOG[key]['purpose']]=key;save(data,value)


def model_source(data,purpose):
    value=configuration(data);key=value['active'][purpose]
    return value['installed'].get(key,CATALOG[key]['repo'])


def status(data):
    from huggingface_hub import try_to_load_from_cache
    value=configuration(data)
    items=[]
    for key,model in CATALOG.items():
        weight='model.bin' if model['purpose']=='whisper' else 'model.safetensors'
        cached=try_to_load_from_cache(model['repo'],weight)
        if model['purpose']=='whisper' and not isinstance(cached,str):
            cached=try_to_load_from_cache(model['repo'],weight,cache_dir=ROOT/'models'/'whisper')
        if not isinstance(cached,str):cached=try_to_load_from_cache(model['repo'],'pytorch_model.bin')
        installed=key in value['installed'] or isinstance(cached,str)
        items.append({'id':key,**model,'installed':installed,'active':value['active'][model['purpose']]==key})
    return {'models':items,'active':value['active']}


def download(data,key,progress):
    if key not in CATALOG:raise ValueError('Nicht unterstütztes Modell')
    from huggingface_hub import snapshot_download
    progress('Lade '+CATALOG[key]['name']+' von Hugging Face; mehrere GB möglich',5)
    model=CATALOG[key]
    patterns=['*.json','*.model','tokenizer*','*.txt']
    if model['purpose']=='whisper':patterns+=['model.bin']
    elif model['purpose']=='lyrics':patterns+=['pytorch_model.bin']
    elif model['purpose']=='audio':patterns+=['pytorch_model.bin','*.safetensors']
    else:patterns+=['*.safetensors']
    path=snapshot_download(model['repo'],allow_patterns=patterns)
    with _lock:
        value=configuration(data);value['installed'][key]=path;save(data,value)
    return {'model_id':key,'installed':True}


def unload_models(engine):
    engine.audio_model=engine.processor=engine.lyric_pipe=None
    gc.collect()
    import torch
    if torch.cuda.is_available():torch.cuda.empty_cache()
