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


def musicbrainz_search(artist,title):
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
    if identity.startswith('itunes:'):
        number=identity.split(':',1)[1]
        if not number.isdigit():raise ValueError('Ungültige Katalog-ID')
        response=httpx.get('https://itunes.apple.com/lookup',params={'id':number,'country':'DE'},timeout=15)
        response.raise_for_status();rows=response.json().get('results',[])
        if not rows:raise ValueError('Katalogaufnahme nicht mehr vorhanden')
        r=rows[0]
        return {'id':identity,'title':r.get('trackName',''),'source':'Apple iTunes',
            'url':r.get('trackViewUrl','https://music.apple.com/'),
            'credits':[{'role':'Interpret laut Katalog','name':r.get('artistName',''),'instruments':[]}],
            'genres':[r['primaryGenreName']] if r.get('primaryGenreName') else [],
            'releases':[{'title':r.get('collectionName',''),'date':r.get('releaseDate','')[:10]}],
            'note':'Katalogdaten zur gewählten Aufnahme. Kein Nachweis der Instrumente oder einer Mashup-Besetzung; Original und Remix bewusst unterscheiden.'}
    if not re.fullmatch(r'[0-9a-fA-F-]{36}',identity):raise ValueError('Ungültige Aufnahme-ID')
    r=request('recording/'+identity,{'inc':'artist-credits+releases+genres+artist-rels+work-rels'})
    credits=[{'role':rel.get('type',''),'name':rel.get('artist',{}).get('name',''),
        'instruments':rel.get('attributes',[])} for rel in r.get('relations',[]) if rel.get('artist')]
    return {'id':identity,'title':r.get('title',''),'credits':credits,
        'genres':[g['name'] for g in r.get('genres',[])],
        'releases':[{'title':v.get('title',''),'date':v.get('date','')} for v in r.get('releases',[])][:12],
        'source':'MusicBrainz','url':'https://musicbrainz.org/recording/'+identity,
        'note':'Datenbankangaben zur ausgewählten Aufnahme; fehlende Instrumente/Besetzungen werden nicht ergänzt oder erfunden.'}


def itunes_search(artist,title):
    response=httpx.get('https://itunes.apple.com/search',params={'term':(artist+' '+title).strip(),
        'country':'DE','media':'music','entity':'song','limit':8},timeout=15)
    response.raise_for_status()
    return [{'id':'itunes:'+str(r['trackId']),'title':r.get('trackName',''),'artist':r.get('artistName',''),
        'duration':r.get('trackTimeMillis',0)/1000,'release':r.get('collectionName',''),
        'source':'Apple iTunes','url':r.get('trackViewUrl','https://music.apple.com/')} for r in response.json().get('results',[]) if r.get('trackId')]


def search(artist,title):
    from concurrent.futures import ThreadPoolExecutor
    candidates=[];unavailable=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks=[('MusicBrainz',pool.submit(musicbrainz_search,artist,title)),('Apple iTunes',pool.submit(itunes_search,artist,title))]
        for name,future in tasks:
            try:
                value=future.result()
                rows=value['candidates'] if isinstance(value,dict) else value
                candidates.extend({**r,'source':name} for r in rows)
            except Exception:unavailable.append(name)
    if len(unavailable)==2:raise RuntimeError('Beide öffentlichen Katalogdienste sind derzeit nicht erreichbar.')
    return {'candidates':candidates,'source':'Öffentliche Musikkataloge','unavailable':unavailable,
        'note':'Treffer sind Vorschläge, keine automatisch bestätigten Songfakten. Für Mashups ggf. Originaltitel getrennt suchen. '+('Derzeit nicht erreichbar: '+', '.join(unavailable)+'.' if unavailable else '')}
