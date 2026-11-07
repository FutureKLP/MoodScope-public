// @vitest-environment jsdom
import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,cleanup,fireEvent} from '@testing-library/react';
import {ExpressionComparison} from './ExpressionComparison';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('restores a separate curve, seeks its intervals, and explicitly recalculates',async()=>{
 setLanguage('de');
 const result={rows:[{start:0,end:5,context_start:0,context_end:10,valence:-.3,arousal:.7,tags:{sad:.8,happy:.6}},{start:5,end:10,context_start:0,context_end:10,valence:.1,arousal:.5,tags:{calm:.5}}]};
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:true,result,stale:false}))));
 const job=vi.fn(async()=>result),seek=vi.fn();
 render(<ExpressionComparison track={{id:'fixture',name:'Authored',duration:10}} analysis={null} time={0} onSeek={seek} busy={false} perform={fn=>fn()} job={job}/>);
 await screen.findByRole('img',{name:'Vergleich der Audiovalenz'});
 expect(screen.getByText(/sad: 0.80/)).toBeTruthy();
 fireEvent.change(screen.getByLabelText('Vergleichsabschnitt'),{target:{value:'5'}});expect(seek).toHaveBeenCalledWith(5);
 fireEvent.click(screen.getByRole('button',{name:'Vergleich neu berechnen'}));
 expect(job).toHaveBeenCalledWith('/tracks/fixture/expression-comparison',{force:true});
});
it('does not offer inference when optional weights are absent',async()=>{
 setLanguage('de');vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({ready:false,result:null,stale:false}))));
 render(<ExpressionComparison track={{id:'fixture',name:'Authored',duration:10}} analysis={null} time={0} onSeek={vi.fn()} busy={false} perform={fn=>fn()} job={vi.fn()}/>);
 await screen.findByText(/nicht eingerichtet/);
 expect((screen.getByRole('button',{name:'Music2Emo vergleichen'}) as HTMLButtonElement).disabled).toBe(true);
});
