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
_lock=threading.RLock()


def entries(data):
    from . import custom_models
    return {**CATALOG,**custom_models.entries(data)}


def config_path(data):return Path(data)/'model-settings.json'


def configuration(data):
    try:
        models=entries(data)
        value=json.loads(config_path(data).read_text(encoding='utf-8'))
        active={k:v for k,v in value.get('active',{}).items() if v in models and models[v]['purpose']==k}
        installed={k:v for k,v in value.get('installed',{}).items() if k in models and Path(v).is_dir()}
        return {'active':{**DEFAULTS,**active},'installed':installed,'incomplete':value.get('incomplete',[])}
    except (OSError,ValueError,TypeError):return {'active':dict(DEFAULTS),'installed':{},'incomplete':[]}


def save(data,value):
    path=config_path(data);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.tmp')
    from .cancellation import check
    check()
    temporary.write_text(json.dumps(value,indent=2),encoding='utf-8');temporary.replace(path)


def select(data,key):
    models=entries(data)
    if key not in models:raise ValueError('Nicht unterstütztes Modell')
    with _lock:
        value=configuration(data)
        if models[key].get('custom') and key not in value['installed']:raise ValueError('Eigenes Modell zuerst herunterladen und prüfen.')
        value['active'][models[key]['purpose']]=key;save(data,value)


def model_source(data,purpose):
    value=configuration(data);key=value['active'][purpose]
    model=entries(data)[key]
    if model.get('custom') and key not in value['installed']:raise ValueError('Eigenes Modell zuerst herunterladen.')
    if purpose=='whisper' and key not in value['installed'] and not model.get('custom'):
        # Explicit model-manager downloads use the shared Hub cache; faster-whisper's
        # own downloader uses a separate directory. Reuse either complete snapshot offline.
        from huggingface_hub import try_to_load_from_cache
        for location in [ROOT/'models'/'hub',ROOT/'models'/'whisper']:
            cached=try_to_load_from_cache(model['repo'],'model.bin',cache_dir=location)
            if isinstance(cached,str) and (Path(cached).parent/'config.json').is_file():return str(Path(cached).parent)
    return value['installed'].get(key,model['repo'])


def status(data):
    from huggingface_hub import try_to_load_from_cache
    value=configuration(data)
    items=[]
    for key,model in entries(data).items():
        weight='model.bin' if model['purpose']=='whisper' else 'model.safetensors'
        cached=try_to_load_from_cache(model['repo'],weight,revision=model.get('revision'))
        if model['purpose']=='whisper' and not isinstance(cached,str):
            cached=try_to_load_from_cache(model['repo'],weight,cache_dir=ROOT/'models'/'whisper')
        if not model.get('custom') and not isinstance(cached,str):cached=try_to_load_from_cache(model['repo'],'pytorch_model.bin')
        installed=(key in value['installed'] or isinstance(cached,str)) and key not in value.get('incomplete',[])
        items.append({'id':key,**model,'installed':installed,'active':value['active'][model['purpose']]==key})
    return {'models':items,'active':value['active']}


