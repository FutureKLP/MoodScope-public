// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {act,cleanup,render,screen,waitFor,fireEvent,within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {App} from './main';
import {setLanguage} from './i18n';

const track={id:'test-song',name:'Authored test.wav',title:'Authored test',artist:'Test',duration:12};
const notes={interpretation:'',instruments:'',personnel:'',genre:'',bpm:null};
const stored={audio:[{start:0,end:5,valence:.2,scores:{},confidence:.3}],lyrics:[],split:null,warnings:[],cached:true,
  device:'cpu',mode:'local',method:'test fixture',models:{audio:'test',lyrics:'test'},source_lyrics:'[00:01.00]Authored sentence\n[00:03.00]'};
let requests:Array<{path:string;body:any}>;
let pendingJob:Promise<any>|null;
let pendingNotes:Promise<any>|null;
let savedInterpretation:any;
let providerProfiles:any[];
let freshAnalysis:boolean;
beforeEach(()=>{
  setLanguage('de');localStorage.clear();
  requests=[];
  pendingJob=null;pendingNotes=null;
  savedInterpretation={};providerProfiles=[];freshAnalysis=false;
  vi.spyOn(HTMLMediaElement.prototype,'pause').mockImplementation(()=>{});
  vi.spyOn(HTMLMediaElement.prototype,'load').mockImplementation(()=>{});
  Element.prototype.scrollIntoView=vi.fn();
  vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
    const path=String(input).split('/api')[1];
    const body=typeof init?.body==='string'?JSON.parse(init.body):null;
    requests.push({path,body});
    let value:any={};
    if(path.startsWith('/health'))value={device:'cpu',device_name:'CPU',api_model:'authored-cloud-model'};
    else if(path==='/tracks')value=track;
    else if(path.startsWith('/tracks/test-song/analysis')){
      if(freshAnalysis)return new Response(JSON.stringify({detail:'Not cached'}),{status:404});
      value=stored;
    }
    else if(path==='/tracks/test-song/lyrics/search')value={text:'',synced:false};
    else if(path==='/tracks/test-song/analyze')value={job_id:'test-analysis'};
    else if(path==='/jobs/test-analysis')value={status:'done',progress:100,result:{...stored,cached:false,lyrics:[]}};
    else if(path==='/tracks/test-song/notes')value=body||await(pendingNotes||Promise.resolve(notes));
    else if(path.startsWith('/tracks/test-song/interpretation'))value=savedInterpretation;
    else if(path==='/tracks/test-song/interpret')value={job_id:'test-insight'};
    else if(path==='/jobs/test-insight')value={status:'done',progress:100,result:savedInterpretation};
    else if(path.startsWith('/tracks/test-song/stems'))value={ready:true,sources:['drums','bass','other','vocals'],note:'Estimated sources'};
    else if(path==='/providers')value={profiles:providerProfiles};
    else if(path==='/tracks/link')value={job_id:'test-import'};
    else if(path==='/jobs/test-import')value=await(pendingJob||Promise.resolve({status:'done',progress:100,result:track}));
    else if(path==='/library')value={tracks:[{...track,analysis_modes:['local']}]};
    else if(path==='/models')value={models:[]};
    else if(path==='/devices')value={devices:[{id:'auto',name:'Automatisch'},{id:'cpu',name:'CPU'}],active:{audio:'auto',lyrics:'auto',whisper:'auto',interpretation:'auto',separation:'auto'}};
    else if(path==='/prompts')value={defaults:{audio:'Authored sound descriptions.',whole_de:'Deute die gelieferten Worte.',line_de:'Deute die gelieferte Zeile.',whole_en:'Interpret the supplied words.',line_en:'Interpret the supplied line.'},active:{audio:'default',whole_de:'default',line_de:'default',whole_en:'default',line_en:'default'},presets:[]};
    else if(path==='/settings')value={cloud:{configured:false,free_project_confirmed:false}};
    return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});
  }));
});
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals()});

