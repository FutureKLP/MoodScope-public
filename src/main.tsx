import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Analysis, Point, Track, clock, activeLine} from './types';
import './style.css';

const API = 'http://127.0.0.1:8765';
async function api(path:string, init?:RequestInit) {
  const response = await fetch(API+'/api'+path,init);
  if(!response.ok) {const error=await response.json().catch(()=>({detail:response.statusText})); throw Error(error.detail||'Anfrage fehlgeschlagen')}
  return response.json();
}
const json = (body:unknown) => ({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});

function Chart({result,duration,time,seek}:{result:Analysis|null;duration:number;time:number;seek:(t:number)=>void}) {
  const w=1000,h=270,p=26;
  const x=(t:number)=>p+t/Math.max(1,duration)*(w-2*p);
  const y=(v:number)=>h/2-v*(h/2-p);
  const path=(points:Point[])=>points.map((a,i)=>`${i?'L':'M'}${x(a.start)},${y(a.valence)}`).join(' ')+(points.length?` L${x(points.at(-1)!.end)},${y(points.at(-1)!.valence)}`:'');
  return <div className="chart"><svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Emotionale Valenz über die Songdauer; zum Springen klicken" onClick={e=>{const r=e.currentTarget.getBoundingClientRect();seek(Math.max(0,Math.min(duration,((e.clientX-r.left)/r.width*w-p)/(w-2*p)*duration)))}}>
    <defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#67ead7" stopOpacity=".16"/><stop offset="1" stopColor="#67ead7" stopOpacity="0"/></linearGradient></defs>
    {[-1,-.5,0,.5,1].map(v=><line key={v} x1={p} x2={w-p} y1={y(v)} y2={y(v)} stroke={v===0?'#35434b':'#202b33'} strokeDasharray={v===0?'4 5':''}/>)}
    {result?.split&&<rect x={x(result.split.start)} y={p} width={Math.max(3,x(result.split.end)-x(result.split.start))} height={h-2*p} fill="#e7be73" opacity=".09"/>}
    {result?.audio.length ? <><path d={path(result.audio)+` L${x(result.audio.at(-1)!.end)},${h-p} L${p},${h-p} Z`} fill="url(#fill)"/><path d={path(result.audio)} className="audio-path"/></>:null}
    {result?.lyrics.map((l,i)=><path key={i} d={`M${x(l.start)},${y(l.valence)} L${x(l.end)},${y(l.valence)}`} className="lyric-path"/>)}
    {result&&<><line x1={x(time)} x2={x(time)} y1={p} y2={h-p} stroke="#f4f8fa" opacity=".65"/><circle cx={x(time)} cy={h-p} r="3" fill="#fff"/></>}
  </svg>{!result&&<div className="chart-empty"><span className="orbit"></span><strong>Jeder Song erzählt zwei Geschichten.</strong><span>Importiere Musik und entdecke, wo Klang und Worte auseinandergehen.</span></div>}
  <div className="axis"><span>{clock(0)}</span><span>{clock(duration/4)}</span><span>{clock(duration/2)}</span><span>{clock(duration*3/4)}</span><span>{clock(duration)}</span></div></div>
}

