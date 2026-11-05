import hashlib
import json
import os
import sqlite3
import subprocess
import threading
import uuid
import tempfile
from contextlib import contextmanager
from typing import Literal
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, SecretStr

from .core import parse_lrc, biggest_split
from .models import ROOT, engines, AUDIO_MODEL, LYRIC_MODEL, PIPELINE_VERSION
from . import cloud, links, catalog, insights, library

DATA = Path(os.environ.get('MOODSCOPE_DATA', ROOT / 'data'))
DATA.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='MoodScope local analysis', version='0.2.0')
ORIGINS = ['http://127.0.0.1:1420', 'http://localhost:1420', 'tauri://localhost', 'http://tauri.localhost', 'https://tauri.localhost', 'http://127.0.0.1:8765']
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=['GET','POST'], allow_headers=['Content-Type'])
executor = ThreadPoolExecutor(max_workers=1)
jobs = {}
job_lock = threading.Lock()


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Pydantic normally includes original input, which may contain a key.
    return JSONResponse(status_code=422,content={'detail':[
        {'loc':list(e['loc']),'msg':e['msg'],'type':e['type']} for e in exc.errors()]})


@app.middleware('http')
async def local_only(request: Request, call_next):
    # Block browser cross-origin form writes and DNS rebinding to the loopback service.
    host = request.headers.get('host', '').split(':')[0]
    origin = request.headers.get('origin')
    if host not in {'127.0.0.1', 'localhost', 'testserver'} or (origin and origin not in ORIGINS):
        return JSONResponse({'detail':'Untrusted local origin'}, status_code=403)
    return await call_next(request)


@contextmanager
def db():
    conn = sqlite3.connect(DATA / 'cache.sqlite3', timeout=30)
    conn.execute('CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, metadata TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, result TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS cache_owner (key TEXT PRIMARY KEY, track_id TEXT NOT NULL)')
    try:
        with conn: yield conn
    finally: conn.close()


