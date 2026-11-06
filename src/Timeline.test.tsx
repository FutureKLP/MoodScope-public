// @vitest-environment jsdom
import {useState} from 'react';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {it,expect,vi,afterEach} from 'vitest';
import {Chart} from './main';
import {LoopScrubber,LoopRange,nextLoopRange} from './LoopScrubber';
import {interpolatePoint,chartTime} from './timeline';
import {Analysis,Point} from './types';
const points:Point[]=[{start:0,end:2,valence:-1,arousal:0,scores:{}},{start:2,end:4,valence:1,arousal:1,scores:{}}];
const result={audio:points,lyrics:[],split:null} as unknown as Analysis;
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('interpolates only visual measurements without mutating stored points',()=>{
 const before=JSON.stringify(points);expect(interpolatePoint(points,2)?.valence).toBe(0);expect(interpolatePoint(points,2)?.arousal).toBe(.5);
 expect(interpolatePoint(points,-1)).toBe(points[0]);expect(interpolatePoint(points,9)).toBe(points[1]);expect(interpolatePoint([],0)).toBeUndefined();expect(JSON.stringify(points)).toBe(before);
 expect(chartTime(-100,0,1000,100)).toBe(0);expect(chartTime(1500,0,1000,100)).toBe(100);
});
it('seeks continuously while dragging and stops on pointer cancellation',()=>{
 vi.stubGlobal('PointerEvent',MouseEvent);const seek=vi.fn();render(<Chart result={result} duration={100} time={0} seek={seek}/>);
 const graph=screen.getByRole('slider');vi.spyOn(graph,'getBoundingClientRect').mockReturnValue({left:0,width:1000} as DOMRect);
 fireEvent.pointerDown(graph,{button:0,clientX:263});fireEvent.pointerMove(graph,{clientX:500});fireEvent.pointerUp(graph,{clientX:737});
 expect(seek.mock.calls.map(c=>c[0])).toEqual([25,50,75]);
 fireEvent.pointerDown(graph,{button:0,clientX:500});fireEvent.pointerCancel(graph);seek.mockClear();fireEvent.pointerMove(graph,{clientX:737});expect(seek).not.toHaveBeenCalled();
 fireEvent.keyDown(graph,{key:'End'});expect(seek).toHaveBeenLastCalledWith(100);
});
it('shares A/B markers between graph and player and clears them on a third right click',()=>{
 function Shared(){const [range,setRange]=useState<LoopRange|null>(null);return <><Chart result={result} duration={100} time={0} seek={()=>{}} loopRange={range} onLoopMark={t=>setRange(nextLoopRange(range,t,100))}/><LoopScrubber duration={100} time={0} disabled={false} onSeek={()=>{}} range={range} onLoopChange={setRange}/></>}
 const {container}=render(<Shared/>);const graph=screen.getByRole('slider',{name:'Wiedergabeposition im Stimmungsverlauf'}),rail=container.querySelector('.scrubber-loop')!;
 vi.spyOn(graph,'getBoundingClientRect').mockReturnValue({left:0,width:1000} as DOMRect);vi.spyOn(rail,'getBoundingClientRect').mockReturnValue({left:0,width:1000} as DOMRect);
 fireEvent.contextMenu(graph,{clientX:263});expect(container.querySelectorAll('.loop-marker')).toHaveLength(1);
 fireEvent.contextMenu(rail,{clientX:750});expect(container.querySelectorAll('.chart-loop line')).toHaveLength(2);expect(container.querySelectorAll('.loop-marker')).toHaveLength(2);
 fireEvent.contextMenu(graph,{clientX:500});expect(container.querySelector('.chart-loop')).toBeNull();expect(container.querySelectorAll('.loop-marker')).toHaveLength(0);
});
