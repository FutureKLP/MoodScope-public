// @vitest-environment jsdom
import {render,screen,cleanup} from '@testing-library/react';
import {afterEach,it,expect} from 'vitest';
import {MusicEvidence} from './MusicEvidence';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();setLanguage('de')});
it('shows measured energy separately from uncertain expression and missing tension',()=>{
 setLanguage('en');render(<MusicEvidence packet={{version:'authored',observations:[
  {id:'M1',kind:'model_estimate',source:'authored',start:0,end:5,value:{valence:-.2,relative_descriptions:{anger:.4,sadness:.3}}},
  {id:'M2',kind:'measurement',source:'authored',start:0,end:5,value:{rms_mean:.2,relative_to_song_db:6.02}}
 ]}}/>);
 expect(screen.getByText(/6.0 dB/)).toBeTruthy();
 expect(screen.getByText(/not a confirmed emotion/)).toBeTruthy();
 expect(screen.getByText(/not independently validated/)).toBeTruthy();
 expect(screen.queryByText(/40.*%/)).toBeNull();
});
