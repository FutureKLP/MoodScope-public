import {Point,MusicalFeatures} from './types';
import {t,useLanguage} from './i18n';

export function EmotionReading({point,features}:{point?:Point;features?:MusicalFeatures}){
 useLanguage();
 const key=features?.harmony?.key;
 return <section className="emotion-reading"><h3>{t('Musikalischer Ausdruck und eigenes Erleben')}</h3>
 <p>{t('Valenz beschreibt die geschätzte positive oder negative Färbung; Aktivierung beschreibt ruhig bis angeregt. Hohe Aktivierung kann zu Freude, Spannung oder Ärger passen. Traurig klingende Musik kann angenehm erlebt werden.')}</p>
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
