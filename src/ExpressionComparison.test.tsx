// @vitest-environment jsdom
import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,cleanup,fireEvent,act} from '@testing-library/react';
import {ExpressionComparison} from './ExpressionComparison';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
const result={rows:[{start:0,end:5,valence:-.3,arousal:.7}]};
const props={track:{id:'fixture',name:'Authored',duration:5},busy:false,perform:(fn:()=>Promise<void>)=>fn(),selected:false};
it('uses the existing main curve instead of creating a second graph',async()=>{
 setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:true,result,stale:false}))));
 const select=vi.fn(),job=vi.fn(async()=>result);
 const {container}=render(<ExpressionComparison {...props} onSelect={select} job={job}/>);
 fireEvent.click(screen.getByText(/Audio-Bewertungsmodell/));await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name:'Music2Emo verwenden'}));
 expect(select).toHaveBeenLastCalledWith(result.rows);expect(container.querySelector('svg')).toBeNull();
 fireEvent.click(screen.getByRole('button',{name:'CLAP verwenden'}));expect(select).toHaveBeenLastCalledWith(null);
 await act(async()=>{fireEvent.click(screen.getByRole('button',{name:'Music2Emo berechnen und verwenden'}))});
 expect(job).toHaveBeenCalledWith('/tracks/fixture/expression-comparison',{force:true});
});
it('does not activate stale cached results',async()=>{
 setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:true,result,stale:true}))));
 render(<ExpressionComparison {...props} onSelect={vi.fn()} job={vi.fn()}/>);
 fireEvent.click(screen.getByText(/Audio-Bewertungsmodell/));await screen.findByText(/älteren Modellstand/);
 expect((screen.getByRole('button',{name:'Music2Emo verwenden'}) as HTMLButtonElement).disabled).toBe(true);
});
it('restores the chosen model only with a current cached result',async()=>{
 setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:true,result,stale:false}))));
 const select=vi.fn();render(<ExpressionComparison {...props} preferred={true} onSelect={select} job={vi.fn()}/>);
 await act(async()=>{});expect(select).toHaveBeenCalledWith(result.rows);
});
it('calculates a missing preferred installed model once',async()=>{
 setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:true,result:null,stale:false}))));
 const select=vi.fn(),job=vi.fn(async()=>result);
 const view=render(<ExpressionComparison {...props} preferred={true} onSelect={select} job={job}/>);
 await act(async()=>{});expect(job).toHaveBeenCalledTimes(1);expect(select).toHaveBeenCalledWith(result.rows);
 view.rerender(<ExpressionComparison {...props} preferred={true} busy={true} onSelect={select} job={job}/>);
 view.rerender(<ExpressionComparison {...props} preferred={true} busy={false} onSelect={select} job={job}/>);
 expect(job).toHaveBeenCalledTimes(1);
});
it('ignores a calculation completed after changing tracks',async()=>{
 setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:true,result:null,stale:false}))));
 let finish!:(value:unknown)=>void;const job=vi.fn(()=>new Promise(resolve=>{finish=resolve}));const select=vi.fn();
 const view=render(<ExpressionComparison {...props} onSelect={select} job={job}/>);
 fireEvent.click(screen.getByText(/Audio-Bewertungsmodell/));await act(async()=>{});
 fireEvent.click(screen.getByRole('button',{name:'Music2Emo berechnen und verwenden'}));
 view.rerender(<ExpressionComparison {...props} track={{...props.track,id:'second'}} onSelect={select} job={job}/>);
 await act(async()=>{finish(result)});expect(select).not.toHaveBeenCalled();
});
