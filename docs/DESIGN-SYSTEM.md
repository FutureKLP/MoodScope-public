# MoodScope Designsprache

Beschreibung der bestehenden Oberfläche und verbindliche Regeln für Änderungen.

## Charakter und Struktur

MoodScope verbindet dunkle, matte, durchscheinende Flächen mit ruhigem farbigem
Licht. Inhalte und Bedienelemente bleiben optisch stabil, wenn die Atmosphäre
wechselt. Sidebar, matte fixierte Kopfzeile, gerundete Panels und bodenständiger
Player bilden die wiederkehrende Struktur. Keine dekorativen Emojis ergänzen.

Die Sidebar ist auf großen Ansichten 224 px breit; unter 950 px wird sie zur
oberen Navigation. Weitere bestehende Umbrüche bei 1100, 800, 700 und 600 px
verdichten einzelne Bereiche. Die Kopfzeile klappt beim Scrollen visuell ein,
ohne die Dokumentgeometrie umzubauen. Dialoge und Meldungen liegen außerhalb
ihres Darstellungskontexts über der Oberfläche. Vorhandene Import-, Player-,
Studio-, Analyse-, Notiz- und Einstellungsfunktionen erhalten.

## Typografie und Flächen

Schriftfamilie Inter mit Segoe UI und sans-serif als Rückfall, 14 px Basisgröße.
Große Überschriften verwenden etwa 24–36 px und mittlere Schriftstärke;
kleine Bereichsmarkierungen sind zurückhaltend gesperrt. Messwerte nutzen
tabellarische Ziffern. Bestehende Größen nicht durch eine neue Skala ersetzen.

Die Grundfläche ist `#0b1015`, Haupttext `#eef3f5`, Eingabetext `#e7edef` auf
`#0e171e`. Sekundärtexte sind gedämpft blaugrün. Kleine Sidebar-Beschriftungen
verwenden bei eingeschalteter Atmosphäre `#9dafb7`, damit Modell-/Geräteangaben
über unterschiedlichen Farbtönen lesbar bleiben. Panels haben dezente Konturen,
meist 10–15 px Rundung, Eingaben und Buttons etwa 7–8 px. Die Kopfzeile besitzt
ihre eigene größere Rundung und weiche Ausblendung. Abstände und Schatten aus
dem bestehenden CSS übernehmen, keine neue Geometrie einführen.

## Eine Palette für Balken und Atmosphäre

`emotionColor` und `emotionMix` in `Atmosphere.tsx` sind die gemeinsame Quelle.
Die ID der Modellkategorie, nicht ihre übersetzte Beschriftung, bestimmt die Farbe.

- Freude / `joy`, `happy`: `#f4ce54`, warmes Gelb.
- Ruhe / `calm`: `#66b8ac`, Blaugrün.
- Trauer / `sadness`, `sad`: `#668cce`, gedämpftes Blau.
- Ärger / `anger`: `#e36b62`, zurückgenommenes Rot.
- Anspannung/Angst / `fear`: `#9d89bb`, gedämpftes Violett.
- Zärtlichkeit/Romantik / `tenderness`, `romantic`: `#e5a0be`, Rosa.
- Melancholie / `melancholic`: `#7c83ad`, graues Violettblau.
- Zuversicht / `hopeful`: `#9bc77a`, Grün.
- Kraft / `powerful`: `#d5a351`, Bernstein.
- Energie / `energetic`: `#eb9c52`, Orange.
- Entspannung / `relaxing`: `#7fc5bd`, helleres Blaugrün.
- Fehlende oder unbekannte Kategoriescores: `#8cb8b8`, neutrales Blaugrün.

CLAP verwendet seine sechs Kategorien. Music2Emo verwendet seine neun gelernten
Tags. API-Scores verwenden die sechs Kategorien plus Kraft und Energie.
Kraft/Energie sind Klangcharakter; sie werden nicht als Ärger oder negative
Valenz umgedeutet. Text und Zahlen bleiben neben den Farben sichtbar.

## Mischung, Dominanz und fehlende Werte

Nur endliche bekannte Scores tragen zur Gestaltung bei; für die Anzeige auf
0–1 begrenzen, negative Werte ignorieren. Positive Scores für die Farbmischung
normalisieren und in OKLab mischen. Das verändert keine Analyse- oder Cachewerte.
Unabhängige Scores sind keine Prozentanteile persönlicher Gefühle.

Die stärkste Audiokategorie prägt das großflächige Licht. Ihr Akzent beträgt
`0.78 * gap / (gap + 0.08)`, wobei `gap` der Abstand der beiden größten
angezeigten Scores ist. Bei Gleichstand fällt der Akzent stetig auf null;
kleinere Anteile bleiben proportional im Mischton und in dezenten Untertönen
erhalten. Der erste Nebel verteilt die Leitfarbe über 130 % der Fläche;
Untertöne verwenden ihre Anteile mit Faktor 0,22. Lyrics können den sekundären
Farbton zu 12 % beeinflussen und ersetzen die Audioleitfarbe nicht.

Ohne Kategoriescores bleibt die Atmosphäre neutral blaugrün. Valenz, Lautstärke
oder Tempo allein erzeugen keine vermeintlich erkannte Emotionskategorie.
Ungültige Energie-/Tempowerte haben begrenzte Rückfallwerte. Ein Song ohne Werte
darf weder Farben noch verspätete Ergebnisse des vorherigen Songs übernehmen.

## Licht, Kontrast und Bewegung

### Verbindliche Bewegungsregel

