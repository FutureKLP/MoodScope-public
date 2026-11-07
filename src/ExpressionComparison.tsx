import {useEffect,useState} from 'react';
import {api} from './api';
import {t,useLanguage} from './i18n';
import {Analysis,Track,clock} from './types';

type Row={start:number;end:number;context_start:number;context_end:number;valence:number;arousal:number;tags:Record<string,number>;outside_training_scale:boolean};
type Result={rows:Row[];experimental:boolean;context_seconds:number;grid_seconds:number};
type State={ready:boolean;result:Result|null;stale:boolean};

export function ExpressionComparison({track,analysis,time,onSeek,busy,perform,job}:{track:Track;analysis:Analysis|null;time:number;onSeek:(time:number)=>void;busy:boolean;perform:(fn:()=>Promise<void>)=>Promise<void>;job:(path:string,body:unknown)=>Promise<any>}){
 useLanguage();const [state,setState]=useState<State|null>(null);const [error,setError]=useState('');
 useEffect(()=>{let active=true;setState(null);setError('');void api(`/tracks/${track.id}/expression-comparison`).then(value=>{if(active)setState(value)}).catch(()=>{if(active)setError('Vergleichsstatus konnte nicht geladen werden.')});return()=>{active=false}},[track.id]);
 const result=state?.result,rows=result?.rows??[],current=rows.find(p=>p.start<=time&&time<p.end)??rows.at(-1);
 const duration=Math.max(.001,track.duration),x=(value:number)=>30+value/duration*940,y=(value:number)=>100-value*75;
 const path=(points:Array<{start:number;end:number;valence:number}>)=>points.map((p,i)=>`${i?'L':'M'}${x((p.start+p.end)/2)},${y(p.valence)}`).join(' ');
 return <section className="panel workspace-panel"><h2>{t('Zweiter Emotionsverlauf: Music2Emo')}</h2>
  <p>{t('Experimenteller Vergleich mit einem spezialisierten Musikmodell. Valenz und Aktivierung werden getrennt gelernt. Die bisherige Analyse und die Playerfarben bleiben bestehen.')}</p>
  <p>{t('30 Sekunden Audiokontext, Anzeige alle 5 Sekunden. Das Modell ist auf Songbewertungen trainiert; schnelle Übergänge und einzelne Emotionen sind noch nicht zuverlässig validiert.')}</p>
  {error&&<p role="alert">{t(error)}</p>}
  {state&&!state.ready&&<p>{t('Die optionale lokale Music2Emo-Erweiterung ist nicht eingerichtet. Einrichtung siehe Projektdokumentation.')}</p>}
  {state?.stale&&<p>{t('Dieser Vergleich stammt von einem älteren Modellstand.')}</p>}
  <button disabled={busy||!state?.ready} onClick={()=>void perform(async()=>{const value=await job(`/tracks/${track.id}/expression-comparison`,{force:!!result});setState({ready:true,result:value,stale:false})})}>{t(result?'Vergleich neu berechnen':'Music2Emo vergleichen')}</button>
  {!!rows.length&&<><div className="legend"><span>Music2Emo</span><span>{t('Bisherige Audiovalenz')}</span></div>
   <svg viewBox="0 0 1000 210" role="img" aria-label={t('Vergleich der Audiovalenz')} style={{width:'100%',display:'block'}}>
    <line x1="30" y1="100" x2="970" y2="100" stroke="currentColor" opacity=".3"/>
    <text x="0" y="28" fill="currentColor" fontSize="12">+1</text><text x="0" y="104" fill="currentColor" fontSize="12">0</text><text x="0" y="180" fill="currentColor" fontSize="12">−1</text>
    <path d={path(analysis?.audio??[])} fill="none" stroke="#b09cf1" strokeWidth="2" strokeDasharray="6 4"/>
    <path d={path(rows)} fill="none" stroke="#6ee7ce" strokeWidth="3"/>
    <line x1={x(time)} x2={x(time)} y1="20" y2="180" stroke="currentColor" opacity=".6"/>
    <text x="30" y="205" fill="currentColor" fontSize="12">0:00</text><text x="970" y="205" textAnchor="end" fill="currentColor" fontSize="12">{clock(track.duration)}</text>
   </svg>
   <label>{t('Vergleichsabschnitt')} <select aria-label={t('Vergleichsabschnitt')} value={current?.start??0} onChange={e=>onSeek(Number(e.target.value))}>{rows.map(row=><option key={row.start} value={row.start}>{clock(row.start)} – {clock(row.end)}</option>)}</select></label>
   {current&&<><div className="measurement-chips"><span>{t('Valenz')}: {current.valence.toFixed(3)}</span><span>{t('Aktivierung')}: {current.arousal.toFixed(3)}</span><span>{t('Audiokontext')}: {clock(current.context_start)}–{clock(current.context_end)}</span></div>
    {current.outside_training_scale&&<p>{t('Rohvorhersage außerhalb der Trainingsskala; nur die Darstellung ist begrenzt.')}</p>}
    <p>{t('Stärkste Modell-Tags, unabhängig voneinander; keine gesicherten Gefühle')}: {Object.entries(current.tags).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([name,value])=>`${name}: ${value.toFixed(2)}`).join(' · ')}</p></>}
  </>}
 </section>;
}
