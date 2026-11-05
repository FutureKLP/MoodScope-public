// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {cleanup,render,screen,waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {App} from './main';

const track={id:'test-song',name:'Authored test.wav',title:'Authored test',artist:'Test',duration:12};
const notes={interpretation:'',instruments:'',personnel:'',genre:'',bpm:null};
const stored={audio:[{start:0,end:5,valence:.2,scores:{},confidence:.3}],lyrics:[],split:null,warnings:[],cached:true,
  device:'cpu',mode:'local',method:'test fixture',models:{audio:'test',lyrics:'test'},source_lyrics:'[00:01.00]Authored sentence\n[00:03.00]'};
let requests:Array<{path:string;body:any}>;
beforeEach(()=>{
  requests=[];
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
    else if(path==='/tracks/test-song/notes')value=body||notes;
    else if(path==='/library')value={tracks:[{...track,analysis_modes:['local']}]};
    else if(path==='/models')value={models:[]};
    else if(path==='/settings')value={cloud:{configured:false,free_project_confirmed:false}};
    return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});
  }));
});
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals()});

describe('workspace flows',()=>{
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
    expect(await screen.findByLabelText('Gemini API-Key')).toBeTruthy();
    expect(requests.some(r=>r.path==='/settings/cloud')).toBe(false);
  });
});
