import React,{Profiler} from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {App,Chart} from '../../src/main';
import {Analysis} from '../../src/types';
import {setLanguage} from '../../src/i18n';

// Formula-generated display fixtures, never model outputs. API replies are
// immediate mocks, so song/model latency excludes real HTTP/backend latency.
const duration=180;
function analysis(seconds:number):Analysis{
 const audio=Array.from({length:Math.ceil(seconds/2)},(_,i)=>({start:i*2,end:Math.min(seconds,i*2+2),valence:.6*Math.sin(i/8),arousal:.4,scores:{joy:.6,calm:.2,sadness:.1,anger:.02,fear:.03,tenderness:.05}}));
 return {audio,lyrics:audio.filter((_,i)=>i%3===0).map((p,i)=>({...p,text:`Synthetic line ${i}`,scores:{joy:.7,sadness:.1,anger:.1,fear:.1}})),split:null,warnings:[],cached:true,device:'fixture',mode:'local',method:'Synthetic display fixture',models:{audio:'fixture',lyrics:'fixture'}};
}
const stored=analysis(duration);
const tracks=['a','b'].map(id=>({id,name:`Synthetic ${id}.wav`,duration}));
let requests=0;
window.fetch=async(input,init)=>{
 requests++;
 const url=new URL(String(input),location.origin),path=url.pathname.replace(/^\/api/,'');
 let value:unknown={};
 if(path==='/health')value={device:'cpu',device_name:'Benchmark mock',api_revision:16};
 else if(path==='/library')value={tracks};
 else if(path==='/models')value={models:[],active:{whisper:'whisper-base'}};
 else if(path==='/settings')value={cloud:{configured:false}};
 else if(path==='/provider-routes')value={routes:{audio:'local',lyrics:'local',transcription:'local',instruments:'local',interpretation:'local'},targets:{},version:'synthetic'};
 else if(path==='/providers')value={profiles:[]};
 else if(path.endsWith('/analysis')){
  if(url.searchParams.get('mode')==='cloud')return new Response('{}',{status:404});
  value=stored;
 }else if(path.endsWith('/notes'))value={interpretation:'',instruments:'',personnel:'',genre:'',bpm:null};
 else if(path.endsWith('/expression-comparison'))value={ready:true,stale:false,result:{rows:stored.audio.map(p=>({...p,tags:{happy:.6,calm:.3,energetic:.2}}))}};
 else if(path.endsWith('/interpretation'))value={};
 else if(path==='/expression-comparison/status')value={ready:false};
 return new Response(JSON.stringify(value),{headers:{'Content-Type':'application/json'}});
};
localStorage.clear();setLanguage('de');localStorage.setItem('moodscope-audio-curve-model','clap');
const commits:Array<{id:string;ms:number;at:number}>=[];
const onRender:React.ProfilerOnRenderCallback=(id,_phase,actual)=>commits.push({id,ms:actual,at:performance.now()});
const root=createRoot(document.getElementById('benchmark-root')!);
const sleep=(ms:number)=>new Promise(r=>setTimeout(r,ms));
const frame=()=>new Promise(r=>requestAnimationFrame(r));
function stats(values:number[]){const s=[...values].sort((a,b)=>a-b);return {n:s.length,min:s[0],median:s.length%2?s[(s.length-1)/2]:(s[s.length/2-1]+s[s.length/2])/2,p95:s[Math.max(0,Math.ceil(s.length*.95)-1)],max:s.at(-1)}}
function button(name:string){const b=[...document.querySelectorAll<HTMLButtonElement>('button')].find(b=>(b.getAttribute('aria-label')||b.textContent?.trim())===name);if(!b)throw Error('Missing benchmark control: '+name);return b}
async function click(name:string){button(name).click();await frame();await frame();await sleep(60)}
async function openSong(index:number){await click('Bibliothek');const choices=[...document.querySelectorAll<HTMLButtonElement>('.library-card button')].filter(b=>b.textContent==='Öffnen');if(!choices[index])throw Error('Missing fixture song');const start=performance.now();choices[index].click();while(document.querySelector('.player-track strong')?.textContent!==tracks[index].name||!document.querySelector('.audio-path')){if(performance.now()-start>2000)throw Error('Song fixture did not render');await frame()}await frame();await frame();const elapsed=performance.now()-start;await sleep(80);return elapsed}
async function windowSample(name:string,ms=5000){
 (window as any).benchmarkPhase=name;
 const from=commits.length,start=performance.now(),deltas:number[]=[];let previous=start;
 while(performance.now()-start<ms){await frame();const now=performance.now();deltas.push(now-previous);previous=now}
 const rows=commits.slice(from),elapsed=performance.now()-start;
 (window as any).benchmarkPhase='transition';
 return {name,wall_ms:elapsed,commits:rows.length,commits_per_second:rows.length/(elapsed/1000),react_actual_ms:stats(rows.map(r=>r.ms)),frame_interval_ms:stats(deltas),frames_over_33ms:deltas.filter(v=>v>33.34).length,requests};
}
async function run(){
 const report:any={schema:1,mode:'production React profiling; mocked API; actual HTML audio and RAF',viewport:[innerWidth,innerHeight],user_agent:navigator.userAgent,time_origin:performance.timeOrigin,rows:[]};
 const start=performance.now();flushSync(()=>root.render(<Profiler id="App" onRender={onRender}><App/></Profiler>));await frame();await frame();
 report.mount_to_two_frames_ms=performance.now()-start;
 await sleep(250);await openSong(0);await click('Stimmungsverlauf');
 report.rows.push(await windowSample('app_paused_atmosphere_off',2000));
 await click('Abspielen');
 const media=document.querySelector('audio')!;if(media.paused)throw Error('Actual audio playback did not start');
 report.rows.push(await windowSample('app_playing_atmosphere_off'));
 await click('Atmosphäre');report.rows.push(await windowSample('app_playing_atmosphere_on'));
 await click('Pause');await click('Atmosphäre');
 const switches=[];for(let i=0;i<6;i++)switches.push(await openSong(i%2));
 report.song_switch_mocked_ui_ms=stats(switches);report.song_switch_includes_fixed_wait_ms=0;
 const models=[];for(const name of ['Music2Emo verwenden','CLAP verwenden','Music2Emo verwenden','CLAP verwenden','Music2Emo verwenden','CLAP verwenden']){const t=performance.now();button(name).click();await frame();await frame();models.push(performance.now()-t)}report.cached_curve_model_switch_to_two_frames_ms=stats(models);
 // UI mode/cache transition; not a model weight load.
 const modes=[];for(const mode of ['cloud','local','cloud','local','cloud','local']){const select=document.querySelector<HTMLSelectElement>('select[aria-label="Analysemodus"]')!;const t=performance.now();select.value=mode;select.dispatchEvent(new Event('change',{bubbles:true}));await frame();await frame();modes.push(performance.now()-t)}report.local_api_switch_to_two_frames_ms=stats(modes);
 const chart=analysis(1800);
 for(const size of [180,1800]){
  const value=size===180?stored:chart;const times=[];const offset=commits.length;
  for(let i=0;i<180;i++){const t=performance.now();flushSync(()=>root.render(<Profiler id="Chart" onRender={onRender}><Chart result={value} duration={size} time={i/60} seek={()=>{}}/></Profiler>));times.push(performance.now()-t);await frame()}
  report.rows.push({name:`chart_${size}s_2s_grid_180_updates`,update_wall_ms:stats(times),react_actual_ms:stats(commits.slice(offset).map(r=>r.ms)),points:value.audio.length,lyric_segments:value.lyrics.length});
 }
 report.commits_total=commits.length;report.requests=requests;
 report.navigation=performance.getEntriesByType('navigation').map(n=>n.toJSON());report.paint=performance.getEntriesByType('paint').map(n=>n.toJSON());
 (window as any).benchmarkReport=report;document.title='MoodScope benchmark complete';
}
run().catch(e=>{(window as any).benchmarkError=String(e);document.title='MoodScope benchmark failed'});
