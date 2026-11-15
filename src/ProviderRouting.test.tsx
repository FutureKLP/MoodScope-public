// @vitest-environment jsdom
import {act,cleanup,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import {ProviderRouting,TASKS} from './ProviderRouting';
import {setLanguage,t} from './i18n';

afterEach(()=>{cleanup();vi.unstubAllGlobals();setLanguage('de')});
const profiles=[
 {id:'text',name:'Authored text',protocol:'anthropic',model:'text-fixture'},
 {id:'audio',name:'Authored audio',protocol:'openai',audio_input:true,model:'audio-fixture'},
];

it('saves all five assignments in English and restores them after remount',async()=>{
 setLanguage('en');let routes=Object.fromEntries(TASKS.map(task=>[task.id,'prepared']));const saved=vi.fn();const bodies:any[]=[];
 vi.stubGlobal('fetch',vi.fn(async(_input:any,init?:RequestInit)=>{
  if(init?.body){routes=JSON.parse(String(init.body));bodies.push(routes)}
  return new Response(JSON.stringify({routes,targets:{},version:'fixture-version'}));
 }));
 const view=render(<ProviderRouting profiles={profiles} busy={false} perform={fn=>fn()} onSaved={saved}/>);await act(async()=>{});
 for(const task of TASKS){
  if(task.name!=='Interpretation')expect(t(task.name)).not.toBe(task.name);
  expect(t(task.data)).not.toBe(task.data);
  const select=screen.getByLabelText(t(task.name)+' · Provider assignment') as HTMLSelectElement;
  expect([...select.options].some(option=>option.value==='text')).toBe(!task.audio);
  fireEvent.change(select,{target:{value:task.audio?'audio':'text'}});
 }
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Save task assignments'})));
 expect(bodies).toEqual([{audio:'audio',lyrics:'text',transcription:'audio',instruments:'audio',interpretation:'text'}]);
 expect(screen.getByRole('status').textContent).toBe('Task assignments saved. Review transfer consent again.');
 expect(saved).toHaveBeenCalledOnce();view.unmount();
 render(<ProviderRouting profiles={profiles} busy={false} perform={fn=>fn()}/>);await act(async()=>{});
 expect((screen.getByLabelText('Audio emotions · Provider assignment') as HTMLSelectElement).value).toBe('audio');
 expect((screen.getByLabelText('Interpretation · Provider assignment') as HTMLSelectElement).value).toBe('text');
});

it('keeps saving disabled when assignments cannot be loaded',async()=>{
 setLanguage('en');vi.stubGlobal('fetch',vi.fn(async()=>new Response('{}',{status:503})));
 render(<ProviderRouting profiles={profiles} busy={false} perform={fn=>fn()}/>);await act(async()=>{});
 expect(screen.getByRole('status').textContent).toBe('Could not load task assignments.');
 expect((screen.getByRole('button',{name:'Save task assignments'}) as HTMLButtonElement).disabled).toBe(true);
});

it('shows a removed profile instead of silently substituting another target',async()=>{
 setLanguage('en');const routes=Object.fromEntries(TASKS.map(task=>[task.id,'missing-profile']));
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({routes,targets:{},version:'fixture'}))));
 render(<ProviderRouting profiles={[]} busy={false} perform={fn=>fn()}/>);await act(async()=>{});
 expect(screen.getAllByRole('option',{name:'Profile no longer available'})).toHaveLength(5);
 expect((screen.getByLabelText('Audio emotions · Provider assignment') as HTMLSelectElement).value).toBe('missing-profile');
});
