import hashlib
import json
import os
import sqlite3
import subprocess
import threading
import uuid
import tempfile
import re
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

from .core import parse_lrc, biggest_split,text_coverage
from .models import ROOT, engines, AUDIO_MODEL, LYRIC_MODEL, PIPELINE_VERSION
from . import cloud, links, catalog, insights, library, diagnostics, research, separation, providers,focus,language,audio_method,cancellation,prompt_presets,runtime_devices

DATA = Path(os.environ.get('MOODSCOPE_DATA', ROOT / 'data'))
DATA.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='MoodScope local analysis', version='0.3.0')
ORIGINS = ['http://127.0.0.1:1420', 'http://localhost:1420', 'tauri://localhost', 'http://tauri.localhost', 'https://tauri.localhost', 'http://127.0.0.1:8765']
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=['GET','POST'], allow_headers=['Content-Type','Accept-Language'])
executor = ThreadPoolExecutor(max_workers=1)
jobs = {}
job_lock = threading.RLock()
cancel_events = {}
SYSTEM_CONTROL=None
INSTANCE_ID=uuid.uuid4().hex


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Pydantic normally includes original input, which may contain a key.
    return JSONResponse(status_code=422,content={'detail':[
        {'loc':list(e['loc']),'msg':e['msg'],'type':e['type']} for e in exc.errors()]})


@app.exception_handler(Exception)
async def unexpected_error(request,exc):
    return JSONResponse(status_code=500,content={'detail':diagnostics.user_error(DATA,'http-request',exc,'Interner Fehler. Bitte Fehler-ID und ausgeführte Funktion melden.')})


@app.middleware('http')
async def local_only(request: Request, call_next):
    # Block browser cross-origin form writes and DNS rebinding to the loopback service.
    host = request.headers.get('host', '').split(':')[0]
    origin = request.headers.get('origin')
    same_origin=f'{request.url.scheme}://{request.headers.get("host","")}'
    if host not in {'127.0.0.1', 'localhost', 'testserver'} or (origin and origin not in ORIGINS and origin!=same_origin):
        return JSONResponse({'detail':'Untrusted local origin'}, status_code=403)
    result=await call_next(request)
    locale=language.language(request.headers.get('accept-language'))
    if locale=='en' and result.headers.get('content-type','').startswith('application/json'):
        raw=b''.join([chunk async for chunk in result.body_iterator])
        value=json.loads(raw)
        # Profile names, musical metadata and personal notes must remain verbatim.
        if result.status_code>=400 or not request.url.path.endswith('/notes'):
            value=language.response(value,locale)
        headers={k:v for k,v in result.headers.items() if k.lower() not in {'content-length','content-type'}}
        headers['Content-Language']=locale
        return JSONResponse(value,status_code=result.status_code,headers=headers,background=result.background)
    result.headers['Content-Language']=locale
    return result


@contextmanager
def db():
    conn = sqlite3.connect(DATA / 'cache.sqlite3', timeout=30)
    conn.execute('CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, metadata TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, result TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS cache_owner (key TEXT PRIMARY KEY, track_id TEXT NOT NULL)')
    try:
        with conn:
            cancellation.check()
            yield conn
            cancellation.check()
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
    from importlib.metadata import version
    runtime={name:version(name) for name in ['torch','transformers','librosa']}
    return PIPELINE_VERSION+prompt_presets.fingerprint(DATA,['audio'])+json.dumps({k:active[k] for k in ['audio','lyrics','whisper']},sort_keys=True)+json.dumps(runtime,sort_keys=True)


@app.get('/api/health')
def health(purpose:Literal['audio','lyrics','whisper','interpretation','separation']='audio'):
    from scripts.runtime import environment_id
    device=engines.device() if purpose=='audio' else engines.device(purpose)
    name=next((d['name'] for d in runtime_devices.available() if d['id']==('cuda:0' if device=='cuda' else device)),device)
    return {'status':'ok','device_name':name,'api_model':cloud.MODEL, 'version':'0.3.0','api_revision':10,'runtime_id':environment_id(),'instance_id':INSTANCE_ID,'system_control':SYSTEM_CONTROL is not None, 'device':device,
            'audio_model':AUDIO_MODEL, 'lyric_model':LYRIC_MODEL}


@app.get('/api/settings')
def get_settings():
    return {'cloud':cloud.settings(),'local_default':True,'link_import_available':bool(
        (ROOT/'.tools'/'yt-dlp'/('yt-dlp.exe' if os.name=='nt' else 'yt-dlp_linux')).exists())}


class CloudSettings(BaseModel):
    api_key: SecretStr = Field(default=SecretStr(''),max_length=300)
    free_project_confirmed: bool = False


class SystemAction(BaseModel):
    action:Literal['restart','stop']
    force:bool=False


