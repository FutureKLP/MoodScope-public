import {CSSProperties,createContext} from 'react';
import {Point} from './types';
export const AtmosphereThemeContext=createContext<{enabled:boolean;style:CSSProperties}>({enabled:false,style:{}});
export const EMOTION_PALETTE=[
 {id:'joy',color:'#dfbe76'},
 {id:'calm',color:'#79bdb5'},
 {id:'sadness',color:'#829fce'},
 {id:'anger',color:'#ce897f'},
 {id:'fear',color:'#ad96cc'},
 {id:'tenderness',color:'#d0a2b8'},
] as const;
export function emotionMix(point?:Point){
 const raw=EMOTION_PALETTE.map(({id})=>{const value=point?.scores?.[id];return Number.isFinite(value)?Math.max(0,Math.min(1,value!)):0});
 const sum=raw.reduce((a,b)=>a+b,0),weights=Object.fromEntries(EMOTION_PALETTE.map((item,i)=>[item.id,sum?raw[i]/sum:0]));
 let color='',total=0;
 EMOTION_PALETTE.forEach((item,i)=>{const value=raw[i]!;if(value<=0)return;color=total?`color-mix(in oklab, ${color} ${total/(total+value)*100}%, ${item.color})`:item.color;total+=value});
 return {weights,color:color||`hsl(${moodHue(point)} 28% 67%)`};
}
export function moodHue(point?:Point){if(!point)return 170;const valence=Math.max(-1,Math.min(1,point.valence));return 210-valence*85+Math.max(0,Math.min(1,point.arousal??0))*12}
export function atmosphereStyle(audio?:Point,lyric?:Point,bpm?:number|null):CSSProperties{
 const mix=emotionMix(audio),words=emotionMix(lyric);
 const energy=audio?.rms===undefined?.2:Math.min(1,Math.sqrt(Math.max(0,audio.rms))*2);
 const tempo=bpm&&Number.isFinite(bpm)?Math.min(200,Math.max(40,bpm)):90;
 return {...Object.fromEntries(Object.entries(mix.weights).map(([id,value])=>['--emotion-'+id,value])),'--mood-color':mix.color,'--lyric-color':words.color,'--mood-hue':moodHue(audio),'--lyric-hue':moodHue(lyric),'--ambient-energy':energy,'--breath-duration':`${240/tempo}s`,'--flow-duration':'24s'} as CSSProperties;
}
export function Atmosphere(){return <div className="ambient-field" aria-hidden="true"><div className="ambient-mist mist-one"/><div className="ambient-mist mist-two"/><div className="ambient-water"/></div>}
