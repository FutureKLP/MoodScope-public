// @vitest-environment jsdom
import {afterEach,expect,it,vi} from 'vitest';
import {invoke,isTauri} from '@tauri-apps/api/core';
import {pickAudioImport,pickLyricsImport} from './importSource';
import {setLanguage} from './i18n';
vi.mock('@tauri-apps/api/core',()=>({isTauri:vi.fn(()=>true),invoke:vi.fn()}));
afterEach(()=>{vi.clearAllMocks();vi.mocked(isTauri).mockReturnValue(true);setLanguage('de')});
it('uses the existing HTML inputs only in a browser',async()=>{
 vi.mocked(isTauri).mockReturnValue(false);const browser=vi.fn();
 expect(await pickAudioImport(browser)).toBeNull();expect(await pickLyricsImport(browser)).toBeNull();
 expect(browser).toHaveBeenCalledTimes(2);expect(invoke).not.toHaveBeenCalled();
});
it('keeps native cancellation separate from the browser fallback and preserves an empty lyric file',async()=>{
 const browser=vi.fn();vi.mocked(invoke).mockResolvedValue(null);
 expect(await pickAudioImport(browser)).toBeNull();expect(await pickLyricsImport(browser)).toBeNull();
 expect(browser).not.toHaveBeenCalled();vi.mocked(invoke).mockResolvedValue('');expect(await pickLyricsImport(browser)).toBe('');
});
it('returns imported metadata and original LRC timestamps through language-bound IPC',async()=>{
 setLanguage('en');vi.mocked(invoke).mockResolvedValue(JSON.stringify({id:'fixture',name:'source.wav',duration:60}));
 expect((await pickAudioImport(vi.fn()))?.name).toBe('source.wav');
 expect(invoke).toHaveBeenLastCalledWith('import_source',{kind:'audio',language:'en'});
 vi.mocked(invoke).mockResolvedValue('[00:10.25]Authored line');expect(await pickLyricsImport(vi.fn())).toBe('[00:10.25]Authored line');
 expect(invoke).toHaveBeenLastCalledWith('import_source',{kind:'lyrics',language:'en'});
});
it('reports backend decode errors and native failures without another import path',async()=>{
 const browser=vi.fn();vi.mocked(invoke).mockRejectedValue('import-http:{"detail":"Audio konnte nicht dekodiert werden."}');
 await expect(pickAudioImport(browser)).rejects.toThrow('Audio konnte nicht dekodiert werden');
 vi.mocked(invoke).mockRejectedValue('import-read');await expect(pickLyricsImport(browser)).rejects.toThrow('Dateiimport fehlgeschlagen');
 vi.mocked(invoke).mockResolvedValue('{}');await expect(pickAudioImport(browser)).rejects.toThrow('Dateiimport fehlgeschlagen');
 expect(browser).not.toHaveBeenCalled();
});
