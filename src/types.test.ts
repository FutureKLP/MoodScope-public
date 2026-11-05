import {describe,it,expect} from 'vitest';
import {clock, activeLine, Point} from './types';
describe('player timing',()=>{
  it('formats track times',()=>{expect(clock(125.9)).toBe('2:05')});
  it('does not invent lyric coverage during gaps or after end',()=>{
    const lines=[{start:10,end:15,text:'hello',valence:1,scores:{}}] satisfies Point[];
    expect(activeLine(lines,9)).toBe(-1);expect(activeLine(lines,10)).toBe(0);expect(activeLine(lines,15)).toBe(-1);
  });
});
