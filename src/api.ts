export const API=import.meta.env.VITE_API_URL || 'http://127.0.0.1:8765';
export class ApiError extends Error{constructor(message:string,public status:number){super(message)}}
export async function api(path:string,init?:RequestInit){
  const response=await fetch(API+'/api'+path,{...init,signal:init?.signal||AbortSignal.timeout(180000)});
  if(!response.ok){
    const error=await response.json().catch(()=>({detail:response.statusText}));
    throw new ApiError(typeof error.detail==='string'?error.detail:'Ungültige Eingabe; bitte Felder prüfen.',response.status);
  }
  return response.json();
}
export const json=(body:unknown)=>({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
