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
 if(signature(0,4)!=='RIFF'||signature(8,12)!=='WAVE'||expected!==blob.size||expected<44)throw Error('export-format');
 let offset=12,alignment=0,hasData=false;
 while(offset+8<=blob.size){
  const chunk=new DataView(await blob.slice(offset,offset+24).arrayBuffer());
  const id=String.fromCharCode(...new Uint8Array(chunk.buffer,0,4)),size=chunk.getUint32(4,true);
  if(offset+8+size+(size%2)>blob.size)throw Error('export-format');
  if(id==='fmt '){
   if(alignment||size<16)throw Error('export-format');
   const format=chunk.getUint16(8,true),channels=chunk.getUint16(10,true),rate=chunk.getUint32(12,true),bits=chunk.getUint16(22,true);
   alignment=chunk.getUint16(20,true);
   if(![1,3].includes(format)||![1,2].includes(channels)||!rate||![8,16,24,32,64].includes(bits)||(format===3&&![32,64].includes(bits))||alignment!==channels*bits/8||chunk.getUint32(16,true)!==rate*alignment)throw Error('export-format');
  }
  if(id==='data'){if(!alignment||hasData||!size||size%alignment)throw Error('export-format');hasData=true}
  offset+=8+size+(size%2);
 }
 if(offset!==blob.size||!hasData)throw Error('export-format');
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
