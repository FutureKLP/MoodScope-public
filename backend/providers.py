"""User-configured model servers. Only non-secret profile settings are persisted."""
import json
import ipaddress
from pathlib import Path
import threading
from urllib.parse import urlsplit
import uuid
import socket
import httpx

_keys={}
_lock=threading.RLock()
_audio_profile=None


def endpoint(value):
    value=value.strip().rstrip('/')
    p=urlsplit(value)
    if p.scheme not in {'http','https'} or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise ValueError('Basis-URL ohne Zugangsdaten, Query oder Fragment eingeben.')
    try:
        address=ipaddress.ip_address(p.hostname)
        address=getattr(address,'ipv4_mapped',None) or address
    except ValueError:address=None
    if address and (address.is_link_local or address.is_unspecified or address.is_multicast):raise ValueError('Diese Serveradresse ist nicht unterstützt.')
    if p.scheme=='http' and p.hostname!='localhost' and not (address and (address.is_private or address.is_loopback)):
        if address:raise ValueError('Entfernte Internetserver benötigen HTTPS; HTTP ist für lokale/LAN-Server erlaubt.')
        try:
            resolved={ipaddress.ip_address(row[4][0]) for row in socket.getaddrinfo(p.hostname,p.port or 80,type=socket.SOCK_STREAM)}
            resolved={getattr(a,'ipv4_mapped',None) or a for a in resolved}
        except (OSError,ValueError):raise ValueError('Heimserver-Name nicht auflösbar. Netzwerkverbindung oder lokale IP-Adresse prüfen.') from None
        if not resolved or any(not (a.is_private or a.is_loopback) or a.is_link_local or a.is_unspecified or a.is_multicast for a in resolved):
            raise ValueError('Entfernte Internetserver benötigen HTTPS; HTTP ist für lokale/LAN-Server erlaubt.')
    return value


def discover_models(base_url,key=''):
    """Read metadata only: never load models or submit text/audio."""
    base=endpoint(base_url)
    try:response=httpx.get(base+'/models',headers={'Authorization':'Bearer '+key} if key else {},timeout=httpx.Timeout(15,connect=5),follow_redirects=False)
    except httpx.HTTPError:raise ValueError('Modellserver nicht erreichbar. Adresse, Port, Serverfreigabe und Firewall prüfen.') from None
    if response.status_code!=200:raise ValueError(f'Modellliste meldet HTTP {response.status_code}. Basis-URL mit /v1 und gegebenenfalls Sitzungs-Key prüfen.')
    try:
        if len(response.content)>2_000_000:raise ValueError()
        rows=response.json()['data']
        if not isinstance(rows,list) or len(rows)>1000:raise ValueError()
        ids=[row['id'] for row in rows]
        if any(not isinstance(value,str) or not value.strip() or len(value)>120 for value in ids):raise ValueError()
        return {'models':sorted(set(ids)),'generated':False}
    except (ValueError,KeyError,TypeError):raise ValueError('Server lieferte keine gültige kompatible Modellliste.') from None


def profiles(data):
    try:return json.loads((Path(data)/'providers.json').read_text(encoding='utf-8'))
    except (OSError,ValueError):return []


def status(data):
    from . import cloud
    with _lock:return {'profiles':[{**p,'configured':p['id'] in _keys,'key_storage':'Nur Arbeitsspeicher; nach Backend-Neustart erneut eingeben'} for p in profiles(data)],'audio':cloud.settings()}


def save(data,request):
    p={'id':request.get('id') or uuid.uuid4().hex,'name':request['name'].strip(),
        'protocol':request['protocol'],'base_url':endpoint(request['base_url']),'model':request['model'].strip(),
        'free_project_confirmed':bool(request.get('free_project_confirmed',False)),
        'audio_input':bool(request.get('audio_input',False)),
        'audio_usage_confirmed':bool(request.get('audio_usage_confirmed',False))}
    if p['audio_input'] and (p['protocol']=='anthropic' or urlsplit(p['base_url']).hostname=='api.deepseek.com'):
        raise ValueError('Dieses Profil unterstützt hier nur Textdeutungen. Ein kompatibles Audiomodell verwenden.')
    if p['protocol']=='gemini' and (p['base_url']!='https://generativelanguage.googleapis.com/v1beta' or not __import__('re').fullmatch(r'[A-Za-z0-9_.-]+',p['model'])):
        raise ValueError('Gemini benötigt die offizielle v1beta-Basis-URL und eine gültige Modell-ID.')
    if not p['name'] or not p['model']:raise ValueError('Name und Modell-ID fehlen.')
    with _lock:
        if _audio_profile==(str(Path(data).resolve()),p['id']):
            from . import cloud
            cloud.configure('',False)
        values=[v for v in profiles(data) if v['id']!=p['id']]+[p]
        if len(values)>20:raise ValueError('Maximal 20 Serverprofile.')
        path=Path(data)/'providers.json';path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(values,indent=2),encoding='utf-8');tmp.replace(path)
        key=request.get('api_key','').strip()
        if key:_keys[p['id']]=key
    return p


