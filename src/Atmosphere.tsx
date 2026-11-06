import {CSSProperties} from 'react';
import {Point} from './types';
export function moodHue(point?:Point){if(!point)return 170;const valence=Math.max(-1,Math.min(1,point.valence));return 210-valence*85+Math.max(0,Math.min(1,point.arousal??0))*12}
export function atmosphereStyle(audio?:Point,lyric?:Point,bpm?:number|null):CSSProperties{
 const energy=audio?.rms===undefined?.2:Math.min(1,Math.sqrt(Math.max(0,audio.rms))*2);
 const tempo=bpm&&Number.isFinite(bpm)?Math.min(200,Math.max(40,bpm)):90;
 return {'--mood-hue':moodHue(audio),'--lyric-hue':moodHue(lyric),'--ambient-energy':energy,'--breath-duration':`${240/tempo}s`,'--flow-duration':'24s'} as CSSProperties;
}
export function Atmosphere(){return <div className="ambient-field" aria-hidden="true"><div className="ambient-mist mist-one"/><div className="ambient-mist mist-two"/><div className="ambient-water"/></div>}
