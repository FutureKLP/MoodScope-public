export type MusicalFeatures={bpm:number|null;brightness_hz:number;rms_mean:number;duration:number;beat_regularity?:number;sections?:Array<{start:number;end:number;bpm?:number|null;rms:number;brightness_hz:number}>;dynamic_range_db?:number;crest_factor_db?:number;harmony?:{version:string;key:{tonic:string;mode:string;similarity:number;margin:number;alternatives:Array<{tonic:string;mode:string;similarity:number}>}|null;tuning_cents?:number;changes_per_minute?:number;key_regions?:Array<{start:number;end:number;key:{tonic:string;mode:string;similarity:number;margin:number}|null}>;chords:Array<{start:number;end:number;label:string|null;similarity:number;margin:number;degree?:string;quality?:string;resolution?:boolean}>}};
export type Point = {start:number; end:number; valence:number; text?:string;uncertain?:boolean;word_confidence?:number; scores:Record<string,number>;confidence?:number;arousal?:number;context_start?:number;context_end?:number;rms?:number;clap_valence?:number;feature_valence?:number;temporal_adjustment?:number;musical_adjustment?:number;dynamic_arousal_adjustment?:number;musical_contributions?:Array<{feature:string;value:number;weight:number;reliability:number;contribution:number}>};
export type AudioMethod={id:string;recording:string;model?:string;grid_seconds?:number;context_seconds?:number;labels:Array<{id:string;valence_weight:number;arousal_weight:number;prompts:string[]}>};
export type Analysis = {audio_method?:AudioMethod;audio_resolution?:number;pipeline_version?:string;text_coverage?:{segments:number;words:number;covered_seconds:number;duration:number;gaps:Array<{start:number;end:number}>;note:string};audio:Point[]; lyrics:Point[]; split:{start:number;end:number;audio:number;lyric:number;gap:number;lyric_coverage?:number}|null;warnings:string[];cached:boolean;stale?:boolean;source_lyrics?:string;device:string;mode?:'local'|'cloud';method:string;models:{audio:string;lyrics:string};features?:MusicalFeatures};
export type Track = {reuse_source_id?:string;id:string; name:string; duration:number; artist?:string; title?:string;source?:string;cache_match?:string;analysis_modes?:string[];tags?:Record<string,string>;original?:{format?:string;sample_rate?:number;channels?:number;bitrate?:number;bits_per_sample?:number};source_url?:string;uploader?:string};
export function trackInitials(track:Track|null){
  if(!track)return 'MS';
  const title=(track.title?.trim()||track.name.replace(/\.[a-z0-9]{2,5}$/i,'')).normalize('NFC');
  const words=title.match(/[\p{L}\p{N}]+/gu)||[];
  if(!words.length)return 'MS';
  return (words.length>1?Array.from(words[0]!)[0]!+Array.from(words[1]!)[0]!:Array.from(words[0]!).slice(0,2).join('')).toLocaleUpperCase();
}
export const clock = (time:number) => `${Math.floor(time/60)}:${Math.floor(time%60).toString().padStart(2,'0')}`;
export function activeLine(lines:Point[],time:number) {return lines.findIndex(l=>l.start<=time && time<l.end)}
export function toLrc(lines:Point[]){
  const stamp=(t:number)=>`[${Math.floor(t/60).toString().padStart(2,'0')}:${(t%60).toFixed(2).padStart(5,'0')}]`;
  return lines.flatMap((line,i)=>[stamp(line.start)+(line.text||''),...(i===lines.length-1||line.end<lines[i+1].start?[stamp(line.end)]:[])]).join('\n');
}
