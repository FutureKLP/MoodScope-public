"""Bounded public catalogue fallbacks with attributed, recording-specific evidence."""
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import httpx

_lock=threading.Lock()
_last=0.
BASE='https://musicbrainz.org/ws/2/'
HEADERS={'User-Agent':'MoodScope/0.3 (https://github.com/FutureKLP/MoodScope)'}


def get_json(url,params=None):
    response=httpx.get(url,params=params,headers=HEADERS,timeout=httpx.Timeout(10,connect=4),follow_redirects=False)
    response.raise_for_status()
    value=response.json()
    if not isinstance(value,dict) or value.get('error'):raise RuntimeError('Katalogdienst meldet einen Fehler.')
    return value


def request(path,params):
    global _last
    for attempt in range(2):
        with _lock:
            delay=1.1-(time.monotonic()-_last)
            if delay>0:time.sleep(delay)
            try:return get_json(BASE+path,{**params,'fmt':'json'})
            except httpx.HTTPStatusError as exc:
                if attempt or exc.response.status_code not in {429,502,503,504}:raise
            finally:_last=time.monotonic()
        time.sleep(.5)


def quote(text):return '"'+re.sub(r'["\\\x00-\x1f]',' ',text).strip()+'"'


def clean_query(artist,title):
    artist=re.sub(r'\s*-\s*Topic$','',artist,flags=re.I).strip()
    title=re.sub(r'[\[(](?:official|lyrics?|audio|video|hd|hq|visuali[sz]er)[^\])]*[\])]',' ',title,flags=re.I)
    title=re.sub(r'\s+(?:official\s+(?:music\s+)?video|official\s+audio)\s*$','',title,flags=re.I)
    title=' '.join(title.split())
    if not artist and ' - ' in title:
        left,right=title.split(' - ',1)
        if left.strip() and right.strip():artist,title=left.strip(),right.strip()
    return artist,title


def musicbrainz_search(artist,title):
    query='recording:'+quote(title)
    if artist.strip():query+=' AND artist:'+quote(artist)
    data=request('recording',{'query':query,'limit':8})
    return {'candidates':[{'id':r['id'],'title':r.get('title',''),
        'artist':''.join(a.get('name',a.get('artist',{}).get('name',''))+a.get('joinphrase','') for a in r.get('artist-credit',[])),
        'duration':r.get('length',0)/1000,'score':r.get('score'),
        'release':next((v.get('title','') for v in r.get('releases',[])),''),
        'url':'https://musicbrainz.org/recording/'+r['id']} for r in data.get('recordings',[]) if r.get('id')]}


def itunes_search(artist,title):
    data=get_json('https://itunes.apple.com/search',{'term':(artist+' '+title).strip(),'country':'DE','media':'music','entity':'song','limit':8})
    return [{'id':'itunes:'+str(r['trackId']),'title':r.get('trackName',''),'artist':r.get('artistName',''),
        'duration':r.get('trackTimeMillis',0)/1000,'release':r.get('collectionName',''),
        'url':r.get('trackViewUrl','https://music.apple.com/')} for r in data.get('results',[]) if r.get('trackId')]


def deezer_search(artist,title):
    data=get_json('https://api.deezer.com/search',{'q':(artist+' '+title).strip(),'limit':8})
    return [{'id':'deezer:'+str(r['id']),'title':r.get('title',''),'artist':r.get('artist',{}).get('name',''),
        'duration':r.get('duration',0),'release':r.get('album',{}).get('title',''),'url':'https://www.deezer.com/track/'+str(r['id'])}
        for r in data.get('data',[]) if isinstance(r.get('id'),int)]


def search(artist,title):
    providers=[('MusicBrainz',musicbrainz_search),('Apple iTunes',itunes_search),('Deezer',deezer_search)]
    candidates=[];unavailable=[];attempts=[]
    cleaned=clean_query(artist,title)
    def lookup(name,provider):
        queries=[(artist,title)]
        if cleaned not in queries:queries.append(cleaned)
        if artist.strip() and ('',cleaned[1]) not in queries:queries.append(('',cleaned[1]))
        # A failed service immediately yields to other providers. Empty results try broader terms.
        for query in queries[:3]:
            value=provider(*query);rows=value.get('candidates',[]) if isinstance(value,dict) else value
            if rows:return rows,query
        return [],queries[-1]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[(name,pool.submit(lookup,name,provider)) for name,provider in providers]
        for name,future in futures:
            try:
                rows,query=future.result();candidates.extend({**r,'source':name} for r in rows[:8]);attempts.append({'source':name,'status':'found' if rows else 'empty'})
            except Exception:
                unavailable.append(name);attempts.append({'source':name,'status':'unavailable'})
    if len(unavailable)==len(providers):raise RuntimeError('Alle öffentlichen Katalogdienste sind derzeit nicht erreichbar. Verbindung prüfen und später erneut versuchen.')
    return {'candidates':candidates,'source':'Öffentliche Musikkataloge','unavailable':unavailable,'attempts':attempts,
        'note':'Automatische Recherche bei MusicBrainz, Apple iTunes und Deezer. Leere Suchen versuchen bereinigte Titel und eine Suche ohne Interpret. Treffer bleiben Vorschläge; Original und Remix selbst bestätigen.'}


