import {useEffect,useRef,useState} from 'react';
import {api} from './api';
import {t,useLanguage} from './i18n';
import {Track} from './types';
import {ExpressionRow} from './expressionTimeline';

type Result={rows:ExpressionRow[]};
type State={ready:boolean;result:Result|null;stale:boolean};
export function ExpressionComparison({track,busy,perform,job,onSelect,selected,preferred=false}:{track:Track;busy:boolean;perform:(fn:()=>Promise<void>)=>Promise<void>;job:(path:string,body:unknown)=>Promise<any>;onSelect:(rows:ExpressionRow[]|null)=>void;selected:boolean;preferred?:boolean}){
 useLanguage();const [state,setState]=useState<State|null>(null);const [error,setError]=useState('');const generation=useRef(0);const autoStarted=useRef(false);const selection=useRef({preferred,onSelect});selection.current={preferred,onSelect};
 useEffect(()=>{const token=++generation.current;autoStarted.current=false;setState(null);setError('');void api(`/tracks/${track.id}/expression-comparison`).then(value=>{if(generation.current===token){setState(value);if(selection.current.preferred&&value.result&&!value.stale)selection.current.onSelect(value.result.rows)}}).catch(()=>{if(generation.current===token)setError('Vergleichsstatus konnte nicht geladen werden.')});return()=>{generation.current++}},[track.id]);
 useEffect(()=>{if(!preferred||busy||!state?.ready||(state.result&&!state.stale)||autoStarted.current)return;autoStarted.current=true;const token=generation.current;void perform(async()=>{const value=await job(`/tracks/${track.id}/expression-comparison`,{force:!!state.result});if(generation.current!==token)return;setState({ready:true,result:value,stale:false});selection.current.onSelect(value.rows)})},[preferred,busy,state,track.id]);
 return <section className="curve-source" aria-label={t('Audioquelle für Kurve und Abschnitt')}>
  <div className="curve-source-status"><strong>{t('Audio-Bewertungsmodell')}: {selected?'Music2Emo':'CLAP'}</strong>
   {!selected&&state?.ready&&<button disabled={busy} onClick={()=>{if(state.result&&!state.stale)onSelect(state.result.rows);else void perform(async()=>{const token=generation.current;const value=await job(`/tracks/${track.id}/expression-comparison`,{force:!!state.result});if(generation.current!==token)return;setState({ready:true,result:value,stale:false});onSelect(value.rows)})}}>{t('Direkte Musikbewertung verwenden')}</button>}
  </div>
  {!selected&&<p className="visual-note">{t('CLAP ist eine Beschreibungsähnlichkeit: Schlagzeug und raue Gitarren können als Ärger erscheinen. Music2Emo bewertet Valenz direkt und trennt Kraft und Energie davon.')}</p>}
  <details className="curve-model-control"><summary>{t('Modellwahl und Grenzen')}</summary>
  <p>{t('Music2Emo schätzt Valenz und Aktivierung direkt. Auf unseren Referenzen trifft es das allgemeine Niveau besser; schnelle Übergänge bleiben unzureichend belegt. 30 Sekunden Kontext, 5 Sekunden Raster.')}</p>
  <p>{t('Die Auswahl gilt für Kurve, Balken, Atmosphärenfarben und Biggest Split. Music2Emo zeigt seine tatsächlich gelernten Musik-Tags; sie werden nicht in die sechs CLAP-Kategorien umgerechnet.')}</p>
  {error&&<p role="alert">{t(error)}</p>}
  {state&&!state.ready&&<p>{t('Die optionale lokale Music2Emo-Erweiterung ist nicht eingerichtet. Einrichtung siehe Projektdokumentation.')}</p>}
  {state?.stale&&<p>{t('Dieser Vergleich stammt von einem älteren Modellstand.')}</p>}
  <div className="tool-row"><button disabled={busy} aria-pressed={!selected} onClick={()=>onSelect(null)}>{t('CLAP verwenden')}</button>
  <button disabled={busy||!state?.result||state.stale} aria-pressed={selected} onClick={()=>{if(state?.result)onSelect(state.result.rows)}}>{t('Music2Emo verwenden')}</button>
  <button disabled={busy||!state?.ready} onClick={()=>void perform(async()=>{const token=generation.current;const value=await job(`/tracks/${track.id}/expression-comparison`,{force:!!state?.result});if(generation.current!==token)return;setState({ready:true,result:value,stale:false});onSelect(value.rows)})}>{t('Music2Emo berechnen und verwenden')}</button></div>
 </details></section>;
}