describe('workspace flows',()=>{
  it('finishes loading the preferred music source in the detail view without restarting it',async()=>{
    const original=vi.mocked(fetch).getMockImplementation()!;
    let finish!:(value:Response)=>void;
    vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
      if(String(input).includes('/expression-comparison'))return new Promise<Response>(resolve=>{finish=resolve});
      return original(input,init);
    }));
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Methode & Werte'}));
    await act(async()=>finish(new Response(JSON.stringify({ready:true,stale:false,result:{rows:[{start:0,end:12,valence:.7,arousal:.8,tags:{happy:.6,powerful:.9,energetic:.8},context_start:0,context_end:12}]}}))));
    expect(await screen.findByRole('meter',{name:'Kraft'})).toBeTruthy();
    expect(screen.queryByRole('meter',{name:'Ärger'})).toBeNull();
    expect(screen.getByText('0.700')).toBeTruthy();
    await userEvent.click(screen.getByRole('button',{name:'Stimmungsverlauf'}));
    expect(vi.mocked(fetch).mock.calls.filter(([input])=>String(input).includes('/expression-comparison'))).toHaveLength(1);
    expect(screen.getByText('0.70')).toBeTruthy();
  });
  it('uses learned valence in the existing curve and restores CLAP without a new chart',async()=>{
    const original=vi.mocked(fetch).getMockImplementation()!;
    vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
      if(String(input).includes('/expression-comparison'))return new Response(JSON.stringify({ready:true,stale:false,result:{rows:[{start:0,end:12,valence:.7,arousal:.6}]}}));
      return original(input,init);
    }));
    const view=render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await screen.findByText('0.70');
    const initial=view.container.querySelector('.audio-path')!.getAttribute('d');
    await userEvent.click(screen.getByText(/Audio-Bewertungsmodell/));
    await userEvent.click(screen.getByRole('button',{name:'CLAP verwenden'}));
    expect(view.container.querySelector('.audio-path')!.getAttribute('d')).not.toBe(initial);
    await userEvent.click(screen.getByRole('button',{name:'Music2Emo verwenden'}));
    expect(view.container.querySelector('.audio-path')!.getAttribute('d')).toBe(initial);
    expect(view.container.querySelectorAll('.audio-path')).toHaveLength(1);
  });
  it('does not restore a deleted playback source when only the subsequent library refresh fails',async()=>{
    vi.spyOn(HTMLMediaElement.prototype,'load').mockImplementation(()=>{});
    const original=vi.mocked(fetch).getMockImplementation()!;let deleted=false;
    vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
      const path=String(input).split('/api')[1];
      if(path==='/tracks/test-song/delete'){deleted=true;return new Response(JSON.stringify({removed_ids:['test-song']}),{status:200})}
      if(path==='/library'&&deleted)return new Response(JSON.stringify({detail:'Authored refresh failure'}),{status:503});
      return original(input,init);
    }));
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Bibliothek'}));
    await userEvent.click(await screen.findByRole('button',{name:'Song vollständig entfernen'}));
    await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Song vollständig entfernen'}));
    await screen.findByText(/Song entfernt. Die Bibliotheksansicht/);
    expect(document.querySelector('audio')!.hasAttribute('src')).toBe(false);
    expect(screen.queryByRole('button',{name:'Öffnen'})).toBeNull();
  });

  it('switches all workspace sections to English, preserves notes and sends the interpretation language',async()=>{
    render(<App/>);
    await userEvent.selectOptions(screen.getByLabelText('App-Sprache'),'en');
    expect(document.documentElement.lang).toBe('en');
    expect(localStorage.getItem('moodscope-language')).toBe('en');
    expect(screen.getByRole('button',{name:'+ Import song'})).toBeTruthy();
    expect(screen.getByLabelText('Transcription model')).toBeTruthy();
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/no new AI inference/);
    await userEvent.click(screen.getByRole('button',{name:'Interpretation'}));
    await screen.findByRole('button',{name:'Interpret entire song'});
    await userEvent.click(screen.getByRole('button',{name:'Interpret entire song'}));
    await waitFor(()=>expect(requests.some(r=>r.path.endsWith('/interpret')&&r.body.language==='en')).toBe(true));
    expect(requests.some(r=>r.path.includes('interpretation?')&&r.path.includes('language=en'))).toBe(true);
    for(const tab of ['Song details','Listening studio','Library','Models & API','Song analysis','Mood timeline']){
      await userEvent.click(screen.getByRole('button',{name:tab}));
      await waitFor(()=>expect(screen.getByLabelText('App language').hasAttribute('disabled')).toBe(false));
      expect(document.body.textContent).not.toMatch(/Gespeicherte Songs|Meine eigene Interpretation|Hör hinter den Mix|KI-Anbieter|Song und einzelne Zeilen/);
    }
    await userEvent.selectOptions(screen.getByLabelText('App language'),'de');
    expect(screen.getByRole('button',{name:'+ Song importieren'})).toBeTruthy();
    expect(document.documentElement.lang).toBe('de');
    expect((screen.getByPlaceholderText('Interpret') as HTMLInputElement).value).toBe('Test');
  });

  it('uses the visible Whisper selection for an automatic uncached import',async()=>{
    freshAnalysis=true;
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await waitFor(()=>expect(requests.some(r=>r.path.endsWith('/analyze'))).toBe(true));
    expect(requests.some(r=>r.path==='/models/select'&&r.body.model_id==='whisper-turbo')).toBe(true);
    const analyzed=requests.find(r=>r.path.endsWith('/analyze'))!;
    expect(analyzed.body.transcription_quality).toBe('precise');
    expect(analyzed.body.transcription_source).toBe('auto');
  });
  it('uses a shared profile editor for Gemini, Claude, OpenAI, DeepSeek and local servers',async()=>{
    render(<App/>);
    await userEvent.click(screen.getByRole('button',{name:'Modelle & API'}));
    await userEvent.selectOptions(screen.getByLabelText('Analysemodus'),'cloud');
    await screen.findByLabelText('KI-Server API-Key');
    expect(screen.queryByText('Optionale Online-KI: Google Gemini')).toBeNull();
    for(const label of ['Google Gemini','OpenAI / ChatGPT','Anthropic Claude','DeepSeek','Ollama','LM Studio'])expect(screen.getByRole('button',{name:label})).toBeTruthy();
    await userEvent.click(screen.getByRole('button',{name:'DeepSeek'}));
    expect((screen.getByLabelText('KI-Server Basis-URL') as HTMLInputElement).value).toBe('https://api.deepseek.com');
    expect(requests.some(r=>r.path==='/providers'&&r.body)).toBe(false);
  });

  it('defaults to joint evidence and preserves the optional text-only reading',async()=>{
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Interpretation'}));
    const checkbox=await screen.findByRole('checkbox',{name:'Musikbelege einbeziehen'});
    expect((checkbox as HTMLInputElement).checked).toBe(true);
    await userEvent.click(checkbox);
    await waitFor(()=>expect(requests.some(r=>r.path.includes('interpretation?')&&r.path.includes('include_music=false'))).toBe(true));
    await userEvent.click(checkbox);
    await waitFor(()=>expect(requests.some(r=>r.path.includes('interpretation?')&&r.path.includes('include_music=true'))).toBe(true));
    await userEvent.click(screen.getByRole('button',{name:'Gesamten Song interpretieren'}));
    await waitFor(()=>expect(requests.some(r=>r.path.endsWith('/interpret')&&r.body.include_music===true)).toBe(true));
  });

  it('restores saved AI interpretation and explicitly requests regeneration',async()=>{
    savedInterpretation={text:'Stored complete song reading.',model:'test model',time:null,cached:true,audio_evidence:'Measured audio evidence.'};
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Interpretation'}));
    expect(await screen.findByText('Stored complete song reading.')).toBeTruthy();
    await userEvent.click(screen.getByRole('button',{name:'Gesamtdeutung neu erstellen'}));
    await waitFor(()=>expect(requests.some(r=>r.path.endsWith('/interpret')&&r.body.force===true&&r.body.time===null)).toBe(true));
  });

  it('preserves the playback position when switching to a separated vocal source',async()=>{
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Hörstudio'}));
    await screen.findByRole('button',{name:'Nur Gesang'});
    const audio=document.querySelector('audio')!;audio.currentTime=7;
    await userEvent.click(screen.getByRole('button',{name:'Nur Gesang'}));
    expect(audio.src).toContain('sources=vocals');
    audio.currentTime=0;fireEvent.loadedMetadata(audio);
    expect(audio.currentTime).toBe(7);
  });

  it('requires confirmation before removing a song or the entire library',async()=>{
    const confirm=vi.spyOn(window,'confirm');
    render(<App/>);
    await userEvent.click(screen.getByRole('button',{name:'Bibliothek'}));
    await screen.findByRole('button',{name:'Song vollständig entfernen'});
    await userEvent.click(screen.getByRole('button',{name:'Song vollständig entfernen'}));
    expect(requests.some(r=>r.path.endsWith('/delete'))).toBe(false);
    await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Abbrechen'}));
    await userEvent.click(screen.getByRole('button',{name:'Gesamte Bibliothek entfernen'}));
    await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Gesamte Bibliothek entfernen'}));
    await waitFor(()=>expect(requests.some(r=>r.path==='/library/delete')).toBe(true));
    expect(confirm).not.toHaveBeenCalled();
    expect(await screen.findByText('Noch keine Songs importiert.')).toBeTruthy();
  });
  it('defaults to local mode, separates areas, and initializes actual player volume',async()=>{
    render(<App/>);
    expect((screen.getByLabelText('Analysemodus') as HTMLSelectElement).value).toBe('local');
    expect(document.querySelector('audio')!.volume).toBe(.8);
    await userEvent.click(screen.getByRole('button',{name:'Songdetails'}));
    expect(screen.getByText('Zuerst einen Song importieren')).toBeTruthy();
    expect(requests.some(r=>r.body?.mode==='cloud')).toBe(false);
  });

  it('restores an imported cached song without triggering another inference',async()=>{
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/Gespeicherte Analyse geladen; keine erneute KI-Inferenz/);
    expect(requests.some(r=>r.path.endsWith('/analyze'))).toBe(false);
    expect(screen.getByRole('button',{name:'Neu analysieren'})).toBeTruthy();
  });

  it('stores personal interpretation in the notes endpoint without requesting AI',async()=>{
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Interpretation'}));
    await userEvent.type(screen.getByLabelText('Meine eigene Interpretation'),'My personal reading');
    await userEvent.click(screen.getByRole('button',{name:'Meine Interpretation speichern'}));
    await screen.findByText('Lokal gespeichert');
    expect(requests.some(r=>r.path.endsWith('/notes')&&r.body?.interpretation==='My personal reading')).toBe(true);
    expect(requests.some(r=>r.path.endsWith('/interpret'))).toBe(false);
  });

  it('opens stored library entries and explains optional API setup',async()=>{
    render(<App/>);
    await userEvent.click(screen.getByRole('button',{name:'Bibliothek'}));
    await screen.findByRole('button',{name:'Öffnen'});
    await userEvent.click(screen.getByRole('button',{name:'Öffnen'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Modelle & API'}));
    await userEvent.selectOptions(screen.getByLabelText('Analysemodus'),'cloud');
    expect(await screen.findByLabelText('KI-Server API-Key')).toBeTruthy();
    expect(requests.some(r=>r.path==='/settings/cloud')).toBe(false);
  });

  it('keeps mutations disabled when another tab loads during a running import',async()=>{
    let finish:(value:any)=>void=()=>{};
    pendingJob=new Promise(resolve=>{finish=resolve});
    render(<App/>);
    await userEvent.type(screen.getByLabelText('YouTube- oder SoundCloud-Link'),'https://youtu.be/BaW_jenozKc');
    await userEvent.click(screen.getByRole('button',{name:'Link importieren'}));
    await userEvent.click(screen.getByRole('button',{name:'Modelle & API'}));
    await screen.findByLabelText('Modellzweck');
    expect((screen.getByLabelText('Modellzweck') as HTMLSelectElement).disabled).toBe(true);
    expect(screen.getByRole('button',{name:'Abbrechen'})).toBeTruthy();
    finish({status:'done',progress:100,message:'Import complete',result:track});
    await waitFor(()=>expect((screen.getByLabelText('Modellzweck') as HTMLSelectElement).disabled).toBe(false));
    await userEvent.click(screen.getByRole('button',{name:'Song-Analyse'}));
    expect(screen.getByRole('button',{name:'+ Song importieren'}).hasAttribute('disabled')).toBe(false);
  });

  it('does not let delayed note loading overwrite a user edit',async()=>{
    let finish:(value:any)=>void=()=>{};
    pendingNotes=new Promise(resolve=>{finish=resolve});
    render(<App/>);
    await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
    await screen.findByText(/keine erneute KI-Inferenz/);
    await userEvent.click(screen.getByRole('button',{name:'Interpretation'}));
    expect(screen.getByLabelText('Meine eigene Interpretation').hasAttribute('disabled')).toBe(true);
    finish({...notes,interpretation:'Previously saved note'});
    await waitFor(()=>expect((screen.getByLabelText('Meine eigene Interpretation') as HTMLTextAreaElement).value).toBe('Previously saved note'));
    expect(screen.getByLabelText('Meine eigene Interpretation').hasAttribute('disabled')).toBe(false);
  });
  it('shares local/API selection across settings and prompts and reports the chosen mode',async()=>{
    render(<App/>);await userEvent.click(screen.getByRole('button',{name:'Modelle & API'}));
    await screen.findByLabelText('Audio Mood · Rechengerät');await userEvent.selectOptions(screen.getByLabelText('Analysemodus'),'cloud');
    await screen.findByLabelText('KI-Server API-Key');expect(screen.queryByLabelText('Audio Mood · Rechengerät')).toBeNull();
    expect(document.querySelector('.local-badge')?.textContent).toContain('API-Modus');expect(document.querySelector('.local-badge')?.textContent).toContain('authored-cloud-model');
    await userEvent.click(screen.getByRole('button',{name:'Prompts'}));await screen.findByLabelText('Prompt-Aufgabe');
    expect((screen.getByLabelText('Analysemodus') as HTMLSelectElement).value).toBe('cloud');expect((screen.getByLabelText('Prompt-Aufgabe') as HTMLSelectElement).value).toBe('whole_de');
    await userEvent.selectOptions(screen.getByLabelText('Analysemodus'),'local');await waitFor(()=>expect((screen.getByLabelText('Prompt-Aufgabe') as HTMLSelectElement).value).toBe('audio'));
    expect(document.querySelector('.local-badge')?.textContent).toContain('CPU');
  });

});

it('clears cached output and automatically analyses the song when reopened',async()=>{
 const original=vi.mocked(fetch).getMockImplementation()!;
 vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
  const path=String(input).split('/api')[1];
  if(path==='/tracks/test-song/cache/delete'){freshAnalysis=true;return new Response(JSON.stringify({affected_ids:['test-song']}),{status:200})}
  return original(input,init);
 }));
 render(<App/>);
 await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
 await screen.findByText(/keine erneute KI-Inferenz/);
 await userEvent.click(screen.getByRole('button',{name:'Bibliothek'}));
 await userEvent.click(await screen.findByRole('button',{name:'Analyse-Cache löschen'}));
 await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Analyse-Cache löschen'}));
 await waitFor(()=>expect(freshAnalysis).toBe(true));
 requests.length=0;
 await userEvent.click(screen.getByRole('button',{name:'Öffnen'}));
 await screen.findByRole('slider',{name:'Wiedergabeposition im Stimmungsverlauf'});
 expect(requests.filter(r=>r.path==='/tracks/test-song/analyze')).toHaveLength(1);
 expect(requests.some(r=>r.path==='/tracks/test-song/lyrics/search')).toBe(true);
 expect(requests.some(r=>r.path==='/tracks/test-song/research')).toBe(true);
});