def musicbrainz_details(identity):
    r=request('recording/'+identity,{'inc':'artist-credits+releases+genres+artist-rels+work-rels+url-rels'})
    credits=[]
    for rel in r.get('relations',[]):
        if rel.get('artist'):
            role=rel.get('type','');attributes=rel.get('attributes',[])
            instruments=[v for v in attributes if v not in {'additional','guest','solo','lead','background'}] if role in {'instrument','vocal'} else []
            if role=='vocal':instruments=['vocals']+instruments
            credits.append({'role':role,'name':rel['artist'].get('name',''),'instruments':instruments,'scope':'recording'})
    result={'id':identity,'title':r.get('title',''),'credits':credits,'genres':[g['name'] for g in r.get('genres',[])],
        'releases':[{'title':v.get('title',''),'date':v.get('date','')} for v in r.get('releases',[])][:12],
        'source':'MusicBrainz','url':'https://musicbrainz.org/recording/'+identity,
        'note':'Credits beziehen sich auf die ausgewählte Aufnahme. Werkangaben werden getrennt gekennzeichnet und belegen nicht die Besetzung eines Remixes.',
        'instrumentation':[]}
    # Linked work data is a fallback, never silently promoted to recording credits.
    relations=list(r.get('relations',[]));warnings=[]
    if not any(c['instruments'] for c in credits):
        for rel in r.get('relations',[]):
            work_id=rel.get('work',{}).get('id','')
            if re.fullmatch(r'[0-9a-fA-F-]{36}',work_id):
                try:relations+=request('work/'+work_id,{'inc':'url-rels'}).get('relations',[])
                except Exception:warnings.append('MusicBrainz work')
                break
    qids=[]
    for rel in relations:
        value=rel.get('url',{}).get('resource','');match=re.fullmatch(r'https://(?:www\.)?wikidata\.org/wiki/(Q[0-9]+)',value)
        if match and match[1] not in qids:qids.append(match[1])
    for qid in qids[:2]:
        try:result['instrumentation']+=wikidata_instruments(qid)
        except Exception:warnings.append('Wikidata')
    result['unavailable']=sorted(set(warnings))
    return enrich_discogs(result,r)


def wikidata_instruments(qid):
    if not re.fullmatch(r'Q[0-9]+',qid):raise ValueError('Ungültige Wikidata-ID')
    base='https://www.wikidata.org/w/api.php'
    data=get_json(base,{'action':'wbgetentities','ids':qid,'props':'claims','format':'json'})
    claims=data.get('entities',{}).get(qid,{}).get('claims',{})
    ids=[]
    for claim in claims.get('P870',[]):
        value=claim.get('mainsnak',{}).get('datavalue',{}).get('value',{})
        name=value.get('id','') if isinstance(value,dict) else ''
        if re.fullmatch(r'Q[0-9]+',name) and name not in ids:ids.append(name)
    if not ids:return []
    labels=get_json(base,{'action':'wbgetentities','ids':'|'.join(ids[:12]),'props':'labels','languages':'en','format':'json'})
    return [{'name':value.get('labels',{}).get('en',{}).get('value',identity),'source':'Wikidata','scope':'linked_work_or_song',
             'url':'https://www.wikidata.org/wiki/'+qid} for identity,value in labels.get('entities',{}).items()]


