// @vitest-environment jsdom
import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,cleanup} from '@testing-library/react';
import {AnalysisReport} from './AnalysisReport';
import {Analysis} from './types';
import {setLanguage} from './i18n';

afterEach(cleanup);
it('interpolates visible scores while preserving the stored section calculation',()=>{
 setLanguage('de');
 const analysis:Analysis={audio:[{start:0,end:2,valence:-.36,scores:{anger:.8,joy:.2}},{start:2,end:4,valence:.8,scores:{anger:0,joy:1}}],lyrics:[],split:null,warnings:[],cached:true,device:'cpu',method:'fixture',models:{audio:'fixture',lyrics:'fixture'},audio_method:{id:'clap-level-controlled-v7',recording:'recorded',labels:[{id:'anger',valence_weight:-.7,arousal_weight:1,prompts:[]},{id:'joy',valence_weight:1,arousal_weight:1,prompts:[]}]}};
 render(<AnalysisReport track={{id:'fixture',name:'Authored',duration:4}} analysis={analysis} time={1.9} onSeek={vi.fn()} onReanalyse={vi.fn()} busy={false}/>);
 expect(Number(screen.getByRole('meter',{name:'Ärger'}).getAttribute('aria-valuenow'))).toBeCloseTo(.44);
 expect(screen.getByText('44.00 %')).toBeTruthy();
 expect(screen.getByText(/keine Sicherheit über Gefühle/)).toBeTruthy();
 expect(screen.getByText(/0.8000 × -0.7/)).toBeTruthy();
});