it('releases the playing song and ignores late play failures when another library song opens',async()=>{
 const second={...track,id:'second-song',name:'Second authored song',title:'Second authored song'};
 const original=vi.mocked(fetch).getMockImplementation()!;
 vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
  const path=String(input).split('/api')[1];
  if(path==='/library')return new Response(JSON.stringify({tracks:[{...track,analysis_modes:['local']},{...second,analysis_modes:['local']}]}));
  if(path.startsWith('/tracks/second-song/'))return new Response(JSON.stringify(path.includes('/analysis')?stored:path.endsWith('/notes')?notes:{}));
  return original(input,init);
 }));
 const paused=new WeakMap<HTMLMediaElement,boolean>();let rejectOld!:(error:Error)=>void;
 vi.spyOn(HTMLMediaElement.prototype,'paused','get').mockImplementation(function(this:HTMLMediaElement){return paused.get(this)??true});
 vi.mocked(HTMLMediaElement.prototype.pause).mockImplementation(function(this:HTMLMediaElement){paused.set(this,true)});
 const play=vi.spyOn(HTMLMediaElement.prototype,'play').mockImplementation(function(this:HTMLMediaElement){paused.set(this,false);fireEvent.play(this);return play.mock.calls.length===1?new Promise<void>((_,reject)=>{rejectOld=reject}):Promise.resolve()});
 render(<App/>);
 await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
 await screen.findByText(/keine erneute KI-Inferenz/);
 const old=document.querySelector('audio')!;
 fireEvent.change(screen.getByLabelText('Lautstärke'),{target:{value:'0.35'}});
 await userEvent.click(screen.getByRole('button',{name:'Abspielen'}));
 expect(screen.getByRole('button',{name:'Pause'})).toBeTruthy();
 await userEvent.click(screen.getByRole('button',{name:'Bibliothek'}));
 await userEvent.click((await screen.findByText('Second authored song')).closest('article')!.querySelector('button')!);
 await waitFor(()=>expect(document.querySelector('audio')!.src).toContain('/second-song/audio'));
 const next=document.querySelector('audio')!;
 expect(next).not.toBe(old);expect(old.isConnected).toBe(false);expect(old.hasAttribute('src')).toBe(false);expect(next.volume).toBe(.35);
 await act(async()=>rejectOld(new DOMException('Old request interrupted','AbortError')));
 expect(screen.queryByRole('alert')).toBeNull();
 await userEvent.click(screen.getByRole('button',{name:'Abspielen'}));
 expect(paused.get(next)).toBe(false);
 await userEvent.click(screen.getByRole('button',{name:'Pause'}));
 expect(paused.get(next)).toBe(true);expect(screen.getByRole('button',{name:'Abspielen'})).toBeTruthy();
});

it('recovers play control when the displayed state and native paused flag disagree',async()=>{
 let paused=true,rejectFirst!:(error:Error)=>void;
 vi.spyOn(HTMLMediaElement.prototype,'paused','get').mockImplementation(()=>paused);
 const play=vi.spyOn(HTMLMediaElement.prototype,'play').mockImplementation(function(this:HTMLMediaElement){
  if(play.mock.calls.length===1)return new Promise<void>((_,reject)=>{rejectFirst=reject});
  paused=false;fireEvent.play(this);return Promise.resolve();
 });
 render(<App/>);
 await userEvent.upload(document.querySelector('input[type=file]') as HTMLInputElement,new File(['fixture'],'test.wav',{type:'audio/wav'}));
 await screen.findByText(/keine erneute KI-Inferenz/);
 await userEvent.click(screen.getByRole('button',{name:'Abspielen'}));
 await userEvent.click(screen.getByRole('button',{name:'Pause'}));
 expect(play).toHaveBeenCalledTimes(2);expect(paused).toBe(false);
 await act(async()=>rejectFirst(new DOMException('Earlier play aborted','AbortError')));
 expect(screen.getByRole('button',{name:'Pause'})).toBeTruthy();expect(screen.queryByRole('alert')).toBeNull();
});
