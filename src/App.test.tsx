// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {cleanup,render,screen,waitFor,fireEvent} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {App} from './main';

const track={id:'test-song',name:'Authored test.wav',title:'Authored test',artist:'Test',duration:12};
const notes={interpretation:'',instruments:'',personnel:'',genre:'',bpm:null};
const stored={audio:[{start:0,end:5,valence:.2,scores:{},confidence:.3}],lyrics:[],split:null,warnings:[],cached:true,
  device:'cpu',mode:'local',method:'test fixture',models:{audio:'test',lyrics:'test'},source_lyrics:'[00:01.00]Authored sentence\n[00:03.00]'};
let requests:Array<{path:string;body:any}>;
let pendingJob:Promise<any>|null;
let pendingNotes:Promise<any>|null;
let savedInterpretation:any;
let providerProfiles:any[];
beforeEach(()=>{
  requests=[];
  pendingJob=null;pendingNotes=null;
  savedInterpretation={};providerProfiles=[];
  vi.spyOn(HTMLMediaElement.prototype,'pause').mockImplementation(()=>{});
  Element.prototype.scrollIntoView=vi.fn();
  vi.stubGlobal('fetch',vi.fn(async(input:any,init?:RequestInit)=>{
    const path=String(input).split('/api')[1];
    const body=typeof init?.body==='string'?JSON.parse(init.body):null;
    requests.push({path,body});
    let value:any={};
    if(path==='/health')value={device:'cpu'};
    else if(path==='/tracks')value=track;
    else if(path.startsWith('/tracks/test-song/analysis'))value=stored;
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
    else if(path==='/settings')value={cloud:{configured:false,free_project_confirmed:false}};
    return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});
  }));
});
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals()});

describe('workspace flows',()=>{
  it('uses a shared profile editor for Gemini, Claude, OpenAI, DeepSeek and local servers',async()=>{
    render(<App/>);
    await userEvent.click(screen.getByRole('button',{name:'Modelle & API'}));
    await screen.findByLabelText('KI-Server API-Key');
    expect(screen.queryByText('Optionale Online-KI: Google Gemini')).toBeNull();
    for(const label of ['Google Gemini','OpenAI / ChatGPT','Anthropic Claude','DeepSeek','Ollama','LM Studio'])expect(screen.getByRole('button',{name:label})).toBeTruthy();
    await userEvent.click(screen.getByRole('button',{name:'DeepSeek'}));
    expect((screen.getByLabelText('KI-Server Basis-URL') as HTMLInputElement).value).toBe('https://api.deepseek.com');
    expect(requests.some(r=>r.path==='/providers'&&r.body)).toBe(false);
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
    const confirm=vi.spyOn(window,'confirm').mockReturnValue(false);
    render(<App/>);
    await userEvent.click(screen.getByRole('button',{name:'Bibliothek'}));
    await screen.findByRole('button',{name:'Song vollständig entfernen'});
    await userEvent.click(screen.getByRole('button',{name:'Song vollständig entfernen'}));
    expect(requests.some(r=>r.path.endsWith('/delete'))).toBe(false);
    confirm.mockReturnValue(true);
    await userEvent.click(screen.getByRole('button',{name:'Gesamte Bibliothek entfernen'}));
    await waitFor(()=>expect(requests.some(r=>r.path==='/library/delete')).toBe(true));
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
    await screen.findByLabelText('KI-Server API-Key');
    expect(screen.getByRole('button',{name:'+ Song importieren'}).hasAttribute('disabled')).toBe(true);
    finish({status:'done',progress:100,message:'Import complete',result:track});
    await waitFor(()=>expect(screen.getByRole('button',{name:'+ Song importieren'}).hasAttribute('disabled')).toBe(false));
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
});