@app.post('/api/system')
def system_action(request:SystemAction):
    if SYSTEM_CONTROL is None:raise HTTPException(409,'Diesen Dienst über Start-MoodScope.cmd oder python -m scripts.service starten, um Neustart und Beenden in der App zu verwenden.')
    with job_lock:
        running=any(j['status']=='running' for j in jobs.values())
        if running and not request.force:raise HTTPException(409,'Ein Auftrag läuft. Für Abbruch Neustart/Beenden ausdrücklich bestätigen.')
        diagnostics.event(DATA,'system',f'action={request.action} force={request.force} running={running}')
        SYSTEM_CONTROL(request.action,request.force and running)
    return {'accepted':True,'action':request.action}


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
    metadata['tags']={}
    for key in ['album','date','genre','composer','performer','tracknumber','discnumber','copyright','organization']:
        value=supplied.get(key) or (tags.get(key,[''])[0] if tags else '')
        if value:metadata['tags'][key]=str(value)[:1000]
    if supplied.get('source_url'):metadata['source_url']=supplied['source_url']
    if supplied.get('uploader'):metadata['uploader']=str(supplied['uploader'])[:200]
    original_info=getattr(tags,'info',None)
    metadata['original']={'format':Path(source).suffix.lstrip('.').upper(),
        'sample_rate':getattr(original_info,'sample_rate',None),'channels':getattr(original_info,'channels',None),
        'bitrate':getattr(original_info,'bitrate',None),'bits_per_sample':getattr(original_info,'bits_per_sample',None)}
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
    force_transcription:bool=False
    transcription_quality:Literal['standard','precise']='standard'
    transcription_source:Literal['auto','mix','vocals']='auto'
    transcription_language:str | None=Field(default=None,pattern=r'^[a-z]{2,3}$')
    audio_resolution:Literal[2,5]=5


def start_job(kind, function, *args):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):
            raise HTTPException(409,'Ein Auftrag läuft bereits. Bitte warten.')
        for identity in list(jobs):
            if len(jobs)<32: break
            if jobs[identity]['status']!='running': jobs.pop(identity)
        job_id=uuid.uuid4().hex
        jobs[job_id]={'kind':kind,'status':'running','progress':0,'message':'Auftrag wird vorbereitet'}
        cancel_events[job_id]=threading.Event()
    diagnostics.event(DATA,kind,'queued job='+job_id)
    executor.submit(execute_job,kind,function,job_id,args)
    return {'job_id':job_id}


def execute_job(kind,function,job_id,args):
    import time
    started=time.monotonic()
    try:
        with cancellation.scope(cancel_events[job_id]):function(job_id,*args)
    except cancellation.Cancelled:
        with job_lock:jobs[job_id].update(status='cancelled',message='Auftrag abgebrochen.',result=None)
    except Exception as exc:
        with job_lock:jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,kind,exc,'Auftrag fehlgeschlagen.'))
    finally:
        with job_lock:
            cancel_events.pop(job_id,None)
            job=jobs.get(job_id,{})
            state=job.get('status','unknown');result=job.get('result') or {}
        diagnostics.event(DATA,kind,f'job={job_id} status={state} elapsed_seconds={time.monotonic()-started:.2f} cached={result.get("cached",False)} audio_segments={len(result.get("audio",[]))} lyric_segments={len(result.get("lyrics",[]))}')


class LinkRequest(BaseModel):
    url: str = Field(min_length=10,max_length=2000)


@app.post('/api/links/search')
def link_search(request:LinkRequest):
    try:return links.search_soundcloud(request.url)
    except ValueError as exc:raise HTTPException(422,str(exc)) from None
    except Exception as exc:raise HTTPException(502,diagnostics.user_error(DATA,'soundcloud-search',exc,'SoundCloud-Suche fehlgeschlagen. Direkten Einzeltrack-Link verwenden.')) from None


