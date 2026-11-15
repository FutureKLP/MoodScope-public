import {useEffect,useState} from 'react';
import {api,json} from './api';
import {t,useLanguage} from './i18n';
export const TASKS=[
 {id:'audio',name:'Audio-Gefühle',data:'Originalmix → Valenz, Aktivierung und Gefühlsbalken.',audio:true},
 {id:'lyrics',name:'Text-Gefühle',data:'Zeitgestempelte Textzeilen → Text-Emotionskurve; kein Audio.',audio:false},
 {id:'transcription',name:'Gesangserkennung',data:'Originalmix → unsichere Wörter und Zeitstempel, wenn keine LRC vorliegt.',audio:true},
 {id:'instruments',name:'Instrumenthinweise',data:'Originalmix → unsichere Instrumentfamilien; nur bei Start in Songdetails.',audio:true},
 {id:'interpretation',name:'Interpretation',data:'Songtext und optional gespeicherte Musikbelege → Textdeutung; kein Audio.',audio:false}
] as const;
export type RoutingState={routes:Record<string,string>;targets:Record<string,{source:string;name?:string;provider?:string;model:string}>;version:string};
export function ProviderRouting({profiles,busy,perform,onSaved}:{profiles:any[];busy:boolean;perform:(fn:()=>Promise<void>)=>Promise<void>;onSaved?:(value:RoutingState)=>void}){
 useLanguage();const [saved,setSaved]=useState<RoutingState|null>(null),[draft,setDraft]=useState<Record<string,string>>({}),[message,setMessage]=useState('');
 useEffect(()=>{let live=true;setSaved(null);void api('/provider-routes').then(value=>{if(!value.routes)throw Error();if(live){setSaved(value);setDraft(value.routes)}}).catch(()=>{if(live)setMessage('Aufgabenzuordnung konnte nicht geladen werden.')});return()=>{live=false}},[profiles]);
 return <section className="task-routing"><h3>{t('Anbieter und Modell je Aufgabe')}</h3><p>{t('Diese Zuordnung gilt im Modus Eingetragene API-Profile verwenden. Jede Aufgabe kann auch lokal bleiben. Eine Profilzeile steht für genau einen Server und eine Modell-ID; für mehrere Modelle mehrere Profile anlegen.')}</p><p>{t('Die bisherige Auswahl Vorbereitetes Audioprofil bleibt erhalten, bis du eine Aufgabe gezielt umstellst. Eine ausdrückliche Auswahl im Reiter Interpretation überschreibt nur deren Zuordnung. Spurentrennung und akustische Messwerte bleiben lokal.')}</p>
 <div className="routing-grid">{TASKS.map(task=>{const value=draft[task.id]??'prepared';return <label key={task.id}><strong>{t(task.name)}</strong><small>{t(task.data)}</small><select aria-label={t(task.name)+' · '+t('Anbieterzuordnung')} value={value} disabled={busy||!saved} onChange={e=>{setDraft({...draft,[task.id]:e.target.value});setMessage('')}}><option value="local">{t('Lokales Modell aus der Modellauswahl')}</option><option value="prepared">{t('Vorbereitetes Audioprofil (bisherige Auswahl)')}</option>{profiles.filter(p=>!task.audio||p.protocol==='gemini'||p.audio_input).map(p=><option key={p.id} value={p.id}>{p.name} · {p.model}</option>)}{!['local','prepared'].includes(value)&&!profiles.some(p=>p.id===value)&&<option value={value}>{t('Profil nicht mehr vorhanden')}</option>}</select>{saved?.targets?.[task.id]&&<small>{t('Gespeichert')}: {t(saved.targets[task.id].name||saved.targets[task.id].provider||'Lokales Modell')} {saved.targets[task.id].model}</small>}</label>})}</div>
 <button disabled={busy||!saved} onClick={()=>void perform(async()=>{const routes=Object.fromEntries(TASKS.map(task=>[task.id,draft[task.id]??'prepared']));const value=await api('/provider-routes',json(routes));setSaved(value);setDraft(value.routes);setMessage('Aufgabenzuordnung gespeichert. Übertragungszustimmung erneut prüfen.');onSaved?.(value)})}>{t('Aufgabenzuordnung speichern')}</button><p role="status">{t(message)}</p></section>
}
