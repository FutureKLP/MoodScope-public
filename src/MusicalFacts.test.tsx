// @vitest-environment jsdom
import {render,screen,fireEvent} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import {MusicalFacts} from './MusicalFacts';
import {setLanguage} from './i18n';
it('shows uncertain harmony in English and seeks actual chord intervals',()=>{
 setLanguage('en');const seek=vi.fn();render(<MusicalFacts time={1} onSeek={seek} features={{bpm:120,duration:4,rms_mean:.1,brightness_hz:2000,dynamic_range_db:6,crest_factor_db:9,harmony:{version:'authored',key:{tonic:'C',mode:'major',similarity:.8,margin:.03,alternatives:[{tonic:'A',mode:'minor',similarity:.77}]},chords:[{start:0,end:2,label:'C',similarity:.9,margin:.1},{start:2,end:4,label:null,similarity:.6,margin:.01}]}}}/>);
 expect(screen.getByText('Key candidate')).toBeTruthy();expect(screen.getByText('C major')).toBeTruthy();
 fireEvent.click(screen.getAllByRole('button')[1]);expect(seek).toHaveBeenCalledWith(2);
 expect(screen.getByText(/not probabilities/)).toBeTruthy();setLanguage('de');
});
