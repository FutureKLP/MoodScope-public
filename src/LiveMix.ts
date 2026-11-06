import {RefObject,useEffect,useRef,useState} from 'react';
import {API} from './api';
export type LiveMixConfig={trackId:string;model:string;sources:string[];selected:string[];gains:Record<string,number>};

export class LiveStemMixer{
 readonly context:AudioContext;
 readonly channels:Array<{name:string;audio:HTMLAudioElement;gain:GainNode;node:MediaElementAudioSourceNode}>;
 private output:GainNode;private frame=0;private lastSync=0;private disposed=false;private generation=0;private starting=false;private priorMuted:boolean;
 private listeners:Array<[string,EventListener]>=[];
 constructor(private master:HTMLAudioElement,urls:Record<string,string>,private report:(state:string)=>void){
  this.context=new AudioContext();this.output=this.context.createGain();this.output.gain.value=0;this.output.connect(this.context.destination);this.priorMuted=master.muted;
  this.channels=Object.entries(urls).map(([name,url])=>{const audio=new Audio();audio.crossOrigin='anonymous';audio.preload='auto';audio.src=url;const gain=this.context.createGain();gain.gain.value=0;const node=this.context.createMediaElementSource(audio);node.connect(gain);gain.connect(this.output);audio.addEventListener('error',()=>{if(!this.disposed){this.report('error');this.dispose()}});return {name,audio,gain,node}});
  const listen=(event:string,fn:()=>void)=>{const callback=fn as EventListener;master.addEventListener(event,callback);this.listeners.push([event,callback])};
  listen('play',()=>void this.activate());listen('pause',()=>this.pause());listen('ended',()=>this.pause());listen('seeked',()=>{this.sync(true);if(!master.paused)void this.activate()});listen('ratechange',()=>this.sync(true));listen('volumechange',()=>this.volume());
  this.report('ready');if(!master.paused)void this.activate();
 }
 setLevels(selected:string[],gains:Record<string,number>){if(this.disposed)return;for(const channel of this.channels){const value=selected.includes(channel.name)?Math.max(0,Math.min(1,gains[channel.name]??1)):0;channel.gain.gain.setTargetAtTime(value,this.context.currentTime,.015)}}
 private volume(){if(!this.disposed)this.output.gain.setTargetAtTime(this.master.paused?0:this.master.volume,this.context.currentTime,.02)}
 private sync(force=false){for(const {audio} of this.channels){audio.playbackRate=this.master.playbackRate;if(force||Math.abs(audio.currentTime-this.master.currentTime)>.09)audio.currentTime=this.master.currentTime}}
 private tick=()=>{if(this.disposed||this.master.paused)return;if(performance.now()-this.lastSync>250){this.sync();this.lastSync=performance.now()}this.frame=requestAnimationFrame(this.tick)};
 private async activate(){
  if(this.disposed||this.starting)return;this.starting=true;const generation=++this.generation;this.report('loading');
  try{await this.context.resume();if(this.disposed||this.master.paused||generation!==this.generation)return;this.sync(true);await Promise.all(this.channels.map(c=>c.audio.play()));if(this.disposed||this.master.paused||generation!==this.generation)return;this.sync(true);this.master.muted=true;this.volume();this.report('playing');cancelAnimationFrame(this.frame);this.tick()}
  catch{if(!this.disposed&&!this.master.paused&&generation===this.generation){this.report('error');this.dispose()}}
  finally{this.starting=false;if(!this.disposed&&!this.master.paused&&generation!==this.generation)void this.activate()}
 }
 private pause(){this.generation++;for(const {audio} of this.channels)audio.pause();if(!this.disposed)this.output.gain.setTargetAtTime(0,this.context.currentTime,.015);cancelAnimationFrame(this.frame);this.report('ready')}
 dispose(){if(this.disposed)return;this.disposed=true;this.generation++;cancelAnimationFrame(this.frame);for(const [event,listener] of this.listeners)this.master.removeEventListener(event,listener);for(const {audio,node,gain} of this.channels){audio.pause();audio.removeAttribute('src');audio.load();node.disconnect();gain.disconnect()}this.output.disconnect();void this.context.close();this.master.muted=this.priorMuted}
}

export function useLiveMix(master:RefObject<HTMLAudioElement|null>,config:LiveMixConfig|null){
 const mixer=useRef<LiveStemMixer|null>(null),latest=useRef(config);latest.current=config;const [state,setState]=useState('');
 const key=config?`${config.trackId}:${config.model}:${config.sources.join(',')}`:'';
 useEffect(()=>{if(!key||!master.current||!latest.current){setState('');return}try{const current=latest.current;const urls=Object.fromEntries(current.sources.map(source=>[source,`${API}/api/tracks/${current.trackId}/mix?model=${current.model}&sources=${source}`]));mixer.current=new LiveStemMixer(master.current,urls,setState);mixer.current.setLevels(current.selected,current.gains)}catch{setState('error')}return()=>{mixer.current?.dispose();mixer.current=null}},[key,master]);
 useEffect(()=>{if(config)mixer.current?.setLevels(config.selected,config.gains)},[config]);
 return state;
}
