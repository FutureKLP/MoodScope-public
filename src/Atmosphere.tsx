import {CSSProperties} from 'react';
import {t,useLanguage} from './i18n';
import {Point} from './types';
export function moodHue(point?:Point){if(!point)return 170;return point.valence<0?(point.arousal??0)>.6?15:260:145+Math.max(-1,Math.min(1,point.valence))*30}
export function Atmosphere({audio,lyric,playing}:{audio?:Point;lyric?:Point;playing:boolean}){
  useLanguage();const energy=audio?.rms===undefined?.2:Math.min(1,Math.sqrt(Math.max(0,audio.rms))*2);
  const style={'--mood-hue':moodHue(audio),'--lyric-hue':moodHue(lyric),'--orb-scale':1+energy*.12,'--orbit-speed':`${16-(audio?.arousal??.4)*10}s`} as CSSProperties;
  return <section className={`atmosphere-panel ${playing?'is-playing':''}`} style={style} aria-label={t('Atmosphärenplayer')}><div className="atmosphere-orb" aria-hidden="true"><div className="orb-core"/><div className="orb-ring ring-one"/><div className="orb-ring ring-two"/><div className="orb-ring ring-three"/><div className="orb-halo"/></div><div className="atmosphere-caption"><span className="eyebrow">{t('KLANG IN FARBE')}</span><h2>{t(playing?'Im Moment der Musik':'Raum für deinen Song')}</h2><p>{t('Farben folgen Audio Mood und Lyric Mood. Bewegung folgt Wiedergabe und gespeicherter RMS-Energie; dies ist kein Live-Frequenzspektrum.')}</p><div className="atmosphere-values"><span>Audio Mood <b>{audio?.valence.toFixed(2)??'—'}</b></span><span>Lyric Mood <b>{lyric?.valence.toFixed(2)??'—'}</b></span></div></div></section>;
}
