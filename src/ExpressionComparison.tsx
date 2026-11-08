import {useEffect,useRef,useState} from 'react';
import {api} from './api';
import {t,useLanguage} from './i18n';
import {Track} from './types';
import {ExpressionRow} from './expressionTimeline';

type Result={rows:ExpressionRow[]};
type State={ready:boolean;result:Result|null;stale:boolean};
export function ExpressionComparison({track,busy,perform,job,onSelect,selected,preferred=false}:{track:Track;busy:boolean;perform:(fn:()=>Promise<void>)=>Promise<void>;job:(path:string,body:unknown)=>Promise<any>;onSelect:(rows:ExpressionRow[]|null)=>void;selected:boolean;preferred?:boolean}){
 useLanguage();const [state,setState]=useState<State|null>(null);const [error,setError]=useState('');const generation=useRef(0);const selection=useRef({preferred,onSelect});selection.current={preferred,onSelect};
 useEffect(()=>{const token=++generation.current;setState(null);setError('');void api(`/tracks/${track.id}/expression-comparison`).then(value=>{if(generation.current===token){setState(value);if(selection.current.preferred&&value.result&&!value.stale)selection.current.onSelect(value.result.rows)}}).catch(()=>{if(generation.current===token)setError('Vergleichsstatus konnte nicht geladen werden.')});return()=>{generation.current++}},[track.id]);
 return <details className="curve-model-control"><summary>{t('Audio-Bewertungsmodell')}: {selected?'Music2Emo':'CLAP'}</summary>
  <p>{t('Music2Emo schätzt Valenz und Aktivierung direkt. Auf unseren Referenzen trifft es das allgemeine Niveau besser; schnelle Übergänge bleiben unzureichend belegt. 30 Sekunden Kontext, 5 Sekunden Raster.')}</p>
  <p>{t('Die Auswahl gilt für die vorhandene Audio-/Lyrics-Kurve und Biggest Split. Die sechs Gefühlsbalken und Atmosphärenfarben stammen weiterhin von CLAP; Music2Emo liefert keine gleichwertigen sechs Kategorien.')}</p>
  {error&&<p role="alert">{t(error)}</p>}
  {state&&!state.ready&&<p>{t('Die optionale lokale Music2Emo-Erweiterung ist nicht eingerichtet. Einrichtung siehe Projektdokumentation.')}</p>}
  {state?.stale&&<p>{t('Dieser Vergleich stammt von einem älteren Modellstand.')}</p>}
  <div className="tool-row"><button disabled={busy} aria-pressed={!selected} onClick={()=>onSelect(null)}>{t('CLAP verwenden')}</button>
  <button disabled={busy||!state?.result||state.stale} aria-pressed={selected} onClick={()=>{if(state?.result)onSelect(state.result.rows)}}>{t('Music2Emo verwenden')}</button>
  <button disabled={busy||!state?.ready} onClick={()=>void perform(async()=>{const token=generation.current;const value=await job(`/tracks/${track.id}/expression-comparison`,{force:!!state?.result});if(generation.current!==token)return;setState({ready:true,result:value,stale:false});onSelect(value.rows)})}>{t('Music2Emo berechnen und verwenden')}</button></div>
 </details>;
}
