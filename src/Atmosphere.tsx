import {CSSProperties,createContext} from 'react';
import {Point} from './types';
export const AtmosphereThemeContext=createContext<{enabled:boolean;style:CSSProperties}>({enabled:false,style:{}});
export const EMOTION_PALETTE=[
 {id:'joy',color:'#f4ce54'},
 {id:'calm',color:'#66b8ac'},
 {id:'sadness',color:'#668cce'},
 {id:'anger',color:'#e36b62'},
 {id:'fear',color:'#9d89bb'},
 {id:'tenderness',color:'#e5a0be'},
] as const;
export const MUSIC_TAG_PALETTE=[
 {id:'happy',color:'#f4ce54'},{id:'calm',color:'#66b8ac'},{id:'sad',color:'#668cce'},
 {id:'melancholic',color:'#7c83ad'},{id:'hopeful',color:'#9bc77a'},{id:'romantic',color:'#e5a0be'},
 {id:'powerful',color:'#d5a351'},{id:'energetic',color:'#eb9c52'},{id:'relaxing',color:'#7fc5bd'}
] as const;
const PROVIDER_PALETTE=[...EMOTION_PALETTE,...MUSIC_TAG_PALETTE.filter(item=>item.id==='powerful'||item.id==='energetic')];
export function emotionColor(id:string){return [...EMOTION_PALETTE,...MUSIC_TAG_PALETTE].find(item=>item.id===id)?.color??'#8cb8b8'}
export function emotionMix(point?:Point){
 const palette=point?.score_source==='music2emo_tags'?MUSIC_TAG_PALETTE:point?.score_source==='provider_emotions'?PROVIDER_PALETTE:EMOTION_PALETTE;
 const raw=palette.map(({id})=>{const value=point?.scores?.[id];return Number.isFinite(value)?Math.max(0,Math.min(1,value!)):0});
 const sum=raw.reduce((a,b)=>a+b,0),weights=Object.fromEntries(palette.map((item,i)=>[item.id,sum?raw[i]/sum:0]));
 let color='',total=0;
 palette.forEach((item,i)=>{const value=raw[i]!;if(value<=0)return;color=total?`color-mix(in oklab, ${color} ${total/(total+value)*100}%, ${item.color})`:item.color;total+=value});
 const ranked=palette.map((item,i)=>({...item,weight:weights[item.id],score:raw[i]})).sort((a,b)=>b.score-a.score);
 const margin=ranked[0].weight-ranked[1].weight;
 const mixed=color||'#8cb8b8';
 // Display accent uses the raw bar gap, not a gap diluted by nine independent tags.
 // It vanishes continuously at a tie; this never changes model scores or bar lengths.
 const gap=ranked[0].score-ranked[1].score;
 const accent=.78*gap/(gap+.08);
 const leadColor=sum?`color-mix(in oklab, ${ranked[0].color} ${accent*100}%, ${mixed})`:mixed;
 return {weights,color:mixed,leadColor,dominant:sum?ranked[0].id:null,dominance:margin,accent};
}
export function moodHue(point?:Point){if(!point)return 170;const valence=Number.isFinite(point.valence)?Math.max(-1,Math.min(1,point.valence)):0;return 210-valence*85+(Number.isFinite(point.arousal)?Math.max(0,Math.min(1,point.arousal!)):0)*12}
export function atmosphereStyle(audio?:Point,lyric?:Point,bpm?:number|null):CSSProperties{
 const mix=emotionMix(audio),words=emotionMix(lyric);
 const energy=Number.isFinite(audio?.rms)?Math.min(1,Math.sqrt(Math.max(0,audio!.rms!))*2):.2;
 const tempo=bpm&&Number.isFinite(bpm)?Math.min(200,Math.max(40,bpm)):90;
 const secondary=words.dominant?`color-mix(in oklab, ${mix.leadColor} 88%, ${words.color})`:mix.leadColor;
 return {...Object.fromEntries(Object.entries(mix.weights).map(([id,value])=>['--emotion-'+id,value])),'--mood-color':mix.leadColor,'--lyric-color':secondary,'--mood-hue':moodHue(audio),'--lyric-hue':moodHue(lyric),'--ambient-energy':energy,'--breath-duration':`${240/tempo}s`,'--flow-duration':'24s'} as CSSProperties;
}
export function Atmosphere(){return <div className="ambient-field" aria-hidden="true"><div className="ambient-mist mist-one"/><div className="ambient-mist mist-two"/><div className="ambient-undertones">{[...EMOTION_PALETTE,...MUSIC_TAG_PALETTE.filter(tag=>!EMOTION_PALETTE.some(item=>String(item.id)===tag.id))].map(item=><span key={item.id} style={{background:`radial-gradient(ellipse, ${item.color}, transparent 70%)`,opacity:`calc(var(--emotion-${item.id}, 0) * .22)`}}/>)}</div><div className="ambient-water"/></div>}
