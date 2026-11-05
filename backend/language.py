"""Translate product-owned response fields, never lyrics, tags, notes or model answers."""
import json
from pathlib import Path

EN=json.loads((Path(__file__).parent/'locales'/'en.json').read_text(encoding='utf8'))
FIELDS={'message','detail','note','warnings','source_warning','description','download','memory','key_storage','bpm_note','warning'}

def language(value):
    # Deliberately support only the two shipped locales.
    return 'en' if (value or '').lower().split(',')[0].split(';')[0].split('-')[0]=='en' else 'de'

def translate(value,locale):
    if locale!='en' or not isinstance(value,str):return value
    if value in EN:return EN[value]
    # Compose fixed fragments (e.g. a progress label plus a model name or error ID).
    for source in sorted(EN,key=len,reverse=True):
        if (len(source)>=12 or source in {'Lade ',' s von '}) and source in value:value=value.replace(source,EN[source])
    if value.startswith('etwa '):value='about '+value[5:]
    return value

def response(value,locale,key=None):
    if isinstance(value,dict):
        # Notes and source metadata are user content, not interface strings.
        return {k:response(v,locale,k) if k not in {'tags','original','selected_lyric_line','full_text'} else v for k,v in value.items()}
    if isinstance(value,list):return [response(v,locale,key) for v in value]
    return translate(value,locale) if key in FIELDS else value