def track(track_id):
    with db() as conn:
        row = conn.execute('SELECT metadata FROM tracks WHERE id=?', (track_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Song nicht gefunden')
    return json.loads(row[0])


def canonical(identity):
    metadata=track(identity)
    seen={identity}
    while metadata.get('reuse_source_id') and metadata['reuse_source_id'] not in seen:
        identity=metadata['reuse_source_id'];seen.add(identity);metadata=track(identity)
    return identity


def own(conn,key,identity):
    conn.execute('INSERT OR REPLACE INTO cache_owner VALUES (?,?)',(key,canonical(identity)))


def local_version(active):
    return PIPELINE_VERSION+json.dumps({k:active[k] for k in ['audio','lyrics','whisper']},sort_keys=True)


@app.get('/api/health')
def health():
    return {'status':'ok', 'version':'0.2.0', 'device':engines.device(),
            'audio_model':AUDIO_MODEL, 'lyric_model':LYRIC_MODEL}


@app.get('/api/settings')
def get_settings():
    return {'cloud':cloud.settings(),'local_default':True,'link_import_available':bool(
        (ROOT/'.tools'/'yt-dlp'/('yt-dlp.exe' if os.name=='nt' else 'yt-dlp_linux')).exists())}


class CloudSettings(BaseModel):
    api_key: SecretStr = Field(default=SecretStr(''),max_length=300)
    free_project_confirmed: bool = False


@app.post('/api/settings/cloud')
def set_cloud_settings(request: CloudSettings):
    key=request.api_key.get_secret_value().strip()
    if key and (len(key)<15 or any(c.isspace() for c in key)):
        raise HTTPException(422,'Ungültiges Key-Format; der Wert wird nicht gespeichert oder protokolliert.')
    cloud.configure(key,request.free_project_confirmed)
    return cloud.settings()


def import_path(source, name, supplied=None):
    supplied=supplied or {}
    digest=hashlib.sha256(b'moodscope-stereo-decoder-v2')
    size=0
    with Path(source).open('rb') as stream:
        while chunk:=stream.read(1024*1024):
            size+=len(chunk)
            if size>250*1024*1024: raise HTTPException(413,'Maximal 250 MB pro Song')
            digest.update(chunk)
    identity=digest.hexdigest();target=DATA/f'{identity}.wav'
    if not target.exists():
        import imageio_ffmpeg
        converted=DATA/f'{uuid.uuid4().hex}.wav'
        try:
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-v','error','-y','-i',str(source),
                '-t','1801','-ac','2','-ar','48000',str(converted)],check=True,capture_output=True,timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            info=sf.info(converted)
            if info.duration<=0: raise ValueError('Leere Audiodatei')
            if info.duration>1800: raise HTTPException(413,'Maximal 30 Minuten; Datei wurde nicht abgeschnitten importiert.')
            converted.replace(target)
        except HTTPException: raise
        except (subprocess.SubprocessError,ValueError,RuntimeError):
            raise HTTPException(422,'Audio konnte nicht dekodiert werden.') from None
        finally: converted.unlink(missing_ok=True)
    import mutagen
    try: tags=mutagen.File(source,easy=True)
    except mutagen.MutagenError: tags=None
    metadata={'id':identity,'name':Path(name).name,'duration':sf.info(target).duration,
              'sample_rate':48000,'channels':2,
              'artist':supplied.get('artist') or (tags.get('artist',[''])[0] if tags else ''),
              'title':supplied.get('title') or (tags.get('title',[''])[0] if tags else ''),
              'source':supplied.get('source','Datei')}
    with db() as conn:
        previous=conn.execute('SELECT metadata FROM tracks WHERE id=?',(identity,)).fetchone()
        if previous:
            prior=json.loads(previous[0])
            if prior.get('reuse_source_id'):metadata['reuse_source_id']=prior['reuse_source_id']
            metadata['cache_match']='same-file'
        else:
            fingerprint=library.signature(target)
            matched=library.find_metadata_match(conn,metadata,fingerprint)
            if fingerprint:conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(f'fingerprint:{identity}',json.dumps(fingerprint)))
            if matched:metadata['reuse_source_id']=canonical(matched);metadata['cache_match']='metadata-and-audio'
        conn.execute('INSERT OR REPLACE INTO tracks VALUES (?,?)',(identity,json.dumps(metadata)))
    return metadata


@app.post('/api/tracks')
def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in {'.mp3','.wav','.flac'}:
        raise HTTPException(415, 'Bitte MP3, WAV oder FLAC importieren')
    temp = DATA / f'{uuid.uuid4().hex}{suffix}'
    size = 0
    try:
        with temp.open('wb') as out:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > 250 * 1024 * 1024:
                    raise HTTPException(413, 'Maximal 250 MB pro Song')
                out.write(chunk)
        return import_path(temp,file.filename or 'Song')
    except HTTPException:
        raise
    except (subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        raise HTTPException(422,'Audio konnte nicht dekodiert werden.') from None
    finally:
        temp.unlink(missing_ok=True)


@app.get('/api/tracks/{identity}/audio')
def audio(identity: str):
    track(identity)
    return FileResponse(DATA / f'{identity}.wav', media_type='audio/wav')


class LyricsQuery(BaseModel):
    artist: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)


