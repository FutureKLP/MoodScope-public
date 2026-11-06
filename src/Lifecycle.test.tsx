// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {render,screen,waitFor,cleanup,within,act} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {Lifecycle} from './Lifecycle';
import {AtmosphereThemeContext} from './Atmosphere';
import {setLanguage,t} from './i18n';
beforeEach(()=>{setLanguage('de');vi.stubGlobal('fetch',vi.fn(async(url)=>new Response(JSON.stringify(String(url).endsWith('/health')?{system_control:true,instance_id:'test'}:{accepted:true}),{status:200})));});
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals();vi.useRealTimers();setLanguage('de')});
it('recovers controls when the initial service health request times out',async()=>{
 vi.useFakeTimers();let calls=0;
 vi.stubGlobal('fetch',vi.fn(async(_url,init)=>{calls++;if(calls===1)return new Promise<Response>((_resolve,reject)=>init?.signal?.addEventListener('abort',()=>reject(new DOMException('Timed out','AbortError'))));return new Response(JSON.stringify({system_control:true,instance_id:'recovered'}))}));
 render(<Lifecycle onStop={vi.fn()}/>);expect(screen.getByText('Verbindung prüfen …')).toBeTruthy();
 await act(async()=>{await vi.advanceTimersByTimeAsync(9400)});
 expect(screen.getByRole('button',{name:'Neustarten'}).hasAttribute('disabled')).toBe(false);expect(screen.getByText('Dienst bereit')).toBeTruthy();expect(calls).toBe(2);
});
it.each(['restart','stop'])('shows a styled, keyboard accessible %s dialog before any mutation',async action=>{
  const stop=vi.fn(),browserConfirm=vi.spyOn(window,'confirm');render(<Lifecycle onStop={stop}/>);
  const label=action==='restart'?'Neustarten':'Beenden';
  await waitFor(()=>expect(screen.getByRole('button',{name:label}).hasAttribute('disabled')).toBe(false));
  await userEvent.click(screen.getByRole('button',{name:label}));
  const modal=screen.getByRole('alertdialog');
  expect(modal.getAttribute('aria-modal')).toBe('true');
  expect(document.activeElement).toBe(within(modal).getByRole('button',{name:'Abbrechen'}));
  await userEvent.tab({shift:true});expect(document.activeElement).toBe(within(modal).getByRole('button',{name:label}));
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('alertdialog')).toBeNull();expect(stop).not.toHaveBeenCalled();
  expect(document.activeElement).toBe(screen.getByRole('button',{name:label}));
  expect(browserConfirm).not.toHaveBeenCalled();
});
it('only stops the backend after explicit in-app confirmation and localises the result',async()=>{
  setLanguage('en');const stop=vi.fn();render(<AtmosphereThemeContext.Provider value={{enabled:true,style:{'--mood-hue':250,'--lyric-hue':190} as React.CSSProperties}}><header style={{position:'sticky',zIndex:50}}><Lifecycle onStop={stop}/></header></AtmosphereThemeContext.Provider>);
  await waitFor(()=>expect(screen.getByRole('button',{name:'Quit'}).hasAttribute('disabled')).toBe(false));
  await userEvent.click(screen.getByRole('button',{name:'Quit'}));
  expect((screen.getByRole('alertdialog').closest('.ambient-dialog') as HTMLElement).style.getPropertyValue('--mood-hue')).toBe('250');
  await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Quit'}));
  await screen.findByText('Finished for today.');expect(stop).toHaveBeenCalledTimes(1);
  const overlay=document.querySelector('.lifecycle-overlay') as HTMLElement;expect(overlay.parentElement).toBe(document.body);expect(overlay.classList.contains('ambient-dialog')).toBe(true);expect(overlay.style.getPropertyValue('--mood-hue')).toBe('250');expect(document.body.style.overflow).toBe('hidden');
  const calls=vi.mocked(fetch).mock.calls.filter(([url])=>String(url).endsWith('/system'));
  expect(calls).toHaveLength(1);expect(JSON.parse(String(calls[0][1]?.body))).toEqual({action:'stop',force:true});
});
it('keeps template values intact and can translate stored UI messages back to German',()=>{
  setLanguage('en');expect(t('Größter Kontrast bei {0}',['0:30'])).toBe('Biggest contrast at 0:30');
  expect(t('Song importiert. Test [a+b]')).toBe('Song imported. Test [a+b]');
  setLanguage('de');expect(t('Saved analysis loaded; no new AI inference.')).toContain('keine erneute KI-Inferenz');
});
it('can finish quitting after the service already disappeared without leaving an error',async()=>{
 const ended=vi.fn();let online=true;
 vi.stubGlobal('fetch',vi.fn(async(url)=>{if(String(url).endsWith('/health')&&online)return new Response(JSON.stringify({system_control:true,instance_id:'authored'}));online=false;throw new TypeError('offline')}));
 render(<Lifecycle onStop={vi.fn()} onStopped={ended}/>);
 await waitFor(()=>expect(screen.getByRole('button',{name:'Beenden'}).hasAttribute('disabled')).toBe(false));
 await userEvent.click(screen.getByRole('button',{name:'Beenden'}));
 await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Beenden'}));
 await screen.findByText('Für heute beendet.');expect(ended).toHaveBeenCalledOnce();expect(screen.queryByRole('alert')).toBeNull();
});