Animationen und visuelle Zustandswechsel sollen flüssig und kontinuierlich
verlaufen. Farben, Atmosphäre, Ein-/Ausblendungen, Größen- und Positionswechsel
verwenden zusammenhängende Übergänge und sanfte Beschleunigung beziehungsweise
Verzögerung. Ein unterbrochener Übergang setzt am aktuell dargestellten Zustand
an, damit wiederholte Bedienung keine abrupten Neustarts oder Sprünge auslöst.
Diese Vorgabe gilt für bestehende und künftige Oberflächenarbeiten.

Bewegung folgt der tatsächlichen Wiedergabezeit; Bedienaktionen und sichtbare
Statusmeldungen reagieren unmittelbar. Übergänge bleiben begrenzt und werden
am gerenderten Ergebnis unter Wiedergabe, Pause und Zustandswechseln geprüft.
Die Einstellung für reduzierte Bewegung bleibt maßgeblich und unterbindet
dekorative Animationen und Übergänge wie unten beschrieben.

Der Hintergrund besitzt deutlich mehr Farbpräsenz als die Inhaltsflächen.
Browser mit relativen OKLCH-Farben begrenzen deren wahrnehmungsbezogene
Helligkeit: Hintergrund 0,31/0,265, Inhaltsflächen 0,22/0,205 bei 0,88/0,90
Deckkraft. Das sind OKLCH-L-Werte, keine Kontrastverhältnisse. Ohne diese
Browserfunktion bleibt die vorhandene `color-mix`-Darstellung aktiv.
Die Hauptaktion hat dunklen Text auf heller, getönter Fläche.

Für neue oder geänderte Texte mindestens 4,5:1 Kontrast bei normaler Schrift
anstreben; große Schrift und grafische Bedienelemente getrennt prüfen. Gradienten,
Transparenz, Hover, Fokus und Dialoge berücksichtigen. Ein einzelnes berechnetes
Farbenpaar belegt keine vollständige Barrierefreiheit. Vorhandene sichtbare
Tastaturfokusse erhalten; Informationen nie ausschließlich über Farbe vermitteln.

Farbübergänge dauern etwa zwei Sekunden, einzelne Gewichte 1,8 Sekunden.
Der Akzent wechselt stetig an Kategoriegleichständen. Nebel und Wasser folgen
Wiedergabe; Pause hält die Bewegung an. Das Grundfließen dauert 24 Sekunden,
Atmung `240 / bpm` Sekunden bei auf 40–200 begrenztem Tempo, Rückfall 90 bpm.
RMS steuert begrenzte Bewegungsintensität, kein Live-Frequenzspektrum.
`prefers-reduced-motion: reduce` unterbindet Animationen und Übergänge.

## Headerkontur

Die unteren Hintergrund- und Lichtlagen teilen eine Rundung von 36 px,
unter 800 px 24 px. Der vorhandene vertikale Verlauf blendet am unteren Rand
über 104 px aus, im kompakten Scrollzustand über 48 px. Die Kontur bleibt
vollbreit; kein zusätzlicher seitlicher Spalt zwischen Sidebar und Header.
Scrollmaß, Bedienelemente, weiche Farbübergänge und Reduced Motion bleiben
unverändert. Diese begrenzte Anpassung folgt dem ergänzenden Gestaltungsauftrag.

## Zustände, Sprache und Datenerhalt

Die angezeigte Audioquelle ist für Kurve, Detailbalken und Atmosphäre dieselbe.
Lokale Music2Emo-Tags gelten ausschließlich für den zugehörigen Song und lokalen
Modus. Modellwechsel und Cachetreffer aktualisieren die Darstellung; ein Wechsel
zu API ohne Cache wird neutral. Rückkehr zu lokal stellt die lokale Darstellung
wieder her. Ein-/Ausschalten erzeugt genau ein dekoratives, für Hilfstechnologien
verborgenes Atmosphärenfeld und startet keine Anbieteranalyse.

Deutsch und Englisch verwenden dieselben IDs, Farben und Layoutregeln.
Bedientexte über den vorhandenen Übersetzungskatalog führen; Profilnamen,
Musikmetadaten und eigene Notizen nicht übersetzen oder überschreiben.
Die Atmosphäre liest Analysewerte; sie verändert keine Musikdateien, Notizen,
Modellwerte oder gespeicherten Ergebnisse.

## Wissenschaftlicher Rahmen und Nachweise

Die Palette ist Gestaltung mit nachvollziehbaren Assoziationen, keine
universelle Emotionscodierung. Die Studie von
[Palmer et al. (2013)](https://doi.org/10.1073/pnas.1212562110) untersucht
Musik-Farb-Zuordnungen in zwei kulturellen Stichproben und einem begrenzten
Musikmaterial. [Jonauskaite et al. (2020)](https://doi.org/10.1177/0956797620948810)
berichten gemeinsame Muster mit sprachlichen und geografischen Unterschieden.
Daraus folgt keine individuelle Gefühlsdiagnose und keine wissenschaftliche
Bestätigung unserer Hex-Werte. Violett für Angst, Grün für Zuversicht und die
Klangcharakterfarben sind insbesondere Entscheidungen für Unterscheidbarkeit
im dunklen UI. Weitere Einordnung: [MUSIC-PSYCHOLOGY.md](MUSIC-PSYCHOLOGY.md).

Regressionen liegen in `Atmosphere.test.ts` und `App.test.tsx`. Sichtprüfung
und Kontrastprüfung müssen zusätzlich am gerenderten CSS erfolgen. Grenzen
und offene native Abnahmen: [Kernabnahme](CORE-ACCEPTANCE.md).
