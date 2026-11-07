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
 const ranked=EMOTION_PALETTE.map(item=>({...item,weight:weights[item.id]})).sort((a,b)=>b.weight-a.weight);
 const margin=ranked[0].weight-ranked[1].weight;
 const mixed=color||'#8cb8b8';
 // A continuous dominance margin avoids hue jumps when two labels trade places.
 const leadColor=sum?`color-mix(in oklab, ${ranked[0].color} ${margin*65}%, ${mixed})`:mixed;
 return {weights,color:mixed,leadColor,dominant:sum?ranked[0].id:null,dominance:margin};
}
export function moodHue(point?:Point){if(!point)return 170;const valence=Number.isFinite(point.valence)?Math.max(-1,Math.min(1,point.valence)):0;return 210-valence*85+(Number.isFinite(point.arousal)?Math.max(0,Math.min(1,point.arousal!)):0)*12}
export function atmosphereStyle(audio?:Point,lyric?:Point,bpm?:number|null):CSSProperties{
 const mix=emotionMix(audio),words=emotionMix(lyric);
 const energy=Number.isFinite(audio?.rms)?Math.min(1,Math.sqrt(Math.max(0,audio!.rms!))*2):.2;
 const tempo=bpm&&Number.isFinite(bpm)?Math.min(200,Math.max(40,bpm)):90;
 const secondary=words.dominant?`color-mix(in oklab, ${mix.leadColor} 88%, ${words.color})`:mix.leadColor;
 return {...Object.fromEntries(Object.entries(mix.weights).map(([id,value])=>['--emotion-'+id,value])),'--mood-color':mix.leadColor,'--lyric-color':secondary,'--mood-hue':moodHue(audio),'--lyric-hue':moodHue(lyric),'--ambient-energy':energy,'--breath-duration':`${240/tempo}s`,'--flow-duration':'24s'} as CSSProperties;
}
export function Atmosphere(){return <div className="ambient-field" aria-hidden="true"><div className="ambient-mist mist-one"/><div className="ambient-mist mist-two"/><div className="ambient-undertones">{EMOTION_PALETTE.map(item=><span key={item.id} style={{background:`radial-gradient(ellipse, ${item.color}, transparent 70%)`,opacity:`calc(var(--emotion-${item.id}) * .22)`}}/>)}</div><div className="ambient-water"/></div>}
