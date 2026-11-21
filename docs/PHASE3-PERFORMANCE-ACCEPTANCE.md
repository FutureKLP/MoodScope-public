# Phase 3: Langzeitstabilität und Ressourcen

Aktueller Nachtrag: [Phase 3.2](#phase-32-ununterbrochener-nachlauf-und-speicherdiagnose)
schließt das einzelne 20-Minuten-Ziel. Speicherrestbedarf und Proactor-Ursache
bleiben offen; Phase 3 weiterhin teilweise bestanden. Die ersten Abschnitte
halten die früheren getrennten Sitzungen als datierte Nachweise fest.

Prüfserie vom 20./21. November 2026. **Entscheidung: teilweise bestanden.**
Keine allgemeine Kern- oder Releasefreigabe.
Historische Phase-2B-/2C-Berichte bleiben unverändert. Aktueller Überblick:
[STATUS.md](STATUS.md).

## Ausgangsstand und Messkonzept

Neuer Entwicklungsbranch `codex/phase3-performance-acceptance`, direkt von
`723b8c296283bd09468066617344a999543a143d` auf öffentlicher Abstammung.
Main beim PR-Abgleich `1717ffd`; #11/#12 offen, #13/#14 Draft.
Die vier Windows-/Ubuntu-Test-/Native-Buildjobs jedes Ausgangs-PRs erfolgreich;
der anfangs laufende #14-Lauf
[44811474870](https://github.com/FutureKLP/MoodScope-public/actions/runs/44811474870)
wurde erneut mit vier erfolgreichen Jobs geprüft. Kein Merge oder Force-Push.

Abschließender PR-Abgleich am 21. November:

| PR | Basis / Head | Status |
|---|---|---|
| #11 | main / `ff585f5` | Offen, vier grüne Jobs, keine Reviews/Reviewthreads |
| #12 | main / `5d459f0` | Offen, vier grüne Jobs, keine Reviews/Reviewthreads |
| #13 | Phase 2A / `b3e4b9c` | Draft, vier grüne Jobs, keine Reviews/Reviewthreads |
| #14 | Phase 2B / `723b8c2` | Draft, vier grüne Jobs, keine Reviews/Reviewthreads |
| [#15](https://github.com/FutureKLP/MoodScope-public/pull/15) | main / derselbe Phase-2C-Head `723b8c2` | Zusätzlich vorhandener offener Sammel-PR; vier grüne Jobs, keine Reviews/Reviewthreads |
| [#16](https://github.com/FutureKLP/MoodScope-public/pull/16) | Phase 2C / Phase-3-Dokumentationsbranch | Neuer Draft; eigene CI separat vom erfolgreichen Ausgangshead prüfen |

#15 ist eine zusätzliche bestehende Integrationslinie, keine bereits erfolgte
Übernahme der gestapelten PRs. Vor späteren Merges Basis und verbleibenden Diff
erneut abstimmen. Diese Phase ändert weder Main noch bestehende Reviewbranches.

Windows 11 Build 26200, Ryzen 5 7600X, zwölf logische CPUs, 31,14 GiB RAM,
RTX 5070 und integrierte Radeon. Bestehender Tauri-Releaseclient mit WebView2,
eigene SQLite, eigener Dienst und frisches WebView-Profil. Hauptfenster zunächst
1920 × 1032, danach 1442 × 1012 Bildregion; Win32 bestätigt 1440 × 980 Client,
96 DPI und separaten sichtbaren 16-Pixel-Tao-Helfer. Keine weitere DPI-Abnahme.
Modelle ausschließlich vorhanden und offline, keine Downloads. CLAP/XLM/Demucs:
Python 3.13.17, Torch 2.15.0+cu132, vier Torchthreads. Music2Emo nutzt den
vorhandenen Kompatibilitätsworker mit Python 3.10.9/Torch 2.8.0+cu129.
CPU und ausdrücklich angeforderte CUDA-Läufe erfolgen nacheinander.

Zwei quellbenannte Ausschnitte derselben freigegebenen lokalen Aufnahme,
zehn und zwölf Sekunden, Stereo; Quelldateien 44,1 kHz, verwaltete Wiedergabe
48 kHz. Das sind keine zwei unabhängigen Songs. Die übernommene synthetische
Zwei-Sekunden-Fixture wird nicht als Musikabnahme gezählt. Übernommene verfasste
Anzeige-Caches sind keine Inferenz; neue echte Berechnungen separat ausgewiesen.
Importvorbereitung per HTTP ist kein nativer Importnachweis. Musikidentitäten,
Lyrics, Rohanalysen, lokale Pfade und Einzelprotokolle bleiben ignoriert lokal.

Vor dem Start festgelegtes Ziel: mindestens 20 Minuten beaufsichtigte Desktopserie,
zehn Original-/Live-Mix-Zyklen, periodische Zustands-/Song-/Modellwechsel und
kontrollierter Neustart. Tatsächliche Dauer und Wiederholungen stehen unten.
Alle fünf Sekunden werden eigene Tauri-/WebView- und Dienst-/Workerfamilien
nach PID und Prozessstartzeit erfasst: RSS, Private Bytes, Handles, CPU und
Prozesszahl. Supervisor und unabhängige Modellprüfprozesse sind ausgeschlossen.
CPU ist Intervallmittel in Kernprozent: 100 % entspricht einem CPU-Kern.
Prozess-/Dateizahlen, JS-Heap und Listener sind Stichproben, keine Peakgarantien.
Temporäre Dateien und Music2Emo-Bereiche werden separat gezählt.

Erste 60 Sekunden gelten als Aufwärmphase; Quellöffnung und Modellladen bleiben
zusätzlich als Lastwechsel erkennbar. Trends nur innerhalb derselben Prozess-
lebensdauer und mit bezeichnetem Bedienzustand vergleichen. Regressionen und
unabhängige Modellläufe überlappen frühe Desktopabschnitte: deren CPU-/Zeitwerte
sind keine ungestörte Performancebaseline. Es gibt keinen vorhandenen verbindlichen
RSS-/Handle-Grenzwert. Projektziele sind keine erfundenen Performancebudgets:
keine Abstürze, bedienbare UI, geschlossene eigene Audiographen, keine eigenen
Workerreste, unveränderte Originale/Gewichte/produktive Daten und intakte SQLite.
Anhaltendes Wachstum erfordert Nachprüfung, keinen automatischen Leckfreiheitsbeweis.

## Native Audio- und Sitzungsprüfung

Eindeutiges Hauptfenster über tatsächlichen Prozess und Titel gebunden, große
frische Bildregion gewählt. Harmloser Bibliothek-/Analyse-Rückwechsel sichtbar
bestanden. Ein erster Accessibility-Indexklick änderte die Fensterdarstellung;
er zählt nicht als Reiterprüfung. Bildgebundene Wiederholung erfolgreich.
Keine Eingaben aus einer 16-Pixel-Hilfsregion.

Zehn nativ bediente Original-/Mix-Zyklen während gemeinsamer A/B-Wiedergabe:
Solo Gesang beziehungsweise Instrumental, Originalrückkehr. Nach Zyklus zehn:
**10 Contexts erzeugt und geschlossen, 90 Nodes erzeugt und getrennt**; alle
schwachen Contextreferenzen bereits durch normale GC eingesammelt. Nur das
Original-Audioelement bleibt, spielt und ist ungemutet. Kein erzwungener GC
für diese Primärmessung. AudioContext-Zähler vor dem ersten Mix installiert;
instrumentiert sind die verwendeten Gain-/MediaElementSource-Nodes.

Zusätzlich: Spur zum Mix hinzufügen/entfernen, Gesangspegel 100 → 50 %,
Original- und Live-Pause/Resume, Seeking im pausierten Original und Live-Mix,
zwei Hörstudio-/Analyse-Rückwechsel bei laufendem elftem Graphen. Ansichtswechsel
erhalten denselben aktiven Context. Live-Pause suspendiert ihn und pausiert
alle vier Stemquellen. Tatsächlicher Wechsel zum zweiten Musikausschnitt schließt
auch den elften Context und trennt alle 99 Nodes. Masterlistener sinken direkt
von 43 auf 35: die acht Mixerlistener sind entfernt. Vier Stemelemente entfernt,
neuer Master pausiert/ungemutet bei null, Loop zurückgesetzt. Keine fehlenden
Lyrics als geprüfte Lyrics-Synchronisation ausgeben.

160 Medienzeitstichproben im Abstand ungefähr 100 ms zeigen drei Looprücksprünge;
maximaler Player-/Masterunterschied 28,33 ms, Stem-/Masterunterschied 124,58 ms.
Die Folge enthält auch einen Originalwechsel und damit ein beziehungsweise fünf
Audioelemente. Das sind Anzeige-/Decoderzustände, keine physische Ausgangslatenz.
Weitere 360 Stichproben über 363,11 Sekunden mit Pause, Seeking, Song- und
Modellwechsel: 160 Proben mit laufendem Master; 28 Zeitrücksprünge einschließlich
manueller Seeks/Songwechsel, daher nicht 28 reine Loopdurchläufe. Maximum
Player/Master 40,38 ms, Stem/Master 121,06 ms, Kurve/Player 24,74 ms.
Das ist keine durchgängige sechsminütige Wiedergabe. Zwei echte Songwechsel
zwischen den Ausschnitten, native CLAP-/Music2Emo-Rückwahl und nativ gestartete
erneute Music2Emo-Berechnung bei weiter laufendem zweiten Loop bestanden.

Eine zwischenzeitliche Benutzereingabe aktivierte die Atmosphäre. Der nächste
Automationsschritt wurde bis zur frischen Beobachtung verworfen; diese Eingabe
zählt nicht als automatisierter Test. Nach dem vollständigen Neustart erschien
erneut eine 16-Pixel-Grenze trotz großer Erstaufnahme. Eindeutige Fensterbindung
erneuert, beide Bildregionen geprüft und große Region explizit gewählt; danach
Bibliothek, gespeicherte Modellkurve und Loopwiedergabe nativ bestätigt.

## Tatsächliche Audioausgabe

Kein zuverlässiger bereits verfügbarer Loopback-Weg nachgewiesen: vorhandenes
FFmpeg bietet DirectShow/OpenAL, aber kein WASAPI; DirectShow findet keine
Audioaufnahmegeräte. Keine installierten SoundCard-, SoundDevice-, PyAudio- oder
PyAudioWPatch-Bibliotheken. Keine Aufnahme, Treiberinstallation, globale
Audioänderung oder Mikrofonumgehung. Doppeltes Ausgangssignal, hörbare Lücken,
Sampleversatz und numerische Seek-/Loop-Ausgangsqualität bleiben **offen**.

## Echte lokale KI- und Workerläufe

Zeiten sind Einzelmessungen dieser Umgebung, keine Leistungsgrenzen. Kalt bedeutet
frischer Prüfprozess beziehungsweise erster Worker; Betriebssystem-Dateicache
wurde nicht geleert. Cachezeiten direkter Funktionsaufrufe und HTTP-Aufträge
mit 100-ms-Polling sind nicht direkt vergleichbar.

| Modell / Gerät | Ausgeführt | Ergebnis |
|---|---|---|
| CLAP CPU | Kalt, zwei residente Wiederholungen, ungültiges Audio, Abbruch nach erstem Zeitabschnitt, Neulauf, echter Analyseauftrag, drei Cachetreffer | 5,265 s; 0,755/0,693 s; ungültige Werte verworfen; Abbruch 0,234 s; Neulauf 0,747 s; Analyse 2,973 s; Cache 17,7–18,9 ms ohne Inferenz |
| CLAP CUDA | Gleiche getrennte Folge | 5,146 s; 0,148/0,202 s; Abbruch 0,065 s; Neulauf 0,144 s; Analyse 2,492 s; Cache etwa 17 ms. Torch-Peak im Prüfprozess 650,84 MiB belegt / 706 MiB reserviert |
| XLM-EMO CPU | Zwei eigens verfasste englische Prüfzeilen, Kaltstart, zwei Wiederholungen, Abbruch am Eingang, Neulauf | 5,727 s; 0,074/0,077 s; Neulauf 0,076 s. Kein zweites Textemotionsmodell und keine Musiktextqualitätsabnahme |
| Music2Emo CPU | Drei frische Worker, Abbruch, erneuter Worker | 16,880/10,591/10,837 s; Abbruch 9,849 s; Neulauf 10,605 s; keine eigenen Bereiche übrig |
| Music2Emo CUDA angefordert | Gleiche getrennte Folge im Kompatibilitätsworker | 12,851/11,082/10,833 s; Abbruch 10,325 s; Neulauf 11,141 s; keine eigenen Bereiche übrig. Elternprozess-Peak null misst ausdrücklich nicht den Worker-VRAM |
| Demucs CPU | Drei ungecachte Trennungen und drei direkte Cachetreffer | 9,161/6,796/6,603 s; Cache 13,1–17,9 ms |
| Demucs CPU im tatsächlichen Dienst | Laufend bei Fortschritt ≥15 bestätigt, nach 0,5 s Abbruch, kein fertiger Cache; Neulauf und Cacheauftrag | Abbruchantwort nach 3,831 s; Neulauf 4,788 s; Cacheauftrag 0,106 s inklusive Polling |

Ein erster CLAP-Halteraufruf übergab 44,1 kHz direkt und wurde vom Modell korrekt
abgewiesen. Halter auf den regulären 48-kHz-Resamplingpfad korrigiert, obenstehende
Folge wiederholt. Keine Anwendungskorrektur daraus abgeleitet. Eine direkte
Demucs-Abbruchprobe setzte nur ein Cancellationevent ohne den Dienstcallback;
die Berechnung beendete sich und erzeugte Cache. Sie zählt **nicht** als aktiver
Abbruch. Der gesonderte echte Dienstlauf oben schließt diesen gezielten Nachweis.

Weitere echte Dienst-CLAP-Analyse auf dem zweiten Ausschnitt: 5,999 s, Cacheauftrag
0,107 s einschließlich Polling. Native Audio-Modellwahl CLAP/Music2Emo und
Songöffnung sind von diesen HTTP-Vorbereitungen getrennt. Keine vollständige
CPU-/GPU-/Fehler-/Neustart-Kreuzmatrix aller vier Modelle behauptet. Die sichere
Music2Emo-Besitz-/Sperrbereinigung bleibt unverändert erhalten.

## Ressourcen, Regression und Datenabschluss

Erste beaufsichtigte Sitzung: **17 Minuten 18,90 Sekunden**, 206 Ressourcenproben
von Sekunde 5,13 bis 1033,80. Sauberer protokollierter Prozessabschluss vor der
Unterbrechung. Die Fortsetzung am Folgetag ist eine getrennte Prozesslebensdauer;
die dazwischenliegende Zeit ist kein Test. Das vorab gesetzte Ziel eines einzelnen
mindestens 20-minütigen Laufs wurde im ersten Lauf nicht erreicht. Kein
mehrstündiger oder ununterbrochener Gesamtzeitnachweis.

| Erste Prozesslebensdauer / Fenster | Native Familie | Dienstfamilie |
|---|---|---|
| Sekunde 300–600, wechselnde Mixwiedergabe | RSS 589,60–618,45 MiB; Private Bytes 395,50–490,99 MiB; 5.246–5.324 Handles; acht Prozesse; CPU-Median 52,63 Kernprozent | Enthält gezielte Inferenz: RSS 660,93–1.446,46 MiB; Private Bytes 1.718,10–2.708,63 MiB; 621–672 Handles; drei Prozesse; CPU-Spitze 359,91 Kernprozent |
| Sekunde 900–1033,80, andere Song-/Modell-/Atmosphärenzustände | RSS 604,32–672,87 MiB; Private Bytes 441,59–969,21 MiB; 5.171–5.232 Handles; acht Prozesse | Mit Music2Emo-Worker kurz bis sechs Prozesse; RSS bis 1.637,43 MiB; Private Bytes bis 3.811,63 MiB; bis 1.992 Handles |
| Letzte Minute desselben Dienstprozesses nach Workerende | Native Last nicht als identisch zum früheren Fenster behandeln | RSS 995,19–995,36 MiB; Private Bytes 2.096,30–2.096,55 MiB; 650–672 Handles; drei Prozesse; CPU-Median 0,16 Kernprozent |

Keine fortlaufende Handlevermehrung über die zehn Mixzyklen beobachtet.
Die höheren späteren nativen Private-Bytes-Spitzen bleiben auffällig, aber
Zustands-/Atmosphärenwechsel verhindern einen sauberen Vorher/Nachhervergleich.
Die genaue Ursache ist nicht belegt. Gezielte Wiederholung nach Neustart mit
konstantem Song, Originalloop und aktiver Atmosphäre separat ausgewertet;
kein Vergleich der absoluten Neustartwerte als Leaktrend. Keine Optimierung
auf Verdacht. JS-Heap und globale Listenerzahlen schwanken durch normale GC;
die direkt gezählten acht Masterlistener und Audiographen sind der stärkere
gezielte Lebenszyklusnachweis.

Vorher/Nachher: vollständige Hashmanifeste des freigegebenen Originalordners,
aller Modellcachedateien, produktiver SQLite und produktiver verwalteter WAVs
identisch. Produktive und isolierte SQLite `integrity_check=ok`. Nach Neustart,
100 lesenden Bibliotheks-/Analysecacheabfragen und nativer Songöffnung alle
Tabellenzeilen und Audio-/Stemhashes identisch, drei Bibliothekseinträge,
keine verwaisten Cachebesitzer. SQLite-Verbindungen erst in der zweiten
Dienstlebensdauer instrumentiert; erste Lebensdauer nicht nachträglich gezählt.

Keine eigenen Music2Emo-Bereiche nach den abgeschlossenen Aufträgen. Zwei
Music21-Bibliothekscachedateien und ein leerer Torchinductor-Ordner bleiben im
eigenen Tempbereich; sie sind keine verwaisten Workerbereiche und werden erhalten.
Ein erster Snapshotversuch wollte zusätzlich eine aktive Workersperrdatei hashen
und erhielt korrekt Zugriff verweigert. Halter auf Audio-/Stemdateien vor dem
Hashen begrenzt; korrigierte SQLite-/Medienvergleiche bestanden.

Im lokalen Dienstlog acht Windows-Asyncio-Proactor-`ConnectionResetError`-
Callbacks über beide Serien; kein entsprechender Prozessabsturz oder
fehlgeschlagener Modellabschluss. Zehn gezielt früh geschlossene Audiostreams
erzeugten keinen weiteren Callback. Ursache dadurch nicht reproduziert oder
geklärt; keine Anwendungskorrektur und kein fehlerfreies Log behauptet.

Fortsetzung am 21. November: **6 Minuten 4,98 Sekunden**, 71 Ressourcenproben
von Sekunde 8,54 bis 359,91. Zusammen 23 Minuten 23,88 Sekunden in zwei getrennten
beaufsichtigten Sitzungen, keine ununterbrochene 20-Minuten-Serie.
Letzte vergleichbare Minute der zweiten Prozesslebensdauer, Originalloop mit
Atmosphäre: native RSS 606,46–609,59 MiB, Private Bytes 573,91–603,78 MiB,
5.254–5.266 Handles, acht Prozesse, CPU-Median 53,08 Kernprozent. Eigener Dienst
RSS 655,77–655,79 MiB, Private Bytes 1.718,93–1.718,96 MiB, 608–609 Handles,
drei Prozesse, CPU-Median null. Innerhalb dieses Fensters keine fortlaufende
Handlevermehrung; die kurze Dauer erlaubt weiterhin keinen Leckfreiheitsbeweis.

100 zusätzliche lesende Bibliotheks-/Cacheabfragen erfolgreich. In der zweiten
Dienstlebensdauer einschließlich nativer Zugriffe insgesamt **493 tatsächliche
SQLite-Verbindungen geöffnet und geschlossen**, maximal vier gleichzeitig,
abschließend null aktiv. Nach nativer Songöffnung und nach Appschluss weiterhin
sämtliche Tabellen und Audio-/Stemhashes identisch zur Neustartbaseline.
Beide eigenen Prozessfamilien vollständig beendet, Ports 8765/19222 frei,
keine Inferenzworkerbereiche oder temporären Mixdateien. Vier absichtlich
erhaltene unklare/verlinkte Worker-Schutzfixtures der Regressionstests werden
getrennt gezählt und nicht als echte Workerreste behandelt.

Windows-Releasekompilierung mit `cargo build --release --locked --offline
--features tauri/custom-protocol --manifest-path src-tauri/Cargo.toml`
bestanden (18,48 s). Erneute neun Rusttests im Buildhalter bestanden. Kein
Installer-/Bundlelauf. Der wiederverwendete lokale Buildhalter schrieb zunächst
in seine historischen Logpfade; neue Buildnachweise anschließend im eigenen
Phase-3-Bereich gesichert. Anwendungscode unverändert, keine neuen Feature-,
Architektur-, Datenbank- oder Abhängigkeitsänderungen.

Bereinigter Dokumentationsstand wird ausschließlich nach exakter Index- und
erreichbarer Historienprüfung als separater Draft auf Phase 2C veröffentlicht.
Kein automatischer Main-Merge; öffentliche Musik-/Modellrohbelege werden nicht
Bestandteil der Abnahmedokumentation.

Projektseite, Kernaufgabe und Performanceaufgabe in Notion wurden in-place um
einen kurzen Status mit Link zu diesem öffentlichen Bericht und Draft #16 ergänzt;
ihre Arbeitsstatus bleiben erhalten. Der ausführliche lokale Nachtrag wurde von
der automatischen Übertragungsprüfung abgelehnt und nicht gespeichert. Keine
neuen Projekt-/Aufgabenduplikate.

Bereits neu bestanden: 399 Backendtests (38,37 s), 156 Frontendtests in 29 Dateien
(19,32 s), neun Rusttests locked/offline, fünf Node-Dialogdrivertests sowie
TypeScript/Vite. Bestehende Vite-Chunkwarnung bei 505,50 kB. Erster Sandbox-
Backendlauf ohne Fortschritt beendet und mit eigenen lokalen Socket-/Prozessrechten
erneut vollständig ausgeführt. Kein Appfehler daraus abgeleitet.

## Zentrale Freigabematrix

| Übernommenes Kriterium | Phase-3-Nachweis | Weiteres Gate |
|---|---|---|
| Wiederholte native Original-/Mixressourcen | Zehn Zyklen, elf Contexts inklusive Songwechsel, 99 Nodes und acht Masterlistener freigegeben | Im bezeichneten Ablauf geschlossen; längere und vielfältigere Musiklast weiter erforderlich |
| Vollständige native Wechselmatrix aus 2B/2C | Gezielte Mix-/Ansichts-/Song-/Modell-/Pause-/Seekfolge erweitert | Gesamte Kreuzmatrix einschließlich Lyrics/API/Fehlerkombinationen offen, vor Phase-5-Release |
| Zweite echte Textemotionsmodell-Inferenz | Nur vorhandenes XLM-EMO wiederholt | Fehlende Gewichte; eigenes freigegebenes Modellvorhaben vor Phase-5-Release |
| Audioausgabesynchronisation | Kein sicherer Aufnahmeweg | Offen; geeignete Loopbackumgebung vor Phase-5-Audiofreigabe |
| Längere Performance-/Ressourcenprüfung | Erste Serie 17 Minuten 18,9 Sekunden; getrennte Fortsetzung nach Neustart | Begrenzte Prüfung teilweise geschlossen; einzelnes 20-Minuten-Ziel und breitere mehrstündige Last offen |
| Weitere DPI, Mehrmonitor und Plattformen | Kein zusätzlicher Lauf | Phase 4 |
| Installation/Deinstallation und eigenständiges Backend | Build allein genügt nicht | Phase 4 |
| Qualitätsgrenzen von Text, Stimmen und Emotionsverlauf | Keine neue Qualitätsfreigabe | Phase 5 |

Keine externe Datenbankphase begonnen. Eine Teilabnahme hebt das Kern-Gate
nicht auf. Offene historische Kriterien werden hier nachgeführt, ohne die
damaligen Berichte umzuschreiben.
## Phase 3.2: Integrationsprüfung am 21. November 2026

Live geprüft: Main `1717ffd`, #11 `ff585f5`, #12 `5d459f0`, #13
`b3e4b9c`, #14/#15 `723b8c2`, #16 `1da542d`. Alle sechs PRs offen,
keiner gemergt; #13/#14/#16 Draft. Die zugehörigen Actions-Läufe sind erfolgreich:
#11 44382936443, #12 44384587002, #13 44756726817, #14/#15
44811473779 und 44811474870, #16 44925957880. Für #16 zusätzlich alle vier
Windows-/Ubuntu-Test- und Native-Buildjobs einzeln erfolgreich bestätigt.
Das ersetzt keine Reviews und keine offenen Abnahmekriterien.

Abstammung und Diffs lokal mit den öffentlich bestätigten SHAs geprüft:
#11 enthält 14 Dokumentationsdateien; #12 drei Quell-/Abnahmecommits und 19
Dateien gegenüber Main. Der Mergecommit `89bd4a8` in #13 verbindet beide Linien;
`ff585f5` ist Vorfahr von #13. #13 umfasst gegen #12 sieben Commits und 34
Dateien einschließlich dieser Dokumentation. #14 fügt drei Commits und acht
Dateien hinzu, darunter die Prüfung nicht endlicher Solo-WAV-Samples. #16 fügt
zwei Commits und sechs Dokumentationsdateien hinzu. #15 hat exakt denselben
Head wie #14, aber Main als Basis: 13 Commits, 48 Dateien. Es ist kein weiterer
unabhängiger Änderungsblock.

**Empfehlung: kleine Integrationsschritte #11, #12, #13, #14, danach #16.**
Jeweils erst nach Review und erfolgreichen Pflichtchecks des tatsächlich zu
integrierenden Stands. Mergecommits bevorzugen, damit die bereits gestapelte
Abstammung erhalten bleibt. Nach jedem Merge die nächste Basis auf Main
nachführen, verbleibenden Diff erneut prüfen und CI erneut abwarten. Bei
Dokumentationskonflikten den jüngsten geprüften Status erhalten und ältere
Nachweise als datierte Historie bewahren. Drafts erst nach bewusster fachlicher
Freigabe bereitstellen; Teilabnahme nicht in Releasefreigabe umdeuten.

**#15 in dieser Route nicht zusätzlich mergen.** Nach Übernahme von #14 muss
sein Head bereits Vorfahr von Main und sein verbleibender Inhaltsdiff leer sein;
danach kann der PR nach separater Entscheidung als redundant geschlossen
werden. Alternativ könnte #15 nach umfassendem Review #12–#14 gesammelt
ersetzen, wäre aber der größere und hier nicht bevorzugte Schritt. Niemals beide
Routen unabhängig squashen oder cherry-picken. Bei abweichender Mergeart
Abstammung und patchäquivalente Änderungen vor jeder weiteren Übernahme erneut
prüfen. In dieser Sitzung kein Merge, keine Schließung, kein Force-Push und
keine Änderung fremder Reviewbranches.
## Phase 3.2: ununterbrochener Nachlauf und Speicherdiagnose

Am 21. November 2026 von **18:04:05,529 bis 18:25:00,042 MEZ**:
**20 Minuten 54,51 Sekunden tatsächlich gemessene Zeit**. 251 Ressourcenproben,
maximaler Abstand 5,025 Sekunden. Dieselbe App- und Dienstprozessidentität mit
unveränderter Startzeit über alle Proben; kein Neustart, keine Unterbrechung.
Startvorbereitung und Prozessabbau zählen nicht zur Dauer. Ein vorheriger
Sandboxstart ohne native Bereitschaft lief in ein Readiness-Timeout und zählt
nicht als Performance-Sitzung. Der anschließende eigene native Lauf nutzte lokale
Socket-/Prozessrechte, isolierte SQLite/Bibliothek, frisches WebView-Profil und
vorhandene Offlinegewichte. Keine Downloads und keine echten API-Transfers.

Zwei quellbenannte zehn-/zwölfsekündige Ausschnitte derselben erlaubten lokalen
Aufnahme; keine zwei unabhängigen Songs. Die mitkopierte historische synthetische
Fixture wurde nicht geöffnet oder als Musikabnahme gezählt. Vorbereitete
Anzeige-Caches bleiben von echter Inferenz getrennt. Fenster frisch gebunden,
große Bildregion verwendet. Ein erster Accessibility-Reiterklick führte zur
Verlaufsansicht; anschließende bildgebundene Bibliotheksnavigation bestätigt.
Nach Scrollanimationen vor weiteren Koordinateneingaben erneut beobachtet.
Keine Geometrie-/Hilfsfensterabnahme aus unklaren Eingaben abgeleitet.

Zehn native Original-/Live-Mixzyklen mit Gesangs-/Instrumentalwahl,
zweimal Live-Pause/Seek/Resume, laufendem Live-Seek, zweimal Original-Pause/
Seek/Resume, zwei nativ gesetzten A/B-Bereichen und zwei tatsächlichen Songwechseln.
Alle zehn Contexts geschlossen und alle 90 instrumentierten Gain-/Source-Nodes
getrennt; sämtliche schwachen Contextreferenzen durch normale GC eingesammelt.
Abschließend ein pausiertes, ungemutetes Originalelement, keine Stemelemente,
keine aktiven AudioHandler. Kein erzwungener GC. Fünfsekündige Medienproben
bestätigen die wechselnden Wiedergabezustände, ersetzen aber keine hochauflösende
Ausgangs-/Looplatenzmessung. Kein physischer Audioausgabenachweis.

Eine ausdrücklich per HTTP gestartete lokale CLAP-Neuberechnung ohne Whisper
wurde während nativer Originalwiedergabe nach **12,03 Sekunden** abgeschlossen.
Dies ist echte Offline-Inferenz im selben Dienst, kein nativer Auslösebeleg und
kein Music2Emo-Lauf trotz ausgewähltem Music2Emo-Anzeigecache. Modellladen und
Analyse wurden separat markiert. Kein zweites Textemotionsmodell geprüft.
Regressionen und Builds liefen erst nach Ende der Performance-Sitzung.

### Zustandsgetrennte Ressourcen

Alle Werte summieren jeweils die eigene native beziehungsweise Dienstfamilie;
CPU in Kernprozent, 100 % entspricht einem Kern. Konstante Fenster nach den ersten
20 Sekunden des bezeichneten Zustands ausgewertet. Die ersten 60 Sekunden sind
Aufwärmphase; die darüber hinausgehende Einrichtungsphase bis Sekunde 80 bleibt
zusätzlich getrennt. Der erste Originalabschnitt enthält am Ende die Navigation
ins Studio und ist nur mit dieser Einschränkung vergleichbar. Keine absoluten
Neustartwerte als Trend verglichen, keine erfundenen Speicherbudgets.

| Zustand innerhalb derselben Sitzung | Native RSS / Private Bytes (MiB) | Handles / CPU-Median |
|---|---|---|
| Original, Atmosphäre aus, erster Abschnitt | 557,11–570,87 / 374,72–434,50 | 5.335–5.411 / 37,99 % |
| Konstanter Live-Mix, Atmosphäre aus, 140,50 s Abschnitt | 596,29–602,29 / 411,95–417,75 | 5.385–5.404 / 43,91 % |
| Derselbe Live-Mix, Atmosphäre an, 130,48 s Abschnitt | 619,20–629,58 / 500,69–524,42 | 5.358–5.386 / 52,32 % |
| Original nach Context-Freigabe, Atmosphäre an, 135,49 s | 599,22–607,66 / 505,43–534,62 | 5.331–5.373 / 49,51 % |
| Original im Studio, Atmosphäre wieder aus, 130,45 s | 590,50–593,43 / 412,00–415,27 | 5.329–5.335 / 35,81 % |
| Wiederholungszyklen, wechselnde Graphen | bis 810,77 / bis 711,88 | bis 5.420 / kein konstanter Lastvergleich |
| Letzter pausierter Zustand nach Songrückkehr, 60,21 s Abschnitt | 782,01–788,65 / 640,03–648,30 | 5.306–5.317 / 14,01 % |

Native Familie nach dem Aufwärmen acht Prozesse; Dienst drei. Gesamtspitzen
native RSS 810,77 MiB, Private Bytes 711,88 MiB, 5.437 Handles und 105,57
Kernprozent; das sind Fünfsekundenstichproben, keine garantierten Maxima.
Dienst vor Modellladen etwa 657 MiB RSS / 1.720 MiB Private Bytes, danach
etwa 1.427 / 2.649 MiB; maximal 661 Handles und 77,82 Kernprozent.
Letztes Dienstfenster Private Bytes konstant 2.648,86 MiB, 634 Handles,
CPU-Median null. Residente Modelllast nicht mit nativem Wiedergabespeicher mischen.

**Einordnung der Private Bytes:** Die kontrollierte Atmosphärenzuschaltung
verschiebt das native Niveau um ungefähr 90–110 MiB; nach Ausschalten liegt
es wieder bei 412–415 MiB. Damit ist ein zustandsabhängiger Anteil bestätigt.
Die anschließende gezielte Wiederholung weiterer neun Graphzyklen zeigt jedoch
zusätzlichen Speicherverbleib: bei geschlossenem Graphen, demselben Song,
Originalwiedergabe im Studio und ausgeschalteter Atmosphäre etwa 413 MiB vor
der Folge, 498 nach Zyklus zwei, 575 nach fünf und 656 nach zehn. Die Nähe zur
jeweiligen Freigabe variiert; das sind keine gleich langen Erholungsfenster.
Zwei über die gesamte Sitzung identische WebView-Kindprozesse tragen den größten
Zuwachs. Ihre genaue interne Allokationsart ist nicht bestimmt.

JS-Heap im Live-Mix ohne Atmosphäre 3,71–5,31 MiB, mit Atmosphäre 4,09–8,49 MiB,
während der Wiederholungsfolge 3,82–6,69 MiB und abschließend 3,90–4,02 MiB.
Graph-/Nodefreigabe und fehlender fortlaufender Handletrend erklären den nativen
Restbedarf nicht. Der spätere pausierte Zustand bleibt erhöht, ist aber ein
anderer Bedienzustand. **Kein Leckfreiheitsnachweis und keine bestätigte Leckursache.**
Keine spekulative Optimierung. Nächster Speicherlauf: pro Zyklus feste gleiche
Wiedergabe-/Erholungsfenster und native Allokations-/Medienpufferdiagnose der
betroffenen WebView-Prozesse; langfristiges Plateau oder fortgesetztes Wachstum
getrennt prüfen. Diese Diagnose bleibt offen.

### Windows-Proactor

Sechs `ConnectionResetError`-Callbacks im laufenden Dienst: 18:08:50,276;
vier zwischen 18:19:05,629 und 18:19:05,741; einer 18:19:25,080 MEZ.
Der lokale Diagnosehandler protokolliert Zeit, Callback und beide Socketenden
und ruft anschließend unverändert den Standardhandler auf. Keine Unterdrückung.
Alle sechs betreffen Loopback-TCP-Verbindungen zum eigenen Audiodienst.
App, Browser und Dienst liefen dabei weiter; kein Testhalterabbruch zu diesen
Zeitpunkten. Vier Ereignisse liegen innerhalb derselben etwa 0,12 Sekunden wie
browserseitige `net::ERR_ABORTED`-Meldungen der Stem-Mix-Requests. Ein weiterer
Callback stimmt zeitlich mit einem solchen Abbruch überein. Der erste trat vor
Beginn der Browser-Netzaufzeichnung auf und ist nur dem ersten Live-Wechsel
zuzuordnen. Die genaue Eins-zu-eins-Zuordnung von Request zu Socket fehlt.

Lokaler gezielter Reproduktionsablauf: gespeicherte Vier-Gruppen-Stems öffnen,
Original-A/B-Loop spielen, Gesang beziehungsweise Instrumental aktivieren,
Pause/Seek/Resume und Originalrückkehr wiederholen; Callback- und Netzwerkzeiten
parallel erfassen. In dieser Folge erneut beobachtet, aber nicht bei jedem Zyklus.
Ein separater minimaler Proactor-TCP-Test mit 20 absichtlichen Resets und zehn
früh mit TCP-RST geschlossene echte Stem-Antworten erzeugten **keinen** Callback.
Die lokalen Testskripte und das Wiederholungsprotokoll bleiben erhalten; kein
zuverlässiger isolierter Minimalreproduzierer und keine endgültige Ursache.

Der Stack endet beim Socket-`shutdown` im Verbindungsabbau der vorhandenen
Python-Proactor-Laufzeit. Das grenzt die Meldung ein, beweist aber weder einen
Anwendungsfehler noch den genauen Auslöser der früheren acht Meldungen.
Kein Prozessabsturz, fehlgeschlagener Analyseabschluss oder Datenverlust in der
Nachlaufsitzung beobachtet. Auswirkung auf langfristige Socketbereinigung bleibt
gezielt zu prüfen. Keine Laufzeitänderung und keine Anwendungskorrektur auf Verdacht.

### Regression, Datenabschluss und Entscheidung

Neu bestanden: **399 Backendtests (49,21 s), 156 Frontendtests in 29 Dateien
(19,44 s), neun Rusttests locked/offline, fünf Node-Dialogdrivertests,
TypeScript/Vite und Windows-Custom-Protocol-Releasebuild locked/offline (18,22 s)**.
Bestehende Vite-Chunkwarnung bei 505,50 kB. Kein Installer-/Bundlelauf.

Vollständige Vorher-/Nachher-Hashes: Originalordner, Modellgewichte, produktive
SQLite und produktive verwaltete Audiodateien unverändert. Produktive und
isolierte SQLite `integrity_check=ok`. Isolierte Trackzeilen, Cachebesitzer und
Audio-/Stemhashes unverändert. Erwartet neu geschrieben wurde ausschließlich
ein `latest`-Analyse-Anzeigecache durch die ausdrücklich erzwungene Neuberechnung;
alle anderen vorhandenen Cacheeinträge unverändert. Nach Appschluss sämtliche
isolierten Tabellen und Medienhashes gleich zum unmittelbar vorherigen Snapshot,
keine verwaisten Cachebesitzer. **210 tatsächliche Dienst-SQLite-Verbindungen
geöffnet und geschlossen, maximal vier gleichzeitig, abschließend null aktiv.**
Keine eigenen Workerbereiche, temporären Mixdateien oder Tempdateien verblieben.
Alle gemessenen Prozessidentitäten beendet, Ports 8765/19222 frei. Absichtlich
erhaltene Worker-Schutzfixtures der Regression sind separat und keine Dienstreste.

**Phase 3 bleibt teilweise bestanden.** Das einzelne 20-Minuten-Ziel ist jetzt
im bezeichneten engen Musik-/Windowsumfang geschlossen. Speicherrestbedarf und
Proactor-Ursache bleiben offen; keine neue allgemeine Langzeit-, Kern- oder
Releasefreigabe. Physische Audioausgabe, zweites echtes Textemotionsmodell,
vollständige native Lyrics-/API-/Audiokreuzmatrix, weitere DPI/Mehrmonitor,
Windows 10/Linux, Installation/Update/Deinstallation und Musik-/Modellqualität
bleiben unverändert offen.

Übergabe an Phase 4: geprüften Integrationsweg oben beibehalten; pro Plattform
und DPI einen isolierten Daten-/Prozess-/Ausgabeschutz vorsehen; Windows-10-/
Linux- und Mehrmonitorabnahme sowie Installation, Update und Deinstallation
separat planen und tatsächlich durchführen. Den offenen Speicher- und
Proactor-Diagnoseauftrag mitführen; erfolgreiche Builds ersetzen keine dieser
Abnahmen. Keine externe Datenbankphase und keine Releasefreigabe.