def run_link_job(job_id,url):
    def progress(message,value):
        cancellation.check()
        with job_lock: jobs[job_id].update(message=message,progress=value)
    try:
        with tempfile.TemporaryDirectory(prefix='link-',dir=DATA) as directory:
            source,metadata=links.download(url,directory,progress)
            progress('Dekodiere Song für synchronisierte Wiedergabe',80)
            result=import_path(source,metadata['title'],metadata)
        with job_lock: jobs[job_id].update(status='done',progress=100,message='Link importiert',result=result)
    except Exception as exc:
        with job_lock: jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'link-import',exc,'Linkimport fehlgeschlagen: Plattform nicht erreichbar, Download gesperrt oder kein unterstützter Einzeltrack. Lokalen Import verwenden.'))


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
        cancellation.check()
        with job_lock:
            jobs[job_id].update(message=message, progress=value)
    try:
        engines.data=DATA
        metadata = track(identity)
        cache_identity=canonical(identity)
        active=catalog.configuration(DATA)['active']
        version=local_version(active) if request.mode=='local' else cloud.VERSION+cloud.MODEL
        key = hashlib.sha256((cache_identity + version + json.dumps(request.model_dump(exclude={'force','force_transcription','upload_consent'}),sort_keys=True)).encode()).hexdigest()
        with db() as conn:
            cached = conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached and not request.force and not request.force_transcription:
            result = {**json.loads(cached[0]), 'cached':True}
        else:
            lines = parse_lrc(request.lyrics, metadata['duration'])
            lyric_source='lrc' if lines else 'plain-text' if request.lyrics.strip() else 'none'
            warnings = []
            if request.lyrics.strip() and not lines:
                warnings.append('Text ohne LRC-Zeitstempel: keine synchronisierte Textkurve. Bitte LRC importieren oder Whisper aktivieren.')
            if not lines and request.whisper and request.mode=='local':
                vocal_candidates=[separation.folder(DATA,identity,name)/'vocals.wav' for name in ['htdemucs_auto','htdemucs_ft','htdemucs','htdemucs_6s']]
                vocal_file=next((p for p in vocal_candidates if p.exists()),vocal_candidates[0])
                if request.transcription_source=='vocals' and not vocal_file.exists():
                    separation.separate(DATA,identity,'htdemucs_auto',engines,progress)
                input_file=vocal_file if request.transcription_source!='mix' and vocal_file.exists() else DATA / f'{identity}.wav'
                if request.transcription_quality=='standard' and not request.transcription_language:
                    lines=engines.transcribe(input_file,progress)
                else:lines=engines.transcribe(input_file,progress,request.transcription_quality,request.transcription_language)
                lyric_source='whisper' if lines else 'none'
                warnings.append('Whisper-Zeitstempel und Gesangserkennung können ungenau sein.')
            if request.mode=='cloud' and request.whisper:
                warnings.append('Im API-Modus wird kein lokales Whisper gestartet. Für Textkurve synchronisierte LRC-Lyrics verwenden.')
            audio_version=PIPELINE_VERSION+prompt_presets.fingerprint(DATA,['audio'])+':audio-model:'+active['audio'] if request.mode=='local' else cloud.VERSION+cloud.MODEL
            audio_key = f'audio:{cache_identity}:{audio_version}:resolution{request.audio_resolution}'
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
                analyzer=engines.audio if request.mode=='local' else cloud.audio_mood
                a=analyzer(y,sr,progress) if request.audio_resolution==5 else analyzer(y,sr,progress,request.audio_resolution)
                if request.mode=='local':a=audio_method.musical_projection(a,summary)
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
                      'lyrics_source':lyric_source,
                      'audio_resolution':request.audio_resolution,
                      'text_coverage':text_coverage(l,metadata['duration']),
                      'models':{'audio':catalog.entries(DATA)[active['audio']]['repo'] if request.mode=='local' else cloud.MODEL,
                                'lyrics':catalog.entries(DATA)[active['lyrics']]['repo'] if request.mode=='local' else cloud.MODEL},
                      'method':'CLAP Prompt-Ensemble und XLM-EMO mit Textkontext' if request.mode=='local' else 'Gemini: getrennte Audio- und Textanalyse; subjektive unkalibrierte Valenz.'}
            if request.mode=='local':result['audio_method']=audio_method.describe_musical(result['models']['audio'],request.audio_resolution,DATA)
            else:result=audio_method.with_method(result)
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
            jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'analysis',exc,diagnostics.sanitize(message)))


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
        value=dict(jobs[job_id])
        if isinstance(value.get('result'),dict) and 'audio' in value['result']:value['result']=audio_method.with_method(value['result'])
        return value


@app.post('/api/jobs/{job_id}/cancel')
def cancel_job(job_id:str):
    with job_lock:
        if job_id not in jobs:raise HTTPException(404,'Analyseauftrag nicht gefunden')
        value=jobs[job_id]
        if value['status']=='running' and job_id in cancel_events:
            cancel_events[job_id].set()
            value.update(cancel_requested=True,message='Abbruch angefordert. Aktueller Rechenschritt wird sicher beendet.')
        return {'status':value['status'],'cancel_requested':value.get('cancel_requested',False)}


@app.get('/api/models')
def models():return catalog.status(DATA)


@app.get('/api/prompts')
def prompt_settings():return prompt_presets.status(DATA)


class PromptChange(BaseModel):
    action:Literal['save','select','delete']
    purpose:Literal['audio','instruments','whole_de','whole_en','line_de','line_en']
    preset_id:str | None=Field(default=None,max_length=64)
    name:str=Field(default='',max_length=80)
    content:str=Field(default='',max_length=6000)


@app.post('/api/prompts')
def update_prompts(request:PromptChange):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        try:return prompt_presets.change(DATA,request.action,request.purpose,request.preset_id,request.name,request.content)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None


@app.get('/api/devices')
def device_settings():return {'devices':runtime_devices.available(),'active':runtime_devices.configuration(DATA)}


class DeviceChoices(BaseModel):
    audio:str=Field(max_length=20)
    lyrics:str=Field(max_length=20)
    whisper:str=Field(max_length=20)
    interpretation:str=Field(max_length=20)
    separation:str=Field(max_length=20)


