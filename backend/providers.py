"""User-configured text model servers. Only non-secret profile settings are persisted."""
import json
import ipaddress
from pathlib import Path
import threading
from urllib.parse import urlsplit
import uuid
import httpx

_keys={}
_lock=threading.Lock()


def endpoint(value):
    value=value.strip().rstrip('/')
    p=urlsplit(value)
    if p.scheme not in {'http','https'} or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise ValueError('Basis-URL ohne Zugangsdaten, Query oder Fragment eingeben.')
    try:address=ipaddress.ip_address(p.hostname)
    except ValueError:address=None
    if address and (address.is_link_local or address.is_unspecified or address.is_multicast):raise ValueError('Diese Serveradresse ist nicht unterstützt.')
    if p.scheme=='http' and p.hostname!='localhost' and not (address and (address.is_private or address.is_loopback)):
        raise ValueError('Entfernte Internetserver benötigen HTTPS; HTTP ist für lokale/LAN-Server erlaubt.')
    return value


def profiles(data):
    try:return json.loads((Path(data)/'providers.json').read_text(encoding='utf-8'))
    except (OSError,ValueError):return []


def status(data):
    with _lock:return {'profiles':[{**p,'configured':p['id'] in _keys,'key_storage':'Nur Arbeitsspeicher; nach Backend-Neustart erneut eingeben'} for p in profiles(data)]}


def save(data,request):
    p={'id':request.get('id') or uuid.uuid4().hex,'name':request['name'].strip(),
        'protocol':request['protocol'],'base_url':endpoint(request['base_url']),'model':request['model'].strip()}
    if not p['name'] or not p['model']:raise ValueError('Name und Modell-ID fehlen.')
    with _lock:
        values=[v for v in profiles(data) if v['id']!=p['id']]+[p]
        if len(values)>20:raise ValueError('Maximal 20 Serverprofile.')
        path=Path(data)/'providers.json';path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(values,indent=2),encoding='utf-8');tmp.replace(path)
        key=request.get('api_key','').strip()
        if key:_keys[p['id']]=key
    return p


def remove(data,identity):
    with _lock:
        values=[p for p in profiles(data) if p['id']!=identity]
        (Path(data)/'providers.json').write_text(json.dumps(values),encoding='utf-8')
        _keys.pop(identity,None)


def profile(data,identity):
    p=next((p for p in profiles(data) if p['id']==identity),None)
    if not p:raise ValueError('Serverprofil nicht vorhanden.')
    return p


def generate(data,identity,prompt):
    p=profile(data,identity)
    with _lock:key=_keys.get(identity,'')
    base=endpoint(p['base_url'])
    if p['protocol']=='anthropic':
        url=base+'/messages'
        headers={'x-api-key':key,'anthropic-version':'2023-06-01'}
        payload={'model':p['model'],'max_tokens':1800,'messages':[{'role':'user','content':prompt}]}
    else:
        url=base+'/chat/completions'
        headers={'Authorization':'Bearer '+key} if key else {}
        payload={'model':p['model'],'max_completion_tokens':1800,'messages':[{'role':'user','content':prompt}]}
        # Many local compatible servers accept max_tokens rather than max_completion_tokens.
        if urlsplit(base).hostname not in {'api.openai.com'}:
            payload['max_tokens']=payload.pop('max_completion_tokens')
    try:response=httpx.post(url,headers=headers,json=payload,timeout=httpx.Timeout(180,connect=10),follow_redirects=False)
    except httpx.HTTPError:raise RuntimeError('Modellserver nicht erreichbar oder Zeitlimit überschritten. Adresse, Dienst und Firewall prüfen.') from None
    if response.status_code!=200:raise RuntimeError(f'Modellserver meldet HTTP {response.status_code}. Key, Modell-ID, Kontingent und API-Protokoll prüfen; keine automatische Wiederholung.')
    try:
        value=response.json()
        if p['protocol']=='anthropic':
            text=''.join(b.get('text','') for b in value['content'] if b.get('type')=='text')
            cut=value.get('stop_reason')=='max_tokens'
        else:
            text=value['choices'][0]['message']['content'];cut=value['choices'][0].get('finish_reason')=='length'
        if not isinstance(text,str) or len(text.strip())<20 or len(text)>20000:raise ValueError()
        return {'text':text.strip(),'model':p['model'],'provider':p['name'],'output_truncated':cut}
    except (ValueError,KeyError,IndexError,TypeError):raise RuntimeError('Server lieferte keine gültige Textantwort; keine Ersatzdeutung erzeugt.') from None
