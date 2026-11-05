export type Point = {start:number; end:number; valence:number; text?:string; scores:Record<string,number>;confidence?:number;arousal?:number};
export type Analysis = {audio:Point[]; lyrics:Point[]; split:{start:number;end:number;audio:number;lyric:number;gap:number;lyric_coverage?:number}|null;warnings:string[];cached:boolean;stale?:boolean;source_lyrics?:string;device:string;mode?:'local'|'cloud';method:string;models:{audio:string;lyrics:string};features?:{bpm:number|null;brightness_hz:number;rms_mean:number;duration:number}};
export type Track = {id:string; name:string; duration:number; artist?:string; title?:string;source?:string;cache_match?:string;analysis_modes?:string[]};
export const clock = (time:number) => `${Math.floor(time/60)}:${Math.floor(time%60).toString().padStart(2,'0')}`;
export function activeLine(lines:Point[],time:number) {return lines.findIndex(l=>l.start<=time && time<l.end)}
export function toLrc(lines:Point[]){
  const stamp=(t:number)=>`[${Math.floor(t/60).toString().padStart(2,'0')}:${(t%60).toFixed(2).padStart(5,'0')}]`;
  return lines.flatMap((line,i)=>[stamp(line.start)+(line.text||''),...(i===lines.length-1||line.end<lines[i+1].start?[stamp(line.end)]:[])]).join('\n');
}