@app.post('/api/devices')
def update_devices(request:DeviceChoices):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        try:runtime_devices.save(DATA,request.model_dump())
        except ValueError as exc:raise HTTPException(422,str(exc)) from None
        catalog.unload_models(engines);engines.data=DATA
        return device_settings()


class ModelChoice(BaseModel):
    model_id: str = Field(max_length=80)


class CustomModel(BaseModel):
    url:str=Field(min_length=20,max_length=500)
    purpose:Literal['audio','lyrics','interpretation','whisper']


@app.post('/api/models/custom')
def add_custom_model(request:CustomModel):
    from . import custom_models
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        try:custom_models.add(DATA,request.url,request.purpose)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None
        except Exception as exc:raise HTTPException(502,diagnostics.user_error(DATA,'model-register',exc,'Modellseite konnte nicht geprüft werden. Öffentliches Repository und Verbindung prüfen.')) from None
    return catalog.status(DATA)


@app.post('/api/models/delete')
def delete_model(request:ModelChoice):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        catalog.unload_models(engines)
        try:return catalog.remove(DATA,request.model_id)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None
        except Exception as exc:raise HTTPException(500,diagnostics.user_error(DATA,'model-delete',exc,'Modelldateien konnten nicht vollständig gelöscht werden. App neu starten und erneut versuchen.')) from None


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
        cancellation.check()
        with job_lock:jobs[job_id].update(message=message,progress=value)
    try:
        result=catalog.download(DATA,key,progress)
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Modell heruntergeladen',result=result)
    except Exception as exc:
        with job_lock:jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'model-download',exc,'Modelldownload fehlgeschlagen. Netzwerk, freien Speicher und Offline-Einstellung prüfen.'))


@app.post('/api/models/download')
def download_model(request: ModelChoice):
    if request.model_id not in catalog.entries(DATA):raise HTTPException(422,'Nicht unterstütztes Modell')
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
    force: bool = False
    provider_id: str | None = Field(default=None,max_length=64)
    language: Literal['de','en'] = 'de'


def run_interpretation(job_id,identity,request):
    try:
        engines.data=DATA
        cache_identity=canonical(identity);identity=cache_identity
        with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(f'latest:{cache_identity}:{request.mode}',)).fetchone()
        if not row:raise RuntimeError('Zuerst den Song im ausgewählten Modus analysieren.')
        analysis=json.loads(row[0]);metadata=track(identity)
        if request.time is not None and request.time>=metadata['duration']:raise RuntimeError('Zeitpunkt liegt außerhalb des Songs.')
        selected=json.dumps(providers.profile(DATA,request.provider_id),sort_keys=True) if request.provider_id else catalog.configuration(DATA)['active']['interpretation']
        # Add measured instrument hints when available, keeping them out of the text-only LLM prompt.
        with db() as conn:
            detail=conn.execute('SELECT result FROM cache WHERE key=?',(f'details:{identity}:{catalog.configuration(DATA)["active"]["audio"]}:v4-harmony-prompts:{prompt_presets.fingerprint(DATA,["instruments"])}',)).fetchone()
        if detail:analysis['instruments']=json.loads(detail[0]).get('instruments',[])
        with db() as conn:research_row=conn.execute('SELECT result FROM cache WHERE key=?',(f'research-selected:{cache_identity}',)).fetchone()
        research_facts=json.loads(research_row[0]) if research_row else None
        research_basis=hashlib.sha256(json.dumps(research_facts,sort_keys=True).encode()).hexdigest()
        prompt_basis=prompt_presets.fingerprint(DATA,[('whole_' if request.time is None else 'line_')+request.language])
        key='interpretation:'+hashlib.sha256(('whole-song-v10-prompt'+prompt_basis+research_basis+cache_identity+insights.analysis_basis(analysis)+json.dumps(analysis.get('instruments',[]),sort_keys=True)+json.dumps(request.model_dump(exclude={'force','upload_consent'}),sort_keys=True)+selected).encode()).hexdigest()
        with db() as conn:cached=conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached and not request.force:result={**json.loads(cached[0]),'cached':True}
        else:
            with job_lock:jobs[job_id].update(message='Interpretiere Belege und Textkontext; erster Start kann Modell laden',progress=20)
            result=insights.interpretation(DATA,engines,analysis,metadata,request.time,request.mode,request.provider_id,request.language)
            result['cached']=False
            result['text_evidence']=[{'start':r['start'],'end':r['end'],'text':r.get('text','')} for r in analysis.get('lyrics',[]) if request.time is None or r['start']<=request.time<r['end']]
            result['online_evidence']={k:v for k,v in research_facts.items() if k in {'source','url','title','musical_facts'}} if research_facts else None
            result['research_basis']=research_basis
            result['language']=request.language
            result['analysis_basis']=insights.analysis_basis(analysis)
            result['model_basis']=selected
            result['prompt_basis']=prompt_basis
            result['saved_with_song']=True
            result['source_warning']='Diese Deutung basiert auf automatisch erkannten Wörtern. Whisper kann Wörter verwechseln; bitte den Text im Verlauf prüfen und gegebenenfalls korrigieren.' if analysis.get('lyrics_source')=='whisper' else 'Auch diese Deutung ist eine mögliche Lesart. Die Textquelle und konkrete Belege selbst prüfen.'
            result['source_warning']=language.translate(result['source_warning'],request.language)
            with db() as conn:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(result)))
                own(conn,key,identity)
        latest_key=f'interpretation-latest:{cache_identity}:{request.mode}:{request.provider_id or "default"}:{request.language}'
        scoped_key=latest_key+(':whole' if request.time is None else ':position')
        with db() as conn:
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(latest_key,json.dumps(result)))
            own(conn,latest_key,identity)
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(scoped_key,json.dumps(result)))
            own(conn,scoped_key,identity)
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Interpretation abgeschlossen',result=result)
    except Exception as exc:
        message=str(exc)[:800] if request.mode=='local' or isinstance(exc,cloud.CloudError) else 'API-Interpretation fehlgeschlagen; keine Ersatzwerte erzeugt.'
        with job_lock:jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'interpretation',exc,diagnostics.sanitize(message)))


