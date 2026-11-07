// @vitest-environment jsdom
import React from 'react';
import {beforeEach,afterEach,it,expect,vi} from 'vitest';
import {render,screen,within,waitFor,cleanup,fireEvent} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {SourceStudio} from './SongTools';
import {AnalysisReport} from './AnalysisReport';
import {Atmosphere,atmosphereStyle} from './Atmosphere';
import {setLanguage} from './i18n';
const track={id:'authored',name:'Authored fixture',duration:10};
let info:any,calls:any[];
beforeEach(()=>{setLanguage('de');calls=[];info={ready:true,sources:['vocals','piano','drums'],audible_sources:['vocals','drums'],hidden_sources:[],shown_sources:[],activity:{vocals:.8,drums:.2,piano:0}};vi.stubGlobal('fetch',vi.fn(async(url,init)=>{const body=init?.body?JSON.parse(init.body):null;calls.push({url:String(url),body});if(String(url).includes('/visibility'))info={...info,hidden_sources:body.hidden,shown_sources:body.shown};return new Response(JSON.stringify(String(url).includes('/stems')?info:null),{status:200})}));});
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('restores manually hidden and automatically quiet stems, including after remount',async()=>{
 const source=vi.fn(),props={track,busy:false,perform:async(f:()=>Promise<void>)=>f(),job:vi.fn(),onSource:source};
 const view=render(<SourceStudio {...props}/>);
 await screen.findByRole('button',{name:'Klavier · Wieder anzeigen'});
 const vocals=screen.getByRole('heading',{name:'Gesang / Stimmen'}).closest('article')!;
 await userEvent.click(within(vocals).getByRole('button',{name:'Spur ausblenden'}));
 await screen.findByRole('button',{name:'Gesang / Stimmen · Wieder anzeigen'});
 await userEvent.click(screen.getByRole('button',{name:'Gesang / Stimmen · Wieder anzeigen'}));
 await screen.findByRole('heading',{name:'Gesang / Stimmen'});
 await userEvent.click(screen.getByRole('button',{name:'Klavier · Wieder anzeigen'}));
 await screen.findByRole('heading',{name:'Klavier'});
 view.unmount();render(<SourceStudio {...props}/>);
 expect(await screen.findByRole('heading',{name:'Klavier'})).toBeTruthy();
 expect(info.shown_sources).toContain('piano');
 expect(screen.queryByRole('button',{name:'Klavier · Wieder anzeigen'})).toBeNull();
});
it('applies actual per-source gains and keeps remaining selected sources when hiding one',async()=>{
 const source=vi.fn();render(<SourceStudio track={track} busy={false} perform={async f=>f()} job={vi.fn()} onSource={source}/>);
 await screen.findByRole('heading',{name:'Gesang / Stimmen'});
 for(const name of ['Gesang / Stimmen','Schlagzeug'])await userEvent.click(within(screen.getByRole('heading',{name}).closest('article')!).getByRole('button',{name:'Zum Mix hinzufügen'}));
 fireEvent.change(screen.getByLabelText('Spurpegel Schlagzeug'),{target:{value:'50'}});
 await userEvent.click(screen.getByRole('button',{name:'Mix anwenden'}));
 expect(source.mock.calls.at(-1)![0]).toContain('gains=1,0.5');
 await userEvent.click(within(screen.getByRole('heading',{name:'Gesang / Stimmen'}).closest('article')!).getByRole('button',{name:'Spur ausblenden'}));
 await waitFor(()=>expect(source.mock.calls.at(-1)![0]).toContain('sources=drums&gains=0.5'));
});
it('shows the actual weighted calculation, context and seek selection without inventing metadata',async()=>{
 const seek=vi.fn();const analysis:any={audio:[{start:0,end:5,valence:-.2,scores:{joy:.4,sadness:.6},confidence:.1,rms:.2,context_start:0,context_end:7.5},{start:5,end:10,valence:0,scores:{}}],lyrics:[],models:{audio:'authored model'},device:'cpu',cached:true,method:'fixture',audio_method:{id:'clap-prompt-ensemble-v4',recording:'recorded',grid_seconds:5,context_seconds:10,labels:[{id:'joy',valence_weight:1,arousal_weight:.8,prompts:['Authored positive description']},{id:'sadness',valence_weight:-1,arousal_weight:.3,prompts:['Authored negative description']} ]}};
 render(<AnalysisReport track={track} analysis={analysis} time={0} onSeek={seek} onReanalyse={vi.fn()} busy={false}/>);
 expect(screen.getByText('0.4000 × 1 + 0.6000 × -1 = -0.2000')).toBeTruthy();
 await userEvent.selectOptions(screen.getByLabelText('Abschnitt auswählen'),'1');expect(seek).toHaveBeenCalledWith(5);
 expect(screen.getByText(/gehen nicht direkt in die CLAP/)).toBeTruthy();
});
it('renders decorative global atmosphere without audio interception or controls',()=>{
 const {container}=render(<Atmosphere/>);
 expect(container.querySelector('.ambient-field')?.getAttribute('aria-hidden')).toBe('true');
 expect(container.querySelectorAll('button,audio,canvas').length).toBe(0);
 const style=atmosphereStyle({start:0,end:5,valence:-.5,scores:{},rms:.1},undefined,120) as any;
 expect(style['--mood-hue']).toBeGreaterThan(240);expect(style['--breath-duration']).toBe('2s');
});
it('applies live source level changes without requesting a new server mix file',async()=>{
 const live=vi.fn();render(<SourceStudio track={track} busy={false} perform={async f=>f()} job={vi.fn()} onSource={vi.fn()} onLiveMix={live}/>);
 await screen.findByRole('heading',{name:'Gesang / Stimmen'});
 await userEvent.click(within(screen.getByRole('heading',{name:'Gesang / Stimmen'}).closest('article')!).getByRole('button',{name:'Zum Mix hinzufügen'}));
 fireEvent.change(screen.getByLabelText('Spurpegel Gesang / Stimmen'),{target:{value:'35'}});
 expect(live.mock.calls.at(-1)![0].gains.vocals).toBe(.35);expect(live.mock.calls.at(-1)![0].selected).toEqual(['vocals']);
 expect(calls.some(c=>c.url.includes('/mix?'))).toBe(false);expect(screen.queryByRole('button',{name:'Mix anwenden'})).toBeNull();
});

