import {useSyncExternalStore} from 'react';
import translations from '../backend/locales/en.json';
export type Language='de'|'en';
const dictionary:Record<string,string>=translations;
const reverse=Object.fromEntries(Object.entries(dictionary).map(([de,en])=>[en,de]));
let language:Language='de';
try{if(localStorage.getItem('moodscope-language')==='en')language='en'}catch{}
if(typeof document!=='undefined')document.documentElement.lang=language;
const listeners=new Set<()=>void>();
export const getLanguage=()=>language;
export function setLanguage(next:Language){language=next;try{localStorage.setItem('moodscope-language',next)}catch{}document.documentElement.lang=next;listeners.forEach(f=>f())}
export function useLanguage(){return useSyncExternalStore(f=>{listeners.add(f);return()=>{listeners.delete(f)}},getLanguage)}
const cache:Record<Language,Map<string,string>>={de:new Map(),en:new Map()};
const catalogues={de:reverse,en:dictionary};
const escape=(part:string)=>part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const templates=Object.fromEntries(Object.entries(catalogues).map(([locale,entries])=>[locale,Object.entries(entries).filter(([key])=>key.includes('{0}')).map(([key,value])=>({pattern:new RegExp('^'+key.split(/\{\d+\}/g).map(escape).join('(.+?)')+'$'),value}))])) as Record<Language,{pattern:RegExp;value:string}[]>;
const fragments=Object.fromEntries(Object.entries(catalogues).map(([locale,entries])=>[locale,Object.entries(entries).filter(([key])=>key.length>=12).sort((a,b)=>b[0].length-a[0].length)])) as Record<Language,[string,string][]>;
export function t(value:string,args:unknown[]=[]):string{
  if(typeof value!=='string')return '';
  let translated=cache[language].get(value);
  if(translated===undefined){
    translated=catalogues[language][value]??value;
    if(translated===value){
      for(const template of templates[language]){
        const match=value.match(template.pattern);
        if(match){translated=template.value.replace(/\{(\d+)\}/g,(_,i)=>match[Number(i)+1]);break}
      }
      if(translated===value)for(const [from,to] of fragments[language])if(translated.includes(from))translated=translated.replaceAll(from,to);
    }
    if(cache[language].size>=2048)cache[language].clear();
    cache[language].set(value,translated);
  }
  return translated.replace(/\{(\d+)\}/g,(match,index)=>index in args?String(args[Number(index)]):match);
}
export function LanguageSelect({disabled=false}:{disabled?:boolean}){const selected=useLanguage();return <label className="language-select"><span>{t('App-Sprache')}</span><select aria-label={t('App-Sprache')} value={selected} disabled={disabled} onChange={e=>setLanguage(e.target.value as Language)}><option value="de">Deutsch</option><option value="en">English</option></select></label>}