def remove(data,identity):
    global _audio_profile
    with _lock:
        values=[p for p in profiles(data) if p['id']!=identity]
        (Path(data)/'providers.json').write_text(json.dumps(values),encoding='utf-8')
        _keys.pop(identity,None)
        if _audio_profile==(str(Path(data).resolve()),identity):
            from . import cloud
            cloud.configure('',False);_audio_profile=None


def profile(data,identity):
    p=next((p for p in profiles(data) if p['id']==identity),None)
    if not p:raise ValueError('Serverprofil nicht vorhanden.')
    return p


def generate(data,identity,prompt):
    with _lock:
        p=profile(data,identity);key=_keys.get(identity,'')
    base=endpoint(p['base_url'])
    if not key and (p['protocol'] in {'gemini','anthropic'} or urlsplit(base).hostname in {'api.openai.com','api.deepseek.com','api.mistral.ai'}):
        raise RuntimeError('API-Key für dieses Anbieterprofil fehlt. In Modelle & API den Sitzungs-Key setzen oder ein lokales Modell wählen.')
    if p['protocol']=='gemini':
        url=base+'/models/'+p['model']+':generateContent'
        headers={'x-goog-api-key':key}
        payload={'contents':[{'role':'user','parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':1800}}
    elif p['protocol']=='anthropic':
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
        if p['protocol']=='gemini':
            candidate=value['candidates'][0]
            text=''.join(b.get('text','') for b in candidate['content']['parts'] if not b.get('thought'))
            cut=candidate.get('finishReason')=='MAX_TOKENS'
        elif p['protocol']=='anthropic':
            text=''.join(b.get('text','') for b in value['content'] if b.get('type')=='text')
            cut=value.get('stop_reason')=='max_tokens'
        else:
            text=value['choices'][0]['message']['content'];cut=value['choices'][0].get('finish_reason')=='length'
        if not isinstance(text,str) or len(text.strip())<20 or len(text)>20000:raise ValueError()
        return {'text':text.strip(),'model':p['model'],'provider':p['name'],'output_truncated':cut}
    except (ValueError,KeyError,IndexError,TypeError):raise RuntimeError('Server lieferte keine gültige Textantwort; keine Ersatzdeutung erzeugt.') from None


def activate_audio(data,identity):
    with _lock:return _activate_audio(data,identity)


def _activate_audio(data,identity):
    global _audio_profile
    from . import cloud
    p=profile(data,identity)
    if p['protocol']!='gemini' and not (p['protocol']=='openai' and p.get('audio_input')):
        raise ValueError('Für dieses Profil zuerst ein Modell mit kompatibler Audioeingabe konfigurieren.')
    if p['protocol']=='gemini' and not p.get('free_project_confirmed'):raise ValueError('Für die optionale Gemini-Audioanalyse ein Projekt ohne Abrechnung bestätigen.')
    if p['protocol']=='openai' and not p.get('audio_usage_confirmed'):raise ValueError('Nutzungsbedingungen und mögliche API-Kosten für dieses Audioprofil bestätigen.')
    with _lock:key=_keys.get(identity,'')
    if not key and (p['protocol']=='gemini' or urlsplit(p['base_url']).hostname in {'api.openai.com','api.mistral.ai'}):raise ValueError('API-Key für dieses Profil fehlt in der aktuellen Sitzung.')
    cloud.configure_profile(p,key)
    _audio_profile=(str(Path(data).resolve()),identity)
    return {'configured':True,'provider':p['name'],'model':p['model']}
