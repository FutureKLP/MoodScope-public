// @vitest-environment jsdom
import {afterEach,expect,it,vi} from 'vitest';
import {API} from './api';
import {playbackFailure} from './playbackFailure';
import {setLanguage} from './i18n';

afterEach(()=>{vi.unstubAllGlobals();setLanguage('de')});
const url=API+'/api/tracks/'+'a'.repeat(64)+'/audio';

it('explains a missing or damaged managed copy in both languages and closes the probe body',async()=>{
 const cancel=vi.fn();const fetcher=vi.fn(async()=>({status:409,body:{cancel}}));vi.stubGlobal('fetch',fetcher);
 expect(await playbackFailure(url)).toContain('Originaldatei erneut importieren');
 setLanguage('en');expect(await playbackFailure(url)).toContain('Reimport the original file');
 expect(fetcher.mock.calls[0]).toEqual([url,{headers:{Range:'bytes=0-0'},signal:expect.any(AbortSignal)}]);
 expect(cancel).toHaveBeenCalledTimes(2);
});
it('does not probe external, blob, stem, or unrelated URLs',async()=>{
 const fetcher=vi.fn();vi.stubGlobal('fetch',fetcher);
 for(const value of ['blob:fixture','https://example.test/api/tracks/'+'a'.repeat(64)+'/audio',url+'?other=1',url.replace('/audio','/stems'),url.replace('/tracks/','/other/')])expect(await playbackFailure(value)).toBe('Audio-Wiedergabe fehlgeschlagen');
 expect(fetcher).not.toHaveBeenCalled();
});
it('keeps a general playback failure for valid audio, network errors, and other HTTP failures',async()=>{
 const cancel=vi.fn();
 for(const status of [200,206,404,500]){
  vi.stubGlobal('fetch',vi.fn(async()=>({status,body:{cancel}})));
  expect(await playbackFailure(url)).toBe('Audio-Wiedergabe fehlgeschlagen');
 }
 expect(cancel).toHaveBeenCalledTimes(4);
 vi.stubGlobal('fetch',vi.fn(async()=>{throw Error('offline')}));
 expect(await playbackFailure(url)).toBe('Audio-Wiedergabe fehlgeschlagen');
});
