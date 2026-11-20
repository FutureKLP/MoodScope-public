// @vitest-environment jsdom
import {afterEach,it,expect,vi} from 'vitest';
import {api,ApiError,CONTROL_API,controlOrigin} from './api';
import {setLanguage} from './i18n';
afterEach(()=>{vi.unstubAllGlobals();setLanguage('de')});
it('preserves caller headers, payload and cancellation while selecting the active locale',async()=>{
 setLanguage('en');const abort=new AbortController();const fetcher=vi.fn(async()=>new Response(JSON.stringify({tracks:[]})));vi.stubGlobal('fetch',fetcher);
 const value=await api<{tracks:unknown[]}>('/library',{headers:new Headers({'X-Authored':'fixture'}),signal:abort.signal});
 expect(value.tracks).toEqual([]);const [url,init]=fetcher.mock.calls[0] as unknown as [string,RequestInit];
 expect(url).toBe(CONTROL_API+'/api/library');expect(new Headers(init.headers).get('Accept-Language')).toBe('en');expect(new Headers(init.headers).get('X-Authored')).toBe('fixture');expect(init.signal).toBe(abort.signal);
});
it('reports non-JSON server failures and structured validation without echoing sensitive input',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response('unavailable',{status:503,statusText:'Unavailable'})));
 await expect(api('/library')).rejects.toMatchObject({status:503,message:'Unavailable'});
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({detail:[{input:'authored-confidential-value'}]}),{status:422})));
 try{await api('/providers');throw Error('Expected failure')}catch(error){expect(error).toBeInstanceOf(ApiError);expect(String(error)).not.toContain('authored-confidential-value')}
});
it('uses a separate connection pool only for loopback HTTP services',()=>{
 expect(controlOrigin('http://127.0.0.1:8765')).toBe('http://localhost:8765');expect(controlOrigin('http://localhost:8765')).toBe('http://127.0.0.1:8765');expect(controlOrigin('https://example.invalid')).toBe('https://example.invalid');
});

it('explains a service interruption in both languages without retrying the request',async()=>{
 const fetcher=vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
 vi.stubGlobal('fetch',fetcher);
 await expect(api('/jobs/fixture')).rejects.toMatchObject({status:0,message:'Lokaler Dienst nicht erreichbar oder Zeitlimit überschritten. Dienststatus prüfen und erneut versuchen. Gespeicherte Analysen bleiben erhalten.'});
 setLanguage('en');
 await expect(api('/jobs/fixture')).rejects.toMatchObject({status:0,message:'The local service is unreachable or the request timed out. Check the service status before trying again. Saved analyses are preserved.'});
 expect(fetcher).toHaveBeenCalledTimes(2);
});

it('preserves deliberate request cancellation instead of reporting a service failure',async()=>{
 const failure=new DOMException('Authored cancellation','AbortError');
 vi.stubGlobal('fetch',vi.fn().mockRejectedValue(failure));
 await expect(api('/library')).rejects.toBe(failure);
});