def download(data,key,progress):
    models=entries(data)
    if key not in models:raise ValueError('Nicht unterstütztes Modell')
    from huggingface_hub import snapshot_download
    progress('Lade '+models[key]['name']+' von Hugging Face; mehrere GB möglich',5)
    model=models[key]
    patterns=['*.json','*.model','tokenizer*','*.txt']
    if model['purpose']=='whisper':patterns+=['model.bin']
    elif model['purpose']=='lyrics':patterns+=['pytorch_model.bin']
    elif model['purpose']=='audio':patterns+=['pytorch_model.bin','*.safetensors']
    else:patterns+=['*.safetensors']
    from . import cancellation
    checkpoint=cancellation.capture()
    from tqdm.auto import tqdm
    class DownloadProgress(tqdm):
        def update(self,n=1):
            checkpoint()
            return super().update(n)
    kwargs={}
    if model.get('custom'):
        patterns=['*.json','*.model','tokenizer*','*.txt','*.safetensors']
        if model['purpose']=='whisper':patterns+=['model.bin']
        kwargs={'revision':model['revision'],'token':False,'local_dir':ROOT/'models'/'managed'/key,'ignore_patterns':['*.py','*.pkl','*.pickle','*.pt','*.pth','*.ckpt']}
    with _lock:
        value=configuration(data);value['incomplete']=list(set(value.get('incomplete',[])+[key]));save(data,value)
    path=snapshot_download(model['repo'],allow_patterns=patterns,tqdm_class=DownloadProgress,**kwargs)
    checkpoint()
    if model.get('custom'):
        from .custom_models import validate_config
        validate_config(model['purpose'],json.loads((Path(path)/'config.json').read_text(encoding='utf8')))
        if model['purpose']=='interpretation':
            from transformers import AutoTokenizer
            tokenizer=AutoTokenizer.from_pretrained(path,trust_remote_code=False,local_files_only=True)
            if not tokenizer.chat_template:raise ValueError('Interpretationsmodell benötigt ein Chat-Template.')
    with _lock:
        value=configuration(data);value['installed'][key]=str(path);value['incomplete']=[v for v in value.get('incomplete',[]) if v!=key];save(data,value)
    return {'model_id':key,'installed':True}


def unload_models(engine):
    engine.audio_model=engine.processor=engine.lyric_pipe=None
    gc.collect()
    import torch
    if torch.cuda.is_available():torch.cuda.empty_cache()


def remove(data,key):
    """Delete only verified app-owned model paths, never arbitrary configured folders."""
    import shutil
    from huggingface_hub import scan_cache_dir
    from . import custom_models
    with _lock:
        models=entries(data)
        if key not in models:raise ValueError('Nicht unterstütztes Modell')
        model=models[key];value=configuration(data)
        for purpose,active in list(value['active'].items()):
            if active==key:value['active'][purpose]=DEFAULTS[purpose]
        root=(ROOT/'models').resolve()
        if not root.is_relative_to(ROOT.resolve()):raise ValueError('Modellordner liegt außerhalb des Projekts')
        managed=root/'managed'/key
        installed=value['installed'].get(key)
        if installed and not Path(installed).resolve().is_relative_to(root):
            raise ValueError('Modell liegt außerhalb des verwalteten Modellordners; keine Datei gelöscht.')
        if managed.exists():
            resolved=managed.resolve()
            if resolved!=managed or managed.is_symlink() or (hasattr(managed,'is_junction') and managed.is_junction()):raise ValueError('Ungültiger Modellpfad')
            shutil.rmtree(resolved)
        # Existing curated downloads live in the project Hugging Face cache.
        if not model.get('custom'):
            if any(active!=key and models[active]['repo']==model['repo'] for active in value['active'].values()):
                raise ValueError('Ein anderes ausgewähltes Modell verwendet dieselben Gewichte.')
            for location in [root/'hub',root/'whisper']:
                if not location.is_dir():continue
                cache=scan_cache_dir(location)
                for repo in cache.repos:
                    if repo.repo_id!=model['repo']:continue
                    strategy=cache.delete_revisions(*(r.commit_hash for r in repo.revisions))
                    for field in ['blobs','refs','snapshots','repos']:
                        for target in getattr(strategy,field,[]):
                            resolved=Path(target).resolve()
                            if not resolved.is_relative_to(root) or resolved==root:raise ValueError('Cachepfad außerhalb des Modellordners')
                    strategy.execute()
        value['installed'].pop(key,None);value['incomplete']=[v for v in value.get('incomplete',[]) if v!=key];save(data,value)
        if model.get('custom'):
            custom=custom_models.entries(data);custom.pop(key,None);custom_models.save(data,custom)
    return status(data)
