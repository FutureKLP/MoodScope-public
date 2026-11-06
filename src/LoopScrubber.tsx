import {useState} from 'react';
import {clock} from './types';
import {t,useLanguage} from './i18n';
export type LoopRange={a:number;b:number|null};
export function LoopScrubber({duration,time,disabled,onSeek,onLoopChange}:{duration:number;time:number;disabled:boolean;onSeek:(time:number)=>void;onLoopChange:(range:LoopRange|null)=>void}){
 useLanguage();const [range,setRange]=useState<LoopRange|null>(null);
 function mark(position:number){if(disabled)return;const point=Math.min(duration,Math.max(0,position));let next:LoopRange|null;
  if(!range)next={a:point,b:null};else if(range.b===null){if(Math.abs(point-range.a)<.1)return;next={a:Math.min(point,range.a),b:Math.max(point,range.a)};if(time<next.a||time>=next.b!)onSeek(next.a)}else next=null;
  setRange(next);onLoopChange(next);
 }
 return <div className="loop-control"><div className="scrubber-loop" onContextMenu={e=>{e.preventDefault();const rect=e.currentTarget.getBoundingClientRect();mark(rect.width?((e.clientX-rect.left)/rect.width)*duration:time)}} title={t('Rechtsklick: A setzen, B setzen, beim dritten Mal Loop löschen. Shift+F10 setzt den Punkt an der aktuellen Position.')}>
  {range&&<><span className="loop-marker" style={{left:`${range.a/Math.max(1,duration)*100}%`}}>A</span>{range.b!==null&&<><span className="loop-selection" style={{left:`${range.a/Math.max(1,duration)*100}%`,width:`${(range.b-range.a)/Math.max(1,duration)*100}%`}}/><span className="loop-marker marker-b" style={{left:`${range.b/Math.max(1,duration)*100}%`}}>B</span></>}</>}
  <input aria-label={t('Wiedergabeposition')} className="scrubber" type="range" min={0} max={duration||1} step=".05" value={time} disabled={disabled} onChange={e=>onSeek(Number(e.target.value))} onKeyDown={e=>{if(e.key==='ContextMenu'||(e.key==='F10'&&e.shiftKey)){e.preventDefault();mark(time)}}}/>
 </div><button className="loop-mark-button" disabled={disabled} aria-label={t(range?.b!==null&&range?'Loop löschen':'Loop-Punkt an aktueller Position setzen')} onClick={()=>mark(time)} title={range?`A ${clock(range.a)}${range.b!==null?` · B ${clock(range.b)}`:''}`:t('Abschnitt in Dauerschleife hören')}>{range?.b!==null&&range?t('Loop aus'):range?'B':'A'}</button></div>;
}
