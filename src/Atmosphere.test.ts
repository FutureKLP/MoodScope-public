import {it,expect} from 'vitest';
import {emotionMix,EMOTION_PALETTE,atmosphereStyle} from './Atmosphere';
const point=(scores:Record<string,number>)=>({start:0,end:2,valence:0,scores});
it('blends all six emotions without choosing only the strongest label',()=>{
 const scores=Object.fromEntries(EMOTION_PALETTE.map(e=>[e.id,1/6]));const before=JSON.stringify(scores),mix=emotionMix(point(scores));
 expect(Object.values(mix.weights).reduce((a,b)=>a+b,0)).toBeCloseTo(1);
 for(const item of EMOTION_PALETTE){expect(mix.weights[item.id]).toBeCloseTo(1/6);expect(mix.color).toContain(item.color)}
 expect(JSON.stringify(scores)).toBe(before);
 expect(emotionMix(point({joy:.5,calm:.5})).color).not.toBe(emotionMix(point({joy:.5,fear:.5})).color);
});
it('keeps motion timing unchanged while exposing continuous palette shares',()=>{
 const style=atmosphereStyle(point({joy:.25,sadness:.75}),undefined,120) as Record<string,string|number>;
 expect(style['--emotion-joy']).toBe(.25);expect(style['--emotion-sadness']).toBe(.75);expect(style['--flow-duration']).toBe('24s');expect(style['--breath-duration']).toBe('2s');
 expect(style['--mood-color']).toContain('oklab');expect(emotionMix(point({joy:NaN,anger:-2})).color).not.toContain('NaN');
});
it('uses the leading audio category while keeping subordinate shares proportional',()=>{
 const mix=emotionMix(point({anger:.8,joy:.15,calm:.05}));
 expect(mix.dominant).toBe('anger');expect(mix.dominance).toBeCloseTo(.65);
 expect(mix.leadColor).toMatch(/^color-mix\(in oklab, #ce897f /);
 expect(mix.weights.joy).toBeCloseTo(.15);expect(mix.weights.calm).toBeCloseTo(.05);
 const style=atmosphereStyle(point({anger:1}),point({joy:1})) as Record<string,string>;
 expect(style['--lyric-color']).toContain('88%');
 const noLyrics=atmosphereStyle(point({sadness:1})) as Record<string,string>;
 expect(noLyrics['--lyric-color']).toBe(noLyrics['--mood-color']);
});
it('removes dominant accent at a tie and uses neutral colors for missing evidence',()=>{
 const mix=emotionMix(point({joy:.5,sadness:.5}));
 expect(mix.dominance).toBe(0);expect(mix.leadColor).toContain(' 0%,');
 expect(emotionMix(point({})).dominant).toBeNull();
 const style=atmosphereStyle({...point({}),valence:NaN,rms:NaN,arousal:NaN});
 expect(JSON.stringify(style)).not.toMatch(/NaN|null/);
});
