import {silentTransport} from './audioTransport';
import {ErrorNotice} from './ErrorNotice';
import {DeviceSettings} from './DeviceSettings';
import {PromptManager} from './PromptManager';
import {useAutoFollow} from './useAutoFollow';
import {TooltipLayer} from './Tooltip';
import {interpolatePoint,chartTime} from './timeline';
import {LoopScrubber,LoopRange,nextLoopRange} from './LoopScrubber';
import {LiveMixConfig,useLiveMix} from './LiveMix';
import {invoke,isTauri} from '@tauri-apps/api/core';
import {Atmosphere,AtmosphereThemeContext,moodHue,atmosphereStyle} from './Atmosphere';
import {AnalysisReport} from './AnalysisReport';
import {ExpressionComparison} from './ExpressionComparison';
import {t as tr,useLanguage,LanguageSelect} from './i18n';
import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Analysis, Point, Track, clock, activeLine,toLrc,trackInitials} from './types';
import './style.css';
import {API,api,json,ApiError} from './api';
import {Workspace} from './Workspace';
import {SourceStudio,OnlineFacts,DiagnosticPanel,SourceMetadata} from './SongTools';
import {ProviderSettings} from './Providers';
import {ManualFocus} from './ManualFocus';
import {Lifecycle} from './Lifecycle';

