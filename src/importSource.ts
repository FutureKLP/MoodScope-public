import {invoke,isTauri} from '@tauri-apps/api/core';
import {getLanguage,t} from './i18n';
import {Track} from './types';

async function choose(kind:'audio'|'lyrics',browser:()=>void):Promise<string|null>{
 if(!isTauri()){browser();return null}
 try{return await invoke<string|null>('import_source',{kind,language:getLanguage()})}
 catch(error){
  const reason=String(error);
  if(reason.startsWith('import-http:')){
   let detail:unknown;try{detail=JSON.parse(reason.slice('import-http:'.length)).detail}catch{}
   if(typeof detail==='string')throw new Error(t(detail));
  }
  throw new Error(t('Dateiimport fehlgeschlagen. Prüfe Dateityp, Dateigröße, Leserechte und den lokalen Dienst.'));
 }
}
export async function pickAudioImport(browser:()=>void):Promise<Track|null>{
 const value=await choose('audio',browser);if(value===null)return null;
 try{const track=JSON.parse(value);if(typeof track.id!=='string'||typeof track.name!=='string'||!Number.isFinite(track.duration))throw Error();return track}
 catch{throw new Error(t('Dateiimport fehlgeschlagen. Prüfe Dateityp, Dateigröße, Leserechte und den lokalen Dienst.'))}
}
export function pickLyricsImport(browser:()=>void){return choose('lyrics',browser)}
