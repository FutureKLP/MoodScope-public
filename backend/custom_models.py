"""User-added public, pinned Hugging Face models using existing code-free adapters."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

PURPOSES={'audio','lyrics','interpretation','whisper'}


def repository(url):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.netloc!='huggingface.co' or parsed.query or parsed.fragment:
        raise ValueError('Nur öffentliche HTTPS-Modellseiten von huggingface.co werden unterstützt.')
    match=re.fullmatch(r'/([\w.-]+/[\w.-]+)/?',parsed.path)
    if not match or any(p in {'.','..'} for p in match[1].split('/')):raise ValueError('Modellseite als https://huggingface.co/owner/model angeben; keine einzelne Gewichtsdatei.')
    return match[1]


def path(data):return Path(data)/'custom-models.json'


def entries(data):
    try:
        raw=json.loads(path(data).read_text(encoding='utf8'))
        return {key:value for key,value in raw.items() if re.fullmatch(r'custom-[a-f0-9]{20}',key)
                and value.get('purpose') in PURPOSES and re.fullmatch(r'[a-f0-9]{40}',value.get('revision',''))
                and repository('https://huggingface.co/'+value.get('repo',''))}
    except (OSError,ValueError,TypeError,AttributeError):return {}


def save(data,value):
    from .cancellation import check
    check();target=path(data);target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(value,indent=2),encoding='utf8');temporary.replace(target)


def validate_config(purpose,config):
    if config.get('auto_map'):raise ValueError('Modelle mit eigenem Python-Code werden nicht unterstützt.')
    kind=config.get('model_type','')
    if purpose=='audio' and kind!='clap':raise ValueError('Audio benötigt ein Transformers-CLAP-Modell mit passendem CLAP-Prozessor.')
    if purpose=='lyrics':
        labels={str(v).casefold() for v in config.get('id2label',{}).values()}
        if kind not in {'xlm-roberta','roberta','bert'} or labels!={'joy','sadness','anger','fear'}:
            raise ValueError('Lyrics benötigen einen Textklassifikator mit exakt joy, sadness, anger und fear als Modelllabels.')
    if purpose=='interpretation' and kind not in {'qwen2','qwen3','llama','mistral','gemma','gemma2','gemma3_text','phi3','gpt2'}:
        raise ValueError('Interpretation benötigt ein unterstütztes generatives Transformers-Instruct-Modell; GGUF gehört zu einem Serverprofil.')
    if purpose=='whisper' and not (kind.casefold()=='whisper' or
            (not kind and isinstance(config.get('lang_ids'),list) and isinstance(config.get('alignment_heads'),list))):
        raise ValueError('Whisper benötigt ein konvertiertes faster-whisper/CTranslate2-Modell.')


def add(data,url,purpose):
    if purpose not in PURPOSES:raise ValueError('Nicht unterstützter Modellzweck')
    repo=repository(url)
    from huggingface_hub import HfApi,hf_hub_download
    info=HfApi().model_info(repo,token=False,files_metadata=True)
    revision=info.sha
    if not re.fullmatch(r'[a-f0-9]{40}',revision or ''):raise ValueError('Keine unveränderliche Modellrevision verfügbar.')
    config=json.loads(Path(hf_hub_download(repo,'config.json',revision=revision,token=False)).read_text(encoding='utf8'))
    validate_config(purpose,config)
    files={s.rfilename:s.size or 0 for s in info.siblings}
    weights=[name for name in files if name.endswith('.safetensors')] if purpose!='whisper' else [name for name in files if name=='model.bin']
    if not weights:raise ValueError('Keine kompatiblen Gewichte: Safetensors bzw. CTranslate2 model.bin erforderlich.')
    size=sum(files[name] for name in weights)
    if size>30*1024**3:raise ValueError('Modell überschreitet das lokale Downloadlimit von 30 GB.')
    key='custom-'+hashlib.sha256((repo+revision+purpose).encode()).hexdigest()[:20]
    descriptions={'audio':'Eigenes CLAP-Modell für Audio Mood und Instrumenthinweise. Kompatibilität prüfen.',
                  'lyrics':'Eigener Vier-Emotions-Klassifikator für Lyric Mood. Sprachabdeckung selbst prüfen.',
                  'interpretation':'Eigenes Textmodell für Deutungen. Benötigt ein Chat-Template; Speicherbedarf hängt von den Gewichten ab.',
                  'whisper':'Eigenes CTranslate2-Whisper für lokale Transkription.'}
    values=entries(data);values[key]={'repo':repo,'revision':revision,'purpose':purpose,'name':repo,
        'custom':True,'description':descriptions[purpose],'download':f'{size/1024**3:.2f} GB',
        'memory':'Zusätzlicher RAM/VRAM für Inferenz erforderlich'}
    save(data,values);return key
