// @vitest-environment jsdom
import {render,screen,cleanup,act} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {CombinedReading} from './CombinedReading';
import {Analysis} from './types';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
const analysis={models:{audio:'authored'},mode:'local'} as Analysis;
it('follows the selected audio model and playback interval without adding a graph',async()=>{
 setLanguage('de');const fetcher=vi.fn(async(_input:unknown)=>new Response(JSON.stringify({audio_source:'Music2Emo',rows:[{start:0,end:5,relation:'contrasting',text_coverage:1,usable_text_coverage:1,text_references:['L1']},{start:5,end:10,relation:'uncertain_text',text_coverage:1,usable_text_coverage:0,text_references:['L2']}]})));
 vi.stubGlobal('fetch',fetcher);
 const view=render(<CombinedReading trackId="authored" analysis={analysis} musicSource="music2emo" time={2}/>);
 await screen.findByText(/gegensätzliche Valenztendenzen/);
 expect(String(fetcher.mock.calls[0][0])).toContain('music_source=music2emo');
 expect(view.container.querySelector('svg')).toBeNull();
 view.rerender(<CombinedReading trackId="authored" analysis={analysis} musicSource="music2emo" time={7}/>);
 expect(screen.getByText(/Texterkennung.*zu unsicher/)).toBeTruthy();
 view.rerender(<CombinedReading trackId="authored" analysis={analysis} musicSource="music2emo" time={12}/>);
 expect(view.container.textContent).toBe('');expect(fetcher).toHaveBeenCalledTimes(1);
});
it('does not invent a joint reading for an unavailable response',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response('{}')));
 const view=render(<CombinedReading trackId="authored" analysis={analysis} musicSource="analysis" time={2}/>);
 await act(async()=>{});expect(view.container.textContent).toBe('');
});
