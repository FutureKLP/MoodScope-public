// @vitest-environment jsdom
import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,cleanup,fireEvent} from '@testing-library/react';
import {ErrorNotice} from './ErrorNotice';
import {AtmosphereThemeContext} from './Atmosphere';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();setLanguage('de')});
it('stacks errors outside the sticky header and allows explicit dismissal',()=>{
 setLanguage('de');const close=vi.fn();render(<header><ErrorNotice message="Authored failure" onDismiss={close}/><ErrorNotice message="Another authored failure"/></header>);
 expect(screen.getAllByRole('alert')).toHaveLength(2);const stack=document.getElementById('moodscope-notices')!;expect(stack.parentElement).toBe(document.body);expect(stack.querySelectorAll('.app-notice')).toHaveLength(2);
 fireEvent.click(screen.getByRole('button',{name:'Fehlermeldung schließen'}));expect(close).toHaveBeenCalledOnce();
});
