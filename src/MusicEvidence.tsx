import {t,useLanguage} from './i18n';
import {clock} from './types';

export type MusicPacket={version:string;observations:Array<{id:string;kind:string;source:string;start:number;end:number;value:Record<string,any>}>};
const labels:Record<string,string>={joy:'Freude',calm:'Ruhe',sadness:'Trauer',anger:'Ärger',fear:'Anspannung/Angst',tenderness:'Zärtlichkeit'};
const stamp=(value:number)=>{const tenths=Math.round(value*10);return clock(Math.floor(tenths/10))+(tenths%10?'.'+tenths%10:'')};

export function MusicEvidence({packet}:{packet?:MusicPacket|null}){
 useLanguage();if(!packet)return null;
 return <details className="source-reading" open><summary>{t('Musikbelege zur Deutung')}</summary>
  <p>{t('Messwerte, Modellschätzungen und Deutung bleiben getrennt. Hohe Energie kann verschiedene Gefühle verstärken und beweist keinen Ärger.')}</p>
  {packet.observations.map(row=>{const value=row.value;return <article key={row.id}>
   <small>{row.id} · {stamp(row.start)}–{stamp(row.end)} · {t(row.kind==='measurement'?'Messwert':row.kind==='candidate'?'Kandidat':'Modellschätzung')}</small>
   {value.relative_descriptions&&<p>{t('Geschätzte Valenz')}: {Number(value.valence).toFixed(2)}. {t('Ähnlichste Beschreibungen')}: {Object.entries(value.relative_descriptions as Record<string,number>).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([name])=>t(labels[name]||name)).join(' · ')}. {t('Relative Ähnlichkeit, keine bestätigte Emotion.')}</p>}
   {'rms_mean' in value&&<p>{t('Energie gegenüber dem Songmittel')}: {value.relative_to_song_db==null?'—':`${Number(value.relative_to_song_db).toFixed(1)} dB`}. {t('RMS-Vergleich, keine wahrgenommene Lautheit.')}</p>}
   {'energy_range_db' in value&&<p>{t('Energieentwicklung')}: {t('Kräftigster gemessener Abschnitt')} {clock(value.peak_start)}–{clock(value.peak_end)}. {t('RMS-Vergleich, keine wahrgenommene Lautheit.')}</p>}
   {'bpm' in value&&<p>{t('Tempo-Schätzung')}: {Number(value.bpm).toFixed(1)} BPM. {t('Halbes oder doppeltes Tempo ist möglich.')}</p>}
   {'dynamic_range_db' in value&&<p>{t('Energieschwankung')}: {Number(value.dynamic_range_db).toFixed(1)} dB.</p>}
   {value.tonic&&<p>{t('Tonart-Kandidat')}: {value.tonic} {t(value.mode==='major'?'Dur':'Moll')}. {t('Weitere Tonart-Kandidaten')}: {(value.alternatives||[]).map((key:any)=>`${key.tonic} ${t(key.mode==='major'?'Dur':'Moll')}`).join(' · ')}</p>}
   {value.sequence_examples&&<><p>{t('Akkordabdeckung')}: {(Number(value.coverage)*100).toFixed(0)} %. {t('Beispiele aus der Auswahl, keine vollständige Akkordfolge.')}</p><div className="measurement-chips">{value.sequence_examples.map((chord:any,i:number)=><span key={i}>{stamp(chord.start)}–{stamp(chord.end)} · {chord.label}</span>)}</div></>}
  </article>})}
  {!packet.observations.length&&<p>{t('Für diese Auswahl liegen keine Musikbelege vor.')}</p>}
  <p>{t('Klanghärte und emotionale Spannung sind hier noch nicht unabhängig validiert. Tonarten und Akkorde sind Schätzungen und bestimmen kein Gefühl.')}</p>
 </details>;
}
