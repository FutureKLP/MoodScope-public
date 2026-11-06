import {useConfirm} from './ConfirmDialog';
import {useEffect,useState} from 'react';
import {invoke,isTauri} from '@tauri-apps/api/core';
import {api,json} from './api';
import {t as tr,useLanguage} from './i18n';

export function Lifecycle({onStop,onStopped=()=>{}}:{onStop:()=>void;onStopped?:()=>void}){
  useLanguage();
  const [health,setHealth]=useState<any>(null),[state,setState]=useState(''),[error,setError]=useState('');
  const {confirm,dialog}=useConfirm();
  useEffect(()=>{api('/health',{signal:AbortSignal.timeout(3000)}).then(setHealth).catch(()=>{})},[]);
  async function finishStop(){setState('stopped');onStopped();if(isTauri())await invoke('exit_app')}
  async function control(action:'restart'|'stop'){
    if(!await confirm({title:action==='restart'?'MoodScope neu starten':'MoodScope beenden',message:action==='restart'?'MoodScope neu starten? Wiedergabe wird beendet und laufende Analyseaufträge werden abgebrochen. Gespeicherte Daten bleiben erhalten.':'MoodScope beenden? Wiedergabe und laufende Analyseaufträge werden beendet. Gespeicherte Daten bleiben erhalten.',confirmLabel:action==='restart'?'Neustarten':'Beenden',danger:action==='stop'}))return;
    setError('');setState(action);onStop();
    try{
      if(!health?.system_control&&isTauri()){
        await invoke(action==='restart'?'restart_app':'exit_app');return;
      }
      try{await api('/system',{...json({action,force:true}),signal:AbortSignal.timeout(5000)})}
      catch(e){
        let online=false;try{online=(await api('/health',{signal:AbortSignal.timeout(2000)})).status==='ok'}catch{}
        if(online)throw e;
        if(action==='stop'){await finishStop();return}
        if(isTauri()){await invoke('restart_app');return}
        throw Error('Der Dienst ist bereits beendet. Für einen neuen Start Start-MoodScope.cmd oder das Startskript öffnen.');
      }
      if(action==='stop')await finishStop();
      else{
        const deadline=Date.now()+45000;
        while(Date.now()<deadline){
          await new Promise(r=>setTimeout(r,900));
          try{
            const next=await api('/health',{signal:AbortSignal.timeout(2500)});
            if(next.status==='ok'&&next.instance_id!==health?.instance_id){
              if(isTauri())await invoke('restart_app');else window.location.reload();return;
            }
          }catch{}
        }
        throw Error('Neustart dauert länger. Diagnose prüfen oder Start-MoodScope.cmd erneut öffnen.');
      }
    }catch(e){setError(e instanceof Error?e.message:String(e));setState('')}
  }
  return <><div className="system-actions"><span data-tooltip={tr(health?.system_control?'App und lokaler Dienst werden gemeinsam gesteuert':'Für die Dienststeuerung den Projektstarter verwenden')}>{tr(health?.system_control?'Dienst bereit':'Direkter Dienst')}</span>{(['restart','stop'] as const).map(action=><button key={action} disabled={(!health?.system_control&&!isTauri())||!!state} onClick={()=>void control(action)}>{tr(action==='restart'?'Neustarten':'Beenden')}</button>)}</div>{error&&<div className="lifecycle-error" role="alert">{tr(error)}</div>}{dialog}{state&&<div className="lifecycle-overlay"><div className="panel"><span className="eyebrow">MOODSCOPE</span><h2>{tr(state==='stopped'?'Für heute beendet.':state==='stop'?'MoodScope wird beendet.':'MoodScope startet neu.')}</h2><p>{tr(state==='stopped'?'Der lokale Dienst ist beendet. Deine gespeicherten Songs bleiben erhalten. Zum nächsten Start Start-MoodScope.cmd oder das Startskript öffnen.':state==='stop'?'Wiedergabe wird gestoppt und der lokale Dienst beendet.':'Der Analysedienst wird als neuer Prozess gestartet und die Oberfläche anschließend neu geladen.')}</p></div></div>}</>;
}