export function Chart({result,duration,time,seek,loopRange,onLoopMark}:{result:Analysis|null;duration:number;time:number;seek:(t:number)=>void;loopRange?:LoopRange|null;onLoopMark?:(time:number)=>void}) {
  const dragging=useRef<number|null>(null);
  const move=(e:React.PointerEvent<SVGSVGElement>)=>{const rect=e.currentTarget.getBoundingClientRect();seek(chartTime(e.clientX,rect.left,rect.width,duration))};
  const w=1000,h=270,p=26;
  const x=(t:number)=>p+t/Math.max(1,duration)*(w-2*p);
  const y=(v:number)=>h/2-v*(h/2-p);
  const path=(points:Point[])=>points.length?`M${x(points[0].start)},${y(points[0].valence)}`+points.map(a=>` L${x((a.start+a.end)/2)},${y(a.valence)}`).join('')+` L${x(points.at(-1)!.end)},${y(points.at(-1)!.valence)}`:'';
  return <div className="chart"><svg viewBox={`0 0 ${w} ${h}`} role={result?'slider':'img'} tabIndex={result?0:-1} aria-label={tr('Wiedergabeposition im Stimmungsverlauf')} aria-valuemin={0} aria-valuemax={duration} aria-valuenow={time} aria-valuetext={clock(time)}
    onPointerDown={e=>{if(!result||e.button!==0)return;e.preventDefault();dragging.current=e.pointerId;e.currentTarget.setPointerCapture?.(e.pointerId);move(e)}}
    onPointerMove={e=>{if(dragging.current===e.pointerId)move(e)}}
    onPointerUp={e=>{if(dragging.current!==e.pointerId)return;move(e);dragging.current=null;if(e.currentTarget.hasPointerCapture?.(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId)}}
    onContextMenu={e=>{e.preventDefault();if(result&&onLoopMark){const rect=e.currentTarget.getBoundingClientRect();onLoopMark(chartTime(e.clientX,rect.left,rect.width,duration))}}}
    onPointerCancel={()=>{dragging.current=null}} onLostPointerCapture={()=>{dragging.current=null}}
    onKeyDown={e=>{if(!result)return;const next=e.key==='Home'?0:e.key==='End'?duration:e.key==='ArrowRight'?time+(e.shiftKey?10:2):e.key==='ArrowLeft'?time-(e.shiftKey?10:2):null;if(next!==null){e.preventDefault();seek(Math.min(duration,Math.max(0,next)))}}}
    onClick={e=>{if(result&&e.detail===0){const rect=e.currentTarget.getBoundingClientRect();seek(chartTime(e.clientX,rect.left,rect.width,duration))}}}>
    <defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#67ead7" stopOpacity=".16"/><stop offset="1" stopColor="#67ead7" stopOpacity="0"/></linearGradient></defs>
    {[-1,-.5,0,.5,1].map(v=><line key={v} x1={p} x2={w-p} y1={y(v)} y2={y(v)} stroke={v===0?'#35434b':'#202b33'} strokeDasharray={v===0?'4 5':''}/>)}
    {loopRange&&<g className="chart-loop" aria-label={tr('Gemeinsamer A/B-Loop')}>{loopRange.b!==null&&<rect x={x(loopRange.a)} y={p} width={Math.max(1,x(loopRange.b)-x(loopRange.a))} height={h-2*p}/>}<line x1={x(loopRange.a)} x2={x(loopRange.a)} y1={p} y2={h-p}/><text x={x(loopRange.a)+5} y={p-8}>A</text>{loopRange.b!==null&&<><line x1={x(loopRange.b)} x2={x(loopRange.b)} y1={p} y2={h-p}/><text x={x(loopRange.b)+5} y={p-8}>B</text></>}</g>}
    {result?.split&&<rect x={x(result.split.start)} y={p} width={Math.max(3,x(result.split.end)-x(result.split.start))} height={h-2*p} fill="#e7be73" opacity=".09"/>}
    {result?.audio.length ? <><path d={path(result.audio)+` L${x(result.audio.at(-1)!.end)},${h-p} L${p},${h-p} Z`} fill="url(#fill)"/><path d={path(result.audio)} className="audio-path"/></>:null}
    {result?.lyrics.map((l,i)=><path key={i} d={`M${x(l.start)},${y(l.valence)} L${x(l.end)},${y(l.valence)}`} className="lyric-path"/>)}
    {result&&<><line x1={x(time)} x2={x(time)} y1={p} y2={h-p} stroke="#f4f8fa" opacity=".65"/><circle cx={x(time)} cy={h-p} r="3" fill="#fff"/></>}
  </svg>{!result&&<div className="chart-empty"><span className="orbit"></span><strong>{tr("Jeder Song erzählt zwei Geschichten.")}</strong><span>{tr("Importiere Musik und entdecke, wo Klang und Worte auseinandergehen.")}</span></div>}
  <div className="axis"><span>{clock(0)}</span><span>{clock(duration/4)}</span><span>{clock(duration/2)}</span><span>{clock(duration*3/4)}</span><span>{clock(duration)}</span></div></div>
}

export function App(){
  const language=useLanguage();
  useEffect(()=>{const handle=(event:KeyboardEvent)=>{if(event.key==='F11'&&isTauri()){event.preventDefault();void invoke('toggle_fullscreen').catch(e=>setError(String(e)))}};window.addEventListener('keydown',handle);return()=>window.removeEventListener('keydown',handle)},[]);
  const [ambient,setAmbient]=useState(()=>{try{return localStorage.getItem('moodscope-atmosphere')==='true'}catch{return false}});
  useEffect(()=>{try{localStorage.setItem('moodscope-atmosphere',String(ambient))}catch{}},[ambient]);
  const [track,setTrack]=useState<Track|null>(null),[result,setResult]=useState<Analysis|null>(null);
  const [cacheRevision,setCacheRevision]=useState(0),[studioRevision,setStudioRevision]=useState(0),[studioModel,setStudioModel]=useState('htdemucs_auto');
  const [lyrics,setLyrics]=useState(''),[artist,setArtist]=useState(''),[title,setTitle]=useState('');
  const [whisper,setWhisper]=useState(true),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('');
  const [serviceStopped,setServiceStopped]=useState(false);
  const [activeJob,setActiveJob]=useState(''),[cancelRequested,setCancelRequested]=useState(false);
  const [progress,setProgress]=useState(0),[time,setTime]=useState(0),[playing,setPlaying]=useState(false),[device,setDevice]=useState(tr("Verbindung …"));
  const [deviceName,setDeviceName]=useState(''),[apiModel,setApiModel]=useState('Gemini'),[textProvider,setTextProvider]=useState<{name:string;model:string}|null>(null);
  const [view,setView]=useState('timeline'),[mode,setMode]=useState<'local'|'cloud'>('local'),[consent,setConsent]=useState(false),[link,setLink]=useState('');
  const settingsView=view==='settings'||view==='prompts';
  const headerRef=useRef<HTMLDivElement>(null),heroRef=useRef<HTMLDivElement>(null);
  useLayoutEffect(()=>{
    const header=headerRef.current,hero=heroRef.current;if(!header||!hero)return;
    let frame=0;
    const update=()=>{const height=hero.offsetHeight||120;header.style.setProperty('--header-hero-height',`${height}px`);header.style.setProperty('--header-collapse',String(Math.max(0,Math.min(1,window.scrollY/height))))};
    const scroll=()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(update)};
    const resize=typeof ResizeObserver==='undefined'?null:new ResizeObserver(update);resize?.observe(hero);update();window.addEventListener('scroll',scroll,{passive:true});window.addEventListener('resize',scroll);
    return()=>{cancelAnimationFrame(frame);resize?.disconnect();window.removeEventListener('scroll',scroll);window.removeEventListener('resize',scroll)};
  },[settingsView,language,serviceStopped]);
  const lastSongView=useRef('timeline');
  useEffect(()=>{if(!settingsView)lastSongView.current=view},[view]);
  const audio=useRef<HTMLAudioElement>(null),file=useRef<HTMLInputElement>(null),lrcFile=useRef<HTMLInputElement>(null);
  const [liveMix,setLiveMix]=useState<LiveMixConfig|null>(null);
  const stopLiveMix=useRef<(()=>void)|null>(null);
  const liveState=useLiveMix(audio,liveMix,stopLiveMix);
  const loopRef=useRef<LoopRange|null>(null);const [loopRange,setLoopRange]=useState<LoopRange|null>(null);
  useEffect(()=>{loopRef.current=null;setLoopRange(null)},[track?.id]);
  const mounted=useRef(true);
  const pendingOperations=useRef(0);
  const [versionWarning,setVersionWarning]=useState(''),[resolution,setResolution]=useState(2),[recognitionSource,setRecognitionSource]=useState('auto'),[recognitionLanguage,setRecognitionLanguage]=useState(''),[recognitionModel,setRecognitionModel]=useState('whisper-turbo');
  const [whisperChoices,setWhisperChoices]=useState<Array<{id:string;name:string}>>([]);
  useEffect(()=>{if(view==='timeline')api('/models').then(r=>{setWhisperChoices(r.models.filter((m:any)=>m.purpose==='whisper'));if(r.active?.whisper)setRecognitionModel(r.active.whisper)}).catch(()=>{})},[view]);
  const [linkResults,setLinkResults]=useState<any>(null);
  const [sourceUrl,setSourceUrl]=useState(''),[sourceLabel,setSourceLabel]=useState(tr("Originalmix"));
  const mediaEpoch=useRef(0),playAttempt=useRef(0),volume=useRef(.8),trackRequest=useRef(0);
  const [playbackSession,setPlaybackSession]=useState(0);
  const liveClock=useRef<{trackId:string;url:string}|null>(null);
  const playbackRestore=useRef<{time:number;playing:boolean;url?:string;epoch?:number}|null>(null);
  function releaseLive(){stopLiveMix.current?.();setLiveMix(null);if(liveClock.current){URL.revokeObjectURL(liveClock.current.url);liveClock.current=null}}
  useEffect(()=>()=>{if(liveClock.current)URL.revokeObjectURL(liveClock.current.url)},[]);
  function playMedia(element:HTMLAudioElement){const epoch=mediaEpoch.current,attempt=++playAttempt.current;setPlaying(true);void element.play().catch(e=>{if(audio.current!==element||epoch!==mediaEpoch.current||attempt!==playAttempt.current)return;setPlaying(false);if(e?.name!=='AbortError')setError(tr('Wiedergabe bitte erneut starten.'))})}
  function togglePlayback(){const element=audio.current;if(!element)return;if(element.paused)playMedia(element);else{playAttempt.current++;element.pause();setPlaying(false)}}

  function changeSource(url:string,label:string,position?:number){
    const element=audio.current,wasPlaying=!!element&&!element.paused&&!element.ended;
    const epoch=++mediaEpoch.current,at=position??element?.currentTime??0;
    releaseLive();playbackRestore.current=null;setSourceLabel(label);setSourceUrl(url);
    if(element?.src===url){if(position!==undefined)element.currentTime=at;setPlaying(!element.paused);return}
    element?.pause();setPlaying(false);playbackRestore.current={time:at,playing:wasPlaying,url,epoch};
  }
  function changeLiveMix(config:LiveMixConfig){
    if(!track||config.trackId!==track.id)return;
    if(!liveMix){
      const element=audio.current,at=element?.currentTime??0,wasPlaying=!!element&&!element.paused&&!element.ended;
      const epoch=++mediaEpoch.current;stopLiveMix.current?.();
      if(liveClock.current)URL.revokeObjectURL(liveClock.current.url);
      const url=URL.createObjectURL(silentTransport(track.duration));liveClock.current={trackId:track.id,url};
      element?.pause();setPlaying(false);playbackRestore.current={time:at,playing:wasPlaying,url,epoch};setSourceUrl(url);
    }
    setSourceLabel(tr('Live-Quellenmix'));setLiveMix(config);
  }
  useEffect(()=>{if(audio.current)audio.current.volume=volume.current},[playbackSession]);
  useEffect(()=>{if(liveState==='error'&&liveMix&&track){changeSource(`${API}/api/tracks/${track.id}/audio`,tr('Originalmix'));setError(tr('Live-Mix konnte nicht geladen werden. Der Originalmix wurde wiederhergestellt.'))}},[liveState]);
  const computePurpose=view==='studio'?'separation':view==='interpretation'?'interpretation':'audio';
  useEffect(()=>{let current=true;void api(`/health?purpose=${computePurpose}`).then(r=>{if(current){setDeviceName(r.device_name||'');setDevice(String(r.device).startsWith('cuda')?'NVIDIA CUDA':tr('CPU lokal'))}}).catch(()=>{});return()=>{current=false}},[computePurpose]);
  useEffect(()=>{mounted.current=true;api('/health').then(r=>{setDeviceName(r.device_name||'');setApiModel(r.api_model||'Gemini');setDevice(String(r.device).startsWith('cuda')?'NVIDIA CUDA':tr("CPU lokal"));if(r.version&&(r.version!=='0.3.0'||r.api_revision!==12))setVersionWarning(tr("Ein älterer MoodScope-Dienst läuft. Mit Neustarten werden Dienst und Oberfläche aktualisiert. Bis dahin sind neue Funktionen gesperrt."))}).catch(()=>setDevice(tr("Backend offline")));return()=>{mounted.current=false}},[]);
  useEffect(()=>{let id=0; const tick=()=>{if(audio.current){const loop=loopRef.current;if(loop?.b!==null&&loop&&!audio.current.paused&&audio.current.currentTime>=loop.b)audio.current.currentTime=loop.a;setTime(audio.current.currentTime);}id=requestAnimationFrame(tick)};id=requestAnimationFrame(tick);return()=>cancelAnimationFrame(id)},[]);
  const [followLyrics,setFollowLyrics]=useState(true);const lyricScroll=useAutoFollow(activeLine(result?.lyrics||[],time),followLyrics&&view==='timeline');

  async function switchMode(next:'local'|'cloud'){setMode(next);setConsent(false);if(track)await perform(async()=>{try{setResult(await api(`/tracks/${track.id}/analysis?mode=${next}`))}catch(e){if(e instanceof ApiError&&e.status===404){setResult(null);setMessage(tr('Für diesen Modus ist noch keine Analyse gespeichert.'))}else throw e}})}
  async function perform(action:()=>Promise<void>){setError('');pendingOperations.current++;setBusy(true);try{await action()}catch(e){if(e instanceof Error&&e.name==='JobCancelled')setMessage(tr('Auftrag abgebrochen.'));else setError(e instanceof Error?e.message:String(e))}finally{pendingOperations.current=Math.max(0,pendingOperations.current-1);if(mounted.current)setBusy(pendingOperations.current>0)}}
  function prepareDeletion(identity?:string){if(!track||(identity&&track.id!==identity&&track.reuse_source_id!==identity)||!audio.current)return()=>{};mediaEpoch.current++;const wasLive=!!liveMix;releaseLive();setPlaying(false);const element=audio.current;const previous=wasLive?`${API}/api/tracks/${track.id}/audio`:element.src;const position=element.currentTime;element.pause();element.removeAttribute('src');element.load();return()=>{playbackRestore.current={time:position,playing:false,url:previous,epoch:mediaEpoch.current};setSourceUrl(previous);if(wasLive)setSourceLabel(tr('Originalmix'));element.src=previous;element.load()}}
  async function recognize(){if(!track)return;await perform(async()=>{await api('/models/select',json({model_id:recognitionModel}));const recognized=await runJob(`/tracks/${track.id}/analyze`,{lyrics:'',whisper:true,mode:'local',force_transcription:true,transcription_quality:'precise',transcription_source:recognitionSource,transcription_language:recognitionLanguage||null,audio_resolution:resolution});setResult(recognized);setLyrics(toLrc(recognized.lyrics));setMessage(tr("Präziser lokaler Durchlauf abgeschlossen. Transkript vergleichen und Erkennungsfehler bei Bedarf im Textfeld korrigieren."))})}
  async function importAudio(f:File){await perform(async()=>{
    setMessage(tr("Audio wird importiert …"));setProgress(0);
    const body=new FormData();body.append('file',f);
    const t:Track=await api('/tracks',{method:'POST',body});
    await acceptTrack(t);
  })}
  function researchAutomatically(t:Track){if(t.title&&(t.artist||['YouTube','SoundCloud'].includes(t.source||'')))void api(`/tracks/${t.id}/research`,json({artist:t.artist||'',title:t.title,auto_match:true})).catch(()=>{})}
  async function acceptTrack(t:Track){const request=++trackRequest.current;mediaEpoch.current++;releaseLive();setPlaying(false);setPlaybackSession(n=>n+1);loopRef.current=null;setLoopRange(null);setFollowLyrics(true);
    researchAutomatically(t);
    audio.current?.pause();audio.current?.removeAttribute('src');audio.current?.load();playbackRestore.current=null;setSourceUrl('');setSourceLabel(tr("Originalmix"));setTrack(t);setResult(null);setLyrics('');setTime(0);
    setArtist(t.artist||'');setTitle(t.title||t.name.replace(/\.[^.]+$/,''));
    try{
      const cached:Analysis=await api(`/tracks/${t.id}/analysis?mode=${mode}`);
      if(request!==trackRequest.current)return;
      setResult(cached);setLyrics(cached.source_lyrics?.trim()?cached.source_lyrics:toLrc(cached.lyrics));
      setMessage(cached.stale?tr("Gespeicherte Analyse geladen. Modellversion geändert; bei Bedarf neu analysieren."):t.cache_match==='metadata-and-audio'?tr("Vorhandene Analyse anhand Metadaten und Audioabgleich geladen."):tr("Gespeicherte Analyse geladen; keine erneute KI-Inferenz."));
      return;
    }catch(e){if(!(e instanceof ApiError&&e.status===404))throw e}
    if(request!==trackRequest.current)return;
    let importedLyrics='';
    if(t.artist&&t.title){
      setMessage(tr("Suche automatisch Lyrics anhand der Song-Tags …"));
      try {
        const r=await api(`/tracks/${t.id}/lyrics/search`,json({artist:t.artist,title:t.title}));
        if(request!==trackRequest.current)return;
        importedLyrics=r.text;
        setLyrics(r.text);setMessage(r.synced?tr("Synchronisierte Lyrics automatisch gefunden"):r.instrumental?tr("Instrumental erkannt"):tr("Nur unsynchronisierter Text gefunden – Whisper oder LRC wählen"));
      } catch(e) {setMessage(tr("Song importiert. {0}",[e instanceof Error?e.message:String(e)]))}
    } else setMessage(tr("Bereit zur Analyse. Ohne Interpret-/Titel-Tags: Lyrics manuell suchen oder importieren."));
    if(request===trackRequest.current)await runAnalysis(t,importedLyrics);
  }
  async function runJob(path:string,body:unknown={}){
    setProgress(0);const {job_id}=await api(path,json(body));setActiveJob(job_id);setCancelRequested(false);const deadline=Date.now()+30*60*1000;
    try{while(mounted.current&&Date.now()<deadline){const job=await api(`/jobs/${job_id}`);setMessage(job.message);setProgress(job.progress);if(job.status==='cancelled'){const error=new Error(job.message);error.name='JobCancelled';throw error}if(job.status==='error')throw Error(job.message);if(job.status==='done')return job.result;await new Promise(r=>setTimeout(r,900))}
      throw Error(tr('Auftrag noch nicht abgeschlossen. Backend-Status prüfen; keine Ersatzwerte wurden erzeugt.'));
    }finally{setActiveJob('');setCancelRequested(false)}
  }

  async function importLink(value=link){await perform(async()=>{const u=new URL(value);if(u.hostname.endsWith('soundcloud.com')&&u.pathname==='/search'){setLinkResults(await api('/links/search',json({url:value})));setMessage(tr("Bitte einen einzelnen Suchtreffer auswählen."));return}const t:Track=await runJob('/tracks/link',{url:value});setLink('');setLinkResults(null);await acceptTrack(t)})}
  async function runAnalysis(selected:Track,text:string,force=false){
    const request=trackRequest.current;
    const needsRecognition=mode==='local'&&whisper&&!/\[\d{1,3}:\d{2}(?:[.:]\d+)?\]/.test(text||'');
    if(needsRecognition)await api('/models/select',json({model_id:recognitionModel}));
    const analyzed=await runJob(`/tracks/${selected.id}/analyze`,{lyrics:text,whisper:mode==='local'&&whisper,mode,upload_consent:consent,force,audio_resolution:resolution,
      transcription_quality:needsRecognition?'precise':'standard',transcription_source:recognitionSource,transcription_language:recognitionLanguage||null});
    if(request!==trackRequest.current)return;
    setResult(analyzed);if(!text.trim()&&analyzed.lyrics?.length)setLyrics(toLrc(analyzed.lyrics));
  }
  async function analyze(){if(track)await perform(()=>runAnalysis(track,lyrics,true))}
  const seek=(t:number)=>{if(audio.current){audio.current.currentTime=t;setTime(t)}};
  function markGraphLoop(position:number){const next=nextLoopRange(loopRef.current,position,track?.duration||0);loopRef.current=next;setLoopRange(next);if(next?.b!==null&&next&&(time<next.a||time>=next.b!))seek(next.a)}
  const index=activeLine(result?.lyrics||[],time);
  const current=interpolatePoint(result?.audio||[],time);
  if(serviceStopped)return <div className="ended-screen"><section className="panel"><span className="eyebrow">MOODSCOPE</span><h1>{tr('Für heute beendet.')}</h1><p>{tr('Der lokale Dienst ist beendet. Deine gespeicherten Songs bleiben erhalten. Zum nächsten Start Start-MoodScope.cmd oder das Startskript öffnen.')}</p><button onClick={()=>void api('/health',{signal:AbortSignal.timeout(2500)}).then(()=>window.location.reload()).catch(()=>setError(tr('Der Dienst ist bereits beendet. Für einen neuen Start Start-MoodScope.cmd oder das Startskript öffnen.')))}>{tr('Dienst erneut prüfen')}</button>{isTauri()&&<button onClick={()=>void invoke('exit_app')}>{tr('Fenster schließen')}</button>}{error&&<p role="status">{tr(error)}</p>}</section></div>;
  return <AtmosphereThemeContext.Provider value={{enabled:ambient,style:atmosphereStyle(current,index>=0?interpolatePoint(result?.lyrics||[],time):undefined,result?.features?.bpm)}}><div className={`app ${ambient?'ambient-enabled':''} ${playing?'is-playing':''}`} style={atmosphereStyle(current,index>=0?interpolatePoint(result?.lyrics||[],time):undefined,result?.features?.bpm)}><TooltipLayer/>{ambient&&<Atmosphere/>}<aside className="sidebar"><a className="brand" href="#"><span className="brand-icon">MS</span>MoodScope<span className="beta">LAB</span></a><div className="workspace-label">{tr("DEIN WORKSPACE")}</div><nav className="workspace-navigation" aria-label={tr('Hauptbereiche')}><button className={settingsView?'nav':'nav active'} aria-pressed={!settingsView} onClick={()=>setView(lastSongView.current)}><span>{tr("Song-Analyse")}</span><span className="nav-dot"/></button><button className={view==='settings'?'nav active':'nav'} aria-pressed={view==='settings'} onClick={()=>setView('settings')}><span>{tr("Modelle & API")}</span><span className="nav-dot"/></button><button className={view==='prompts'?'nav active':'nav'} aria-pressed={view==='prompts'} onClick={()=>setView('prompts')}><span>{tr('Prompts')}</span><span className="nav-dot"/></button></nav><div className="sidebar-note"><div className="mini-wave">AUDIO / LYRICS</div><strong>{tr("Musik fühlen.")}<br/>{tr("Kontraste entdecken.")}</strong><p>{tr("Zwei Perspektiven.")}<br/>{tr("Eine neue Art zuzuhören.")}</p></div><div className="local-badge"><i/>{tr(view==='interpretation'&&textProvider?'Text-Server':mode==='cloud'?'API-Modus':'Lokal auf deinem Rechner')}<span>{view==='interpretation'&&textProvider?`${textProvider.name} · ${textProvider.model}`:mode==='cloud'?(apiModel==='Gemini'?'Gemini':`Gemini · ${apiModel}`):deviceName||tr(device)}</span></div></aside>
  <main><div ref={headerRef} className="sticky-workspace-header">
    <header><div className="breadcrumb">WORKSPACE <span>/</span> {tr(view==='prompts'?'PROMPTS':settingsView?'MODELLE & API':'SONG-ANALYSE')}</div><label className="mode-switch">{tr("Analysemodus")}<select aria-label={tr("Analysemodus")} value={mode} disabled={busy||!!versionWarning} onChange={e=>void switchMode(e.target.value as 'local'|'cloud')}><option value="local">{tr("Lokal auf meinem Rechner")}</option><option value="cloud">{tr("Optional: Audio-API (Gemini-Profil)")}</option></select></label><LanguageSelect disabled={busy}/><Lifecycle onStopped={()=>{setVersionWarning('');setError('');setServiceStopped(true)}} onStop={()=>{mediaEpoch.current++;releaseLive();setPlaying(false);audio.current?.pause();audio.current?.removeAttribute('src');audio.current?.load()}}/></header>
    <div ref={heroRef} className="header-hero">{settingsView?<div className="page-heading"><div><div className="eyebrow">{tr('DEIN SETUP')}</div><h1>{view==='prompts'?tr('Prompt-Vorlagen'):<>{tr('Modelle')} <em>& API</em></>}</h1><p>{tr(view==='prompts'?'Arbeitsaufträge und Klangbeschreibungen nachvollziehbar anpassen.':'Lokale Modelle und optionale Server an einem Ort verwalten.')}</p></div></div>:<div className="page-heading"><div><div className="eyebrow">BEYOND THE SOUND</div><h1>{tr("Was hörst du.")} <em>{tr("Was fühlst du?")}</em></h1><p>{tr("Entdecke die emotionale Verbindung zwischen Musik und Text.")}</p></div></div>}</div>
    {!settingsView&&<div className="song-toolbar"><div className="heading-actions"><button disabled={!track||busy||!!versionWarning} onClick={()=>void analyze()}>{tr("Song neu analysieren")}</button><button className="import-button" disabled={busy||!!versionWarning} onClick={()=>file.current?.click()}>{tr("+ Song importieren")}</button></div><div className="source-controls"><label>{tr("Songlink")}<input aria-label={tr("YouTube- oder SoundCloud-Link")} value={link} onChange={e=>setLink(e.target.value)} placeholder={tr("https://www.youtube.com/watch?v=… oder soundcloud.com/artist/track")} disabled={busy||!!versionWarning}/></label><button disabled={busy||!!versionWarning||!link.trim()} onClick={()=>void importLink()}>{tr("Link importieren")}</button></div></div>}
    </div>
    {!settingsView&&<nav className="tabs" aria-label={tr("Songbereiche")}>{[['library',tr("Bibliothek")],['details',tr("Songdetails")],['timeline',tr("Stimmungsverlauf")],['report',tr('Methode & Werte')],['studio',tr("Hörstudio")],['interpretation','Interpretation']].map(([id,label])=><button key={id} className={view===id?'selected':''} aria-pressed={view===id} onClick={()=>setView(id)}>{label}</button>)}</nav>}
    {!settingsView&&(linkResults||mode==='cloud')&&<div className="content-stack pre-analysis-options">
    {!settingsView&&linkResults&&<section className="panel workspace-panel"><h2>{tr("SoundCloud-Suchtreffer")}</h2><p>{tr(linkResults.note)}</p>{!linkResults.candidates?.length&&<p>{tr("Keine Einzeltracks gefunden. Direkten Songlink verwenden.")}</p>}{linkResults.candidates?.map((r:any)=><div className="research-candidate" key={r.url}><span><strong>{r.title}</strong><small>{r.uploader}</small></span><button disabled={busy||!!versionWarning} onClick={()=>void importLink(r.url)}>{tr("Diesen Track importieren")}</button></div>)}</section>}
    {!settingsView&&mode==='cloud'&&<div className="cloud-notice"><label className="check"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/>{tr("Bei ausdrücklich gewähltem API-Modus dürfen in dieser Sitzung Audio und Lyrics an Google gesendet werden. Gratis-Kontingent, eigenes Projekt ohne Abrechnung.")}</label><button onClick={()=>setView('settings')}>{tr("Anbieter verwalten")}</button></div>}
    </div>}
    <input ref={file} type="file" accept=".mp3,.wav,.flac" hidden onChange={e=>{const f=e.target.files?.[0];if(f)void importAudio(f);e.target.value=''}}/>
    <input ref={lrcFile} type="file" accept=".lrc,.txt" hidden onChange={e=>{const f=e.target.files?.[0];if(f)f.text().then(setLyrics);e.target.value=''}}/>
    {liveMix&&<div className="live-mix-status" role="status">{tr(liveState==='error'?'Live-Mix konnte nicht gestartet werden. Originalmix verwenden oder die Live-Option ausschalten.':liveState==='loading'?'Live-Spuren werden synchronisiert …':'Live-Mix aktiv · Regler wirken sofort')}<button onClick={()=>{if(track)changeSource(`${API}/api/tracks/${track.id}/audio`,tr('Originalmix'))}}>{tr('Originalmix')}</button></div>}<ErrorNotice message={versionWarning}/>
    <ErrorNotice message={error} onDismiss={()=>setError('')}/>{activeJob&&<section className="job-banner" aria-label={tr('Laufender Auftrag')}><div role="status"><strong>{tr(message)}</strong><progress value={progress} max={100}/><small>{tr('Ein GPU-Schritt oder Netzwerkaufruf kann vor dem Abbruch noch auslaufen.')}</small></div><button disabled={cancelRequested} onClick={()=>{setCancelRequested(true);void api(`/jobs/${activeJob}/cancel`,json({})).catch(e=>{setCancelRequested(false);setError(String(e))})}}>{tr(cancelRequested?'Abbruch angefordert':'Abbrechen')}</button></section>}
    {!settingsView&&<section className="song-card" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();if(!busy&&!versionWarning&&e.dataTransfer.files[0])void importAudio(e.dataTransfer.files[0])}}><div className={`cover ${playing?'playing':''}`}><span aria-hidden="true">{trackInitials(track)}</span></div><div className="song-info"><div className="eyebrow">{track?tr("DEIN TRACK"):tr("DEIN NÄCHSTER FUND")}</div><h2>{track?.name||tr("Gib deinem Song eine neue Dimension")}</h2><p>{track?tr("{0} · Lokal importiert · WAV-Wiedergabe",[clock(track.duration)]):tr("MP3, WAV oder FLAC hier ablegen · bis 250 MB / 30 Min.")}</p></div><div className="song-status"><i/>{result?tr("Analyse bereit"):track?tr("Bereit zur Analyse"):tr("Warte auf Musik")}</div></section>}
    
    <div className="content-stack"><div className="content-stack" hidden={view!=='studio'}>{(track||view==='studio')&&<><SourceStudio evidenceRevision={cacheRevision} onModelChange={setStudioModel} onReady={()=>setStudioRevision(r=>r+1)} track={track} busy={busy||!!versionWarning} perform={perform} job={runJob} onSource={changeSource} liveActive={!!liveMix} onLiveMix={typeof AudioContext!=='undefined'?changeLiveMix:undefined}/><ManualFocus model={studioModel} revision={studioRevision} key={track?.id} track={track} busy={busy||!!versionWarning} perform={perform} job={runJob} onSource={changeSource}/></>}</div>
    {view==='timeline'&&<div className="analysis-layout"><div className="main-column"><section className="panel curve-panel"><div className="panel-heading"><div><span className="eyebrow">{tr("EMOTIONALE SIGNATUR")}</span><h2>{tr("Zwei Stimmen. Ein Song.")}</h2></div><div className="legend"><span><i className="mint"/>Audio Mood</span><span><i className="purple"/>Lyric Mood</span></div></div><div className="chart-labels"><span>{tr("POSITIV")}</span><span>{tr("VALENZ · −1 BIS +1")}</span></div><Chart result={result} duration={track?.duration||0} time={time} seek={seek} loopRange={loopRange} onLoopMark={markGraphLoop}/><p className="chart-interaction-hint">{tr('Ziehen zum Spulen · Rechtsklick setzt oder löscht den gemeinsamen A/B-Loop')}</p><div className="chart-foot"><span>{tr("NEGATIV")}</span><span>{result?`${result.device.toUpperCase()} · ${result.cached?tr("AUS CACHE"):result.mode==='cloud'?tr("API-ANALYSE"):tr("LOKALE INFERENZ")}`:tr("Keine Beispieldaten · Deine Analyse beginnt mit einem Song")}</span></div>{current&&<p className="confidence-hint">{tr("Modelltrennschärfe:")} {current.confidence!==undefined?(current.confidence*100).toFixed(0)+' %':tr("nicht verfügbar")} {tr("· keine kalibrierte Genauigkeit.")} <button onClick={()=>setView('interpretation')}>{tr("Aktuelle Stelle erklären")}</button></p>}</section>
    <div className="stats"><section className="panel stat"><span className="eyebrow"><i className="mint"/> AUDIO MOOD</span><strong>{current?current.valence.toFixed(2):'—'}</strong><p>{tr("Wie die Musik klingt")}</p><span className="model-label">{tr("CLAP · Zero-Shot-Musikemotion")}</span></section><section className="panel stat"><span className="eyebrow"><i className="purple"/> LYRIC MOOD</span><strong>{index>=0?result!.lyrics[index].valence.toFixed(2):'—'}</strong><p>{tr("Was die Worte ausdrücken")}</p><span className="model-label">{tr("XLM-EMO · mehrsprachig")}</span></section><section className="panel stat split"><span className="eyebrow"> BIGGEST SPLIT</span><strong>{result?.split?`${(result.split.gap/2*100).toFixed(0)} %`:'—'}</strong><p>{result?.split?tr("Größter Kontrast bei {0}",[clock(result.split.start)]):tr("Wo Klang und Text sich trennen")}</p><button disabled={!result?.split} onClick={()=>seek(result!.split!.start)}>{tr("Zum Moment springen")} </button></section></div>
    <section className="panel setup"><div className="panel-heading"><h2>{tr("Deine Analyse")}</h2><span className="step-label">{tr("01 IMPORT 02 LYRICS 03 ENTDECKEN")}</span></div><div className="search-row"><label>{tr("Interpret")}<input value={artist} onChange={e=>setArtist(e.target.value)} placeholder={tr("Interpret")} disabled={busy||!!versionWarning}/></label><label>{tr("Songtitel")}<input value={title} onChange={e=>setTitle(e.target.value)} placeholder={tr("Songtitel")} disabled={busy||!!versionWarning}/></label><button disabled={!track||busy||!artist.trim()||!title.trim()} onClick={()=>void perform(async()=>{setMessage(tr("Suche bei LRCLIB …"));const r=await api(`/tracks/${track!.id}/lyrics/search`,json({artist,title}));setLyrics(r.text);setMessage(r.instrumental?tr("Instrumental erkannt"):r.synced?tr("Synchronisierte Lyrics gefunden"):tr("Nur Text ohne Zeitstempel gefunden – Whisper für Synchronisierung aktivieren"))})}>{tr("Lyrics suchen")} </button><button disabled={busy||!!versionWarning} onClick={()=>lrcFile.current?.click()}>{tr("LRC importieren")}</button></div><textarea value={lyrics} disabled={busy||!!versionWarning} onChange={e=>setLyrics(e.target.value)} placeholder={tr("Synchronisierte Lyrics einfügen, z. B. [00:12.50] Deine erste Zeile …")}/><div className="quality-controls"><label>{tr("Verlaufsraster")}<select aria-label={tr("Verlaufsraster")} value={resolution} disabled={busy||!!versionWarning} onChange={e=>setResolution(Number(e.target.value))}><option value={2}>{tr("Fein · 2 Sekunden")}</option><option value={5}>{tr("Standard · 5 Sekunden")}</option></select></label><label>{tr("Whisper-Modell")}<select aria-label={tr("Texterkennungsmodell")} value={recognitionModel} disabled={busy||!!versionWarning} onChange={e=>setRecognitionModel(e.target.value)}>{whisperChoices.length?whisperChoices.map(m=><option key={m.id} value={m.id}>{tr(m.name)}</option>):<option value="whisper-turbo">Whisper Large v3 Turbo</option>}</select></label><label>{tr("Texterkennungsquelle")}<select aria-label={tr("Texterkennungsquelle")} value={recognitionSource} disabled={busy||!!versionWarning} onChange={e=>setRecognitionSource(e.target.value)}><option value="vocals">{tr("Gesang trennen und erkennen")}</option><option value="mix">{tr("Originalmix vergleichen")}</option><option value="auto">{tr("Vorhandene Gesangsspur, sonst Mix")}</option></select></label><label>{tr("Sprache")}<select aria-label={tr("Texterkennungssprache")} value={recognitionLanguage} disabled={busy||!!versionWarning} onChange={e=>setRecognitionLanguage(e.target.value)}><option value="">{tr("Automatisch")}</option><option value="en">{tr("Englisch")}</option><option value="de">{tr("Deutsch")}</option></select></label></div><p className="confidence-hint">{tr("Die präzise Texterkennung nutzt überlappende Abschnitte ohne Sprachaktivitätsfilter. Bei Mashups ggf. Mix und Gesang vergleichen und Text korrigieren. Ein feineres Raster ist keine höhere Genauigkeitsgarantie.")}</p><div className="analyze-row"><button disabled={!track||busy||!!versionWarning||mode!=='local'} onClick={()=>void recognize()}>{tr("Text lokal erkennen")}</button><label className="check"><input type="checkbox" checked={whisper} disabled={busy||!!versionWarning} onChange={e=>setWhisper(e.target.checked)}/>{tr("Whisper-Fallback, falls keine LRC-Zeitstempel vorliegen")}</label><button className="primary" onClick={()=>void analyze()} disabled={!track||busy||!!versionWarning}>{busy?tr("Analyse läuft …"):result?tr("Neu analysieren"):tr("Song analysieren")}</button></div>{message&&!activeJob&&<div className="progress" role="status"><span>{tr(message)}</span>{busy&&<progress value={progress} max="100"/>}</div>}{result?.text_coverage&&<div className="coverage-report"><strong>{result.text_coverage.segments} {tr("Textsegmente ·")} {result.text_coverage.words} {tr("Wörter")}</strong><p>{tr(result.text_coverage.note)}</p>{result.text_coverage.gaps.length>0&&<><p>{tr("Bereiche ohne erkannten Text · zum Anhören klicken:")}</p><div>{result.text_coverage.gaps.map(g=><button key={g.start} onClick={()=>seek(g.start)}>{clock(g.start)}–{clock(g.end)}</button>)}</div></>}</div>}{result?.warnings.map(w=><p key={tr(w)} className="warning">{tr(w)}</p>)}</section>
    </div><section className="panel lyric-panel"><div className="panel-heading"><h2>{tr("Zwischen den Zeilen")}</h2><button className="lyrics-follow" aria-pressed={followLyrics} onClick={()=>setFollowLyrics(v=>!v)}>{tr(followLyrics?'Auto-Scroll an':'Lyrics folgen')}</button></div><div className="lyrics-scroll" ref={lyricScroll} onWheel={()=>setFollowLyrics(false)} onPointerDown={()=>setFollowLyrics(false)} onKeyDown={e=>{if(['PageUp','PageDown','ArrowUp','ArrowDown','Home','End'].includes(e.key))setFollowLyrics(false)}} onTouchStart={()=>setFollowLyrics(false)}>{result?.lyrics.length?result.lyrics.map((line,i)=><button key={i} className={`lyric-row ${i===index?'active':''}`} onClick={()=>seek(line.start)}><time>{clock(line.start)}</time><span>{line.text}{line.uncertain&&<em className="asr-uncertain">{tr("Automatische Texterkennung unsicher · bitte prüfen")}</em>}</span><small>{line.valence.toFixed(2)}</small></button>):<div className="lyrics-empty"><span></span><h3>{tr("Worte werden zu Gefühl.")}</h3><p>{tr("Importiere eine LRC-Datei, suche bei LRCLIB oder lasse Whisper lokal transkribieren.")}</p></div>}</div><div className="lyric-footer">{tr("Modellschätzungen sind keine objektive Emotionsmessung. Gesang und Kontext können die Werte beeinflussen.")}</div></section></div>}
    {view==='report'&&<AnalysisReport track={track} analysis={result} time={time} onSeek={seek} onReanalyse={()=>void analyze()} busy={busy||!!versionWarning}/>}
    {view==='report'&&track&&<ExpressionComparison key={track.id} track={track} analysis={result} time={time} onSeek={seek} busy={busy||!!versionWarning} perform={perform} job={runJob}/>}
    {view==='settings'&&mode==='local'&&<DeviceSettings onSaved={()=>void api('/health').then(r=>{setDevice(String(r.device).startsWith('cuda')?'NVIDIA CUDA':tr("CPU lokal"));setDeviceName(r.device_name||'')}).catch(()=>{})} busy={busy||!!versionWarning} perform={perform}/>}<div hidden={view==='timeline'||view==='studio'||view==='report'||view==='prompts'||(view==='settings'&&mode==='cloud')}><Workspace cacheRevision={cacheRevision} onProviderChange={setTextProvider} view={view} track={track} analysis={result} time={time} mode={mode} consent={consent} busy={busy||!!versionWarning} perform={perform} job={runJob} onPrepareDelete={prepareDeletion} onOpen={t=>void perform(async()=>{setView('timeline');await acceptTrack(t)})} onSongDeleted={ids=>{if(ids&&track&&!ids.includes(track.id))return;mediaEpoch.current++;releaseLive();audio.current?.pause();setTrack(null);setResult(null);setLyrics('');setSourceUrl('');setSourceLabel(tr("Originalmix"));setTime(0);setPlaying(false)}} onCacheDeleted={ids=>{if(track&&ids.includes(track.id)){changeSource(`${API}/api/tracks/${track.id}/audio`,tr('Originalmix'));setResult(null);setLyrics('');setCacheRevision(r=>r+1)}}}/></div>
    {view==='details'&&<><SourceMetadata track={track}/><OnlineFacts key={`${track?.id}:${cacheRevision}`} track={track} busy={busy} perform={perform} job={runJob}/></>}
    {view==='prompts'&&<PromptManager key={mode} mode={mode} busy={busy||!!versionWarning} perform={perform}/>}
    {view==='settings'&&<>{mode==='cloud'&&<ProviderSettings busy={busy||!!versionWarning} perform={perform}/>}<DiagnosticPanel perform={perform}/></>}
    {view!=='timeline'&&message&&!activeJob&&<div className="progress" role="status">{tr(message)}{busy&&<progress value={progress} max="100"/>}</div>}
    </div><footer><span>MOODSCOPE / EXPLORING THE SPACE BETWEEN</span><span>{tr(mode==='cloud'?'API nur nach Zustimmung · Lyrics-Suche und Downloads separat':"Analyse lokal · LRCLIB nur bei Suche · Modelldownload beim ersten Start")}</span></footer>
  </main><div className={`player ${ambient?'atmosphere-on':''}`} style={{'--mood-hue':moodHue(current)} as React.CSSProperties}><div className="player-track"><div className="tiny-cover" aria-hidden="true">{trackInitials(track)}</div><div><strong>{track?.name||tr("Noch kein Song")}</strong><span>{track?tr(sourceLabel):tr('Bereit, wenn du es bist.')}</span></div></div><button className="ambient-toggle" data-tooltip={tr('Mischt die Farbanteile von Freude, Ruhe, Trauer, Ärger, Angst und Zärtlichkeit weich. Farben sind eine Gestaltungswahl, keine zusätzliche Emotionsmessung.')} aria-pressed={ambient} onClick={()=>setAmbient(v=>!v)}>{tr('Atmosphäre')}</button><div className="transport"><button aria-label={tr("10 Sekunden zurück")} disabled={!track} onClick={()=>seek(Math.max(0,time-10))}>-10s</button><button className="play" aria-label={playing?'Pause':tr("Abspielen")} disabled={!track} onClick={togglePlayback}><svg viewBox='0 0 24 24' aria-hidden='true'>{playing?<path d='M6 4h4v16H6zm8 0h4v16h-4z'/>:<path d='M7 3l15 9L7 21z'/>}</svg></button><button aria-label={tr("10 Sekunden vor")} disabled={!track} onClick={()=>seek(Math.min(track!.duration,time+10))}>+10s</button></div><span className="player-time">{clock(time)}</span><LoopScrubber key={track?.id} duration={track?.duration||0} time={time} disabled={!track} onSeek={seek} range={loopRange} onLoopChange={range=>{loopRef.current=range;setLoopRange(range)}}/><span className="player-time">{clock(track?.duration||0)}</span><label className="volume">VOL <input aria-label={tr("Lautstärke")} type="range" min="0" max="1" step=".01" defaultValue=".8" onChange={e=>{volume.current=Number(e.target.value);if(audio.current)audio.current.volume=volume.current}}/></label></div>
    <audio key={playbackSession} ref={audio} preload="auto" src={track?(sourceUrl||`${API}/api/tracks/${track.id}/audio`):undefined}
      onLoadedMetadata={e=>{const element=e.currentTarget;if(element!==audio.current)return;element.volume=volume.current;const pending=playbackRestore.current;if(!pending)return;if(pending.epoch!==undefined&&pending.epoch!==mediaEpoch.current)return;if(pending.url&&element.src!==pending.url)return;playbackRestore.current=null;element.currentTime=Math.min(pending.time,Number.isFinite(element.duration)?element.duration:pending.time);if(pending.playing)playMedia(element)}}
      onPlay={e=>{if(e.currentTarget===audio.current)setPlaying(!e.currentTarget.paused)}} onPlaying={e=>{if(e.currentTarget===audio.current)setPlaying(!e.currentTarget.paused)}}
      onPause={e=>{if(e.currentTarget===audio.current)setPlaying(!e.currentTarget.paused)}} onEmptied={e=>{if(e.currentTarget===audio.current)setPlaying(!e.currentTarget.paused)}} onAbort={e=>{if(e.currentTarget===audio.current)setPlaying(!e.currentTarget.paused)}}
      onEnded={()=>setPlaying(false)} onError={e=>{if(e.currentTarget===audio.current&&track){setPlaying(false);setError(tr("Audio-Wiedergabe fehlgeschlagen"))}}}/>

  </div></AtmosphereThemeContext.Provider>
}
const root=document.getElementById('root');
if(root)createRoot(root).render(<App/>);
