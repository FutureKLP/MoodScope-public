import {useEffect,useState} from 'react';
import {api,json} from './api';

type Props={perform:(work:()=>Promise<void>)=>Promise<void>;busy:boolean};
const presets:Record<string,{name:string;protocol:string;url:string}>={
  gemini:{name:'Google Gemini',protocol:'gemini',url:'https://generativelanguage.googleapis.com/v1beta'},
  openai:{name:'OpenAI / ChatGPT',protocol:'openai',url:'https://api.openai.com/v1'},
  anthropic:{name:'Anthropic Claude',protocol:'anthropic',url:'https://api.anthropic.com/v1'},
  deepseek:{name:'DeepSeek',protocol:'openai',url:'https://api.deepseek.com'},
  ollama:{name:'Ollama',protocol:'openai',url:'http://127.0.0.1:11434/v1'},
  lm:{name:'LM Studio',protocol:'openai',url:'http://127.0.0.1:1234/v1'},
};

export function ProviderSettings({perform,busy}:Props){
  const [profiles,setProfiles]=useState<any[]>([]),[name,setName]=useState(''),[url,setUrl]=useState(presets.ollama.url);
  const [protocol,setProtocol]=useState('openai'),[model,setModel]=useState(''),[key,setKey]=useState('');
  const [editing,setEditing]=useState<string|null>(null),[free,setFree]=useState(false),[message,setMessage]=useState('');
  async function refresh(){setProfiles((await api('/providers')).profiles||[])}
  useEffect(()=>{void perform(refresh)},[]);
  function preset(type:string){const p=presets[type];setEditing(null);setKey('');setModel('');setFree(false);setProtocol(p.protocol);setName(p.name);setUrl(p.url);setMessage('')}
  return <section className="panel workspace-panel">
    <h2>KI-Anbieter und eigene Modellserver</h2>
    <p>Eine gemeinsame Profilverwaltung für Gemini, OpenAI, Claude, DeepSeek und lokale Server. Du wählst das Profil für Textdeutungen im Reiter Interpretation. Lokale KI auf diesem Rechner bleibt der Standard.</p>
    <div className="provider-presets">{Object.entries(presets).map(([id,p])=><button key={id} onClick={()=>preset(id)}>{p.name}</button>)}</div>
    <div className="note-grid">
      <label>Profilname<input aria-label="KI-Profilname" value={name} onChange={e=>setName(e.target.value)}/></label>
      <label>API-Protokoll<select aria-label="API-Protokoll" value={protocol} onChange={e=>setProtocol(e.target.value)}><option value="openai">OpenAI-kompatibel · Text</option><option value="anthropic">Anthropic Messages · Text</option><option value="gemini">Gemini · Text und vorbereitete Audioanalyse</option></select></label>
      <label>Basis-URL<input aria-label="KI-Server Basis-URL" value={url} onChange={e=>setUrl(e.target.value)}/></label>
      <label>Exakte Modell-ID<input aria-label="KI-Server Modell-ID" value={model} onChange={e=>setModel(e.target.value)} placeholder="Modell-ID aus deinem Anbieter oder lokalen Server"/></label>
      <label>API-Key · bei lokalem Server optional<input aria-label="KI-Server API-Key" autoComplete="off" type="password" value={key} onChange={e=>setKey(e.target.value)}/></label>
    </div>
    <p>OpenAI, Claude und DeepSeek können kostenpflichtig sein. Ein Chat-Abonnement ist kein API-Key. Eigene lokale Server können ohne Key laufen. Adresse und Modellwahl werden lokal gespeichert, Keys ausschließlich im Arbeitsspeicher bis zum Backend-Neustart. Leeres Key-Feld beim Bearbeiten erhält den vorhandenen Sitzungs-Key. Profil entfernen löscht ihn.</p>
    {protocol==='gemini'&&<><p>Für Gemini-Audio werden Audio und Lyrics übertragen. Kostenlose Kontingente sind begrenzt; die App kann den Abrechnungsstatus nicht überprüfen. Im Gratis-Tarif können Inhalte zur Produktverbesserung verwendet werden.</p><label className="check"><input type="checkbox" checked={free} onChange={e=>setFree(e.target.checked)}/>Mein Gemini-Projekt hat keine aktivierte Abrechnung; Gratisbedingungen habe ich geprüft.</label></>}
    <p>Textprofile übertragen keine Audiodateien. Lokale/LAN-Server können selbst Cloud-Modelle nutzen; deren Konfiguration prüfen. Es gibt keinen automatischen Anbieterwechsel und keine pauschale Gratiszusage.</p>
    <button disabled={busy||!name.trim()||!model.trim()} onClick={()=>void perform(async()=>{await api('/providers',json({id:editing,name,protocol,base_url:url,model,api_key:key,free_project_confirmed:free}));setKey('');setEditing(null);await refresh();setMessage('Profil lokal gespeichert. Zugangsdaten bleiben nur in dieser Sitzung.')})}>Serverprofil speichern</button>
    <p className="progress" role="status">{message}</p>
    <div className="library-list">{profiles.map(p=><article className="library-card" key={p.id}>
      <div><h3>{p.name} · {p.model}</h3><p>{p.base_url} · {p.configured?'Sitzungs-Key vorhanden':'Kein Sitzungs-Key'} · {p.protocol==='gemini'?'Text + Audio möglich':'Textdeutung'}</p></div>
      {p.protocol==='gemini'&&<button disabled={busy||!p.configured||!p.free_project_confirmed} onClick={()=>void perform(async()=>{const result=await api(`/providers/${p.id}/audio`,json({}));setMessage(`${result.provider} / ${result.model} für den ausdrücklich gewählten Audio-API-Modus vorbereitet.`)})}>Für Audio-API verwenden</button>}
      <button disabled={busy} onClick={()=>{setEditing(p.id);setName(p.name);setUrl(p.base_url);setProtocol(p.protocol);setModel(p.model);setFree(p.free_project_confirmed||false);setKey('')}}>Bearbeiten / Key setzen</button>
      <button disabled={busy} onClick={()=>void perform(async()=>{await api(`/providers/${p.id}/remove`,json({}));await refresh()})}>Profil entfernen</button>
    </article>)}</div>
  </section>;
}
