import {CSSProperties} from 'react';
import {Point} from './types';
export function moodHue(point?:Point){if(!point)return 170;return point.valence<0?(point.arousal??0)>.6?15:260:145+Math.max(-1,Math.min(1,point.valence))*30}
export function atmosphereStyle(audio?:Point,lyric?:Point,bpm?:number|null):CSSProperties{
 const energy=audio?.rms===undefined?.2:Math.min(1,Math.sqrt(Math.max(0,audio.rms))*2);
 const tempo=bpm&&Number.isFinite(bpm)?Math.min(200,Math.max(40,bpm)):90;
 return {'--mood-hue':moodHue(audio),'--lyric-hue':moodHue(lyric),'--ambient-energy':energy,'--breath-duration':`${240/tempo}s`,'--flow-duration':`${28-(audio?.arousal??.4)*12}s`} as CSSProperties;
}
export function Atmosphere(){return <div className="ambient-field" aria-hidden="true"><div className="ambient-mist mist-one"/><div className="ambient-mist mist-two"/><div className="ambient-water"/></div>}