@app.post('/api/tracks/{identity}/interpret')
def interpret(identity: str,request: InterpretationRequest):
    track(identity)
    if request.provider_id:
        if not request.upload_consent:raise HTTPException(422,'Zustimmung zum Textversand an den gewählten Server fehlt.')
        try:providers.profile(DATA,request.provider_id)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None
    elif request.mode=='cloud':
        if not request.upload_consent:raise HTTPException(422,'Text und Analysebelege werden an Google gesendet; Zustimmung fehlt.')
        try:cloud.credential()
        except cloud.CloudError as exc:raise HTTPException(422,str(exc)) from None
    return start_job('interpretation',run_interpretation,identity,request)


@app.get('/api/tracks/{identity}/interpretation')
def saved_interpretation(identity:str,mode:Literal['local','cloud']='local',provider_id:str | None=None,language:Literal['de','en']='de',scope:Literal['whole','position']='whole'):
    identity=canonical(identity)
    key=f'interpretation-latest:{identity}:{mode}:{provider_id or "default"}:{language}'
    with db() as conn:
        row=conn.execute('SELECT result FROM cache WHERE key=?',(key+':'+scope,)).fetchone()
        if not row:
            legacy=conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
            if legacy and ((json.loads(legacy[0]).get('time') is None)==(scope=='whole')):row=legacy
    if not row and language=='de':
        with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(key.rsplit(':',1)[0],)).fetchone()
    if not row:raise HTTPException(404,'Noch keine gespeicherte Deutung für dieses Modellprofil.')
    value=json.loads(row[0])
    with db() as conn:analysis=conn.execute('SELECT result FROM cache WHERE key=?',(f'latest:{identity}:{mode}',)).fetchone()
    stale=value.get('prompt_basis') not in {None,prompt_presets.fingerprint(DATA,[('whole_' if value.get('time') is None else 'line_')+language])}
    stale=stale or not analysis or value.get('analysis_basis')!=insights.analysis_basis(json.loads(analysis[0]))
    with db() as conn:research_row=conn.execute('SELECT result FROM cache WHERE key=?',(f'research-selected:{identity}',)).fetchone()
    current_research=json.loads(research_row[0]) if research_row else None
    research_basis=hashlib.sha256(json.dumps(current_research,sort_keys=True).encode()).hexdigest()
    stale=stale or (value.get('research_basis') is not None and value['research_basis']!=research_basis)
    try:
        selected=json.dumps(providers.profile(DATA,provider_id),sort_keys=True) if provider_id else catalog.configuration(DATA)['active']['interpretation']
        stale=stale or (value.get('model_basis') is not None and value['model_basis']!=selected)
    except ValueError:stale=True
    return {**value,'cached':True,'stale':stale}


def run_details(job_id,identity):
    def progress(message,value):
        cancellation.check()
        with job_lock:jobs[job_id].update(message=message,progress=value)
    try:
        engines.data=DATA
        version=catalog.configuration(DATA)['active']['audio']
        key=f'details:{identity}:{version}:v4-harmony-prompts:{prompt_presets.fingerprint(DATA,["instruments"])}'
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
    except Exception as exc:
        with job_lock:jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'details',exc,'Songdetails konnten nicht analysiert werden. Lokales Audiomodell und Modelldownload prüfen.'))


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
    return {**audio_method.with_method(result),'cached':True,'stale':result.get('pipeline_version')!=version}


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


