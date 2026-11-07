import {it,expect} from 'vitest';
import {silentTransport} from './audioTransport';
import {controlOrigin} from './api';

it('provides an exact-duration silent WAV without a streaming HTTP connection',async()=>{
  const blob=silentTransport(237.087354),bytes=new Uint8Array(await blob.arrayBuffer()),view=new DataView(bytes.buffer);
  expect(new TextDecoder().decode(bytes.slice(0,4))).toBe('RIFF');
  expect(new TextDecoder().decode(bytes.slice(8,12))).toBe('WAVE');
  expect(view.getUint16(20,true)).toBe(1);expect(view.getUint16(22,true)).toBe(1);
  expect(view.getUint32(24,true)).toBe(8000);expect(view.getUint16(34,true)).toBe(8);
  const frames=view.getUint32(40,true);
  expect(Math.abs(frames/8000-237.087354)).toBeLessThan(1/8000);
  expect(bytes.slice(44,44+frames).every(v=>v===128)).toBe(true);
  expect(view.getUint32(4,true)+8).toBe(bytes.length);expect(bytes.length%2).toBe(0);
  expect(silentTransport(1800).size).toBeLessThan(15_000_000);
  for(const invalid of [0,-1,NaN,Infinity,1801])expect(()=>silentTransport(invalid)).toThrow(RangeError);
});

it('separates only matching loopback control connections and preserves remote endpoints',()=>{
  expect(controlOrigin('http://127.0.0.1:8772')).toBe('http://localhost:8772');
  expect(controlOrigin('http://localhost:8765')).toBe('http://127.0.0.1:8765');
  expect(controlOrigin('https://example.test:9443/service')).toBe('https://example.test:9443/service');
});
