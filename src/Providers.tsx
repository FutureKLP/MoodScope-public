import {useConfirm} from './ConfirmDialog';
import {t as tr,useLanguage} from './i18n';
import {useEffect,useState} from 'react';
import {api,json} from './api';

type Props={perform:(work:()=>Promise<void>)=>Promise<void>;busy:boolean;onAudioChange?:(profile:{provider:string;model:string})=>void};
const presets:Record<string,{name:string;protocol:string;url:string}>={
  gemini:{name:'Google Gemini',protocol:'gemini',url:'https://generativelanguage.googleapis.com/v1beta'},
  openai:{name:'OpenAI / ChatGPT',protocol:'openai',url:'https://api.openai.com/v1'},
  mistral:{name:'Mistral / Voxtral',protocol:'openai',url:'https://api.mistral.ai/v1'},
  anthropic:{name:'Anthropic Claude',protocol:'anthropic',url:'https://api.anthropic.com/v1'},
  deepseek:{name:'DeepSeek',protocol:'openai',url:'https://api.deepseek.com'},
  ollama:{name:'Ollama',protocol:'openai',url:'http://127.0.0.1:11434/v1'},
  lm:{name:'LM Studio',protocol:'openai',url:'http://127.0.0.1:1234/v1'},
};

export function ProviderSettings({perform,busy,onAudioChange}:Props){
  const language=useLanguage();
  const {confirm,dialog}=useConfirm();
  const [profiles,setProfiles]=useState<any[]>([]),[name,setName]=useState(''),[url,setUrl]=useState(presets.ollama.url);
  const [protocol,setProtocol]=useState('openai'),[model,setModel]=useState(''),[key,setKey]=useState('');
  const [audioInput,setAudioInput]=useState(false),[usage,setUsage]=useState(false),[activeAudio,setActiveAudio]=useState<any>(null);
  const [editing,setEditing]=useState<string|null>(null),[free,setFree]=useState(false),[message,setMessage]=useState('');
  async function refresh(){const value=await api('/providers');setProfiles(value.profiles||[]);setActiveAudio(value.audio||null)}
  useEffect(()=>{void perform(refresh)},[]);
  function preset(type:string){const p=presets[type];setEditing(null);setKey('');setModel('');setFree(false);setAudioInput(false);setUsage(false);setProtocol(p.protocol);setName(p.name);setUrl(p.url);setMessage('')}
  return <>{dialog}<section className="panel workspace-panel provider-settings">
    <h2>{tr("KI-Anbieter und eigene Modellserver")}</h2>
    <p>{tr("Profile für Gemini, OpenAI, Mistral, Claude, DeepSeek und eigene Server. Textprofile wählst du unter Interpretation. Ein passendes Audioprofil aktivierst du hier für Emotionskurve, Gesangserkennung und Instrumenthinweise. Lokale Berechnung bleibt der Standard.")}</p>
    <div className="provider-presets">{Object.entries(presets).map(([id,p])=><button key={id} onClick={()=>preset(id)}>{p.name}</button>)}</div>
    <div className="note-grid provider-form">
      <label>{tr("Profilname")}<input aria-label={tr("KI-Profilname")} value={name} onChange={e=>setName(e.target.value)}/></label>
      <label>{tr("API-Protokoll")}<select aria-label={tr("API-Protokoll")} value={protocol} onChange={e=>{setProtocol(e.target.value);setAudioInput(false);setUsage(false)}}><option value="openai">{tr("OpenAI-kompatibel · Text / optional Audio")}</option><option value="anthropic">{tr("Anthropic Messages · Text")}</option><option value="gemini">{tr("Gemini · Text und vorbereitete Audioanalyse")}</option></select></label>
      <label>{tr("Basis-URL")}<input aria-label={tr("KI-Server Basis-URL")} value={url} onChange={e=>setUrl(e.target.value)}/></label>
      <label>{tr("Exakte Modell-ID")}<input aria-label={tr("KI-Server Modell-ID")} value={model} onChange={e=>setModel(e.target.value)} placeholder={tr("Modell-ID aus deinem Anbieter oder lokalen Server")}/></label>
      <label>{tr("API-Key · bei lokalem Server optional")}<input aria-label={tr("KI-Server API-Key")} autoComplete="off" type="password" value={key} onChange={e=>setKey(e.target.value)}/></label>
    </div>
    {protocol==='openai'&&<><label className="check"><input type="checkbox" checked={audioInput} onChange={e=>{setAudioInput(e.target.checked);setUsage(false)}}/>{tr('Dieses Modell unterstützt Audioeingaben über Chat Completions (input_audio).')}</label><p>{tr('Zum Beispiel OpenAI-Audiomodelle, Mistral/Voxtral oder ein kompatibler eigener Audioserver. Eine normale Textmodell-ID reicht nicht. Claude und das DeepSeek-Textprofil erhalten hier keine Audiodateien.')}</p>{audioInput&&<label className="check"><input type="checkbox" checked={usage} onChange={e=>setUsage(e.target.checked)}/>{tr('Nutzungsbedingungen und mögliche Kosten dieses Audioprofils habe ich geprüft.')}</label>}</>}
    {activeAudio?.configured&&<p>{tr('Vorbereitetes Audioprofil')}: {activeAudio.provider} · {activeAudio.model}</p>}
    <p>{tr("OpenAI, Claude und DeepSeek können kostenpflichtig sein. Ein Chat-Abonnement ist kein API-Key. Eigene lokale Server können ohne Key laufen. Adresse und Modellwahl werden lokal gespeichert, Keys ausschließlich im Arbeitsspeicher bis zum Backend-Neustart. Leeres Key-Feld beim Bearbeiten erhält den vorhandenen Sitzungs-Key. Profil entfernen löscht ihn.")}</p>
    {protocol==='gemini'&&<><p>{tr("Für Gemini-Audio werden Audio und Lyrics übertragen. Kostenlose Kontingente sind begrenzt; die App kann den Abrechnungsstatus nicht überprüfen. Im Gratis-Tarif können Inhalte zur Produktverbesserung verwendet werden.")}</p><label className="check"><input type="checkbox" checked={free} onChange={e=>setFree(e.target.checked)}/>{tr("Mein Gemini-Projekt hat keine aktivierte Abrechnung; Gratisbedingungen habe ich geprüft.")}</label></>}
    <p>{tr("Textprofile übertragen keine Audiodateien. Lokale/LAN-Server können selbst Cloud-Modelle nutzen; deren Konfiguration prüfen. Es gibt keinen automatischen Anbieterwechsel und keine pauschale Gratiszusage.")}</p>
    <button disabled={busy||!name.trim()||!model.trim()} onClick={()=>void perform(async()=>{await api('/providers',json({id:editing,name,protocol,base_url:url,model,api_key:key,free_project_confirmed:free,audio_input:audioInput,audio_usage_confirmed:usage}));setKey('');setEditing(null);await refresh();setMessage(tr("Profil lokal gespeichert. Zugangsdaten bleiben nur in dieser Sitzung."))})}>{tr("Serverprofil speichern")}</button>
    <p className="progress" role="status">{tr(message)}</p>
    <div className="library-list">{profiles.map(p=><article className="library-card" key={p.id}>
      <div><h3>{p.name} · {p.model}</h3><p>{p.base_url} · {p.configured?tr("Sitzungs-Key vorhanden"):tr("Kein Sitzungs-Key")} · {(p.protocol==='gemini'||p.audio_input)?tr("Text + Audio möglich"):tr("Textdeutung")}</p></div>
      {(p.protocol==='gemini'||p.audio_input)&&<button aria-pressed={activeAudio?.profile_id===p.id} disabled={busy||(p.protocol==='gemini'?(!p.configured||!p.free_project_confirmed):!p.audio_usage_confirmed)} onClick={()=>void perform(async()=>{const result=await api(`/providers/${p.id}/audio`,json({}));await refresh();onAudioChange?.(result);setMessage(tr("{0} / {1} für den ausdrücklich gewählten Audio-API-Modus vorbereitet.",[result.provider,result.model]))})}>{tr("Für Audio-API verwenden")}</button>}
      <button disabled={busy} onClick={()=>{setEditing(p.id);setName(p.name);setUrl(p.base_url);setProtocol(p.protocol);setModel(p.model);setFree(p.free_project_confirmed||false);setAudioInput(p.audio_input||false);setUsage(p.audio_usage_confirmed||false);setKey('')}}>{tr("Bearbeiten / Key setzen")}</button>
      <button disabled={busy} onClick={async()=>{if(await confirm({title:'Profil entfernen',message:'Dieses Serverprofil und den gespeicherten Sitzungs-Key entfernen? Songdaten bleiben erhalten.',confirmLabel:'Profil entfernen',danger:true}))void perform(async()=>{await api(`/providers/${p.id}/remove`,json({}));await refresh()})}}>{tr("Profil entfernen")}</button>
    </article>)}</div>
  </section></>;
}