@app.post('/api/tracks/{identity}/delete')
def delete_song(identity:str):
    import shutil
    import re
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        root_identity=canonical(identity)
        with db() as conn:ids=[r[0] for r in conn.execute('SELECT id FROM tracks').fetchall()]
        family=[i for i in ids if canonical(i)==root_identity]
        if any(not re.fullmatch(r'[a-f0-9]{64}',i) for i in family):raise HTTPException(409,'Ungültige gespeicherte Song-ID; keine Dateien gelöscht.')
        # Quarantine only generated files inside DATA; original imported files are never touched.
        quarantine=DATA/('delete-'+uuid.uuid4().hex);quarantine.mkdir()
        moved=[]
        try:
            for song_id in family:
                for path in [DATA/(song_id+'.wav'),DATA/'stems'/song_id]:
                    if path.exists():
                        destination=quarantine/(song_id+('-stems' if path.is_dir() else '.wav'))
                        path.rename(destination);moved.append((path,destination))
            with db() as conn:
                keys=[r[0] for r in conn.execute('SELECT key FROM cache_owner WHERE track_id=?',(root_identity,)).fetchall()]
                for song_id in family:
                    keys.extend(r[0] for r in conn.execute('SELECT key FROM cache WHERE key LIKE ? OR key LIKE ? OR key LIKE ? OR key LIKE ? OR key LIKE ? OR key LIKE ?',
                        (f'audio:{song_id}:%',f'latest:{song_id}:%',f'details:{song_id}:%',f'notes:{song_id}',f'fingerprint:{song_id}',f'research-selected:{song_id}')))
                for key in set(keys):conn.execute('DELETE FROM cache WHERE key=?',(key,))
                conn.execute('DELETE FROM cache_owner WHERE track_id=?',(root_identity,))
                for song_id in family:conn.execute('DELETE FROM tracks WHERE id=?',(song_id,))
        except Exception as exc:
            for original,temporary in reversed(moved):
                if temporary.exists():temporary.rename(original)
            raise HTTPException(409,diagnostics.user_error(DATA,'delete-song',exc,'Song konnte nicht entfernt werden. Wiedergabe stoppen und erneut versuchen.')) from None
        if quarantine.resolve().parent!=DATA.resolve():raise RuntimeError('Löschpfad liegt außerhalb des Datenordners.')
        try:shutil.rmtree(quarantine)
        except OSError as exc:
            diagnostics.failure(DATA,'delete-song-cleanup',exc)
            return {'deleted':True,'removed_ids':family,'warning':'Bibliothekseintrag entfernt, temporäre Löschdateien sind noch gesperrt. Lokales Protokoll prüfen.'}
    return {'deleted':True,'removed_ids':family,'removed_import_variants':len(family),'original_source_preserved':True}


@app.post('/api/library/delete')
def delete_library():
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        with db() as conn:identities=[r[0] for r in conn.execute('SELECT id FROM tracks').fetchall()]
        roots=list(dict.fromkeys(canonical(i) for i in identities))
        warnings=[]
        for identity in roots:
            result=delete_song(identity)
            if result.get('warning'):warnings.append(result['warning'])
        with db() as conn:
            conn.execute('DELETE FROM cache');conn.execute('DELETE FROM cache_owner')
    return {'deleted':True,'removed_songs':len(roots),'warnings':warnings,'original_sources_preserved':True}


class SeparationRequest(BaseModel):
    model: Literal['htdemucs','htdemucs_6s','htdemucs_ft','htdemucs_auto']='htdemucs'


def run_separation(job_id,identity,request):
    def progress(message,value):
        cancellation.check()
        with job_lock:jobs[job_id].update(message=message,progress=value)
    try:
        result=separation.separate(DATA,identity,request.model,engines,progress)
        result={**stem_status(identity,request.model),'cached':result.get('cached',False)}
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Quellen getrennt',result=result)
    except Exception as exc:
        message='Quellentrennung fehlgeschlagen. Modell, freien Speicher und optionale Demucs-Installation prüfen.'
        if isinstance(exc,ImportError):message='Demucs fehlt. Projektlokal backend/requirements-separation.txt installieren.'
        with job_lock:jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'separation',exc,message))


@app.post('/api/tracks/{identity}/separate')
def separate_track(identity:str,request:SeparationRequest):
    track(identity)
    return start_job('separation',run_separation,identity,request)


@app.get('/api/tracks/{identity}/stems')
def stem_status(identity:str,model:Literal['htdemucs','htdemucs_6s','htdemucs_ft','htdemucs_auto']='htdemucs'):
    track(identity)
    info=separation.status(DATA,identity,model)
    with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(f'stem-visibility:{identity}:{model}',)).fetchone()
    visibility=json.loads(row[0]) if row else {}
    if isinstance(visibility,list):visibility={'hidden':visibility}
    return {**info,'hidden_sources':visibility.get('hidden',[]),'shown_sources':visibility.get('shown',[])}


class StemVisibility(BaseModel):
    model:Literal['htdemucs','htdemucs_6s','htdemucs_ft','htdemucs_auto']='htdemucs'
    hidden:list[Literal['vocals','drums','bass','other','guitar','piano']]=Field(default_factory=list,max_length=6)
    shown:list[Literal['vocals','drums','bass','other','guitar','piano']]=Field(default_factory=list,max_length=6)


