"""Explicit, attributed public MusicBrainz lookups; never infer a recording identity."""
import re
import threading
import time
import httpx

_lock=threading.Lock()
_last=0.
BASE='https://musicbrainz.org/ws/2/'


def request(path,params):
    global _last
    with _lock:
        delay=1.1-(time.monotonic()-_last)
        if delay>0:time.sleep(delay)
        try:
            response=httpx.get(BASE+path,params={**params,'fmt':'json'},
                headers={'User-Agent':'MoodScope/0.2 (https://github.com/FutureKLP/MoodScope)'},timeout=25)
            response.raise_for_status()
            return response.json()
        finally:_last=time.monotonic()


def quote(text):return '"'+re.sub(r'["\\\x00-\x1f]',' ',text).strip()+'"'


def search(artist,title):
    query='recording:'+quote(title)
    if artist.strip():query+=' AND artist:'+quote(artist)
    data=request('recording',{'query':query,'limit':8})
    return {'candidates':[{'id':r['id'],'title':r.get('title',''),
        'artist':''.join(a.get('name',a.get('artist',{}).get('name',''))+a.get('joinphrase','') for a in r.get('artist-credit',[])),
        'duration':r.get('length',0)/1000,'score':r.get('score'),
        'release':next((v.get('title','') for v in r.get('releases',[])),''),
        'url':'https://musicbrainz.org/recording/'+r['id']} for r in data.get('recordings',[])],
        'source':'MusicBrainz','note':'Suchtreffer sind Vorschläge. Passende Aufnahme selbst auswählen; Remix und Original können abweichen.'}


def details(identity):
    if not re.fullmatch(r'[0-9a-fA-F-]{36}',identity):raise ValueError('Ungültige Aufnahme-ID')
    r=request('recording/'+identity,{'inc':'artist-credits+releases+genres+artist-rels+work-rels'})
    credits=[{'role':rel.get('type',''),'name':rel.get('artist',{}).get('name',''),
        'instruments':rel.get('attributes',[])} for rel in r.get('relations',[]) if rel.get('artist')]
    return {'id':identity,'title':r.get('title',''),'credits':credits,
        'genres':[g['name'] for g in r.get('genres',[])],
        'releases':[{'title':v.get('title',''),'date':v.get('date','')} for v in r.get('releases',[])][:12],
        'source':'MusicBrainz','url':'https://musicbrainz.org/recording/'+identity,
        'note':'Datenbankangaben zur ausgewählten Aufnahme; fehlende Instrumente/Besetzungen werden nicht ergänzt oder erfunden.'}
