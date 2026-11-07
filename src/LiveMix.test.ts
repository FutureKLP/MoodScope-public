// @vitest-environment jsdom
import {it,expect,vi,afterEach} from 'vitest';
import {LiveStemMixer} from './LiveMix';
class Media extends EventTarget{paused=true;private position=0;get currentTime(){return this.position}set currentTime(value:number){this.position=value}readyState=4;seeking=false;volume=.8;muted=false;playbackRate=1;src='';preload='';crossOrigin='';play=vi.fn(async()=>{this.paused=false;this.dispatchEvent(new Event('play'))});pause=vi.fn(()=>{this.paused=true;this.dispatchEvent(new Event('pause'))});removeAttribute=vi.fn();load=vi.fn()}
class Gain{gain={value:0,setTargetAtTime:vi.fn()};connect=vi.fn();disconnect=vi.fn()}
class Context{currentTime=0;destination={};gains:Gain[]=[];resume=vi.fn(async()=>{});close=vi.fn(async()=>{});createGain(){const g=new Gain();this.gains.push(g);return g}createMediaElementSource(){return {connect:vi.fn(),disconnect:vi.fn()}}}
afterEach(()=>vi.unstubAllGlobals());
it('updates stem gains live, follows master transport and restores original audio on cleanup',async()=>{
 vi.stubGlobal('Audio',Media);vi.stubGlobal('AudioContext',Context);vi.stubGlobal('requestAnimationFrame',vi.fn(()=>1));vi.stubGlobal('cancelAnimationFrame',vi.fn());
 const master=new Media(),state=vi.fn(),mixer=new LiveStemMixer(master as unknown as HTMLAudioElement,{vocals:'http://localhost/vocals',drums:'http://localhost/drums'},state);
 mixer.setLevels(['vocals'],{vocals:.5});const context=mixer.context as unknown as Context;
 expect(context.gains[1].gain.setTargetAtTime).toHaveBeenLastCalledWith(.5,0,.015);expect(context.gains[2].gain.setTargetAtTime).toHaveBeenLastCalledWith(0,0,.015);
 await master.play();await vi.waitFor(()=>expect(state).toHaveBeenCalledWith('playing'));
 expect(master.muted).toBe(true);expect(state).toHaveBeenCalledWith('playing');
 master.currentTime=7;master.dispatchEvent(new Event('seeked'));expect(mixer.channels.every(c=>c.audio.currentTime===7)).toBe(true);
 mixer.setLevels(['vocals','drums'],{vocals:.25,drums:.75});expect(context.gains[2].gain.setTargetAtTime).toHaveBeenLastCalledWith(.75,0,.015);
 expect(mixer.channels).toHaveLength(2);master.pause();expect(mixer.channels.every(c=>c.audio.paused)).toBe(true);
 mixer.dispose();expect(master.muted).toBe(false);expect(context.close).toHaveBeenCalledOnce();expect(mixer.channels.every(c=>(c.audio.load as any).mock.calls.length===1)).toBe(true);
});
it('does not repeatedly seek streaming stems for small drift or while buffering',async()=>{
 let frame:FrameRequestCallback=()=>{};let now=0;vi.spyOn(performance,'now').mockImplementation(()=>now);
 vi.stubGlobal('Audio',Media);vi.stubGlobal('AudioContext',Context);vi.stubGlobal('requestAnimationFrame',vi.fn(fn=>{frame=fn;return 1}));vi.stubGlobal('cancelAnimationFrame',vi.fn());
 const master=new Media(),mixer=new LiveStemMixer(master as unknown as HTMLAudioElement,{vocals:'local'},vi.fn());
 await master.play();for(let i=0;i<5;i++)await Promise.resolve();
 const audio=mixer.channels[0].audio,write=vi.spyOn(audio,'currentTime','set');
 master.currentTime=10;audio.currentTime=9.8;write.mockClear();now=6000;frame(now);
 expect(write).not.toHaveBeenCalled();expect(audio.playbackRate).toBeGreaterThan(1);
 // A decoder that is still buffering must not be reset every polling interval.
 (audio as unknown as Media).readyState=2;master.currentTime=15;now+=6000;frame(now);now+=300;frame(now);expect(write).not.toHaveBeenCalled();
 master.dispatchEvent(new Event('waiting'));expect(audio.paused).toBe(true);
 master.dispatchEvent(new Event('playing'));for(let i=0;i<5;i++)await Promise.resolve();expect(audio.paused).toBe(false);
 write.mockClear();master.currentTime=30;master.dispatchEvent(new Event('seeked'));expect(write).toHaveBeenCalledOnce();expect(audio.currentTime).toBe(30);
 mixer.dispose();vi.restoreAllMocks();
});

it('times out an unresponsive source and releases every channel',async()=>{
 vi.useFakeTimers();vi.stubGlobal('Audio',Media);vi.stubGlobal('AudioContext',Context);vi.stubGlobal('requestAnimationFrame',vi.fn(()=>1));vi.stubGlobal('cancelAnimationFrame',vi.fn());
 const master=new Media(),state=vi.fn(),mixer=new LiveStemMixer(master as unknown as HTMLAudioElement,{vocals:'local'},state);
 vi.mocked(mixer.channels[0].audio.play).mockImplementation(()=>new Promise(()=>{}));
 await master.play();await vi.advanceTimersByTimeAsync(20001);
 expect(state).toHaveBeenCalledWith('error');expect(master.muted).toBe(false);
 expect(mixer.channels[0].audio.load).toHaveBeenCalledOnce();vi.useRealTimers();
});

it('can resume immediately after cancelling an unresolved play request',async()=>{
 vi.stubGlobal('Audio',Media);vi.stubGlobal('AudioContext',Context);vi.stubGlobal('requestAnimationFrame',vi.fn(()=>1));vi.stubGlobal('cancelAnimationFrame',vi.fn());
 const master=new Media(),state=vi.fn(),mixer=new LiveStemMixer(master as unknown as HTMLAudioElement,{vocals:'local'},state);
 vi.mocked(mixer.channels[0].audio.play).mockImplementationOnce(()=>new Promise(()=>{}));
 await master.play();for(let i=0;i<5;i++)await Promise.resolve();master.pause();await master.play();
 await vi.waitFor(()=>expect(state).toHaveBeenCalledWith('playing'));
 expect(mixer.channels[0].audio.play).toHaveBeenCalledTimes(2);mixer.dispose();
});

it('cleans up already-created and failing channels when audio graph construction fails',()=>{
 const created:Media[]=[];class TrackedMedia extends Media{constructor(){super();created.push(this)}}
 vi.stubGlobal('Audio',TrackedMedia);vi.stubGlobal('AudioContext',Context);vi.stubGlobal('cancelAnimationFrame',vi.fn());
 const create=vi.spyOn(Context.prototype,'createMediaElementSource');create.mockImplementationOnce(()=>({connect:vi.fn(),disconnect:vi.fn()})).mockImplementationOnce(()=>{throw Error('Authored graph failure')});
 expect(()=>new LiveStemMixer(new Media() as unknown as HTMLAudioElement,{vocals:'local',drums:'local'},vi.fn())).toThrow('Authored graph failure');
 expect(created).toHaveLength(2);for(const audio of created)expect(audio.load).toHaveBeenCalledOnce();create.mockRestore();
});