@app.post('/api/tracks/{identity}/stems/visibility')
def save_stem_visibility(identity:str,request:StemVisibility):
    track(identity)
    if set(request.hidden)&set(request.shown):raise HTTPException(422,'Eine Spur kann nicht zugleich ausgeblendet und eingeblendet sein.')
    key=f'stem-visibility:{identity}:{request.model}'
    with db() as conn:
        conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps({'hidden':request.hidden,'shown':request.shown})));own(conn,key,identity)
    return stem_status(identity,request.model)


@app.get('/api/tracks/{identity}/mix')
def stem_mix(identity:str,sources:str,model:Literal['htdemucs','htdemucs_6s','htdemucs_ft','htdemucs_auto']='htdemucs',gains:str | None=None,download:bool=False):
    metadata=track(identity)
    try:
        if len(sources)>80 or (gains is not None and len(gains)>100):raise ValueError('Ungültiger Quellenmix')
        weights=[float(v) for v in gains.split(',')] if gains is not None else None
        path=separation.mix(DATA,identity,model,sources.split(','),weights)
    except ValueError as exc:raise HTTPException(422,str(exc)) from None
    title=metadata.get('title') or Path(metadata['name']).stem
    safe=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',title+' - '+sources.replace(',', ' + ')).strip()[:160]
    name=(safe or 'MoodScope-Mix')+'.wav' if download else None
    return FileResponse(path,media_type='audio/wav',filename=name)


class FocusRequest(BaseModel):
    source:Literal['original','vocals','drums','bass','other','guitar','piano']='vocals'
    model:Literal['htdemucs','htdemucs_6s','htdemucs_ft','htdemucs_auto']='htdemucs'
    stereo:Literal['stereo','left','right','center','sides']='stereo'
    start:float=Field(default=0,ge=0,le=1800)
    end:float | None=Field(default=None,gt=0,le=1800)
    low_hz:float=Field(default=80,ge=20,le=10000)
    high_hz:float=Field(default=10000,ge=50,le=22000)
    gain_db:float=Field(default=0,ge=-12,le=12)


def run_focus(job_id,identity,request):
    try:
        with job_lock:jobs[job_id].update(progress=15,message='Filtere gewählte Quelle, Stereoposition und Frequenzband lokal')
        key=focus.render(DATA,identity,request.model_dump())
        result={'focus_id':key,'url':f'/api/tracks/{identity}/focus/{key}',
            'note':'Manueller EQ-/Stereo-Fokus; keine KI-Trennung einzelner Sänger. Überlagerte Stimmen können im selben Frequenz- und Stereobereich bleiben.'}
        with job_lock:jobs[job_id].update(status='done',progress=100,message='Manueller Stimmenfokus vorbereitet',result=result)
    except Exception as exc:
        with job_lock:jobs[job_id].update(status='error',message=diagnostics.user_error(DATA,'focus',exc,diagnostics.sanitize(str(exc))))


@app.post('/api/tracks/{identity}/focus')
def manual_focus(identity:str,request:FocusRequest):
    track(identity)
    return start_job('focus',run_focus,identity,request)


@app.get('/api/tracks/{identity}/focus/{key}')
def focused_audio(identity:str,key:str):
    import re
    track(identity)
    if not re.fullmatch(r'[a-f0-9]{64}',key):raise HTTPException(422,'Ungültige Fokus-ID')
    path=DATA/'stems'/identity/'focus'/(key+'.wav')
    if not path.exists():raise HTTPException(404,'Fokusdatei fehlt; Filter erneut anwenden.')
    return FileResponse(path,media_type='audio/wav')


class ResearchQuery(BaseModel):
    artist:str=Field(default='',max_length=200)
    title:str=Field(min_length=1,max_length=200)
    force:bool=False
    auto_match:bool=False


