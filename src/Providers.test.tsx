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
