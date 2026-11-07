// @vitest-environment jsdom
import {it,expect,vi,afterEach} from 'vitest';
import {exportWave,waveFilename} from './exportWave';
import {setLanguage} from './i18n';
import {API} from './api';
vi.mock('@tauri-apps/api/core',()=>({isTauri:()=>false}));
afterEach(()=>{vi.unstubAllGlobals();delete (window as any).showSaveFilePicker;setLanguage('de')});
it('suggests song and selected instruments and writes only after destination selection',async()=>{
 const order:string[]=[],write=vi.fn(),close=vi.fn();
 const picker=vi.fn(async(_options:unknown)=>{order.push('picker');return {createWritable:async()=>({write,close,abort:vi.fn()})}});
 (window as any).showSaveFilePicker=picker;
 vi.stubGlobal('fetch',vi.fn(async()=>{order.push('download');return new Response(new Blob(['RIFF____WAVEdata']))}));
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
 const create=vi.fn(()=> 'blob:authored'),revoke=vi.fn();vi.stubGlobal('URL',{createObjectURL:create,revokeObjectURL:revoke});vi.stubGlobal('fetch',vi.fn(async()=>new Response(new Blob(['RIFF____WAVEdata']))));
 const click=vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(function(this:HTMLAnchorElement){expect(this.download).toBe('Song - Gesang.wav');expect(this.href).toBe('blob:authored')});
 vi.useFakeTimers();try{expect(await exportWave({id:'fixture',name:'Song.wav',duration:10},'htdemucs',['vocals'])).toBe(true);expect(click).toHaveBeenCalledOnce();vi.runAllTimers();expect(revoke).toHaveBeenCalledWith('blob:authored')}finally{vi.useRealTimers();click.mockRestore()}
});
