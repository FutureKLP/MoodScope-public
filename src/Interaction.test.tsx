// @vitest-environment jsdom
import {render,screen,fireEvent,cleanup,act,waitFor} from '@testing-library/react';
import {it,expect,vi,afterEach,beforeEach} from 'vitest';
import {AnalysisReport} from './AnalysisReport';
import {TooltipLayer} from './Tooltip';
import {PromptManager} from './PromptManager';
import {DeviceSettings} from './DeviceSettings';
import {setLanguage} from './i18n';
beforeEach(()=>setLanguage('de'));
afterEach(()=>{cleanup();vi.unstubAllGlobals();vi.useRealTimers()});
it('keeps the section dropdown and meter mounted while interpolating playback values',()=>{
 const analysis:any={audio:[{start:0,end:2,valence:-1,scores:{joy:0}},{start:2,end:4,valence:1,scores:{joy:1}}],lyrics:[],models:{audio:'authored'},device:'cpu',features:{},audio_method:{id:'clap-prompt-ensemble-v4',labels:[]}};
 const props={track:{id:'authored',name:'Authored signal',duration:4},analysis,onSeek:vi.fn(),onReanalyse:vi.fn(),busy:false};
 const view=render(<AnalysisReport {...props} time={0}/>),select=screen.getByLabelText('Abschnitt auswählen'),meter=screen.getByRole('meter');
 fireEvent.pointerDown(select);view.rerender(<AnalysisReport {...props} time={2}/>);
 expect(screen.getByLabelText('Abschnitt auswählen')).toBe(select);expect((select as HTMLSelectElement).value).toBe('0');expect(screen.getByRole('meter')).toBe(meter);expect(meter.getAttribute('aria-valuenow')).toBe('0.5');
 fireEvent.blur(select);expect((select as HTMLSelectElement).value).toBe('1');
});
it('shows a styled keyboard-accessible tooltip and dismisses it with Escape',()=>{
 vi.useFakeTimers();render(<><button data-tooltip="Authored loop instructions">A/B</button><TooltipLayer/></>);const button=screen.getByRole('button');
 fireEvent.focusIn(button);act(()=>vi.advanceTimersByTime(200));expect(screen.getByRole('tooltip').textContent).toBe('Authored loop instructions');expect(button.getAttribute('aria-describedby')).toContain('moodscope-tooltip');
 fireEvent.keyDown(document,{key:'Escape'});expect(screen.queryByRole('tooltip')).toBeNull();expect(button.hasAttribute('aria-describedby')).toBe(false);
});
it('saves custom prompt variants, activates explicitly and resets without deleting them',async()=>{
 const value:any={defaults:{audio:'Authored comparison lines',whole_en:'Interpret the supplied words carefully.'},active:{audio:'default',whole_en:'default'},presets:[]};const actions:any[]=[];
 vi.stubGlobal('fetch',vi.fn(async(_url,init)=>{if(init?.body){const body=JSON.parse(String(init.body));actions.push(body);if(body.action==='save')value.presets.push({id:'authored',purpose:body.purpose,name:body.name,content:body.content});if(body.action==='select')value.active[body.purpose]=body.preset_id}return new Response(JSON.stringify(value))}));
 render(<PromptManager busy={false} perform={async work=>work()}/>);await screen.findByLabelText('Prompt-Aufgabe');fireEvent.change(screen.getByLabelText('Prompt-Aufgabe'),{target:{value:'whole_en'}});
 fireEvent.change(screen.getByLabelText('Vorlagenname'),{target:{value:'Authored variant'}});fireEvent.change(screen.getByLabelText('Prompt bearbeiten'),{target:{value:'Compare two readings using the supplied evidence.'}});fireEvent.click(screen.getByRole('button',{name:'Als neue Vorlage speichern'}));
 await waitFor(()=>expect((screen.getByLabelText('Gespeicherte Vorlage') as HTMLSelectElement).value).toBe('authored'));expect(value.active.whole_en).toBe('default');fireEvent.click(screen.getByRole('button',{name:'Vorlage aktivieren'}));await waitFor(()=>expect(value.active.whole_en).toBe('authored'));
 fireEvent.click(screen.getByRole('button',{name:'Standard wiederherstellen'}));await waitFor(()=>expect(value.active.whole_en).toBe('default'));expect(value.presets).toHaveLength(1);expect(actions[0].purpose).toBe('whole_en');
});
it('offers only detected devices and saves separate choices for model tasks',async()=>{
 const value={devices:[{id:'auto',name:'Automatisch'},{id:'cpu',name:'CPU'},{id:'cuda:1',name:'Authored GPU',vram_gb:12}],active:{audio:'auto',lyrics:'auto',whisper:'auto',interpretation:'auto',separation:'auto'}};let saved:any;
 vi.stubGlobal('fetch',vi.fn(async(_url,init)=>{if(init?.body){saved=JSON.parse(String(init.body));value.active=saved}return new Response(JSON.stringify(value))}));render(<DeviceSettings busy={false} perform={async work=>work()}/>);
 await screen.findByLabelText('Audio Mood · Rechengerät');fireEvent.change(screen.getByLabelText('Audio Mood · Rechengerät'),{target:{value:'cpu'}});fireEvent.change(screen.getByLabelText('Interpretation · Rechengerät'),{target:{value:'cuda:1'}});fireEvent.click(screen.getByRole('button',{name:'Geräteauswahl speichern'}));await waitFor(()=>expect(saved).toMatchObject({audio:'cpu',interpretation:'cuda:1',whisper:'auto'}));
});