@app.post('/api/tracks/{identity}/lyrics/search')
def search(identity: str, query: LyricsQuery):
    metadata = track(identity)
    key = 'lrclib:' + json.dumps([query.artist,query.title,round(metadata['duration'])])
    with db() as conn:
        cached = conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
    if cached:
        return {**json.loads(cached[0]), 'cached':True}
    try:
        response = httpx.get('https://lrclib.net/api/get', params={'artist_name':query.artist,
            'track_name':query.title,'duration':round(metadata['duration'])},
            headers={'User-Agent':'MoodScope/0.1 (local desktop lyrics lookup)'}, timeout=20)
        if response.status_code == 404:
            raise HTTPException(404,'Kein passender Song bei LRCLIB. LRC importieren oder Whisper verwenden.')
        response.raise_for_status()
        result = response.json()
        synced = result.get('syncedLyrics')
        value = {'text':synced or result.get('plainLyrics') or '', 'synced':bool(synced),
                 'instrumental':bool(result.get('instrumental')), 'source':'LRCLIB'}
        with db() as conn:
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(value)))
        return value
    except httpx.HTTPError as exc:
        raise HTTPException(502,'LRCLIB nicht erreichbar. Offline: LRC importieren oder Whisper wählen.') from exc


class AnalyzeRequest(BaseModel):
    lyrics: str = Field(default='', max_length=200000)
    whisper: bool = False
    mode: Literal['local','cloud'] = 'local'
    upload_consent: bool = False
    force: bool = False


def start_job(kind, function, *args):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):
            raise HTTPException(409,'Ein Auftrag läuft bereits. Bitte warten.')
        for identity in list(jobs):
            if len(jobs)<32: break
            if jobs[identity]['status']!='running': jobs.pop(identity)
        job_id=uuid.uuid4().hex
        jobs[job_id]={'kind':kind,'status':'running','progress':0,'message':'Auftrag wird vorbereitet'}
    executor.submit(function,job_id,*args)
    return {'job_id':job_id}


class LinkRequest(BaseModel):
    url: str = Field(min_length=10,max_length=2000)


def run_link_job(job_id,url):
    def progress(message,value):
        with job_lock: jobs[job_id].update(message=message,progress=value)
    try:
        with tempfile.TemporaryDirectory(prefix='link-',dir=DATA) as directory:
            source,metadata=links.download(url,directory,progress)
            progress('Dekodiere Song für synchronisierte Wiedergabe',80)
            result=import_path(source,metadata['title'],metadata)
        with job_lock: jobs[job_id].update(status='done',progress=100,message='Link importiert',result=result)
    except Exception:
        with job_lock: jobs[job_id].update(status='error',message='Linkimport fehlgeschlagen: Plattform nicht erreichbar, Download gesperrt oder kein unterstützter Einzeltrack. Lokalen Import verwenden.')


@app.post('/api/tracks/link')
def import_link(request: LinkRequest):
    try:
        url=links.validate_url(request.url)
        links.downloader()
    except ValueError as exc: raise HTTPException(422,str(exc)) from None
    except RuntimeError as exc: raise HTTPException(503,str(exc)) from None
    return start_job('import',run_link_job,url)