def details(identity):
    if re.fullmatch(r'[0-9a-fA-F-]{36}',identity):return musicbrainz_details(identity)
    if identity.startswith('itunes:') and identity.split(':',1)[1].isdigit():
        rows=get_json('https://itunes.apple.com/lookup',{'id':identity.split(':',1)[1],'country':'DE'}).get('results',[])
        if not rows:raise ValueError('Katalogaufnahme nicht mehr vorhanden')
        r=rows[0];result={'id':identity,'title':r.get('trackName',''),'artist':r.get('artistName',''),'duration':r.get('trackTimeMillis',0)/1000,'source':'Apple iTunes','url':r.get('trackViewUrl','https://music.apple.com/'),
            'credits':[{'role':'artist','name':r.get('artistName',''),'instruments':[]}],'genres':[r['primaryGenreName']] if r.get('primaryGenreName') else [],
            'releases':[{'title':r.get('collectionName',''),'date':r.get('releaseDate','')[:10]}]}
    elif identity.startswith('deezer:') and identity.split(':',1)[1].isdigit():
        r=get_json('https://api.deezer.com/track/'+identity.split(':',1)[1]);result={'id':identity,'title':r.get('title',''),'artist':r.get('artist',{}).get('name',''),'duration':r.get('duration',0),'source':'Deezer','url':'https://www.deezer.com/track/'+identity.split(':',1)[1],
            'credits':[{'role':c.get('role','artist'),'name':c.get('name',''),'instruments':[]} for c in r.get('contributors',[])],
            'genres':[],'releases':[{'title':r.get('album',{}).get('title',''),'date':r.get('release_date','')}]}
    else:raise ValueError('Ungültige Aufnahme-ID')
    result['instrumentation']=[];result['supplemental']=[]
    # Basic catalogues rarely carry instrument credits. Look for an exact MusicBrainz counterpart.
    try:
        normalize=lambda value:re.sub(r'\W+','',value.casefold())
        candidates=musicbrainz_search(result['artist'],result['title'])['candidates']
        exact=[c for c in candidates if normalize(c.get('artist',''))==normalize(result['artist']) and normalize(c.get('title',''))==normalize(result['title']) and abs(c.get('duration',0)-result['duration'])<3]
        if len(exact)==1:
            extra=musicbrainz_details(exact[0]['id']);result['supplemental']=[extra];result['instrumentation']=extra.get('instrumentation',[])
            result['credits']+=[{**c,'source':c.get('source','MusicBrainz'),'url':c.get('url',extra['url'])} for c in extra['credits']]
            result['album_credits']=extra.get('album_credits',[])
            result['supplemental']+=extra.get('supplemental',[])
    except Exception:result['unavailable']=['MusicBrainz enrichment']
    result['note']='Katalogdaten zur ausgewählten Aufnahme. Fehlende Instrumentcredits werden automatisch bei einer eindeutig passenden MusicBrainz-Aufnahme und deren verknüpften Werkdaten gesucht. Werkangaben sind kein Nachweis für Remix-Instrumente.'
    return result

def discogs_credits(identity,track_title=''):
    if not re.fullmatch(r'[0-9]{1,20}',identity):raise ValueError('Ungültige Discogs-ID')
    data=get_json('https://api.discogs.com/releases/'+identity)
    source='https://www.discogs.com/release/'+identity
    normalize=lambda value:re.sub(r'\W+','',value.casefold())
    matches=[track for track in data.get('tracklist',[]) if track_title and normalize(track.get('title',''))==normalize(track_title)]
    instrument_pattern=r'\b(bass guitar|double bass|bass|drums?|guitars?|keyboards?|piano|synthesizers?|percussion|violin|viola|cello|trumpet|trombone|saxophone|flute|organ|accordion|vocals?)\b'
    def credit(row,scope):
        role=row.get('role','')
        instruments=list(dict.fromkeys(v.lower() for v in re.findall(instrument_pattern,role,re.I)))
        return {'name':row.get('name',''),'role':role,'instruments':instruments,'scope':scope,'source':'Discogs','url':source}
    recording=[];album=[]
    for row in data.get('extraartists',[])[:150]:
        positions={p.strip() for p in row.get('tracks','').split(',') if p.strip()}
        explicit=len(matches)==1 and matches[0].get('position') in positions
        value=credit(row,'recording' if explicit else 'album')
        if value['instruments']:(recording if explicit else album).append(value)
    if len(matches)==1:
        recording.extend(credit(row,'recording') for row in matches[0].get('extraartists',[])[:100] if re.search(instrument_pattern,row.get('role',''),re.I))
    return {'source':'Discogs','url':source,'title':data.get('title',''),'credits':recording,'album_credits':album}


def enrich_discogs(result,recording):
    # Recording-level Discogs links, then at most one linked release; never use paid/auth search.
    links=[rel.get('url',{}).get('resource','') for rel in recording.get('relations',[])]
    def release_id(value):
        match=re.fullmatch(r'https?://(?:www\.)?discogs\.com/(?:[a-z]{2}/)?release/([0-9]+)(?:-[^/?#]*)?/?',value)
        return match[1] if match else None
    ids=[release_id(value) for value in links if release_id(value)]
    if not ids:
        release=next((r.get('id','') for r in recording.get('releases',[]) if re.fullmatch(r'[0-9a-fA-F-]{36}',r.get('id',''))),None)
        if release:
            try:
                data=request('release/'+release,{'inc':'url-rels'})
                ids=[release_id(rel.get('url',{}).get('resource','')) for rel in data.get('relations',[])]
                ids=[value for value in ids if value]
            except Exception:result.setdefault('unavailable',[]).append('MusicBrainz release links')
    if ids:
        try:
            extra=discogs_credits(ids[0],result.get('title',''))
            result['credits']+=extra['credits'];result.setdefault('album_credits',[]).extend(extra['album_credits'])
            result.setdefault('supplemental',[]).append({'source':'Discogs','url':extra['url'],'title':extra['title']})
        except Exception:result.setdefault('unavailable',[]).append('Discogs')
    return result
