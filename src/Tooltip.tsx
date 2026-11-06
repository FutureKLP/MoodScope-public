import {useEffect,useState} from 'react';
import {createPortal} from 'react-dom';

export function TooltipLayer(){
 const [tip,setTip]=useState<{text:string;left:number;top:number;above:boolean}|null>(null);
 useEffect(()=>{
  let timer:ReturnType<typeof setTimeout>|undefined,anchor:Element|null=null,previous:string|null=null,frame=0,pointer:{x:number;y:number}|null=null;
  const position=()=>{if(pointer)return {left:Math.max(12,Math.min(window.innerWidth-332,pointer.x+14)),top:pointer.y>window.innerHeight-100?pointer.y-14:pointer.y+18,above:pointer.y>window.innerHeight-100};const rect=anchor!.getBoundingClientRect();return {left:Math.max(12,Math.min(window.innerWidth-332,rect.left+rect.width/2-160)),top:rect.top>100?rect.top-12:rect.bottom+12,above:rect.top>100}};
  const hide=()=>{clearTimeout(timer);cancelAnimationFrame(frame);if(anchor){if(previous===null)anchor.removeAttribute('aria-describedby');else anchor.setAttribute('aria-describedby',previous)}anchor=null;setTip(null)};
  const show=(event:Event)=>{
   const target=event.target instanceof Element?event.target.closest('[data-tooltip]'):null;
   if(target===anchor)return;hide();if(!target)return;
   anchor=target;previous=target.getAttribute('aria-describedby');pointer=event instanceof MouseEvent?{x:event.clientX,y:event.clientY}:null;
   timer=setTimeout(()=>{target.setAttribute('aria-describedby',[previous,'moodscope-tooltip'].filter(Boolean).join(' '));setTip({text:target.getAttribute('data-tooltip')||'',...position()})},180);
  };
  const move=(event:PointerEvent)=>{if(!anchor||!pointer)return;pointer={x:event.clientX,y:event.clientY};cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>setTip(current=>current&&anchor?{...current,...position()}:current))};
  const out=(e:Event)=>{if('relatedTarget' in e&&anchor?.contains((e as MouseEvent).relatedTarget as Node))return;hide()};
  const escape=(e:KeyboardEvent)=>{if(e.key==='Escape')hide()};
  document.addEventListener('pointermove',move);document.addEventListener('pointerover',show);document.addEventListener('focusin',show);document.addEventListener('pointerout',out);document.addEventListener('focusout',out);document.addEventListener('keydown',escape);window.addEventListener('scroll',hide,true);
  return()=>{hide();document.removeEventListener('pointermove',move);document.removeEventListener('pointerover',show);document.removeEventListener('focusin',show);document.removeEventListener('pointerout',out);document.removeEventListener('focusout',out);document.removeEventListener('keydown',escape);window.removeEventListener('scroll',hide,true)};
 },[]);
 return tip?createPortal(<div id="moodscope-tooltip" role="tooltip" className="app-tooltip" style={{left:tip.left,top:tip.top,translate:tip.above?'0 -100%':'none'}}>{tip.text}</div>,document.body):null;
}