def run_job(job_id, identity, request):
    def progress(message, value):
        with job_lock:
            jobs[job_id].update(message=message, progress=value)
    try:
        engines.data=DATA
        metadata = track(identity)
        cache_identity=canonical(identity)
        active=catalog.configuration(DATA)['active']
        version=local_version(active) if request.mode=='local' else cloud.VERSION+cloud.MODEL
        key = hashlib.sha256((cache_identity + version + json.dumps(request.model_dump(exclude={'force','upload_consent'}),sort_keys=True)).encode()).hexdigest()
        with db() as conn:
            cached = conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached and not request.force:
            result = {**json.loads(cached[0]), 'cached':True}
        else:
            lines = parse_lrc(request.lyrics, metadata['duration'])
            warnings = []
            if request.lyrics.strip() and not lines:
                warnings.append('Text ohne LRC-Zeitstempel: keine synchronisierte Textkurve. Bitte LRC importieren oder Whisper aktivieren.')
            if not lines and request.whisper and request.mode=='local':
                lines = engines.transcribe(DATA / f'{identity}.wav', progress)
                warnings.append('Whisper-Zeitstempel und Gesangserkennung können ungenau sein.')
            if request.mode=='cloud' and request.whisper:
                warnings.append('Im API-Modus wird kein lokales Whisper gestartet. Für Textkurve synchronisierte LRC-Lyrics verwenden.')
            audio_key = f'audio:{cache_identity}:{version}'
            with db() as conn:
                audio_cached = conn.execute('SELECT result FROM cache WHERE key=?',(audio_key,)).fetchone()
            if audio_cached and not request.force:
                payload=json.loads(audio_cached[0])
                a, summary = payload['audio'], payload['features']
                progress('Audioanalyse aus lokalem Cache', 65)
            else:
                y, sr = sf.read(DATA / f'{identity}.wav', dtype='float32')
                if y.ndim==2: y=y.mean(axis=1)
                summary = insights.acoustic_features(y,sr)
                a = engines.audio(y,sr,progress) if request.mode=='local' else cloud.audio_mood(y,sr,progress)
                with db() as conn:
                    conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',
                                 (audio_key,json.dumps({'audio':a,'features':summary})))
                    own(conn,audio_key,identity)
            l = engines.lyrics(lines,progress) if request.mode=='local' else cloud.lyric_mood(lines,progress)
            if not l:
                warnings.append('Keine synchronisierten Lyrics: Biggest Split ist nicht verfügbar.')
            result = {'audio':a, 'lyrics':l, 'split':biggest_split(a,l), 'features':summary,
                      'warnings':warnings, 'cached':False, 'device':engines.device() if request.mode=='local' else 'API',
                      'mode':request.mode,
                      'source_lyrics':request.lyrics,'track_id':cache_identity,'pipeline_version':version,
                      'models':{'audio':catalog.CATALOG[active['audio']]['repo'] if request.mode=='local' else cloud.MODEL,
                                'lyrics':catalog.CATALOG[active['lyrics']]['repo'] if request.mode=='local' else cloud.MODEL},
                      'method':'CLAP Prompt-Ensemble und XLM-EMO mit Textkontext' if request.mode=='local' else 'Gemini: getrennte Audio- und Textanalyse; subjektive unkalibrierte Valenz.'}
            result['warnings'].append('Modellwerte und Unsicherheit sind nicht wissenschaftlich kalibriert.')
            with db() as conn:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(result)))
                own(conn,key,identity)
        with db() as conn:
            latest_key=f'latest:{cache_identity}:{request.mode}'
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(latest_key,json.dumps(result)))
            own(conn,latest_key,identity)
        with job_lock:
            jobs[job_id].update(status='done',progress=100,message='Analyse abgeschlossen',result=result)
    except Exception as exc:
        with job_lock:
            message=str(exc)[:800] if request.mode=='local' or isinstance(exc,cloud.CloudError) else 'Online-Analyse fehlgeschlagen; keine Ersatzwerte erzeugt.'
            jobs[job_id].update(status='error',message=message)


@app.post('/api/tracks/{identity}/analyze')
def analyze(identity: str, request: AnalyzeRequest):
    track(identity)
    if request.mode=='cloud':
        if not request.upload_consent: raise HTTPException(422,'API-Modus benötigt deine Zustimmung zum Upload von Audio und Lyrics an Google.')
        try: cloud.credential()
        except cloud.CloudError as exc: raise HTTPException(422,str(exc)) from None
    return start_job('analysis',run_job,identity,request)


@app.get('/api/jobs/{job_id}')
def job(job_id: str):
    with job_lock:
        if job_id not in jobs:
            raise HTTPException(404,'Analyseauftrag nicht gefunden')
        return dict(jobs[job_id])


@app.get('/api/models')
def models():return catalog.status(DATA)


class ModelChoice(BaseModel):
    model_id: str = Field(max_length=80)


@app.post('/api/models/select')
def select_model(request: ModelChoice):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        try:catalog.select(DATA,request.model_id)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None
        catalog.unload_models(engines)
    return catalog.status(DATA)