function App(){
  const [track,setTrack]=useState<Track|null>(null),[result,setResult]=useState<Analysis|null>(null);
  const [lyrics,setLyrics]=useState(''),[artist,setArtist]=useState(''),[title,setTitle]=useState('');
  const [whisper,setWhisper]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('');
  const [progress,setProgress]=useState(0),[time,setTime]=useState(0),[playing,setPlaying]=useState(false),[device,setDevice]=useState('Verbindung …');
  const audio=useRef<HTMLAudioElement>(null),file=useRef<HTMLInputElement>(null),lrcFile=useRef<HTMLInputElement>(null);
  const mounted=useRef(true);
  useEffect(()=>{mounted.current=true;api('/health').then(r=>setDevice(r.device==='cuda'?'NVIDIA CUDA':'CPU lokal')).catch(()=>setDevice('Backend offline'));return()=>{mounted.current=false}},[]);
  useEffect(()=>{let id=0; const tick=()=>{if(audio.current)setTime(audio.current.currentTime);id=requestAnimationFrame(tick)};id=requestAnimationFrame(tick);return()=>cancelAnimationFrame(id)},[]);
  useEffect(()=>{const el=document.querySelector('.lyric-row.active');el?.scrollIntoView({behavior:'smooth',block:'nearest'})},[activeLine(result?.lyrics||[],time)]);
  async function perform(action:()=>Promise<void>){setError('');setBusy(true);try{await action()}catch(e){setError(e instanceof Error?e.message:String(e))}finally{if(mounted.current)setBusy(false)}}
  async function importAudio(f:File){await perform(async()=>{
    setMessage('Audio wird importiert …');setProgress(0);
    const body=new FormData();body.append('file',f);
    const t:Track=await api('/tracks',{method:'POST',body});
    audio.current?.pause();setTrack(t);setResult(null);setLyrics('');setTime(0);
    setArtist(t.artist||'');setTitle(t.title||f.name.replace(/\.[^.]+$/,''));
    let importedLyrics='';
    if(t.artist&&t.title){
      setMessage('Suche automatisch Lyrics anhand der Song-Tags …');
      try {
        const r=await api(`/tracks/${t.id}/lyrics/search`,json({artist:t.artist,title:t.title}));
        importedLyrics=r.text;
        setLyrics(r.text);setMessage(r.synced?'Synchronisierte Lyrics automatisch gefunden':r.instrumental?'Instrumental erkannt':'Nur unsynchronisierter Text gefunden – Whisper oder LRC wählen');
      } catch(e) {setMessage(`Song importiert. ${e instanceof Error?e.message:String(e)}`)}
    } else setMessage('Bereit zur Analyse. Ohne Interpret-/Titel-Tags: Lyrics manuell suchen oder importieren.');
    await runAnalysis(t,importedLyrics);
  })}
  async function runAnalysis(selected:Track,text:string){setProgress(0);setResult(null);const {job_id}=await api(`/tracks/${selected.id}/analyze`,json({lyrics:text,whisper}));let done=false;while(!done&&mounted.current){const job=await api(`/jobs/${job_id}`);setMessage(job.message);setProgress(job.progress);if(job.status==='error')throw Error(job.message);if(job.status==='done'){setResult(job.result);done=true}else await new Promise(r=>setTimeout(r,900))}}
  async function analyze(){if(track)await perform(()=>runAnalysis(track,lyrics))}
  const seek=(t:number)=>{if(audio.current){audio.current.currentTime=t;setTime(t)}};
  const index=activeLine(result?.lyrics||[],time);
  const current=result?.audio.filter(p=>p.start<=time).at(-1);
  return <div className="app"><aside className="sidebar"><a className="brand" href="#"><span className="brand-icon">MS</span>MoodScope<span className="beta">LAB</span></a><div className="workspace-label">DEIN WORKSPACE</div><div className="nav active"> <span>Song-Analyse</span><span className="nav-dot"/></div><div className="sidebar-note"><div className="mini-wave">AUDIO / LYRICS</div><strong>Musik fühlen.<br/>Kontraste entdecken.</strong><p>Zwei Perspektiven.<br/>Eine neue Art zuzuhören.</p></div><div className="local-badge"><i/>Lokal auf deinem Rechner<span>{device}</span></div></aside>
  <main><header><div className="breadcrumb">WORKSPACE <span>/</span> SONG-ANALYSE</div><div className="privacy"> Local-first · Private by design</div></header>
    <div className="page-heading"><div><div className="eyebrow">BEYOND THE SOUND</div><h1>Was hörst du. <em>Was fühlst du?</em></h1><p>Entdecke die emotionale Verbindung zwischen Musik und Text.</p></div><button className="import-button" disabled={busy} onClick={()=>file.current?.click()}>+ Song importieren</button></div>
    <input ref={file} type="file" accept=".mp3,.wav,.flac" hidden onChange={e=>{const f=e.target.files?.[0];if(f)void importAudio(f);e.target.value=''}}/>
    <input ref={lrcFile} type="file" accept=".lrc,.txt" hidden onChange={e=>{const f=e.target.files?.[0];if(f)f.text().then(setLyrics);e.target.value=''}}/>
    {error&&<div className="error" role="alert">{error}</div>}
    <section className="song-card" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();if(!busy&&e.dataTransfer.files[0])void importAudio(e.dataTransfer.files[0])}}><div className={`cover ${playing?'playing':''}`}><span>MS</span></div><div className="song-info"><div className="eyebrow">{track?'DEIN TRACK':'DEIN NÄCHSTER FUND'}</div><h2>{track?.name||'Gib deinem Song eine neue Dimension'}</h2><p>{track?`${clock(track.duration)} · Lokal importiert · WAV-Wiedergabe`:'MP3, WAV oder FLAC hier ablegen · bis 250 MB / 30 Min.'}</p></div><div className="song-status"><i/>{result?'Analyse bereit':track?'Bereit zur Analyse':'Warte auf Musik'}</div></section>
    <div className="analysis-layout"><div className="main-column"><section className="panel curve-panel"><div className="panel-heading"><div><span className="eyebrow">EMOTIONALE SIGNATUR</span><h2>Zwei Stimmen. Ein Song.</h2></div><div className="legend"><span><i className="mint"/>Audio Mood</span><span><i className="purple"/>Lyric Mood</span></div></div><div className="chart-labels"><span>POSITIV</span><span>VALENZ · −1 BIS +1</span></div><Chart result={result} duration={track?.duration||0} time={time} seek={seek}/><div className="chart-foot"><span>NEGATIV</span><span>{result?`${result.device.toUpperCase()} · ${result.cached?'AUS CACHE':'LOKALE INFERENZ'}`:'Keine Beispieldaten · Deine Analyse beginnt mit einem Song'}</span></div></section>
    <div className="stats"><section className="panel stat"><span className="eyebrow"><i className="mint"/> AUDIO MOOD</span><strong>{current?current.valence.toFixed(2):'—'}</strong><p>Wie die Musik klingt</p><span className="model-label">CLAP · Zero-Shot-Musikemotion</span></section><section className="panel stat"><span className="eyebrow"><i className="purple"/> LYRIC MOOD</span><strong>{index>=0?result!.lyrics[index].valence.toFixed(2):'—'}</strong><p>Was die Worte ausdrücken</p><span className="model-label">XLM-EMO · mehrsprachig</span></section><section className="panel stat split"><span className="eyebrow"> BIGGEST SPLIT</span><strong>{result?.split?`${(result.split.gap/2*100).toFixed(0)} %`:'—'}</strong><p>{result?.split?`Größter Kontrast bei ${clock(result.split.start)}`:'Wo Klang und Text sich trennen'}</p><button disabled={!result?.split} onClick={()=>seek(result!.split!.start)}>Zum Moment springen </button></section></div>
    <section className="panel setup"><div className="panel-heading"><h2>Deine Analyse</h2><span className="step-label">01 IMPORT  02 LYRICS  03 ENTDECKEN</span></div><div className="search-row"><label>Interpret<input value={artist} onChange={e=>setArtist(e.target.value)} placeholder="Interpret" disabled={busy}/></label><label>Songtitel<input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Songtitel" disabled={busy}/></label><button disabled={!track||busy||!artist.trim()||!title.trim()} onClick={()=>void perform(async()=>{setMessage('Suche bei LRCLIB …');const r=await api(`/tracks/${track!.id}/lyrics/search`,json({artist,title}));setLyrics(r.text);setMessage(r.instrumental?'Instrumental erkannt':r.synced?'Synchronisierte Lyrics gefunden':'Nur Text ohne Zeitstempel gefunden – Whisper für Synchronisierung aktivieren')})}>Lyrics suchen </button><button disabled={busy} onClick={()=>lrcFile.current?.click()}>LRC importieren</button></div><textarea value={lyrics} disabled={busy} onChange={e=>setLyrics(e.target.value)} placeholder={'Synchronisierte Lyrics einfügen, z. B. [00:12.50] Deine erste Zeile …'}/><div className="analyze-row"><label className="check"><input type="checkbox" checked={whisper} disabled={busy} onChange={e=>setWhisper(e.target.checked)}/>Whisper-Fallback, falls keine LRC-Zeitstempel vorliegen</label><button className="primary" onClick={()=>void analyze()} disabled={!track||busy}>{busy?'Analyse läuft …':'Song analysieren '}</button></div>{message&&<div className="progress" role="status"><span>{message}</span>{busy&&<progress value={progress} max="100"/>}</div>}{result?.warnings.map(w=><p key={w} className="warning">{w}</p>)}</section>
    </div><section className="panel lyric-panel"><div className="panel-heading"><h2>Zwischen den Zeilen</h2><span className="live-label"><i/>SYNC</span></div><div className="lyrics-scroll">{result?.lyrics.length?result.lyrics.map((line,i)=><button key={i} className={`lyric-row ${i===index?'active':''}`} onClick={()=>seek(line.start)}><time>{clock(line.start)}</time><span>{line.text}</span><small>{line.valence.toFixed(2)}</small></button>):<div className="lyrics-empty"><span></span><h3>Worte werden zu Gefühl.</h3><p>Importiere eine LRC-Datei, suche bei LRCLIB oder lasse Whisper lokal transkribieren.</p></div>}</div><div className="lyric-footer">Modellschätzungen sind keine objektive Emotionsmessung. Gesang und Kontext können die Werte beeinflussen.</div></section></div>
    <footer><span>MOODSCOPE / EXPLORING THE SPACE BETWEEN</span><span>Analyse lokal · LRCLIB nur bei Suche · Modelldownload beim ersten Start</span></footer>
  </main><div className="player"><div className="player-track"><div className="tiny-cover">MS</div><div><strong>{track?.name||'Noch kein Song'}</strong><span>{track?'Deine Musik. Deine Perspektive.':'Bereit, wenn du es bist.'}</span></div></div><div className="transport"><button aria-label="10 Sekunden zurück" disabled={!track} onClick={()=>seek(Math.max(0,time-10))}>-10s</button><button className="play" aria-label={playing?'Pause':'Abspielen'} disabled={!track} onClick={()=>{if(audio.current){if(playing)audio.current.pause();else audio.current.play().catch(e=>setError(String(e)))}}}>{playing?'Pause':'Play'}</button><button aria-label="10 Sekunden vor" disabled={!track} onClick={()=>seek(Math.min(track!.duration,time+10))}>+10s</button></div><span className="player-time">{clock(time)}</span><input aria-label="Wiedergabeposition" className="scrubber" type="range" min="0" max={track?.duration||1} step=".05" value={time} disabled={!track} onChange={e=>seek(Number(e.target.value))}/><span className="player-time">{clock(track?.duration||0)}</span><label className="volume">VOL <input aria-label="Lautstärke" type="range" min="0" max="1" step=".01" defaultValue=".8" onChange={e=>{if(audio.current)audio.current.volume=Number(e.target.value)}}/></label></div>
    <audio ref={audio} src={track?`${API}/api/tracks/${track.id}/audio`:undefined} onPlay={()=>setPlaying(true)} onPause={()=>setPlaying(false)} onEnded={()=>setPlaying(false)} onError={()=>{if(track)setError('Audio-Wiedergabe fehlgeschlagen')}}/>
  </div>
}
createRoot(document.getElementById('root')!).render(<App/>);
