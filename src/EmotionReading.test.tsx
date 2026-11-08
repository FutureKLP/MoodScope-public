// @vitest-environment jsdom
import {afterEach,it,expect} from 'vitest';
import {render,screen,cleanup} from '@testing-library/react';
import {EmotionReading} from './EmotionReading';
import {setLanguage} from './i18n';
afterEach(cleanup);
it('shows positive high activation without relabelling it as anger',()=>{
 setLanguage('de');
 const point={start:0,end:5,valence:.8,arousal:.9,scores:{joy:.8,anger:.2}};
 const before=JSON.stringify(point);
 const {container}=render(<EmotionReading point={point}/>);
 expect(screen.queryByRole('img')).toBeNull();
 expect(JSON.stringify(point)).toBe(before);
 expect(screen.getByText(/Erinnerungen, Vertrautheit/)).toBeTruthy();
});
it('does not invent an activation coordinate for legacy results',()=>{
 setLanguage('de');render(<EmotionReading point={{start:0,end:5,valence:0,scores:{}}}/>);
 expect(screen.queryByRole('img')).toBeNull();
});