def run_download(job_id,key):
    def progress(message,value):
        with job_lock:jobs[job_id].update(message=message,progress=value)
    try:
        result=catalog.download(DATA,key,progress)
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Modell heruntergeladen',result=result)
    except Exception:
        with job_lock:jobs[job_id].update(status='error',message='Modelldownload fehlgeschlagen. Netzwerk, freien Speicher und Offline-Einstellung prüfen.')


@app.post('/api/models/download')
def download_model(request: ModelChoice):
    if request.model_id not in catalog.CATALOG:raise HTTPException(422,'Nicht unterstütztes Modell')
    return start_job('download',run_download,request.model_id)


class Notes(BaseModel):
    interpretation: str = Field(default='',max_length=20000)
    instruments: str = Field(default='',max_length=2000)
    personnel: str = Field(default='',max_length=4000)
    genre: str = Field(default='',max_length=200)
    bpm: float | None = Field(default=None,gt=0,le=500)


@app.get('/api/tracks/{identity}/notes')
def get_notes(identity: str):
    identity=canonical(identity)
    with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(f'notes:{identity}',)).fetchone()
    return json.loads(row[0]) if row else Notes().model_dump()


@app.post('/api/tracks/{identity}/notes')
def save_notes(identity: str,request: Notes):
    identity=canonical(identity)
    with db() as conn:conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(f'notes:{identity}',request.model_dump_json()))
    return request


class InterpretationRequest(BaseModel):
    mode: Literal['local','cloud'] = 'local'
    upload_consent: bool = False
    time: float | None = Field(default=None,ge=0)


def run_interpretation(job_id,identity,request):
    try:
        engines.data=DATA
        cache_identity=canonical(identity)
        with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(f'latest:{cache_identity}:{request.mode}',)).fetchone()
        if not row:raise RuntimeError('Zuerst den Song im ausgewählten Modus analysieren.')
        analysis=json.loads(row[0]);metadata=track(identity)
        if request.time is not None and request.time>=metadata['duration']:raise RuntimeError('Zeitpunkt liegt außerhalb des Songs.')
        selected=catalog.configuration(DATA)['active']['interpretation']
        key='interpretation:'+hashlib.sha256(('grounded-text-v2'+identity+json.dumps(analysis,sort_keys=True)+request.model_dump_json()+selected).encode()).hexdigest()
        with db() as conn:cached=conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached:result={**json.loads(cached[0]),'cached':True}
        else:
            with job_lock:jobs[job_id].update(message='Interpretiere Belege und Textkontext; erster Start kann Modell laden',progress=20)
            result=insights.interpretation(DATA,engines,analysis,metadata,request.time,request.mode)
            result['cached']=False
            with db() as conn:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(result)))
                own(conn,key,identity)
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Interpretation abgeschlossen',result=result)
    except Exception as exc:
        message=str(exc)[:800] if request.mode=='local' or isinstance(exc,cloud.CloudError) else 'API-Interpretation fehlgeschlagen; keine Ersatzwerte erzeugt.'
        with job_lock:jobs[job_id].update(status='error',message=message)


@app.post('/api/tracks/{identity}/interpret')
def interpret(identity: str,request: InterpretationRequest):
    track(identity)
    if request.mode=='cloud':
        if not request.upload_consent:raise HTTPException(422,'Text und Analysebelege werden an Google gesendet; Zustimmung fehlt.')
        try:cloud.credential()
        except cloud.CloudError as exc:raise HTTPException(422,str(exc)) from None
    return start_job('interpretation',run_interpretation,identity,request)