@app.post('/api/tracks/{identity}/research')
def research_search(identity:str,query:ResearchQuery):
    metadata=track(identity);identity=canonical(identity)
    key='research-search-v5:'+identity+':'+hashlib.sha256(json.dumps([query.artist,query.title,metadata['duration'],query.auto_match]).encode()).hexdigest()
    try:
        with db() as conn:cached=conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached and not query.force:return {**json.loads(cached[0]),'cached':True}
        result=research.search(query.artist,query.title)
        if query.force:
            with db() as conn:conn.execute('DELETE FROM cache WHERE key=?',(f'research-selected:{identity}',))
        result['candidates']=research.ranked_candidates(result['candidates'],query.artist,query.title,metadata['duration'])
        if query.auto_match:
            matches=[r for r in result['candidates'] if r['auto_eligible']]
            best=None;best_count=-1;trials=[]
            for candidate in matches[:3]:
                try:
                    detail=research_recording(identity,candidate['id'],force=query.force)
                    count=research.recording_credit_count(detail)
                    trials.append({'id':candidate['id'],'source':candidate.get('source'),'duration_delta':candidate['duration_delta'],'recording_instrument_credits':count,'status':'found'})
                    if count>best_count:best,best_count=candidate,count
                    if count:break
                except HTTPException:trials.append({'id':candidate['id'],'status':'unavailable'})
            result['selection_attempts']=trials
            if best:
                result['matched']=research_recording(identity,best['id'])
                result['auto_selection']={'id':best['id'],'duration_delta':best['duration_delta'],'method':'matching artist/title/version and closest duration; up to three compatible credit fallbacks'}
            elif matches:result['details_unavailable']=True
        with db() as conn:
            for cache_key in [key,f'research-results:{identity}']:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(cache_key,json.dumps(result)));own(conn,cache_key,identity)
        return result
    except Exception as exc:
        failure={'candidates':[],'attempts':[{'source':name,'status':'unavailable'} for name in ['MusicBrainz','Apple iTunes','Deezer']],
            'note':'Die automatische Recherche war nicht erreichbar. Vorhandene Angaben wurden nicht aktualisiert. Verbindung prüfen und erneut recherchieren.','failed':True}
        with db() as conn:
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(f'research-results:{identity}',json.dumps(failure)));own(conn,f'research-results:{identity}',identity)
        raise HTTPException(502,diagnostics.user_error(DATA,'research-search',exc,'Katalogrecherche nicht erreichbar; gespeicherte Analysen bleiben verfügbar.')) from None


@app.post('/api/tracks/{identity}/research/{recording}')
def research_recording(identity:str,recording:str,force:bool=False):
    identity=canonical(identity)
    import re
    if not re.fullmatch(r'(?:[0-9a-fA-F-]{36}|(?:itunes|deezer):[0-9]{1,20})',recording):raise HTTPException(422,'Ungültige Aufnahme-ID')
    key='research-recording:'+identity+':'+recording
    try:
        with db() as conn:cached=conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        result=json.loads(cached[0]) if cached and not force else research.details(recording)
        with db() as conn:
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(result)))
            conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(f'research-selected:{identity}',json.dumps(result)))
            own(conn,key,identity);own(conn,f'research-selected:{identity}',identity)
        return result
    except Exception as exc:raise HTTPException(502,diagnostics.user_error(DATA,'research-details',exc,'Aufnahmedetails konnten nicht geladen werden.')) from None


@app.get('/api/tracks/{identity}/research')
def saved_research(identity:str):
    identity=canonical(identity)
    with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(f'research-selected:{identity}',)).fetchone()
    return json.loads(row[0]) if row else None


@app.get('/api/tracks/{identity}/research/candidates')
def saved_research_candidates(identity:str):
    identity=canonical(identity)
    with db() as conn:row=conn.execute('SELECT result FROM cache WHERE key=?',(f'research-results:{identity}',)).fetchone()
    return json.loads(row[0]) if row else None


class ProviderSettings(BaseModel):
    id:str | None=Field(default=None,max_length=64,pattern=r'^[a-f0-9]+$')
    name:str=Field(min_length=1,max_length=100)
    protocol:Literal['openai','anthropic','gemini']='openai'
    base_url:str=Field(min_length=8,max_length=500)
    model:str=Field(min_length=1,max_length=120)
    api_key:SecretStr=Field(default=SecretStr(''),max_length=500)
    free_project_confirmed:bool=False


@app.get('/api/providers')
def provider_status():return providers.status(DATA)


@app.post('/api/providers')
def provider_save(request:ProviderSettings):
    try:return providers.save(DATA,{**request.model_dump(exclude={'api_key'}),'api_key':request.api_key.get_secret_value()})
    except ValueError as exc:raise HTTPException(422,str(exc)) from None


@app.post('/api/providers/{identity}/remove')
def provider_remove(identity:str):
    providers.remove(DATA,identity)
    return providers.status(DATA)


@app.post('/api/providers/{identity}/audio')
def audio_provider(identity:str):
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'Erst laufenden Auftrag beenden lassen.')
        try:return providers.activate_audio(DATA,identity)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None


@app.get('/api/diagnostics')
def diagnostics_status():
    import sys
    from importlib.metadata import version,PackageNotFoundError
    versions={}
    for name in ['torch','transformers','faster-whisper','demucs','librosa','fastapi']:
        try:versions[name]=version(name)
        except PackageNotFoundError:versions[name]='nicht installiert'
    path=DATA/'logs'/'moodscope.log'
    return {'version':'0.3.0','device':engines.device(),'python':sys.version.split()[0],'packages':versions,'log_file':'data/logs/moodscope.log',
        'recent':path.read_text(encoding='utf-8').splitlines()[-40:] if path.exists() else [],
        'note':'Rotierende lokale Fehlerprotokolle: bis zu vier Dateien à 2 MB. Keine Lyrics, Audiodaten oder API-Schlüssel. Fehler-ID ordnet App-Meldung und Codeposition zu.'}


if (ROOT / 'dist').exists():
    from fastapi.staticfiles import StaticFiles
    app.mount('/', StaticFiles(directory=ROOT / 'dist', html=True), name='frontend')
