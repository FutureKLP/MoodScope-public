// @vitest-environment jsdom
import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,cleanup,fireEvent} from '@testing-library/react';
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
it('uses actual learned tags and valence from the same selected model',()=>{
 setLanguage('de');
 const analysis={audio:[{start:0,end:10,valence:-.7,scores:{anger:1}}],lyrics:[],split:null,warnings:[],cached:true,device:'cpu',method:'fixture',models:{audio:'CLAP',lyrics:'fixture'}} as Analysis;
 const rows=[{start:0,end:5,valence:.6,arousal:.8,scores:{happy:.7,powerful:.9},score_source:'music2emo_tags' as const},{start:5,end:10,valence:.4,arousal:.7,scores:{happy:.9,powerful:.5},score_source:'music2emo_tags' as const}];
 render(<AnalysisReport track={{id:'fixture',name:'Authored',duration:10}} analysis={analysis} emotionRows={rows} curveModel="Music2Emo" time={5} onSeek={vi.fn()} onReanalyse={vi.fn()} busy={false}/>);
 expect(screen.getByText('0.500')).toBeTruthy();
 expect(Number(screen.getByRole('meter',{name:'Kraft'}).getAttribute('aria-valuenow'))).toBeCloseTo(.7);
 expect(screen.queryByRole('meter',{name:'Ärger'})).toBeNull();
 expect(screen.getByText(/Valenz wird nicht aus den Tag-Balken berechnet/)).toBeTruthy();
 expect(screen.getByText('Klangcharakter')).toBeTruthy();
 expect(screen.getByText('Valenz: 0.5000')).toBeTruthy();
 expect(screen.getByText('Audiokontext: 0:05–0:10')).toBeTruthy();
});
it('navigates the exact measured sections and flags out-of-scale direct predictions',()=>{
 setLanguage('de');const seek=vi.fn();
 const analysis={audio:[],lyrics:[],split:null,warnings:[],cached:true,device:'cpu',method:'fixture',models:{audio:'CLAP',lyrics:'fixture'}} as Analysis;
 const rows=[{start:0,end:5,valence:1,arousal:.9,scores:{powerful:.9},context_start:0,context_end:30,outside_training_scale:true},{start:5,end:10,valence:.4,arousal:.7,scores:{powerful:.8},context_start:0,context_end:30}];
 render(<AnalysisReport track={{id:'fixture',name:'Authored',duration:40}} analysis={analysis} emotionRows={rows} curveModel="Music2Emo" time={0} onSeek={seek} onReanalyse={vi.fn()} busy={false}/>);
 expect((screen.getByRole('button',{name:'Vorheriger Analyseabschnitt'}) as HTMLButtonElement).disabled).toBe(true);
 fireEvent.click(screen.getByRole('button',{name:'Nächster Analyseabschnitt'}));expect(seek).toHaveBeenCalledWith(5);
 expect(screen.getByText('Audiokontext: 0:00–0:30')).toBeTruthy();
 expect(screen.getByText(/außerhalb der Trainingsskala/)).toBeTruthy();
});
