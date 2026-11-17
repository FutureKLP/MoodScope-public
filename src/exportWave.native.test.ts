// @vitest-environment jsdom
import {afterEach,expect,it,vi} from 'vitest';
import {invoke} from '@tauri-apps/api/core';
import {exportWave} from './exportWave';
import {setLanguage} from './i18n';

vi.mock('@tauri-apps/api/core',()=>({isTauri:()=>true,invoke:vi.fn()}));
const track={id:'a'.repeat(64),name:'Synthetic.wav',duration:2};
afterEach(()=>{vi.resetAllMocks();vi.unstubAllGlobals();setLanguage('de')});

it('preserves native cancellation without browser download or writable fallback',async()=>{
 const fetcher=vi.fn(),picker=vi.fn();vi.stubGlobal('fetch',fetcher);vi.stubGlobal('showSaveFilePicker',picker);
 vi.mocked(invoke).mockResolvedValue(false);
 for(let n=0;n<5;n++)expect(await exportWave(track,'htdemucs',['vocals'])).toBe(false);
 expect(invoke).toHaveBeenCalledTimes(5);expect(fetcher).not.toHaveBeenCalled();expect(picker).not.toHaveBeenCalled();
});
it('can export after cancellation and passes language, filename and gains through IPC',async()=>{
 vi.mocked(invoke).mockResolvedValueOnce(false).mockResolvedValueOnce(true);setLanguage('en');
 expect(await exportWave(track,'htdemucs',['vocals'],{vocals:.5})).toBe(false);
 expect(await exportWave(track,'htdemucs',['vocals'],{vocals:.5})).toBe(true);
 expect(invoke).toHaveBeenLastCalledWith('save_wave_export',{trackId:track.id,model:'htdemucs',sources:['vocals'],gains:[.5],filename:'Synthetic - vocals.wav',language:'en'});
});
it('reports native failures without a second download attempt',async()=>{
 const fetcher=vi.fn();vi.stubGlobal('fetch',fetcher);vi.mocked(invoke).mockRejectedValue('export-download');
 await expect(exportWave(track,'htdemucs',['vocals'])).rejects.toThrow('WAV-Export fehlgeschlagen');expect(fetcher).not.toHaveBeenCalled();
});