def run_details(job_id,identity):
    def progress(message,value):
        with job_lock:jobs[job_id].update(message=message,progress=value)
    try:
        engines.data=DATA
        version=catalog.configuration(DATA)['active']['audio']
        key=f'details:{identity}:{version}:v1'
        with db() as conn:cached=conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached:result={**json.loads(cached[0]),'cached':True}
        else:
            progress('Messe Tempo, Energie und spektrale Helligkeit',5)
            y,sr=sf.read(DATA/f'{identity}.wav',dtype='float32')
            if y.ndim==2:y=y.mean(axis=1)
            features=insights.acoustic_features(y,sr)
            progress('Vergleiche mögliche Instrumente in drei Audioausschnitten',30)
            instruments=engines.instruments(y,sr,progress)
            result={'features':features,'instruments':instruments,'cached':False,
                    'note':'Instrumente sind relative CLAP-Ähnlichkeiten, keine gesicherte Besetzung und keine kalibrierten Wahrscheinlichkeiten.'}
            with db() as conn:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(result)))
                own(conn,key,identity)
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Songdetails analysiert',result=result)
    except Exception:
        with job_lock:jobs[job_id].update(status='error',message='Songdetails konnten nicht analysiert werden. Lokales Audiomodell und Modelldownload prüfen.')


@app.post('/api/tracks/{identity}/details')
def details(identity: str):
    track(identity)
    return start_job('details',run_details,identity)


@app.get('/api/tracks/{identity}/analysis')
def stored_analysis(identity: str,mode: Literal['local','cloud']='local'):
    identity=canonical(identity)
    with db() as conn:
        row=conn.execute('SELECT result FROM cache WHERE key=?',(f'latest:{identity}:{mode}',)).fetchone()
        if not row:raise HTTPException(404,'Keine gespeicherte Analyse für diesen Modus.')
        result=json.loads(row[0])
        # Adopt identical legacy cache entries so deletion also clears old opaque keys.
        comparable={k:v for k,v in result.items() if k!='cached'}
        for key,raw in conn.execute('SELECT key,result FROM cache WHERE key NOT IN (SELECT key FROM cache_owner)').fetchall():
            try:value=json.loads(raw)
            except ValueError:continue
            if isinstance(value,dict) and {k:v for k,v in value.items() if k!='cached'}==comparable:own(conn,key,identity)
    active=catalog.configuration(DATA)['active']
    version=local_version(active) if mode=='local' else cloud.VERSION+cloud.MODEL
    return {**result,'cached':True,'stale':result.get('pipeline_version')!=version}


@app.get('/api/library')
def song_library():
    with db() as conn:
        rows=conn.execute('SELECT metadata FROM tracks ORDER BY rowid DESC').fetchall()
        keys={r[0] for r in conn.execute("SELECT key FROM cache WHERE key LIKE 'latest:%'")}
    output=[];seen=set()
    for raw, in rows:
        metadata=json.loads(raw);identity=canonical(metadata['id'])
        if identity in seen:continue
        seen.add(identity)
        output.append({**metadata,'analysis_modes':[mode for mode in ['local','cloud'] if f'latest:{identity}:{mode}' in keys]})
    return {'tracks':output}


@app.post('/api/tracks/{identity}/cache/delete')
def delete_analysis_cache(identity: str):
    identity=canonical(identity)
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        # First adopt legacy full-analysis entries matching saved latest results.
        for mode in ['local','cloud']:
            try:stored_analysis(identity,mode)
            except HTTPException:pass
        with db() as conn:
            keys=[r[0] for r in conn.execute('SELECT key FROM cache_owner WHERE track_id=?',(identity,))]
            keys += [r[0] for r in conn.execute('SELECT key FROM cache WHERE key LIKE ? OR key LIKE ? OR key LIKE ?',
                (f'audio:{identity}:%',f'latest:{identity}:%',f'details:{identity}:%'))]
            for key in set(keys):conn.execute('DELETE FROM cache WHERE key=?',(key,))
            conn.execute('DELETE FROM cache_owner WHERE track_id=?',(identity,))
    return {'deleted_cache_entries':len(set(keys)),'notes_preserved':True,'audio_preserved':True}


if (ROOT / 'dist').exists():
    from fastapi.staticfiles import StaticFiles
    app.mount('/', StaticFiles(directory=ROOT / 'dist', html=True), name='frontend')
