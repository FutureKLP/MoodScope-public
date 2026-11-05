import {useEffect,useRef,useState} from 'react';
import {invoke,isTauri} from '@tauri-apps/api/core';
import {api,json} from './api';
import {t as tr,useLanguage} from './i18n';

export function Lifecycle({onStop}:{onStop:()=>void}){
  useLanguage();
  const [health,setHealth]=useState<any>(null),[state,setState]=useState(''),[error,setError]=useState('');
  const [confirmation,setConfirmation]=useState<'restart'|'stop'|null>(null);
  const cancel=useRef<HTMLButtonElement>(null),trigger=useRef<HTMLButtonElement|null>(null);
  useEffect(()=>{api('/health').then(setHealth).catch(()=>{})},[]);
  useEffect(()=>{if(confirmation)cancel.current?.focus();else trigger.current?.focus()},[confirmation]);
  async function control(action:'restart'|'stop'){
    setConfirmation(null);setError('');setState(action);onStop();
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
  return <><div className="system-actions"><span title={tr(health?.system_control?'App und lokaler Dienst werden gemeinsam gesteuert':'Für die Dienststeuerung den Projektstarter verwenden')}>{tr(health?.system_control?'Dienst bereit':'Direkter Dienst')}</span>{(['restart','stop'] as const).map(action=><button key={action} disabled={!health?.system_control||!!state} onClick={e=>{trigger.current=e.currentTarget;setConfirmation(action)}}>{tr(action==='restart'?'Neustarten':'Beenden')}</button>)}</div>{error&&<div className="lifecycle-error" role="alert">{tr(error)}</div>}{confirmation&&<div className="confirmation-backdrop"><section className="panel confirmation-dialog" role="alertdialog" aria-modal="true" aria-labelledby="lifecycle-title" aria-describedby="lifecycle-description" onKeyDown={e=>{if(e.key==='Escape'){e.preventDefault();setConfirmation(null)}if(e.key==='Tab'){const buttons=Array.from(e.currentTarget.querySelectorAll('button'));if(e.shiftKey&&document.activeElement===buttons[0]){e.preventDefault();buttons.at(-1)?.focus()}else if(!e.shiftKey&&document.activeElement===buttons.at(-1)){e.preventDefault();buttons[0]?.focus()}}}}><span className="eyebrow">MOODSCOPE</span><h2 id="lifecycle-title">{tr(confirmation==='restart'?'MoodScope neu starten':'MoodScope beenden')}</h2><p id="lifecycle-description">{tr(confirmation==='restart'?'MoodScope neu starten? Wiedergabe wird beendet und laufende Analyseaufträge werden abgebrochen. Gespeicherte Daten bleiben erhalten.':'MoodScope beenden? Wiedergabe und laufende Analyseaufträge werden beendet. Gespeicherte Daten bleiben erhalten.')}</p><div className="confirmation-actions"><button ref={cancel} onClick={()=>setConfirmation(null)}>{tr('Abbrechen')}</button><button className={confirmation==='stop'?'danger-button':'primary'} onClick={()=>void control(confirmation)}>{tr(confirmation==='restart'?'Neustarten':'Beenden')}</button></div></section></div>}{state&&<div className="lifecycle-overlay"><div className="panel"><span className="eyebrow">MOODSCOPE</span><h2>{tr(state==='stopped'?'Für heute beendet.':'MoodScope startet neu.')}</h2><p>{tr(state==='stopped'?'Der lokale Dienst ist beendet. Deine gespeicherten Songs bleiben erhalten. Zum nächsten Start Start-MoodScope.cmd oder das Startskript öffnen.':'Der Analysedienst wird als neuer Prozess gestartet und die Oberfläche anschließend neu geladen.')}</p></div></div>}</>;
}
