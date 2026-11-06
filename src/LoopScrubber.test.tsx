// @vitest-environment jsdom
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {it,expect,vi,afterEach} from 'vitest';
import {LoopScrubber} from './LoopScrubber';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();setLanguage('de')});
it('orders two right-click markers and clears both on the third click',()=>{
 const change=vi.fn(),seek=vi.fn();const {container}=render(<LoopScrubber duration={100} time={0} disabled={false} onSeek={seek} onLoopChange={change}/>);
 const rail=container.querySelector('.scrubber-loop')!;vi.spyOn(rail,'getBoundingClientRect').mockReturnValue({left:0,width:200} as DOMRect);
 fireEvent.contextMenu(rail,{clientX:100});fireEvent.contextMenu(rail,{clientX:40});
 expect(change.mock.calls.at(-1)![0]).toEqual({a:20,b:50});expect(seek).toHaveBeenCalledWith(20);expect(container.querySelectorAll('.loop-marker')).toHaveLength(2);
 fireEvent.contextMenu(rail,{clientX:80});expect(change.mock.calls.at(-1)![0]).toBeNull();expect(container.querySelectorAll('.loop-marker')).toHaveLength(0);
});
it('provides the same loop markers through the keyboard in English',()=>{
 setLanguage('en');const change=vi.fn();const view=render(<LoopScrubber duration={100} time={15} disabled={false} onSeek={vi.fn()} onLoopChange={change}/>);
 fireEvent.click(screen.getByRole('button',{name:'Mark loop point at current position'}));
 view.rerender(<LoopScrubber duration={100} time={25} disabled={false} onSeek={vi.fn()} onLoopChange={change}/>);
 fireEvent.click(screen.getByRole('button',{name:'Mark loop point at current position'}));expect(change.mock.calls.at(-1)![0]).toEqual({a:15,b:25});
});
