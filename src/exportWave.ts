import {invoke,isTauri} from '@tauri-apps/api/core';
import {CONTROL_API} from './api';
import {getLanguage,t} from './i18n';
import {Track} from './types';

const names:Record<string,string>={vocals:'Gesang',drums:'Schlagzeug',bass:'Bass',other:'Instrumente',guitar:'Gitarre',piano:'Klavier'};
export function waveFilename(track:Track,sources:string[]){
 const song=track.title||track.name.replace(/\.[a-z0-9]{2,5}$/i,'');
 const instruments=sources.map(s=>getLanguage()==='en'?s:names[s]||s).join(' + ');
 return `${song} - ${instruments}`.replace(/[<>:"/\\|?*\u0000-\u001f]/g,'_').trim().slice(0,160)+'.wav';
}
type Picker=(options:unknown)=>Promise<{createWritable:()=>Promise<{write:(data:Blob)=>Promise<void>;close:()=>Promise<void>;abort:()=>Promise<void>}>}>;
async function waveBlob(response:Response){
 if(!response.ok)throw Error('export-download');
 const blob=await response.blob();if(blob.size<12)throw Error('export-format');
 const header=new Uint8Array(await blob.slice(0,12).arrayBuffer());
 const signature=(start:number,end:number)=>String.fromCharCode(...header.slice(start,end));
 const expected=new DataView(header.buffer).getUint32(4,true)+8;
 if(signature(0,4)!=='RIFF'||signature(8,12)!=='WAVE'||expected<12||expected>blob.size)throw Error('export-format');
 return blob;
}
export async function exportWave(track:Track,model:string,sources:string[],levels:Record<string,number>={}){
 const filename=waveFilename(track,sources),gains=sources.map(s=>levels[s]??1);
 try{
  if(isTauri())return await invoke<boolean>('save_wave_export',{trackId:track.id,model,sources,gains,filename,language:getLanguage()});
  const url=`${CONTROL_API}/api/tracks/${track.id}/mix?model=${model}&sources=${sources.join(',')}&gains=${gains.join(',')}`;
  const picker=(window as unknown as {showSaveFilePicker?:Picker}).showSaveFilePicker;
  if(picker){
   const handle=await picker.call(window,{suggestedName:filename,types:[{description:'WAV audio',accept:{'audio/wav':['.wav']}}]});
   const blob=await waveBlob(await fetch(url));
   const destination=await handle.createWritable();try{await destination.write(blob);await destination.close()}catch(e){await destination.abort().catch(()=>{});throw e}
  }else{
   // Firefox and older browsers use their configured download destination.
   const blob=await waveBlob(await fetch(url));
   const objectUrl=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=objectUrl;anchor.download=filename;document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(objectUrl),10000);
  }
  return true;
 }catch(e){
  if(typeof e==='object'&&e!==null&&'name' in e&&e.name==='AbortError')return false;
  throw new Error(t(String(e).includes('export-extension')?'Bitte einen Dateinamen mit .wav wählen.':'WAV-Export fehlgeschlagen. Prüfe den Speicherort und die Verbindung zum lokalen Dienst.'));
 }
}
