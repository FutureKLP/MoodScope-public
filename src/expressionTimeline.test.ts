import {it,expect} from 'vitest';
import {expressionTimeline} from './expressionTimeline';
import {Analysis} from './types';
it('recomputes the actual lyric contrast and never invents six-way scores',()=>{
 const analysis={audio:[{start:0,end:5,valence:-.8,scores:{anger:1}}],lyrics:[{start:0,end:5,valence:.8,scores:{joy:1}}],split:{gap:1.6}} as unknown as Analysis;
 const before=JSON.stringify(analysis);
 const projected=expressionTimeline(analysis,[{start:0,end:5,valence:.6,arousal:.9}])!;
 expect(projected.split?.gap).toBeCloseTo(.2);expect(projected.audio[0].scores).toEqual({});
 expect(projected.lyrics).toBe(analysis.lyrics);expect(JSON.stringify(analysis)).toBe(before);
 expect(expressionTimeline(analysis,null)).toBe(analysis);
});
it('does not report a split where lyrics cover less than half an interval',()=>{
 const analysis={audio:[],lyrics:[{start:0,end:2,valence:1,scores:{}}],split:null} as unknown as Analysis;
 expect(expressionTimeline(analysis,[{start:0,end:5,valence:-1,arousal:.9}])?.split).toBeNull();
});
