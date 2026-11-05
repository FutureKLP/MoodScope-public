import hashlib
import json
import os
import sqlite3
import subprocess
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from .core import parse_lrc, biggest_split
from .models import ROOT, engines, AUDIO_MODEL, LYRIC_MODEL, PIPELINE_VERSION

DATA = Path(os.environ.get('MOODSCOPE_DATA', ROOT / 'data'))
DATA.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='MoodScope local analysis', version='0.1.0')
ORIGINS = ['http://127.0.0.1:1420', 'http://localhost:1420', 'tauri://localhost', 'http://tauri.localhost', 'https://tauri.localhost', 'http://127.0.0.1:8765']
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=['GET','POST'], allow_headers=['Content-Type'])
executor = ThreadPoolExecutor(max_workers=1)
jobs = {}
job_lock = threading.Lock()


@app.middleware('http')
async def local_only(request: Request, call_next):
    # Block browser cross-origin form writes and DNS rebinding to the loopback service.
    host = request.headers.get('host', '').split(':')[0]
    origin = request.headers.get('origin')
    if host not in {'127.0.0.1', 'localhost', 'testserver'} or (origin and origin not in ORIGINS):
        return JSONResponse({'detail':'Untrusted local origin'}, status_code=403)
    return await call_next(request)


def db():
    conn = sqlite3.connect(DATA / 'cache.sqlite3', timeout=30)
    conn.execute('CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, metadata TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, result TEXT NOT NULL)')
    return conn


def track(track_id):
    with db() as conn:
        row = conn.execute('SELECT metadata FROM tracks WHERE id=?', (track_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Song nicht gefunden')
    return json.loads(row[0])


@app.get('/api/health')
def health():
    return {'status':'ok', 'device':engines.device(), 'audio_model':AUDIO_MODEL, 'lyric_model':LYRIC_MODEL}


@app.post('/api/tracks')
def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in {'.mp3','.wav','.flac'}:
        raise HTTPException(415, 'Bitte MP3, WAV oder FLAC importieren')
    temp = DATA / f'{uuid.uuid4().hex}{suffix}'
    digest = hashlib.sha256()
    size = 0
    try:
        with temp.open('wb') as out:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > 250 * 1024 * 1024:
                    raise HTTPException(413, 'Maximal 250 MB pro Song')
                digest.update(chunk)
                out.write(chunk)
        identity = digest.hexdigest()
        target = DATA / f'{identity}.wav'
        if not target.exists():
            import imageio_ffmpeg
            converted = DATA / f'{uuid.uuid4().hex}.wav'
            try:
                subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-nostdin', '-v','error','-y','-i',str(temp),
                                '-t','1800','-ac','1','-ar','48000', str(converted)],
                               check=True, capture_output=True, timeout=120,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                info = sf.info(converted)
                if info.duration <= 0:
                    raise ValueError('Leere Audiodatei')
                converted.replace(target)
            finally:
                converted.unlink(missing_ok=True)
        info = sf.info(target)
        import mutagen
        tags = mutagen.File(temp, easy=True)
        artist = (tags.get('artist', [''])[0] if tags else '')
        title = (tags.get('title', [''])[0] if tags else '')
        metadata = {'id':identity,'name':Path(file.filename or 'Song').name,
                    'artist':artist, 'title':title,
                    'duration':info.duration, 'sample_rate':info.samplerate,
                    'note':'Für den MVP auf maximal 30 Minuten begrenzt.'}
        with db() as conn:
            conn.execute('INSERT OR REPLACE INTO tracks VALUES (?,?)', (identity,json.dumps(metadata)))
        return metadata
    except HTTPException:
        raise
    except (subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        raise HTTPException(422, f'Audio konnte nicht dekodiert werden: {str(exc)[:200]}') from exc
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


def run_job(job_id, identity, request):
    def progress(message, value):
        with job_lock:
            jobs[job_id].update(message=message, progress=value)
    try:
        metadata = track(identity)
        key = hashlib.sha256((identity + PIPELINE_VERSION + request.model_dump_json()).encode()).hexdigest()
        with db() as conn:
            cached = conn.execute('SELECT result FROM cache WHERE key=?',(key,)).fetchone()
        if cached:
            result = {**json.loads(cached[0]), 'cached':True}
        else:
            lines = parse_lrc(request.lyrics, metadata['duration'])
            warnings = []
            if request.lyrics.strip() and not lines:
                warnings.append('Text ohne LRC-Zeitstempel: keine synchronisierte Textkurve. Bitte LRC importieren oder Whisper aktivieren.')
            if not lines and request.whisper:
                lines = engines.transcribe(DATA / f'{identity}.wav', progress)
                warnings.append('Whisper-Zeitstempel und Gesangserkennung können ungenau sein.')
            audio_key = f'audio:{identity}:{PIPELINE_VERSION}'
            with db() as conn:
                audio_cached = conn.execute('SELECT result FROM cache WHERE key=?',(audio_key,)).fetchone()
            if audio_cached:
                payload=json.loads(audio_cached[0])
                a, summary = payload['audio'], payload['features']
                progress('Audioanalyse aus lokalem Cache', 65)
            else:
                y, sr = sf.read(DATA / f'{identity}.wav', dtype='float32')
                import librosa
                # Actual acoustic measurements; independent of the emotion model.
                rms = librosa.feature.rms(y=y)[0]
                summary = {'rms_mean':float(np.mean(rms)), 'duration':len(y)/sr}
                a = engines.audio(y, sr, progress)
                with db() as conn:
                    conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',
                                 (audio_key,json.dumps({'audio':a,'features':summary})))
            l = engines.lyrics(lines, progress)
            if not l:
                warnings.append('Keine synchronisierten Lyrics: Biggest Split ist nicht verfügbar.')
            result = {'audio':a, 'lyrics':l, 'split':biggest_split(a,l), 'features':summary,
                      'warnings':warnings, 'cached':False, 'device':engines.device(),
                      'models':{'audio':AUDIO_MODEL,'lyrics':LYRIC_MODEL},
                      'method':'CLAP Zero-Shot; XLM-EMO. Valenz in [-1,1], keine kalibrierte Emotionsmessung.'}
            with db() as conn:
                conn.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(key,json.dumps(result)))
        with job_lock:
            jobs[job_id].update(status='done',progress=100,message='Analyse abgeschlossen',result=result)
    except Exception as exc:
        with job_lock:
            jobs[job_id].update(status='error',message=f'{type(exc).__name__}: {str(exc)[:1000]}')


@app.post('/api/tracks/{identity}/analyze')
def analyze(identity: str, request: AnalyzeRequest):
    track(identity)
    with job_lock:
        if any(j['status']=='running' for j in jobs.values()):
            raise HTTPException(409, 'Eine Analyse läuft bereits. Bitte warten.')
        job_id = uuid.uuid4().hex
        jobs.clear()
        jobs[job_id] = {'status':'running','progress':0,'message':'Analyse wird vorbereitet'}
    executor.submit(run_job,job_id,identity,request)
    return {'job_id':job_id}


@app.get('/api/jobs/{job_id}')
def job(job_id: str):
    with job_lock:
        if job_id not in jobs:
            raise HTTPException(404,'Analyseauftrag nicht gefunden')
        return dict(jobs[job_id])


if (ROOT / 'dist').exists():
    from fastapi.staticfiles import StaticFiles
    app.mount('/', StaticFiles(directory=ROOT / 'dist', html=True), name='frontend')
