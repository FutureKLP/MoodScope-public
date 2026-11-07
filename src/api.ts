import {getLanguage,t} from './i18n';
// A production browser page is served by its own backend; native/dev keep the fixed service URL.
const servedLocally=typeof window!=='undefined'&&window.location.protocol==='http:'&&['127.0.0.1','localhost'].includes(window.location.hostname)&&window.location.port!=='1420';
export const API=import.meta.env.VITE_API_URL || (servedLocally?window.location.origin:'http://127.0.0.1:8765');
// Keep JSON/control requests out of the browser's six streaming connections.
export function controlOrigin(origin:string){
  const url=new URL(origin);
  if(url.protocol==='http:'&&['127.0.0.1','localhost'].includes(url.hostname))url.hostname=url.hostname==='127.0.0.1'?'localhost':'127.0.0.1';
  return url.toString().replace(/\/$/,'');
}
export const CONTROL_API=controlOrigin(API);
export class ApiError extends Error{constructor(message:string,public status:number){super(message)}}
export async function api(path:string,init?:RequestInit){
  const response=await fetch(CONTROL_API+'/api'+path,{...init,headers:{...Object.fromEntries(new Headers(init?.headers).entries()),'Accept-Language':getLanguage()},signal:init?.signal||AbortSignal.timeout(180000)});
  if(!response.ok){
    const error=await response.json().catch(()=>({detail:response.statusText}));
    throw new ApiError(t(typeof error.detail==='string'?error.detail:'Ungültige Eingabe; bitte Felder prüfen.'),response.status);
  }
  return response.json();
}
export const json=(body:unknown)=>({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
