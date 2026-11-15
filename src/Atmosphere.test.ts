import {it,expect} from 'vitest';
import {emotionMix,EMOTION_PALETTE,MUSIC_TAG_PALETTE,emotionColor,atmosphereStyle} from './Atmosphere';
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
 expect(mix.leadColor).toMatch(/^color-mix\(in oklab, #e36b62 /);
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
it('follows learned music tags without mapping power to anger',()=>{
 const mix=emotionMix({...point({powerful:.9,energetic:.5,happy:.2}),score_source:'music2emo_tags'});
 expect(mix.dominant).toBe('powerful');expect(mix.weights.anger).toBeUndefined();
 expect(mix.leadColor).toMatch(/^color-mix\(in oklab, #d5a351 /);
});

it('keeps the largest independent bar visible in the background without changing measured shares',()=>{
 const scores={happy:.55,calm:.1,sad:.3,melancholic:.2,hopeful:.4,romantic:.2,powerful:.71,energetic:.84,relaxing:.1};
 const mix=emotionMix({...point(scores),score_source:'music2emo_tags'});
 expect(mix.dominant).toBe('energetic');expect(mix.accent).toBeGreaterThan(.45);
 expect(mix.leadColor).toMatch(/^color-mix\(in oklab, #eb9c52 /);
 expect(mix.weights.powerful/mix.weights.energetic).toBeCloseTo(.71/.84);
 const tied=emotionMix({...point({...scores,powerful:.84}),score_source:'music2emo_tags'});
 expect(tied.accent).toBe(0);
});

it.each([
 ['clap',EMOTION_PALETTE],['music2emo_tags',MUSIC_TAG_PALETTE],
 ['provider_emotions',[...EMOTION_PALETTE,...MUSIC_TAG_PALETTE.filter(item=>['powerful','energetic'].includes(item.id))]],
] as const)('shares every %s bar color with its atmosphere without inventing other categories',(source,palette)=>{
 for(const item of palette){
  const sample={...point({[item.id]:.8,unknown:1}),score_source:source==='clap'?undefined:source};
  const before=JSON.stringify(sample),mix=emotionMix(sample);
  expect(mix.dominant).toBe(item.id);
  expect(mix.leadColor).toContain(emotionColor(item.id));
  expect(mix.weights[item.id]).toBe(1);
  expect(mix.weights.unknown).toBeUndefined();
  expect(JSON.stringify(sample)).toBe(before);
 }
});

it('uses the same neutral fallback for absent, zero, unknown and invalid category scores',()=>{
 const neutral=atmosphereStyle();
 for(const sample of [undefined,point({}),point({joy:0,calm:0}),point({unknown:1}),
  {...point({joy:NaN,calm:Infinity,sadness:-1}),valence:-1,arousal:1}]){
  const mix=emotionMix(sample);
  expect(mix.dominant).toBeNull();expect(mix.accent).toBe(0);
  expect(atmosphereStyle(sample)['--mood-color' as keyof ReturnType<typeof atmosphereStyle>]).toBe(neutral['--mood-color' as keyof typeof neutral]);
  expect(Object.values(mix.weights).every(value=>value===0)).toBe(true);
 }
});

it('bounds display inputs without changing cached scores or turning loudness into anger',()=>{
 const sample={...point({joy:2,calm:-.4,fear:Infinity}),rms:100,arousal:Infinity};
 const before={...sample.scores};
 const style=atmosphereStyle(sample,undefined,Infinity) as Record<string,string|number>;
 expect(emotionMix(sample).weights.joy).toBe(1);
 expect(style['--ambient-energy']).toBe(1);expect(style['--breath-duration']).toBe(`${240/90}s`);
 expect(style['--emotion-anger']).toBe(0);expect(sample.scores).toEqual(before);
 expect(JSON.stringify(style)).not.toMatch(/NaN|Infinity/);
});

it('fades the dominant accent continuously through a category tie',()=>{
 const before=emotionMix(point({joy:.5+1e-7,sadness:.5}));
 const after=emotionMix(point({joy:.5,sadness:.5+1e-7}));
 expect(before.dominant).toBe('joy');expect(after.dominant).toBe('sadness');
 expect(before.accent).toBeLessThan(.000001);expect(after.accent).toBeLessThan(.000001);
 expect(before.weights.joy).toBeCloseTo(after.weights.joy,6);
});

it('keeps words secondary even when their category contradicts the audio',()=>{
 const audio={...point({powerful:.8,energetic:.4}),score_source:'provider_emotions' as const};
 const plain=atmosphereStyle(audio) as Record<string,string>;
 const withWords=atmosphereStyle(audio,point({sadness:1})) as Record<string,string>;
 expect(withWords['--mood-color']).toBe(plain['--mood-color']);
 expect(withWords['--emotion-powerful']).toBe(plain['--emotion-powerful']);
 expect(withWords['--lyric-color']).toBe(`color-mix(in oklab, ${plain['--mood-color']} 88%, #668cce)`);
});
