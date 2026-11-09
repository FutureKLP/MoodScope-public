import {useEffect,useState} from 'react';
import {api} from './api';
import {Analysis,clock} from './types';
import {t,useLanguage} from './i18n';

type Row={start:number;end:number;relation:string;text_coverage:number;usable_text_coverage:number;text_references:string[];audio_context?:{start:number;end:number};feature_window:{start:number;end:number}|null};
type Packet={audio_source:string;rows:Row[]};
export const RELATION_TEXT:Record<string,string>={
 aligned:'Musik und Text zeigen eine ähnliche Valenztendenz.',
 contrasting:'Musik und Text zeigen gegensätzliche Valenztendenzen.',
 mixed:'Die Modelltendenzen ergeben keine eindeutige gemeinsame Richtung.',
 music_only:'Für eine gemeinsame Einordnung fehlt ausreichend synchronisierter Text.',
 uncertain_text:'Die Texterkennung ist für eine belastbare gemeinsame Einordnung zu unsicher.',
 uncertain_audio:'Die Audioschätzung ist für eine eindeutige gemeinsame Richtung zu instabil.'
};
export function CombinedReading({trackId,analysis,musicSource,time}:{trackId:string;analysis:Analysis|null;musicSource:'analysis'|'music2emo';time:number}){
 useLanguage();const [packet,setPacket]=useState<Packet|null>(null);
 useEffect(()=>{let active=true;setPacket(null);if(analysis)void api(`/tracks/${trackId}/combined-evidence?mode=${analysis.mode??'local'}&music_source=${musicSource}`).then(value=>{if(active)setPacket(Array.isArray(value?.rows)?value:null)}).catch(()=>{});return()=>{active=false}},[trackId,analysis,musicSource]);
 const row=packet?.rows.find(value=>value.start<=time&&time<value.end);
 if(!row)return null;
 return <div className="combined-reading"><p><strong>{t('Musik und Text gemeinsam')}: </strong>{t(RELATION_TEXT[row.relation]??RELATION_TEXT.mixed)}</p>
  <details><summary>{t('Belege der gemeinsamen Einordnung')}</summary>
   <p>{clock(row.start)}–{clock(row.end)} · {t('Audioquelle')}: {packet?.audio_source==='Music2Emo'?'Music2Emo':analysis?.models.audio}</p>
   {row.audio_context&&<p>{t('Tatsächlicher Audiokontext')}: {clock(row.audio_context.start)}–{clock(row.audio_context.end)}. {t('Ein feines Anzeigeraster bedeutet keine ebenso kurze Modellbeobachtung.')}</p>}
   <p>{t('Zeitliche Textabdeckung')}: {(row.text_coverage*100).toFixed(0)} % · {t('Ohne als unsicher markierte Wörter')}: {(row.usable_text_coverage*100).toFixed(0)} %</p>
   {!!row.text_references.length&&<p>{t('Textbelege')}: {row.text_references.join(', ')}</p>}
   {row.feature_window&&<p>{t('Musikmerkmale aus dem gemessenen Zeitfenster')}: {clock(row.feature_window.start)}–{clock(row.feature_window.end)}. {t('Tempo, Energie und Harmoniekandidaten ergänzen die Deutung; sie legen kein Gefühl fest.')}</p>}
   <p>{t('Diese gemeinsame Einordnung vergleicht Modellschätzungen. Sie ist keine gemessene Gefühlsreaktion. Gegensätze werden nicht zu einem scheinbar neutralen Gesamtscore gemittelt.')}</p>
  </details></div>;
}
