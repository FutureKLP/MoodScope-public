// @vitest-environment jsdom
import {render,screen,fireEvent,cleanup,act} from '@testing-library/react';
import {it,expect,vi,afterEach} from 'vitest';
import {ProviderSettings} from './Providers';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});

it.each([
 ['Google Gemini','Google Gemini: cloud models'],['OpenAI / ChatGPT','OpenAI: cloud text models'],
 ['Mistral / Voxtral','Mistral: text models'],['Anthropic Claude','Anthropic Claude: text scoring'],
 ['DeepSeek','DeepSeek: text scoring'],['Ollama','Ollama: your own text model'],
 ['LM Studio','LM Studio: your own model'],['Custom compatible server','Custom server: protocol'],
])('explains %s capabilities in English without sending inference',async(name,description)=>{
 setLanguage('en');const posts:any[]=[];
 vi.stubGlobal('fetch',vi.fn(async(_input:any,init?:RequestInit)=>{if(init?.method==='POST')posts.push(init);return new Response(JSON.stringify({profiles:[]}))}));
 render(<ProviderSettings perform={fn=>fn()} busy={false}/>);await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name}));
 expect(document.querySelector('.provider-description')?.textContent).toContain(description);
 expect(screen.getByLabelText('AI server API key').getAttribute('type')).toBe('password');
 expect(posts).toEqual([]);
});

it('discards model discovery after switching to a different server',async()=>{
 setLanguage('de');let finish!:(response:Response)=>void;
 vi.stubGlobal('fetch',vi.fn(async(input:any)=>{
  if(String(input).endsWith('/providers/models'))return new Promise<Response>(resolve=>{finish=resolve});
  return new Response(JSON.stringify({profiles:[]}));
 }));
 render(<ProviderSettings perform={fn=>fn()} busy={false}/>);await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name:'Verbindung prüfen und Modelle laden'}));
 fireEvent.click(screen.getByRole('button',{name:'LM Studio'}));
 await act(async()=>finish(new Response(JSON.stringify({models:['old-server-model']}))));
 expect(screen.queryByLabelText('Modell vom Server')).toBeNull();
 expect((screen.getByLabelText('KI-Server Modell-ID') as HTMLInputElement).value).toBe('');
});

it('clears entered credentials on recipient changes and after saving, never using local storage',async()=>{
 setLanguage('de');const changes=vi.fn();const bodies:any[]=[];
 vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
  if(init?.body)bodies.push(JSON.parse(String(init.body)));
  if(String(input).endsWith('/provider-routes'))return new Response(JSON.stringify({routes:{},targets:{},version:'updated'}));
  return new Response(JSON.stringify({profiles:[]}));
 }));
 render(<ProviderSettings perform={fn=>fn()} busy={false} onRoutesChange={changes}/>);await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name:'Ollama'}));
 fireEvent.change(screen.getByLabelText('KI-Server API-Key'),{target:{value:'fixture-session-value'}});
 fireEvent.change(screen.getByLabelText('KI-Server Basis-URL'),{target:{value:'https://authored.example/v1'}});
 expect((screen.getByLabelText('KI-Server API-Key') as HTMLInputElement).value).toBe('');
 fireEvent.change(screen.getByLabelText('KI-Server API-Key'),{target:{value:'fixture-new-value'}});
 fireEvent.change(screen.getByLabelText('KI-Server Modell-ID'),{target:{value:'fixture'}});
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Serverprofil speichern'})));
 expect((screen.getByLabelText('KI-Server API-Key') as HTMLInputElement).value).toBe('');
 expect(bodies[0].api_key).toBe('fixture-new-value');expect(changes).toHaveBeenCalledWith(expect.objectContaining({version:'updated'}));
 expect(JSON.stringify(localStorage)).not.toContain('fixture-new-value');
 expect(document.body.textContent).not.toContain('fixture-new-value');
});
it('saves explicit audio capabilities and activates only the selected profile',async()=>{
 setLanguage('de');const calls:Array<{url:string;body:any}>=[];const changed=vi.fn();
 vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
  const url=String(input);const body=typeof init?.body==='string'?JSON.parse(init.body):null;calls.push({url,body});
  if(url.endsWith('/audio'))return new Response(JSON.stringify({provider:'Authored audio',model:'audio-fixture'}));
  return new Response(JSON.stringify({profiles:[{id:'fixture',name:'Authored audio',model:'audio-fixture',base_url:'https://api.openai.com/v1',protocol:'openai',audio_input:true,audio_usage_confirmed:true,configured:true}]}));
 }));
 render(<ProviderSettings perform={fn=>fn()} busy={false} onAudioChange={changed}/>);await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name:'OpenAI / ChatGPT'}));
 fireEvent.change(screen.getByLabelText('KI-Server Modell-ID'),{target:{value:'audio-fixture'}});
 fireEvent.click(screen.getByLabelText('Dieses Modell unterstützt Audioeingaben über Chat Completions (input_audio).'));
 fireEvent.click(screen.getByLabelText('Nutzungsbedingungen und mögliche Kosten dieses Audioprofils habe ich geprüft.'));
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Serverprofil speichern'})));
 expect(calls.find(c=>c.body?.model==='audio-fixture')?.body).toMatchObject({audio_input:true,audio_usage_confirmed:true});
 expect(changed).not.toHaveBeenCalled();
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Für Audio-API verwenden'})));
 expect(changed).toHaveBeenCalledWith({provider:'Authored audio',model:'audio-fixture'});
});

it('discovers a home-server model without saving a profile or submitting audio or text',async()=>{
 setLanguage('de');const bodies:any[]=[];
 vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
  if(String(input).endsWith('/providers/models')){bodies.push(JSON.parse(String(init?.body)));return new Response(JSON.stringify({models:['authored-home-model'],generated:false}))}
  return new Response(JSON.stringify({profiles:[]}));
 }));
 render(<ProviderSettings perform={fn=>fn()} busy={false}/>);await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name:'Ollama'}));
 fireEvent.change(screen.getByLabelText('KI-Server Basis-URL'),{target:{value:'http://192.168.1.20:11434/v1'}});
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Verbindung prüfen und Modelle laden'})));
 fireEvent.change(screen.getByLabelText('Modell vom Server'),{target:{value:'authored-home-model'}});
 expect((screen.getByLabelText('KI-Server Modell-ID') as HTMLInputElement).value).toBe('authored-home-model');
 expect(bodies).toEqual([{base_url:'http://192.168.1.20:11434/v1',api_key:''}]);
});
