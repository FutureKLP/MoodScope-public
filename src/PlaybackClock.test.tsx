// @vitest-environment jsdom
import {StrictMode,useRef} from 'react';
import {act,cleanup,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {createPlaybackClock,PlaybackTime,usePlaybackClock} from './PlaybackClock';
import {PlaybackTheme} from './Atmosphere';
import {LoopRange} from './LoopScrubber';

let frames:Map<number,FrameRequestCallback>,next:number;
beforeEach(()=>{
 frames=new Map();next=0;
 vi.stubGlobal('requestAnimationFrame',vi.fn((callback:FrameRequestCallback)=>{frames.set(++next,callback);return next}));
 vi.stubGlobal('cancelAnimationFrame',vi.fn((id:number)=>frames.delete(id)));
});
afterEach(()=>{cleanup();vi.unstubAllGlobals();vi.restoreAllMocks()});
function frame(){act(()=>{const callbacks=[...frames.values()];frames.clear();callbacks.forEach(callback=>callback(performance.now()))})}
function Harness({session=0,range=null,enabled=true}:{session?:number;range?:LoopRange|null;enabled?:boolean}){
 const media=useRef<HTMLAudioElement>(null),loop=useRef(range);loop.current=range;
 const clock=usePlaybackClock(media,loop,session,enabled);
 return <><audio key={session} ref={media}/><PlaybackTime clock={clock}>{time=><output>{time}</output>}</PlaybackTime></>;
}
function transport(){
 const media=document.querySelector('audio')!;
 let paused=true;
 Object.defineProperty(media,'paused',{configurable:true,get:()=>paused});
 return {media,play:()=>{paused=false;fireEvent.play(media);fireEvent.playing(media)},pause:()=>{paused=true;fireEvent.pause(media)}};
}
it('keeps exact media time, shares one RAF, sleeps on pause/buffering and resumes',()=>{
 render(<Harness/>);const {media,play,pause}=transport();
 expect(frames.size).toBe(0);act(play);expect(frames.size).toBe(1);
 media.currentTime=1.234567;frame();expect(screen.getByRole('status').textContent).toBe('1.234567');expect(frames.size).toBe(1);
 fireEvent.playing(media);expect(frames.size).toBe(1);
 fireEvent.waiting(media);expect(frames.size).toBe(0);media.currentTime=2.345;fireEvent.seeked(media);
 expect(screen.getByRole('status').textContent).toBe('2.345');expect(frames.size).toBe(0);
 fireEvent.playing(media);expect(frames.size).toBe(1);act(pause);expect(frames.size).toBe(0);
 media.currentTime=8.75;fireEvent.seeked(media);expect(screen.getByRole('status').textContent).toBe('8.75');expect(frames.size).toBe(0);
});
it('enforces the shared loop on every frame without looping paused seeks',()=>{
 const view=render(<Harness range={{a:2.125,b:4.875}}/>);const {media,play,pause}=transport();
 act(play);media.currentTime=4.876;frame();expect(media.currentTime).toBe(2.125);expect(screen.getByRole('status').textContent).toBe('2.125');
 act(pause);media.currentTime=7;fireEvent.seeked(media);expect(media.currentTime).toBe(7);
 view.rerender(<Harness range={null}/>);act(play);media.currentTime=9;frame();expect(media.currentTime).toBe(9);
});
it('removes old media listeners and pending frames on replacement, stop and unmount',()=>{
 const view=render(<StrictMode><Harness/></StrictMode>);const old=transport();act(old.play);expect(frames.size).toBe(1);
 view.rerender(<StrictMode><Harness session={1}/></StrictMode>);expect(frames.size).toBe(0);
 old.media.currentTime=99;fireEvent.seeked(old.media);fireEvent.play(old.media);expect(screen.getByRole('status').textContent).toBe('0');expect(frames.size).toBe(0);
 const current=transport();act(current.play);expect(frames.size).toBe(1);
 view.rerender(<StrictMode><Harness session={1} enabled={false}/></StrictMode>);expect(frames.size).toBe(0);
 current.media.currentTime=10;fireEvent.timeUpdate(current.media);expect(screen.getByRole('status').textContent).toBe('0');
 view.unmount();expect(frames.size).toBe(0);
});
it('does not render stable panels or hidden consumers on clock ticks, including atmosphere',()=>{
 const clock=createPlaybackClock(),panel=vi.fn(()=> <textarea defaultValue="Editable notes"/>),hidden=vi.fn(time=><span>{time}</span>);
 const Panel=panel;
 const view=render(<PlaybackTheme clock={clock} analysis={null} curve={null} enabled={true} playing={true}><Panel/><PlaybackTime clock={clock}>{time=><output>{time}</output>}</PlaybackTime><PlaybackTime clock={clock} live={false}>{hidden}</PlaybackTime></PlaybackTheme>);
 const editor=screen.getByRole('textbox');fireEvent.change(editor,{target:{value:'Uncommitted edits'}});editor.focus();
 act(()=>clock.setTime(1.234));act(()=>clock.setTime(2.567));
 expect(panel).toHaveBeenCalledTimes(1);expect(hidden).toHaveBeenCalledTimes(1);expect(screen.getByRole('status').textContent).toBe('2.567');
 expect((editor as HTMLTextAreaElement).value).toBe('Uncommitted edits');expect(document.activeElement).toBe(editor);
 expect(view.container.querySelectorAll('.ambient-field')).toHaveLength(1);
});
