// @vitest-environment jsdom
import {it,expect,vi,afterEach} from 'vitest';
import {exportWave,waveFilename} from './exportWave';
import {setLanguage} from './i18n';
import {API} from './api';
vi.mock('@tauri-apps/api/core',()=>({isTauri:()=>false}));
const authoredWave=()=>{const bytes=new Uint8Array(48),view=new DataView(bytes.buffer);for(const [at,text] of [[0,'RIFF'],[8,'WAVE'],[12,'fmt '],[36,'data']] as const)for(let i=0;i<text.length;i++)bytes[at+i]=text.charCodeAt(i);view.setUint32(4,40,true);view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,2,true);view.setUint32(24,48000,true);view.setUint32(28,192000,true);view.setUint16(32,4,true);view.setUint16(34,16,true);view.setUint32(40,4,true);return bytes};
afterEach(()=>{vi.unstubAllGlobals();delete (window as any).showSaveFilePicker;setLanguage('de')});
it('suggests song and selected instruments and writes only after destination selection',async()=>{
 const order:string[]=[],write=vi.fn(),close=vi.fn();
 const picker=vi.fn(async(_options:unknown)=>{order.push('picker');return {createWritable:async()=>({write,close,abort:vi.fn()})}});
 (window as any).showSaveFilePicker=picker;
 vi.stubGlobal('fetch',vi.fn(async()=>{order.push('download');return new Response(authoredWave())}));
 const track={id:'fixture',title:'Song: One',name:'song.mp3',duration:10};
 expect(await exportWave(track,'htdemucs',['vocals','drums'],{drums:.5})).toBe(true);
 expect(order).toEqual(['picker','download']);expect(picker.mock.calls[0][0]).toMatchObject({suggestedName:'Song_ One - Gesang + Schlagzeug.wav'});
 expect(String(vi.mocked(fetch).mock.calls[0][0])).toContain('gains=1,0.5');expect(new URL(String(vi.mocked(fetch).mock.calls[0][0])).origin).not.toBe(new URL(API).origin);expect(write).toHaveBeenCalledOnce();expect(close).toHaveBeenCalledOnce();
 setLanguage('en');expect(waveFilename(track,['vocals','drums'])).toBe('Song_ One - vocals + drums.wav');
});
it('cancelling the destination does not download or report an error',async()=>{
 (window as any).showSaveFilePicker=vi.fn(async()=>{throw new DOMException('Cancelled','AbortError')});vi.stubGlobal('fetch',vi.fn());
 expect(await exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).toBe(false);expect(fetch).not.toHaveBeenCalled();
});
it('reports transfer failures and keeps an existing destination intact',async()=>{
 const createWritable=vi.fn();(window as any).showSaveFilePicker=vi.fn(async()=>({createWritable}));vi.stubGlobal('fetch',vi.fn(async()=>new Response('',{status:500})));
 setLanguage('en');await expect(exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).rejects.toThrow('WAV export failed');expect(createWritable).not.toHaveBeenCalled();
});
it('uses a named browser download when no save picker is available',async()=>{
 const create=vi.fn(()=> 'blob:authored'),revoke=vi.fn();vi.stubGlobal('URL',{createObjectURL:create,revokeObjectURL:revoke});vi.stubGlobal('fetch',vi.fn(async()=>new Response(authoredWave())));
 const click=vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(function(this:HTMLAnchorElement){expect(this.download).toBe('Song - Gesang.wav');expect(this.href).toBe('blob:authored')});
 vi.useFakeTimers();try{expect(await exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).toBe(true);expect(click).toHaveBeenCalledOnce();vi.runAllTimers();expect(revoke).toHaveBeenCalledWith('blob:authored')}finally{vi.useRealTimers();click.mockRestore()}
});
it('rejects corrupt and truncated WAV before opening an existing destination for writing',async()=>{
 const createWritable=vi.fn();(window as any).showSaveFilePicker=vi.fn(async()=>({createWritable}));
 for(const data of [new TextEncoder().encode('invalid payload'),new Uint8Array([82,73,70,70,100,0,0,0,87,65,86,69])]){
  vi.stubGlobal('fetch',vi.fn(async()=>new Response(data)));
  await expect(exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).rejects.toThrow();
 }
 expect(createWritable).not.toHaveBeenCalled();
});
it('aborts a failed destination write without committing the replacement',async()=>{
 const abort=vi.fn(),close=vi.fn();(window as any).showSaveFilePicker=vi.fn(async()=>({createWritable:async()=>({write:async()=>{throw Error('fixture disk full')},close,abort})}));
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(authoredWave())));
 await expect(exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).rejects.toThrow();
 expect(abort).toHaveBeenCalledOnce();expect(close).not.toHaveBeenCalled();
});

it('requires coherent format and frame chunks before replacing a selected file',async()=>{
 const createWritable=vi.fn();(window as any).showSaveFilePicker=vi.fn(async()=>({createWritable}));
 const missing=authoredWave();missing.set(new TextEncoder().encode('JUNK'),36);
 const alignment=authoredWave();new DataView(alignment.buffer).setUint16(32,3,true);
 const overflow=authoredWave();new DataView(overflow.buffer).setUint32(40,100,true);
 const trailing=new Uint8Array(50);trailing.set(authoredWave());
 for(const bytes of [missing,alignment,overflow,trailing]){
  vi.stubGlobal('fetch',vi.fn(async()=>new Response(bytes)));
  await expect(exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).rejects.toThrow();
 }
 expect(createWritable).not.toHaveBeenCalled();
});
