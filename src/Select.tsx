import {SelectHTMLAttributes, useId, useLayoutEffect, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

// Keep the native field, labels, form value and change contract. Render its popup
// in the webview so GTK and Windows use the same application palette.
export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  const field = useRef<HTMLSelectElement>(null);
  const popup = useRef<HTMLDivElement>(null);
  const id = useId();
  const [open, setOpen] = useState(false);
  const [, refresh] = useState(0);
  const [active, setActive] = useState(-1);
  const [box, setBox] = useState({left: 0, top: 0, width: 0, maxHeight: 280});
  const search = useRef({text: '', time: 0});
  const options = Array.from(field.current?.options ?? []);
  const enabled = (index: number) => {
    const option = field.current?.options[index];
    return !!option && !option.disabled && !(option.parentElement instanceof HTMLOptGroupElement && option.parentElement.disabled);
  };
  function show() {
    if (props.disabled || !field.current) return;
    setActive(field.current.selectedIndex);
    setOpen(true);
  }
  function choose(index: number) {
    if (!enabled(index) || !field.current) return;
    const select = field.current;
    if (select.selectedIndex !== index) {
      select.selectedIndex = index;
      select.dispatchEvent(new Event('change', {bubbles: true}));
    }
    setOpen(false);
    select.focus();
  }
  useLayoutEffect(() => {
    if (!open || props.disabled) { if (open) setOpen(false); return; }
    const position = () => {
      const rect = field.current!.getBoundingClientRect();
      const below = window.innerHeight - rect.bottom - 12;
      const above = rect.top - 12;
      const upward = below < 200 && above > below;
      const height = Math.max(40, Math.min(280, field.current!.options.length * 44 + 12, upward ? above : below));
      const width = Math.min(Math.max(rect.width, 180), window.innerWidth - 16);
      setBox({left: Math.max(8, Math.min(rect.left, window.innerWidth - width - 8)),
        top: upward ? Math.max(8, rect.top - height - 4) : rect.bottom + 4,
        width, maxHeight: height});
    };
    const outside = (event: PointerEvent) => {
      if (!popup.current?.contains(event.target as Node) && event.target !== field.current) setOpen(false);
    };
    const scroll = (event: Event) => { if (!popup.current?.contains(event.target as Node)) setOpen(false); };
    position();
    document.addEventListener('pointerdown', outside, true);
    document.addEventListener('scroll', scroll, true);
    window.addEventListener('resize', position);
    return () => {
      document.removeEventListener('pointerdown', outside, true);
      document.removeEventListener('scroll', scroll, true);
      window.removeEventListener('resize', position);
    };
  }, [open, props.disabled]);
  useLayoutEffect(() => { if (open) refresh(value => value + 1); }, [open, props.children]);
  useLayoutEffect(() => {
    if (open) popup.current?.querySelector<HTMLElement>(`[data-index="${active}"]`)?.scrollIntoView?.({block: 'nearest'});
  }, [open, active]);
  function move(direction: number, edge = false) {
    const count = field.current?.options.length ?? 0;
    let index = edge ? (direction > 0 ? -1 : count) : active;
    for (index += direction; index >= 0 && index < count; index += direction) {
      if (enabled(index)) { setActive(index); return; }
    }
  }
  return <><select {...props} ref={field} className={['app-select', props.className].filter(Boolean).join(' ')}
    aria-expanded={open} aria-controls={open ? id : undefined} aria-activedescendant={open && active >= 0 ? `${id}-${active}` : undefined}
    onPointerDown={event => {
      props.onPointerDown?.(event);
      if (event.button !== 0 || event.defaultPrevented || props.disabled) return;
      event.preventDefault(); event.currentTarget.focus();
      if (open) setOpen(false); else show();
    }}
    onMouseDown={event => { event.preventDefault(); props.onMouseDown?.(event); }}
    onClick={event => {
      event.preventDefault(); props.onClick?.(event);
      if (event.detail === 0 && !props.disabled) { if (open) setOpen(false); else show(); }
    }}
    onBlur={event => { setOpen(false); props.onBlur?.(event); }}
    onKeyDown={event => {
      props.onKeyDown?.(event);
      if (event.defaultPrevented || props.disabled) return;
      if (event.key === 'Tab') { setOpen(false); return; }
      if (event.key === 'Escape') { if (open) {event.preventDefault(); event.stopPropagation(); setOpen(false);} return; }
      if (['Enter', ' ', 'F4'].includes(event.key)) {
        event.preventDefault(); event.stopPropagation();
        if (open) choose(active); else show();
        return;
      }
      if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
        event.preventDefault();
        if (!open) show();
        else move(event.key === 'ArrowDown' || event.key === 'Home' ? 1 : -1, event.key === 'Home' || event.key === 'End');
        return;
      }
      if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();
        const now = Date.now();
        search.current = {text: (now - search.current.time < 700 ? search.current.text : '') + event.key.toLocaleLowerCase(), time: now};
        if (!open) show();
        const all = Array.from(field.current?.options ?? []);
        const index = all.findIndex((option, index) => enabled(index) && option.text.toLocaleLowerCase().startsWith(search.current.text));
        if (index >= 0) setActive(index);
      }
    }}/>{open && createPortal(<div ref={popup} id={id} role="listbox" className="select-popup" style={box}
      aria-label={props['aria-label']} aria-labelledby={props['aria-labelledby']}
      onPointerDown={event => event.preventDefault()}>
      {options.map((option, index) => <div key={index} id={`${id}-${index}`} role="option" data-index={index}
        aria-selected={index === field.current?.selectedIndex} aria-disabled={!enabled(index)}
        className={index === active ? 'select-option active' : 'select-option'}
        onPointerMove={() => {if (enabled(index)) setActive(index);}} onClick={() => choose(index)}>
        <span>{option.text || '\u00a0'}</span><span className="select-option-mark" aria-hidden="true">{index === field.current?.selectedIndex ? '•' : ''}</span>
      </div>)}
    </div>, document.body)}</>;
}
