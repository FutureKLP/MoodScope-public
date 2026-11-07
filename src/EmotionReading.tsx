import {Point,MusicalFeatures} from './types';
import {t,useLanguage} from './i18n';

export function EmotionReading({point,features}:{point?:Point;features?:MusicalFeatures}){
 useLanguage();
 const valid=point&&Number.isFinite(point.valence)&&Number.isFinite(point.arousal);
 const key=features?.harmony?.key;
 return <section className="emotion-reading"><h3>{t('Musikalischer Ausdruck und eigenes Erleben')}</h3>
 <p>{t('Valenz beschreibt die geschätzte positive oder negative Färbung; Aktivierung beschreibt ruhig bis angeregt. Hohe Aktivierung kann zu Freude, Spannung oder Ärger passen. Traurig klingende Musik kann angenehm erlebt werden.')}</p>
 {valid&&<svg viewBox="0 0 480 230" role="img" aria-label={t('Valenz und Aktivierung des aktuellen Abschnitts')} className="emotion-plane">
  <rect x="90" y="30" width="300" height="160" rx="8" fill="currentColor" opacity=".04"/>
  <path d="M90 110H390 M240 30V190" stroke="currentColor" opacity=".3"/>
  <text x="240" y="20" textAnchor="middle">{t('Angeregt')}</text><text x="240" y="215" textAnchor="middle">{t('Ruhig')}</text>
  <text x="80" y="115" textAnchor="end">{t('Negativ')}</text><text x="400" y="115">{t('Positiv')}</text>
  <circle cx={240+Math.max(-1,Math.min(1,point.valence))*150} cy={190-Math.max(0,Math.min(1,point.arousal!))*160} r="6" fill="#91dfcc"/>
 </svg>}
 <div className="measurement-chips">
  {Number.isFinite(features?.bpm)&&<span>{t('Tempo-Schätzung')}: {features!.bpm!.toFixed(1)} BPM</span>}
  {key&&<span>{t('Tonart-Kandidat')}: {key.tonic} {key.mode}</span>}
 </div>
 <details><summary>{t('Wie Musik Gefühle beeinflussen kann')}</summary>
  <p>{t('Tempo, Lautstärke und Klangfarbe können die Aktivierung beeinflussen. Harmonie, Rhythmus und musikalische Erwartungen wirken zusammen. Dur und Moll sind Hinweise im jeweiligen musikalischen und kulturellen Kontext, keine festen Gefühlsregeln.')}</p>
  <p>{t('Erinnerungen, Vertrautheit, Vorlieben und die Hörsituation verändern das eigene Erleben. Aus der Audiodatei lassen sich weder persönliche Erinnerungen noch Dopaminausschüttung oder Gehirnaktivität bestimmen. Diese Einordnung verändert keine Modellwerte.')}</p>
  <p>{t('Forschung')}: <a href="https://doi.org/10.1177/1029864911403364" target="_blank" rel="noreferrer">Tempo, mode and percussiveness</a> · <a href="https://www.nature.com/articles/nn.2726" target="_blank" rel="noreferrer">Anticipation and musical pleasure</a> · <a href="https://doi.org/10.1073/pnas.1212562110" target="_blank" rel="noreferrer">Music–color associations</a></p>
  <p>{t('Die Atmosphärenfarben sind eine konsistente Gestaltungshilfe: die führende Modellkategorie prägt die Grundfarbe, kleinere Anteile mischen sich dezent darunter. Farben sind keine universelle biologische Zuordnung und keine zusätzliche Emotionsmessung.')}</p>
 </details></section>;
}
