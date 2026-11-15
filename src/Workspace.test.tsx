// @vitest-environment jsdom
import {afterEach,beforeEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,cleanup,act} from '@testing-library/react';
import {Workspace} from './Workspace';
import {setLanguage} from './i18n';
const notes={interpretation:'',instruments:'',personnel:'',genre:'',bpm:null};
const first={id:'first',name:'Authored first',duration:12},second={id:'second',name:'Authored second',duration:12};
function deferred<T>(){let resolve!:(value:T)=>void;const promise=new Promise<T>(r=>resolve=r);return {promise,resolve}}
const props={view:'details',track:first,analysis:null,time:0,mode:'local' as const,consent:false,busy:false,perform:async(f:()=>Promise<void>)=>f(),job:vi.fn(),onOpen:vi.fn(),onSongDeleted:vi.fn(),onPrepareDelete:()=>()=>{},onCacheDeleted:vi.fn()};
beforeEach(()=>{setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify(notes))))});
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('discards detail results after changing the song',async()=>{
 const pending=deferred<any>();const job=vi.fn(()=>pending.promise);
 const view=render(<Workspace {...props} job={job}/>);
 await screen.findByLabelText('Instrumente');fireEvent.click(screen.getByRole('button',{name:'Details lokal analysieren'}));
 view.rerender(<Workspace {...props} track={second} job={job}/>);
 await act(async()=>pending.resolve({features:{bpm:177},instruments:[{instrument:'Authored old result'}],note:'Authored old note'}));
 expect(screen.queryByText('Authored old note')).toBeNull();expect(screen.queryByText(/177/)).toBeNull();
});
it('does not mark newer unsaved edits as saved when an earlier save completes',async()=>{
 const pending=deferred<Response>();vi.stubGlobal('fetch',vi.fn(async(_url,init)=>init?.method==='POST'?pending.promise:new Response(JSON.stringify(notes))));
 render(<Workspace {...props}/>);const input=await screen.findByLabelText('Instrumente');
 await act(async()=>{});fireEvent.change(input,{target:{value:'Authored saved version'}});
 fireEvent.click(screen.getByRole('button',{name:'Angaben speichern'}));fireEvent.change(input,{target:{value:'Authored newer edit'}});
 await act(async()=>pending.resolve(new Response(JSON.stringify(notes))));
 expect(screen.queryByText('Lokal gespeichert')).toBeNull();expect((input as HTMLInputElement).value).toBe('Authored newer edit');
});
it.each(['mode','cache'] as const)('discards detail results after changing %s',async(change)=>{
 const pending=deferred<any>();const job=vi.fn(()=>pending.promise);
 const view=render(<Workspace {...props} job={job}/>);
 fireEvent.click(screen.getByRole('button',{name:'Details lokal analysieren'}));
 view.rerender(<Workspace {...props} job={job} mode={change==='mode'?'cloud':'local'} cacheRevision={change==='cache'?1:0}/>);
 await act(async()=>pending.resolve({features:{bpm:177},instruments:[],note:'Authored obsolete result'}));
 expect(screen.queryByText('Authored obsolete result')).toBeNull();
});