it('uses the selected separator model and offers only existing focus sources',async()=>{
 const {ManualFocus}=await import('./ManualFocus');const job=vi.fn(async(...args:any[])=>({url:'/focus.wav'}));
 const props={track,busy:false,perform:async(f:()=>Promise<void>)=>f(),job,onSource:vi.fn()};
 const view=render(<ManualFocus {...props} model="htdemucs_auto"/>);
 await screen.findByRole('option',{name:'Getrennte Gesangsspur'});
 expect(screen.queryByRole('option',{name:'Bass'})).toBeNull();
 await userEvent.selectOptions(screen.getByLabelText('Fokus Quelle'),'vocals');
 await userEvent.click(screen.getByRole('button',{name:'Fokus vorbereiten und auswählen'}));
 expect(job.mock.calls[0][1]).toMatchObject({model:'htdemucs_auto',source:'vocals'});
 info={ready:false,sources:[]};view.rerender(<ManualFocus {...props} model="htdemucs_6s"/>);
 await waitFor(()=>expect(screen.queryByRole('option',{name:'Getrennte Gesangsspur'})).toBeNull());
 expect((screen.getByLabelText('Fokus Quelle') as HTMLSelectElement).value).toBe('original');
});

it('loads existing six-source results without queuing another separation job',async()=>{
 info={ready:true,sources:['drums','bass','other','vocals','guitar','piano'],activity:{}};
 const job=vi.fn(),onModelChange=vi.fn();
 render(<SourceStudio track={track} busy={false} perform={async f=>f()} job={job} onSource={vi.fn()} onModelChange={onModelChange}/>);
 await screen.findByRole('button',{name:'Gespeicherte Spuren laden'});
 await userEvent.selectOptions(screen.getByLabelText('Trennmodell'),'htdemucs_6s');
 await screen.findByRole('heading',{name:'Gitarre'});
 await userEvent.click(screen.getByRole('button',{name:'Gespeicherte Spuren laden'}));
 await screen.findByText(/Gespeicherte Spuren sind bereit/);
 expect(onModelChange).toHaveBeenCalledWith('htdemucs_6s');expect(job).not.toHaveBeenCalled();
 expect(calls.some(c=>c.url.includes('/stems?model=htdemucs_6s'))).toBe(true);
});
