import {describe,it,expect} from 'vitest';
import {clock, activeLine, Point,toLrc} from './types';
describe('player timing',()=>{
  it('formats track times',()=>{expect(clock(125.9)).toBe('2:05')});
  it('does not invent lyric coverage during gaps or after end',()=>{
    const lines=[{start:10,end:15,text:'hello',valence:1,scores:{}}] satisfies Point[];
    expect(activeLine(lines,9)).toBe(-1);expect(activeLine(lines,10)).toBe(0);expect(activeLine(lines,15)).toBe(-1);
  });
  it('preserves instrumental gaps when restoring cached lyric input',()=>{
    const text=toLrc([{start:1,end:3,text:'hello',valence:0,scores:{}},{start:7,end:9,text:'world',valence:0,scores:{}}]);
    expect(text).toBe('[00:01.00]hello\n[00:03.00]\n[00:07.00]world\n[00:09.00]');
  });
});
