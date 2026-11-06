// @vitest-environment jsdom
import {it,expect,vi,afterEach} from 'vitest';
import {LiveStemMixer} from './LiveMix';
class Media extends EventTarget{paused=true;currentTime=0;volume=.8;muted=false;playbackRate=1;src='';preload='';crossOrigin='';play=vi.fn(async()=>{this.paused=false;this.dispatchEvent(new Event('play'))});pause=vi.fn(()=>{this.paused=true;this.dispatchEvent(new Event('pause'))});removeAttribute=vi.fn();load=vi.fn()}
class Gain{gain={value:0,setTargetAtTime:vi.fn()};connect=vi.fn();disconnect=vi.fn()}
class Context{currentTime=0;destination={};gains:Gain[]=[];resume=vi.fn(async()=>{});close=vi.fn(async()=>{});createGain(){const g=new Gain();this.gains.push(g);return g}createMediaElementSource(){return {connect:vi.fn(),disconnect:vi.fn()}}}
afterEach(()=>vi.unstubAllGlobals());
it('updates stem gains live, follows master transport and restores original audio on cleanup',async()=>{
 vi.stubGlobal('Audio',Media);vi.stubGlobal('AudioContext',Context);vi.stubGlobal('requestAnimationFrame',vi.fn(()=>1));vi.stubGlobal('cancelAnimationFrame',vi.fn());
 const master=new Media(),state=vi.fn(),mixer=new LiveStemMixer(master as unknown as HTMLAudioElement,{vocals:'http://localhost/vocals',drums:'http://localhost/drums'},state);
 mixer.setLevels(['vocals'],{vocals:.5});const context=mixer.context as unknown as Context;
 expect(context.gains[1].gain.setTargetAtTime).toHaveBeenLastCalledWith(.5,0,.015);expect(context.gains[2].gain.setTargetAtTime).toHaveBeenLastCalledWith(0,0,.015);
 await master.play();await Promise.resolve();await Promise.resolve();await Promise.resolve();
 expect(master.muted).toBe(true);expect(state).toHaveBeenCalledWith('playing');
 master.currentTime=7;master.dispatchEvent(new Event('seeked'));expect(mixer.channels.every(c=>c.audio.currentTime===7)).toBe(true);
 mixer.setLevels(['vocals','drums'],{vocals:.25,drums:.75});expect(context.gains[2].gain.setTargetAtTime).toHaveBeenLastCalledWith(.75,0,.015);
 expect(mixer.channels).toHaveLength(2);master.pause();expect(mixer.channels.every(c=>c.audio.paused)).toBe(true);
 mixer.dispose();expect(master.muted).toBe(false);expect(context.close).toHaveBeenCalledOnce();expect(mixer.channels.every(c=>(c.audio.load as any).mock.calls.length===1)).toBe(true);
});
