// @vitest-environment jsdom
import {useState} from 'react';
import {render, screen, fireEvent, cleanup, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {afterEach, expect, it, vi} from 'vitest';
import {Select} from './Select';

afterEach(cleanup);
function Fixture({disabled = false}: {disabled?: boolean}) {
  const [value, setValue] = useState('original');
  return <label>Quelle<Select disabled={disabled} value={value} onChange={event => setValue(event.target.value)}>
    <option value="original">Originalmix</option><option disabled value="missing">Nicht verfügbar</option>
    <option value="vocals">Gesang</option><option value="bass">Bass</option>
  </Select><output>{value}</output></label>;
}
it('keeps the native labelled field and commits a popup choice through onChange', async () => {
  const user = userEvent.setup(); render(<Fixture/>);
  const field = screen.getByRole('combobox');
  expect(field.getAttribute('aria-expanded')).toBe('false');
  await user.click(field);
  const menu = screen.getByRole('listbox');
  expect(field.getAttribute('aria-controls')).toBe(menu.id);
  await user.click(within(menu).getByRole('option', {name:'Gesang'}));
  expect((field as HTMLSelectElement).value).toBe('vocals');
  expect(screen.getByRole('status').textContent).toBe('vocals');
  expect(screen.queryByRole('listbox')).toBeNull();
  expect(document.activeElement).toBe(field);
});
it('skips unavailable choices and cancels keyboard navigation without changing the value', async () => {
  const user = userEvent.setup(); render(<Fixture/>);
  await user.tab(); await user.keyboard('{Enter}{ArrowDown}');
  const field = screen.getByRole('combobox');
  expect(document.getElementById(field.getAttribute('aria-activedescendant')!)?.textContent).toBe('Gesang');
  await user.keyboard('{Escape}');
  expect((field as HTMLSelectElement).value).toBe('original');
  await user.keyboard('{Enter}{End}{Enter}');
  expect((field as HTMLSelectElement).value).toBe('bass');
});
it('supports typeahead, outside dismissal and Tab without trapping focus', async () => {
  const user = userEvent.setup(); render(<><Fixture/><button>Weiter</button></>);
  await user.tab(); await user.keyboard('g{Enter}');
  expect((screen.getByRole('combobox') as HTMLSelectElement).value).toBe('vocals');
  await user.keyboard('{Enter}{Tab}');
  expect(document.activeElement).toBe(screen.getByRole('button', {name:'Weiter'}));
  expect(screen.queryByRole('listbox')).toBeNull();
  await user.click(screen.getByRole('combobox')); await user.click(document.body);
  expect(screen.queryByRole('listbox')).toBeNull();
});
it('does not open disabled fields or select disabled options', async () => {
  const user = userEvent.setup(); const {rerender} = render(<Fixture disabled/>);
  await user.click(screen.getByRole('combobox')); expect(screen.queryByRole('listbox')).toBeNull();
  rerender(<Fixture/>); await user.click(screen.getByRole('combobox'));
  await user.click(within(screen.getByRole('listbox')).getByRole('option', {name:'Nicht verfügbar'}));
  expect((screen.getByRole('combobox') as HTMLSelectElement).value).toBe('original');
});
it('fits a long menu above a field near the viewport edge and closes on page scrolling', async () => {
  const user = userEvent.setup(); render(<Fixture/>);
  const field = screen.getByRole('combobox');
  vi.spyOn(field, 'getBoundingClientRect').mockReturnValue({left:950, right:1150, top:700, bottom:744, width:200, height:44, x:950, y:700, toJSON(){}});
  await user.click(field);
  const menu = screen.getByRole('listbox');
  expect(parseFloat(menu.style.left) + parseFloat(menu.style.width)).toBeLessThanOrEqual(window.innerWidth - 8);
  expect(parseFloat(menu.style.top)).toBeLessThan(700);
  fireEvent.scroll(document); expect(screen.queryByRole('listbox')).toBeNull();
});
