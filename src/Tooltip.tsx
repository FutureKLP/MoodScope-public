import {useEffect,useState} from 'react';
import {createPortal} from 'react-dom';

export function TooltipLayer(){
 const [tip,setTip]=useState<{text:string;left:number;top:number;above:boolean}|null>(null);
 useEffect(()=>{
  let timer:ReturnType<typeof setTimeout>|undefined,anchor:Element|null=null,previous:string|null=null;
  const hide=()=>{clearTimeout(timer);if(anchor){if(previous===null)anchor.removeAttribute('aria-describedby');else anchor.setAttribute('aria-describedby',previous)}anchor=null;setTip(null)};
  const show=(event:Event)=>{
   const target=event.target instanceof Element?event.target.closest('[data-tooltip]'):null;
   if(target===anchor)return;hide();if(!target)return;
   anchor=target;previous=target.getAttribute('aria-describedby');
   timer=setTimeout(()=>{const rect=target.getBoundingClientRect();target.setAttribute('aria-describedby',[previous,'moodscope-tooltip'].filter(Boolean).join(' '));setTip({text:target.getAttribute('data-tooltip')||'',left:Math.max(12,Math.min(window.innerWidth-332,rect.left+rect.width/2-160)),top:rect.top>100?rect.top-12:rect.bottom+12,above:rect.top>100})},180);
  };
  const out=(e:Event)=>{if('relatedTarget' in e&&anchor?.contains((e as MouseEvent).relatedTarget as Node))return;hide()};
  const escape=(e:KeyboardEvent)=>{if(e.key==='Escape')hide()};
  document.addEventListener('pointerover',show);document.addEventListener('focusin',show);document.addEventListener('pointerout',out);document.addEventListener('focusout',out);document.addEventListener('keydown',escape);window.addEventListener('scroll',hide,true);
  return()=>{hide();document.removeEventListener('pointerover',show);document.removeEventListener('focusin',show);document.removeEventListener('pointerout',out);document.removeEventListener('focusout',out);document.removeEventListener('keydown',escape);window.removeEventListener('scroll',hide,true)};
 },[]);
 return tip?createPortal(<div id="moodscope-tooltip" role="tooltip" className="app-tooltip" style={{left:tip.left,top:tip.top,translate:tip.above?'0 -100%':'none'}}>{tip.text}</div>,document.body):null;
}
