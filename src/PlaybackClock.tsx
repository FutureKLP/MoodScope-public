import {ReactNode,RefObject,useEffect,useState,useSyncExternalStore} from 'react';
import {LoopRange} from './LoopScrubber';

/** The media element remains the clock. Only time-dependent views subscribe. */
export function createPlaybackClock(){
 let time=0;
 const listeners=new Set<()=>void>();
 return {
  getSnapshot:()=>time,
  subscribe:(listener:()=>void)=>{listeners.add(listener);return()=>{listeners.delete(listener)}},
  setTime:(value:number)=>{if(Object.is(time,value))return;time=value;listeners.forEach(listener=>listener())},
 };
}
export type PlaybackClock=ReturnType<typeof createPlaybackClock>;

export function usePlaybackClock(media:RefObject<HTMLAudioElement|null>,loop:RefObject<LoopRange|null>,session:number,enabled=true){
 const [clock]=useState(createPlaybackClock);
 useEffect(()=>{
  const element=media.current;if(!element||!enabled)return;
  let frame:number|null=null,waiting=false,disposed=false;
  const stop=()=>{if(frame!==null)cancelAnimationFrame(frame);frame=null};
  const sample=()=>{
   const range=loop.current;
   if(range?.b!==null&&range&&!element.paused&&element.currentTime>=range.b)element.currentTime=range.a;
   clock.setTime(element.currentTime);
  };
  const tick=()=>{frame=null;if(disposed||element.paused||element.ended||waiting)return;sample();frame=requestAnimationFrame(tick)};
  const start=()=>{waiting=false;sample();if(frame===null&&!element.paused&&!element.ended)frame=requestAnimationFrame(tick)};
  const pause=()=>{stop();sample()};
  const buffer=()=>{waiting=true;pause()};
  const listeners:Record<string,()=>void>={play:start,playing:start,pause,ended:pause,waiting:buffer,emptied:pause,abort:pause,error:pause,seeked:sample,timeupdate:sample,loadedmetadata:sample};
  for(const [event,listener] of Object.entries(listeners))element.addEventListener(event,listener);
  start();
  return()=>{disposed=true;stop();for(const [event,listener] of Object.entries(listeners))element.removeEventListener(event,listener)};
 },[clock,media,loop,session,enabled]);
 return clock;
}

const idleSubscribe=()=>()=>{};
export function usePlaybackTime(clock:PlaybackClock,live=true){
 return useSyncExternalStore(live?clock.subscribe:idleSubscribe,clock.getSnapshot,clock.getSnapshot);
}
export function PlaybackTime({clock,live=true,children}:{clock:PlaybackClock;live?:boolean;children:(time:number)=>ReactNode}){
 return children(usePlaybackTime(clock,live));
}
