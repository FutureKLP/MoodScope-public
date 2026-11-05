export type Point = {start:number; end:number; valence:number; text?:string; scores:Record<string,number>};
export type Analysis = {audio:Point[]; lyrics:Point[]; split:{start:number;end:number;audio:number;lyric:number;gap:number}|null;warnings:string[];cached:boolean;device:string;method:string;models:{audio:string;lyrics:string}};
export type Track = {id:string; name:string; duration:number; artist?:string; title?:string};
export const clock = (time:number) => `${Math.floor(time/60)}:${Math.floor(time%60).toString().padStart(2,'0')}`;
export function activeLine(lines:Point[],time:number) {return lines.findIndex(l=>l.start<=time && time<l.end)}
