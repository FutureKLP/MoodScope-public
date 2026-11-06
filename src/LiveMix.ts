import {RefObject,useEffect,useRef,useState} from 'react';
import {API} from './api';
export type LiveMixConfig={trackId:string;model:string;sources:string[];selected:string[];gains:Record<string,number>};

export class LiveStemMixer{
 readonly context:AudioContext;
 readonly channels:Array<{name:string;audio:HTMLAudioElement;gain:GainNode;node:MediaElementAudioSourceNode}>;
 private output:GainNode;private frame=0;private lastSync=0;private lastHardSync=-Infinity;private disposed=false;private generation=0;private starting=false;private active=false;private waiting=false;private priorMuted:boolean;
 private listeners:Array<[string,EventListener]>=[];
 constructor(private master:HTMLAudioElement,urls:Record<string,string>,private report:(state:string)=>void){
  this.context=new AudioContext();this.output=this.context.createGain();this.output.gain.value=0;this.output.connect(this.context.destination);this.priorMuted=master.muted;
  this.channels=Object.entries(urls).map(([name,url])=>{const audio=new Audio();audio.crossOrigin='anonymous';audio.preload='auto';audio.src=url;if(master.parentElement){audio.hidden=true;audio.dataset.moodscopeStem=name;master.parentElement.append(audio)}const gain=this.context.createGain();gain.gain.value=0;const node=this.context.createMediaElementSource(audio);node.connect(gain);gain.connect(this.output);audio.addEventListener('error',()=>{if(!this.disposed){this.report('error');this.dispose()}});return {name,audio,gain,node}});
  const listen=(event:string,fn:()=>void)=>{const callback=fn as EventListener;master.addEventListener(event,callback);this.listeners.push([event,callback])};
  listen('play',()=>void this.activate());listen('playing',()=>{this.waiting=false;void this.activate()});listen('waiting',()=>{this.waiting=true;this.pause()});listen('pause',()=>this.pause());listen('ended',()=>this.pause());listen('seeked',()=>{this.sync(true);if(!master.paused&&!this.waiting)void this.activate()});listen('ratechange',()=>this.sync());listen('volumechange',()=>this.volume());
  this.report('ready');if(!master.paused)void this.activate();
 }
 setLevels(selected:string[],gains:Record<string,number>){if(this.disposed)return;for(const channel of this.channels){const value=selected.includes(channel.name)?Math.max(0,Math.min(1,gains[channel.name]??1)):0;channel.gain.gain.setTargetAtTime(value,this.context.currentTime,.015)}}
 private volume(){if(!this.disposed)this.output.gain.setTargetAtTime(this.master.paused?0:this.master.volume,this.context.currentTime,.02)}
 private sync(force=false){
  const now=performance.now();
  // Repeated 90 ms seeks reset streaming decoders. Correct small clock drift
  // gradually, and allow a shared hard correction only when every stem is ready.
  const hard=force||(now-this.lastHardSync>5000&&this.channels.every(c=>c.audio.readyState>=3&&!c.audio.seeking)&&this.channels.some(c=>Math.abs(c.audio.currentTime-this.master.currentTime)>1.25));
  for(const {audio} of this.channels){const drift=this.master.currentTime-audio.currentTime;audio.playbackRate=this.master.playbackRate*(hard||Math.abs(drift)<.04?1:1+Math.max(-.015,Math.min(.015,drift*.03)));if(hard)audio.currentTime=this.master.currentTime}
  if(hard)this.lastHardSync=now;
 }
 private tick=()=>{if(this.disposed||this.master.paused||this.waiting)return;if(performance.now()-this.lastSync>250){this.sync();this.lastSync=performance.now()}this.frame=requestAnimationFrame(this.tick)};
 private async activate(){
  if(this.disposed||this.starting||this.active||this.waiting)return;this.starting=true;const generation=++this.generation;this.report('loading');
  try{await this.context.resume();if(this.disposed||this.master.paused||generation!==this.generation)return;this.sync(true);await Promise.all(this.channels.map(c=>c.audio.play()));if(this.disposed||this.master.paused||generation!==this.generation)return;this.active=true;this.master.muted=true;this.volume();this.report('playing');cancelAnimationFrame(this.frame);this.tick()}
  catch{if(!this.disposed&&!this.master.paused&&generation===this.generation){this.report('error');this.dispose()}}
  finally{this.starting=false;if(!this.disposed&&!this.master.paused&&!this.waiting&&generation!==this.generation)void this.activate()}
 }
 private pause(){this.generation++;this.active=false;for(const {audio} of this.channels)audio.pause();if(!this.disposed)this.output.gain.setTargetAtTime(0,this.context.currentTime,.015);cancelAnimationFrame(this.frame);this.report('ready')}
 dispose(){if(this.disposed)return;this.disposed=true;this.generation++;cancelAnimationFrame(this.frame);for(const [event,listener] of this.listeners)this.master.removeEventListener(event,listener);for(const {audio,node,gain} of this.channels){audio.pause();audio.removeAttribute('src');audio.load();audio.remove?.();node.disconnect();gain.disconnect()}this.output.disconnect();void this.context.close();this.master.muted=this.priorMuted}
}

export function useLiveMix(master:RefObject<HTMLAudioElement|null>,config:LiveMixConfig|null,stopRef?:RefObject<(()=>void)|null>){
 const mixer=useRef<LiveStemMixer|null>(null),latest=useRef(config);latest.current=config;const [state,setState]=useState('');
 useEffect(()=>{if(!stopRef)return;stopRef.current=()=>{mixer.current?.dispose();mixer.current=null;setState('')};return()=>{stopRef.current=null}},[stopRef]);
 const key=config?`${config.trackId}:${config.model}:${config.sources.join(',')}`:'';
 useEffect(()=>{if(!key||!master.current||!latest.current){setState('');return}try{const current=latest.current;const urls=Object.fromEntries(current.sources.map(source=>[source,`${API}/api/tracks/${current.trackId}/mix?model=${current.model}&sources=${source}`]));mixer.current=new LiveStemMixer(master.current,urls,setState);mixer.current.setLevels(current.selected,current.gains)}catch{setState('error')}return()=>{mixer.current?.dispose();mixer.current=null}},[key,master]);
 useEffect(()=>{if(config)mixer.current?.setLevels(config.selected,config.gains)},[config]);
 return state;
}
