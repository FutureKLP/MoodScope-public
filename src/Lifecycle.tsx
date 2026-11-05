import {useEffect,useState} from 'react';
import {invoke,isTauri} from '@tauri-apps/api/core';
import {api,json} from './api';

export function Lifecycle({onStop}:{onStop:()=>void}){
  const [health,setHealth]=useState<any>(null),[state,setState]=useState(''),[error,setError]=useState('');
  useEffect(()=>{api('/health').then(setHealth).catch(()=>{})},[]);
  async function control(action:'restart'|'stop'){
    if(!window.confirm(action==='restart'?'MoodScope neu starten? Wiedergabe wird beendet und laufende Analyseaufträge werden abgebrochen. Gespeicherte Daten bleiben erhalten.':'MoodScope beenden? Wiedergabe und laufende Analyseaufträge werden beendet. Gespeicherte Daten bleiben erhalten.'))return;
    setError('');setState(action);onStop();
    try{
      await api('/system',json({action,force:true}));
      if(action==='stop'){
        setState('stopped');
        if(isTauri())await invoke('exit_app');
      }else{
        const deadline=Date.now()+45000;
        while(Date.now()<deadline){
          await new Promise(r=>setTimeout(r,900));
          try{const next=await api('/health');if(next.status==='ok'&&next.instance_id!==health.instance_id){window.location.reload();return}}catch{}
        }
        throw Error('Neustart dauert länger. Diagnose prüfen oder Start-MoodScope.cmd erneut öffnen.');
      }
    }catch(e){setError(e instanceof Error?e.message:String(e));setState('')}
  }
  return <><div className="system-actions"><span title={health?.system_control?'App und lokaler Dienst werden gemeinsam gesteuert':'Für die Dienststeuerung den Projektstarter verwenden'}>{health?.system_control?'Dienst bereit':'Direkter Dienst'}</span><button disabled={!health?.system_control||!!state} onClick={()=>void control('restart')}>Neustarten</button><button disabled={!health?.system_control||!!state} onClick={()=>void control('stop')}>Beenden</button></div>{error&&<div className="lifecycle-error" role="alert">{error}</div>}{state&&<div className="lifecycle-overlay"><div className="panel"><span className="eyebrow">MOODSCOPE</span><h2>{state==='stopped'?'Für heute beendet.':'MoodScope startet neu.'}</h2><p>{state==='stopped'?'Der lokale Dienst ist beendet. Deine gespeicherten Songs bleiben erhalten. Zum nächsten Start Start-MoodScope.cmd oder das Startskript öffnen.':'Der Analysedienst wird als neuer Prozess gestartet und die Oberfläche anschließend neu geladen.'}</p></div></div>}</>;
}
