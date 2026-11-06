import {useContext,useState} from 'react';
import {createPortal} from 'react-dom';
import {AtmosphereThemeContext} from './Atmosphere';
import {t,useLanguage} from './i18n';

export function ErrorNotice({message,onDismiss}:{message:string;onDismiss?:()=>void}){
 useLanguage();const theme=useContext(AtmosphereThemeContext);
 const [host]=useState(()=>{let element=document.getElementById('moodscope-notices');if(!element){element=document.createElement('div');element.id='moodscope-notices';element.className='app-notice-stack';document.body.append(element)}return element});
 if(!message)return null;
 return createPortal(<section className={`app-notice ${theme.enabled?'ambient-notice':''}`} role="alert" style={theme.style}><p>{t(message)}</p>{onDismiss&&<button aria-label={t('Fehlermeldung schließen')} onClick={onDismiss}>{t('Schließen')}</button>}</section>,host);
}
