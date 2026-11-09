// @vitest-environment jsdom
import {render,screen,fireEvent,cleanup,act} from '@testing-library/react';
import {it,expect,vi,afterEach} from 'vitest';
import {ProviderSettings} from './Providers';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
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
