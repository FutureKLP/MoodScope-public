// @vitest-environment jsdom
import {afterEach,expect,it} from 'vitest';
import {setLanguage,t} from './i18n';

afterEach(()=>setLanguage('de'));

it('translates provider error guidance and diagnostic IDs across a live language switch',()=>{
 const message='Audio-Modellserver meldet HTTP 401. Audiofähigkeit, Modell-ID, Key und Kontingent prüfen. Keine automatische Wiederholung. Fehler-ID: fixture. Details: data/logs/moodscope.log';
 setLanguage('en');
 const english=t(message);
 expect(english).toBe('Audio model server returned HTTP 401. Check audio support, model ID, key and quota. No automatic retry. Error ID: fixture. Details: data/logs/moodscope.log');
 setLanguage('de');
 expect(t(english)).toBe(message);
});
