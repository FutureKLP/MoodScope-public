import {API} from './api';
import {t} from './i18n';

// A media element hides HTTP error details. Probe only our managed original
// endpoint and cancel successful bodies so recovery never downloads a song.
export async function playbackFailure(url:string):Promise<string>{
 const fallback=t('Audio-Wiedergabe fehlgeschlagen');
 try{
  const source=new URL(url),base=new URL(API);
  if(source.origin!==base.origin||!/^\/api\/tracks\/[a-f0-9]{64}\/audio$/.test(source.pathname)||source.search)return fallback;
  const response=await fetch(source.href,{headers:{Range:'bytes=0-0'},signal:AbortSignal.timeout(5000)});
  await response.body?.cancel();
  return response.status===409?t('Lokale Audiokopie fehlt oder ist beschädigt. Originaldatei erneut importieren; gespeicherte Daten bleiben erhalten.'):fallback;
 }catch{return fallback}
}
