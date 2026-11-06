import {useLayoutEffect,useRef} from 'react';

/** Scroll only the transcript/chord container; never move the document. */
export function useAutoFollow(activeKey:string|number,enabled:boolean){
 const ref=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{
  const container=ref.current;if(!container||!enabled)return;
  let frame=0,stopped=false;
  const cancel=()=>{stopped=true;cancelAnimationFrame(frame)};
  const follow=()=>{
   const active=container.querySelector('[aria-current="true"],.lyric-row.active,[aria-pressed="true"]');
   if(!active||!container.clientHeight)return;
   const box=container.getBoundingClientRect(),row=active.getBoundingClientRect();
   const target=Math.max(0,Math.min(container.scrollHeight-container.clientHeight,container.scrollTop+row.top-box.top-container.clientTop-container.clientHeight*.45+row.height/2));
   cancelAnimationFrame(frame);stopped=false;
   if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches){container.scrollTop=target;return}
   let previous=performance.now();
   const tick=(now:number)=>{if(stopped)return;const delta=target-container.scrollTop;container.scrollTop+=delta*(1-Math.exp(-Math.min(64,Math.max(1,now-previous))/70));previous=now;if(Math.abs(delta)>.5)frame=requestAnimationFrame(tick);else container.scrollTop=target};
   frame=requestAnimationFrame(tick);
  };
  container.addEventListener('wheel',cancel,{passive:true});container.addEventListener('touchstart',cancel,{passive:true});container.addEventListener('pointerdown',cancel);
  const observer=typeof ResizeObserver==='undefined'?null:new ResizeObserver(follow);observer?.observe(container);follow();
  return()=>{cancel();observer?.disconnect();container.removeEventListener('wheel',cancel);container.removeEventListener('touchstart',cancel);container.removeEventListener('pointerdown',cancel)};
 },[activeKey,enabled]);
 return ref;
}
