import {useEffect,useId,useRef,useState} from 'react';
import {createPortal} from 'react-dom';
import {t,useLanguage} from './i18n';
type Request={title:string;message:string;confirmLabel?:string;danger?:boolean};
export function useConfirm(){
  const [request,setRequest]=useState<Request|null>(null);
  const pending=useRef<((value:boolean)=>void)|null>(null);
  useEffect(()=>()=>{pending.current?.(false);pending.current=null},[]);
  function close(value:boolean){const resolve=pending.current;pending.current=null;setRequest(null);resolve?.(value)}
  function confirm(options:Request){pending.current?.(false);return new Promise<boolean>(resolve=>{pending.current=resolve;setRequest(options)})}
  return {confirm,dialog:request?<ConfirmationDialog {...request} onClose={close}/>:null};
}
export function ConfirmationDialog({title,message,confirmLabel='Bestätigen',danger=false,onClose}:Request&{onClose:(value:boolean)=>void}){
  useLanguage();const id=useId(),cancel=useRef<HTMLButtonElement>(null),panel=useRef<HTMLElement>(null);
  useEffect(()=>{const before=document.activeElement as HTMLElement|null;cancel.current?.focus();const previousOverflow=document.body.style.overflow;document.body.style.overflow='hidden';
    const keepFocus=(event:FocusEvent)=>{if(!panel.current?.contains(event.target as Node))cancel.current?.focus()};document.addEventListener('focusin',keepFocus);
    return()=>{document.removeEventListener('focusin',keepFocus);document.body.style.overflow=previousOverflow;if(before?.isConnected)before.focus()};},[]);
  return createPortal(<div className="confirmation-backdrop"><section ref={panel} className="panel confirmation-dialog" role="alertdialog" aria-modal="true" aria-labelledby={id+'-title'} aria-describedby={id+'-message'} onKeyDown={e=>{
    if(e.key==='Escape'){e.preventDefault();e.stopPropagation();onClose(false)}
    if(e.key==='Tab'){const buttons=Array.from(e.currentTarget.querySelectorAll('button'));if(e.shiftKey&&document.activeElement===buttons[0]){e.preventDefault();buttons.at(-1)?.focus()}else if(!e.shiftKey&&document.activeElement===buttons.at(-1)){e.preventDefault();buttons[0]?.focus()}}
  }}><span className="eyebrow">MOODSCOPE</span><h2 id={id+'-title'}>{t(title)}</h2><p id={id+'-message'}>{t(message)}</p><div className="confirmation-actions"><button ref={cancel} onClick={()=>onClose(false)}>{t('Abbrechen')}</button><button className={danger?'danger-button':'primary'} onClick={()=>onClose(true)}>{t(confirmLabel)}</button></div></section></div>,document.body);
}
