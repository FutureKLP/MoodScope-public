# Phase 2C: Hörstudio, Live-Mixer und WAV-Export

Prüflauf vom 20. November 2026. **Entscheidung: teilweise bestanden.**
Echte lokale Demucs-Inferenz, native Mixerbedienung, numerisch geprüfte Exporte,
Abbrüche und ein kombinierter Windows-Ablauf sind nachgewiesen. Die vollständige
Audio-Ressourcen-, Ausgabelatenz-, Fehler- und Plattformmatrix ist nicht geschlossen.
Phase 2B bleibt teilweise bestanden; keine allgemeine Kern- oder Releasefreigabe.
Aktueller Überblick: [STATUS.md](STATUS.md).

Die Nachabnahme **2C.2** am Ende dieses Dokuments ergänzt Demucs-Crashnachweise
und instrumentierte native Audiostichproben. Die folgenden Erstnachweise bleiben
historisch erhalten; Phase 2C bleibt teilweise bestanden.

## Git und Integration

Nach Fetch und GitHub-Abgleich bleibt Main auf
`1717ffd074041dd5db4e129f9f3aed3fb1a072dc`.

| PR | Tatsächliche Basis und Head | Diff | Review und CI |
|---|---|---|---|
| [#11](https://github.com/FutureKLP/MoodScope-public/pull/11) | main; `ff585f5` | 14 Markdown-Dateien, +849/-387 | Offen, mergefähig, keine Reviews oder Reviewthreads; alle vier Jobs erfolgreich |
| [#12](https://github.com/FutureKLP/MoodScope-public/pull/12) | main; `5d459f0` | 19 Dateien, +805/-18; native Importpicker, Player-Reparaturhinweis, Tests und Abnahme | Offen, mergefähig, keine Reviews oder Reviewthreads; alle vier Jobs erfolgreich |
| [#13](https://github.com/FutureKLP/MoodScope-public/pull/13) | Phase-2A-Reviewbranch; `b3e4b9c` | 34 Dateien, +2087/-415; enthält auch die Dokumentationsintegration von #11 | Offen, Draft, mergefähig, keine Reviews oder Reviewthreads; alle vier Jobs abschließend erfolgreich |

CI: [#11](https://github.com/FutureKLP/MoodScope-public/actions/runs/44382936443),
[#12](https://github.com/FutureKLP/MoodScope-public/actions/runs/44384587002),
[#13](https://github.com/FutureKLP/MoodScope-public/actions/runs/44756726817).
Der letzte Lauf war anfangs noch aktiv; sein Ubuntu-Native-Job bestand später.
Die Workflowjobs sind Windows-/Ubuntu-Test und Windows-/Ubuntu-Native-Build.
Die genaue serverseitige Branchschutz-Konfiguration wurde nicht separat ausgelesen;
grüne Jobs ersetzen kein Review und keine Prüfung der Mergebedingungen.

Integrationsreihenfolge bleibt **#11 → #12 → #13 → Phase 2C**. #11 und #12
zielen tatsächlich beide auf Main; das ist keine lineare Git-Abstammung.
Nach #11 muss #12 gegen den dann aktuellen Main auf Dokumentationskonflikte
geprüft werden. Danach #13 auf Main ausrichten und den verbleibenden Diff erneut
reviewen. Vor jedem Merge Pflichtchecks und Diskussionen des konkreten Heads prüfen.
Keine dieser PRs wurde automatisch gemergt; kein Force-Push.

Phase 2C entstand als `codex/phase2c-studio-regression` direkt von `b3e4b9c`.
Der öffentliche Dokumentationshead `ff585f5` und Phase 2A sind bereits Vorfahren.
Keine private Archivlinie wurde integriert. Die erreichbare Ausgangshistorie
bestand den Publikationsscanner: 228 Dateien, 912 historische Dateiversionen.

## Umgebung, Testebenen und Belege

Windows 11, WebView2, 96 DPI; Releaseclient, eigene SQLite, eigenes WebView-Profil,
eigener Loopback-Dienst, explizit CPU und offline geschaltete Modell-Hubs.
Der vorhandene Windows-Testhalter und der beaufsichtigte Dialogdriver wurden benutzt.
Der native Eingangstest erkannte das eindeutige Hauptfenster, band eine große
frische Bildregion und bestätigte Hörstudio-/Timeline-Rückwechsel sichtbar.
Die lesende Geometriediagnose zeigte zusätzlich den separaten 16-Pixel-Tao-Helfer.

Nach dem Neustart meldete ein Scrollversuch erneut 16-Pixel-Eingabegrenzen.
Keine Wiederholung mit alten Koordinaten: Fenster neu gewählt, beide Regionen
erfasst, große Region ausdrücklich gebunden und über die sichtbare Scrollleiste
fortgesetzt. Nachgewiesener Zustandswechsel und anschließender Export erfolgreich.
Ein früherer Versuch, eine unsichtbare Hauptfensteraktion per Index auszulösen,
wurde ebenfalls vom Werkzeug verworfen. Beides sind Automationsfehlversuche.

- **N:** native Eingabe im tatsächlichen Windows-Client mit Tauri-IPC und Dialogen.
- **I:** tatsächliche Inferenz mit vorhandenen lokalen Gewichten.
- **H:** tatsächlicher isolierter HTTP-Dienst; kein nativer Bediennachweis.
- **R:** deterministische Regression beziehungsweise kontrollierter Sollvergleich.

Audioquellen sind ausdrücklich synthetisch: ein nativ importierter 60-Sekunden-
Sinuston und eine vorbereitete Zwei-Sekunden-Exportfixture. Der Bibliothekshalter
hatte Anzeige-Caches für zwei geplante Importe vorverfasst. Nur der erste lange
Track wurde importiert; die zwei unbenutzten, ausdrücklich markierten Cachezeilen
des zweiten Plans wurden vor der Neustartbaseline aus der eigenen SQLite entfernt.
Diese Fixturekorrektur ist kein Anwendungsfehler. Vorverfasste Kurven sind keine
Inferenz; die spätere lokale Audio-/Textanalyse ist getrennt tatsächlich ausgeführt.

Echte Demucs-Spuren wurden ausschließlich neu im eigenen Testbereich erzeugt.
Kontrollierte Vier-Spur-Sollfixtures und eine absichtlich beschädigte NaN-Spur
liegen separat; sie sind keine Demucs-Ergebnisse. Keine Originalmusik abgespielt,
keine neuen Testlinks, Gewichte oder echten Cloudschlüssel. Musikqualität und
physische Audioausgabe wurden in dieser synthetischen Prüfung nicht abgenommen.

Lokale Belegserien: **N-entry/import**, **N-separation**, **N-live/clock**,
**N-export**, **N-api**, **N-restart/error**, **H-wave**, **P-resources**,
**D-integrity**, **R-suites**. Rohbäume, Hashmanifeste, SQLite-Vergleiche,
Prozessdaten und Fallskripte bleiben ignoriert lokal. Tabellen nennen ausgeführte
Prüfungen; „offen“ oder „teilweise“ ist ausdrücklich kein bestandener nativer Fall.

## A – Stem-Trennung

| Fall / Erwartung | Ausgeführter Test und Ergebnis | Status / Ebene | Beleg und Grenze |
|---|---|---|---|
| A01 Hörstudio erreichbar | Reiter geöffnet, leerer und ausgewählter Track sichtbar | Bestanden · N | N-entry/import; Windows, 96 DPI |
| A02 synthetischen Track wählen | 60-Sekunden-WAV nativ ausgewählt und importiert | Bestanden · N | N-entry/import; Anzeige-Cache vorverfasst |
| A03 Gewichte vorhanden | Lokale Checkpoints erfasst, echter Loader prüft den verwendeten Checkpoint | Bestanden · I | N-separation; keine Downloads |
| A04 Modelle und Modi | Auto, vier Gruppen, Fine-tuned und sechs Gruppen sichtbar; vier und sechs gewählt | Bestanden · N | N-separation, N-restart/error; nur vier Gruppen tatsächlich inferiert |
| A05 echte lokale Trennung | htdemucs-Neulauf auf CPU erzeugt vier Stereo-Float-Spuren | Bestanden · N/I | N-separation; synthetischer Sinuston, keine Isolationsqualität |
| A06 Fortschritt | Vorbereitung, Laden und Trennphase mit 15-%-Anzeige gesehen | Bestanden · N | N-separation; keine kontinuierliche Prozentmessung während jedes Modellsegments |
| A07 regulärer Abbruch | Natives Abbrechen; Dienststatus cancelled, kein neues Trennresultat | Bestanden · N/I | N-separation; kooperativer Abbruch, Modellschritt kann noch auslaufen |
| A08 Wiederholung | Nativ neu gestartet; tatsächlicher erfolgreicher Neulauf in 19,40 s | Bestanden · N/I | N-separation; kein Cachetreffer |
| A09 Cache erneut öffnen | Nach Neustart vier Gruppen gewählt; vorhandene Spuren ohne neue Trennung geladen | Bestanden · N/H | N-restart, D-integrity |
| A10 Song-/Modellwechsel | Zwei Songs und unterschiedliche Cachemodelle gewählt; keine alte Live-Auswahl übernommen | Bestanden · N | N-live, N-restart/error; keine volle Wechselmatrix während Inferenz |
| A11 fehlende Gewichte | Vorhandene Varianten lokal installiert; kein Gewichtsbestand verändert oder Download erzwungen | Offen · N | Keine neue native Fehlgewichtsabnahme |
| A12 Dienst-/Fehlerwiederherstellung | Vollständiger regulärer App-/Dienstneustart und Cache-/Exportwiederöffnung bestanden | Teilweise · N/H | N-restart/error; kein neuer harter Dienstabbruch während Demucs |

Echter erfolgreicher Output: 44.100 Hz, zwei Kanäle, 2.646.000 Frames je Spur,
60 Sekunden. Manifest-Rekonstruktions-RMS vor/nach unveränderter Standardtrennung:
0,00020355. Abgebrochener erster Auftrag: insgesamt 20,29 Sekunden bis Ende;
dies ist nicht die separat gemessene Abbruchreaktionszeit. Keine samplegenaue
Phasenkohärenz oder Sänger-/Instrumentisolation daraus ableiten.

## B – Live-Mixer

| Fall / Erwartung | Ausgeführter Test und Ergebnis | Status / Ebene | Beleg und Grenze |
|---|---|---|---|
| B01 Original wiedergeben | Nativ gestartet, Zeit läuft | Bestanden · N | N-live; keine akustische Qualitätsmessung |
| B02 vier Spuren | Instrumental gewählt, Gesang hinzugefügt; vier tatsächliche Quellabrufe und Vier-Spur-Export | Bestanden · N/H | N-live, N-export |
| B03 stummschalten | Gesang aus Mix entfernt; resultierender Export ohne Gesang geprüft | Bestanden · N/H | N-export; kein physischer Ausgangspegel gemessen |
| B04 Solo | Gesang solo, übrige Quellen abgewählt; Solo-WAV entspricht Spur | Bestanden · N/H | N-live, N-export |
| B05 Pegel | Übrige Instrumente auf 50 % gesetzt, Livezustand bleibt aktiv; Export numerisch geprüft | Bestanden · N/H | N-live, N-export |
| B06 mehrere Quellen | Instrumental und vollständiger Mix; unterschiedliche Gain-Konfigurationen | Bestanden · N/H | N-live, H-wave |
| B07 Seeking | Loopabschluss springt von 53,35 auf 11,25 s; fortlaufende Zeit danach | Teilweise · N | N-live/clock; kein eigener beliebiger Seek während jedes Mixzustands |
| B08 Pause/Resume | Pause bei 53,35 s, später Wiederaufnahme im gemeinsamen Loop | Bestanden · N | N-live/clock; keine Ausgangslatenzmessung |
| B09 gemeinsamer A/B-Loop | Zwei Rechtsklickpunkte, Markierungen und tatsächlicher Rücksprung | Bestanden · N | 32 Zeitstichproben einschließlich Rücksprung |
| B10 Original/Stem | Laufender Original→Instrumental-/Stem-Wechsel, später Originalrückkehr mit erhaltener Zeit/Loop | Bestanden · N | N-live/clock; Umschaltlücke akustisch nicht gemessen |
| B11 Songwechsel | Während Originalwiedergabe anderen Song geöffnet: neuer Titel, Zeit null, pausiert, Loop gelöscht | Bestanden · N | N-live; zusätzlich Wechsel aus pausiertem Live-Mix nach Neustart |
| B12 Studio/Analyse | Bei laufendem Stem-Mix zur Timeline gewechselt, Mix und Zeit laufen weiter | Bestanden · N | N-live/clock |
| B13 Player/Lyrics/Kurve | Aktive zeitgestempelte Zeile; 32 native Player-/Kurvenpaare, maximale Differenz 0,02330 s | Teilweise · N | N-live/clock; Anzeigevergleich, keine Messung der Stem-/DAC-Ausgabe |

Mehrfaches Umschalten von Solo, Instrumental, vier Quellen und Gain erzeugte
keinen sichtbaren alten Song oder Wiedergabefehler. Diese Beobachtung beweist
weder Lückenfreiheit noch Ausschluss doppelter Audioausgabe. AudioNode-Anzahlen,
Decoderdrift pro Spur und Loopback-Aufzeichnung wurden nicht erhoben.
Die vorhandenen LiveMix-Regressionen prüfen zusätzlich Eventablösung,
Context-/Node-Freigabe, langsame Quellen, Fehler, Timeout und schnelle Wiederaufnahme.

## C – WAV-Export

| Fall / Erwartung | Ausgeführter Test und Ergebnis | Status / Ebene | Beleg und Grenze |
|---|---|---|---|
| C01 alle Spuren | Vier-Spur-Mix nativ gespeichert; numerischer Vergleich mit Quellensumme exakt | Bestanden · N/H | N-export, H-wave |
| C02 eine Spur stumm | Gesang entfernt, Instrumentalmix nativ gespeichert | Bestanden · N/H | N-export; gleichzeitig anderer Pegel gesetzt |
| C03 Solo | Nativ gespeicherte Gesangsspur samplegleich und bytegleich zur Quelle | Bestanden · N/H | N-export |
| C04 unterschiedliche Gains | Nativ other=0,5, drums=bass=1; Sollvergleich exakt | Bestanden · N/H | N-export, H-wave |
| C05 mehrere aktive Spuren | Drei-/Vier-Spur-Export und zusätzlicher Zwei-Spur-Dienstvergleich | Bestanden · N/H | Zwei-Spur-Variante H, nicht zusätzlich nativ gespeichert |
| C06 vorhandenes Ziel | Vorhandene WAV beim Escape und später beim tatsächlichen Exportfehler bytegleich | Bestanden · N/H | D-integrity, N-restart/error |
| C07 Escape | Dialog mit vorhandenem Ziel per Escape geschlossen, kein neuer Export | Bestanden · N | N-export, Hash-/Bestandsvergleich nach Dialogschluss |
| C08 Cancel | Sichtbare Cancel-Schaltfläche bildgebunden betätigt, kein Export | Bestanden · N | N-export; keine numerischen Dialogklicks |
| C09 Name ändern/abbrechen | Eigenen vollständigen Zielnamen gesetzt und geprüft, dann Cancel | Bestanden · N | N-export, unveränderter Exportbestand |
| C10 Erfolg nach Abbruch | Solo und vollständiger Mix anschließend erfolgreich gespeichert | Bestanden · N/H | N-export, H-wave |
| C11 nach Neustart | Neuer App-/Dienstprozess; Solo erneut gespeichert, identischer SHA-256 | Bestanden · N/H | N-restart, H-wave |
| C12 Fehler | Neue absichtlich beschädigte synthetische Float-Spur mit NaN, native Auswahl vorhandenen Ziels und bestätigtes Überschreiben; HTTP-Fehler, verständliche Appmeldung, Ziel bytegleich | Bestanden · N/H/R | N-restart/error; prüft korrigierten Solo-Pfad, kein echter Datenträgerausfall |

Alle drei ersten nativen Demucs-Exporte: RIFF/WAVE mit korrekter Größenangabe,
IEEE Float32, Stereo, 44.100 Hz, 2.646.000 Frames, 60 s und 21.168.088 Bytes;
sämtliche Samples endlich. Der Neustartexport ist bytegleich zum Soloexport.
Maximale absolute Sampleabweichung gegen die jeweils gewählte Float32-Summe: 0.
Solo-, Vollmix- und gewichteter Instrumentalmix unterscheiden sich tatsächlich.
Das ist eine rechnerische Mixprüfung, keine musikalische Solltrennung.

Zusätzlich fünf tatsächliche Dienstvarianten: alle, Gesang stumm, Solo,
vier unterschiedliche Gains und zwei Quellen. Separat fünf kontrollierte
Vier-Spur-Sollvergleiche mit verfassten Stereo-Signalen: 48 kHz, 96.000 Frames,
zwei Sekunden, Float32, endlich, maximale Abweichung jeweils 0. Diese Dateien
sind deterministische Fixtures und ausdrücklich keine echte Trennung.

Abbruch betrifft den Speicherdialog vor HTTP-Abruf/Dateizugriff. Ein eigener
Cancel nach bestätigtem Transferstart existiert nicht und wurde nicht behauptet.

## D – kombinierter Desktop-Lebenszyklus

| Schritt / Erwartung | Ausgeführter Test und Ergebnis | Status / Ebene | Beleg und Grenze |
|---|---|---|---|
| D01 Audio importieren | 60-Sekunden-Quelle nativ ausgewählt und bestätigt | Bestanden · N | N-entry/import |
| D02 Bibliothek öffnen | Beide isolierten Tracks nativ geöffnet, nach Neustart erneut | Bestanden · N | N-live, N-restart |
| D03 Wiedergabe starten | Originalstart und Mix-Wiederaufnahme | Bestanden · N | N-live/clock |
| D04 Lyrics anzeigen | Verfasste Zeitzeilen, später tatsächlich lokal analysierte Zeilen wieder geöffnet | Bestanden · N/I | N-live, N-restart |
| D05 Seek/Loop | Gemeinsame Markierungen und Rücksprung gemessen | Teilweise · N | B07/B09; keine vollständige Seekkreuzmatrix |
| D06 lokale Analyse | Nativ ausgelöste echte Audio-/Textanalyse, 30 Audiosegmente und vier Lyricszeilen, 16,87 s | Bestanden · N/I | N-api/lifecycle; vorverfasste Music2Emo-Anzeigekurve davon getrennt |
| D07 Atmosphäre | Nativ eingeschaltet; bei Wiedergabe und Moduswechsel sichtbar | Bestanden · N | Keine neue umfassende Bewegungs-/Reduced-Motion-Abnahme |
| D08 Hörstudio | Nativ geöffnet, echte vier Gruppen | Bestanden · N/I | N-separation |
| D09 Stem-Mix | Mehrspur-, Solo-, Gain- und Loopablauf | Bestanden · N | N-live/clock |
| D10 Song/Modell | Trackwechsel, vier Gruppen und separates Sechsgruppen-Cachemodell | Bestanden · N | Keine zweite tatsächliche Demucs-Modellinferenz |
| D11 WAV | Solo, Vollmix, gewichtetes Instrumental und Neustartexport | Bestanden · N/H | N-export, H-wave |
| D12 Loopback-API | Routing vorbereitend über HTTP, Zustimmung und Analyse nativ; genau ein erfolgreicher Anbieteraufruf ohne Authheader | Bestanden · N/H | N-api; nur synthetisches Zwei-Sekunden-Audio, kein echter Cloudanbieter |
| D13 Widerruf | Nativ widerrufen; erneute native Analyse HTTP 422, null zusätzliche Anbieteraufrufe | Bestanden · N/H | N-api; vorheriger unbestätigter Klickversuch ebenfalls abgewiesen |
| D14 lokal zurück | Nativ lokaler Modus gewählt, lokale Anzeige wiederhergestellt | Bestanden · N | N-api |
| D15 App/Dienst neu | Eigene Prozesse beendet, Releasebuild erstellt, neue Prozesse und Fenster gebunden | Bestanden · N/H | N-restart, R-suites |
| D16 Daten wieder öffnen | Bibliothek, lokale Analyse/Lyrics, echter Stemcache und erneuter WAV-Export | Bestanden · N/H | N-restart, D-integrity; keine Wiederherstellung der zuletzt gewählten Mixregler behauptet |

Die kleine Zustimmungscheckbox ließ sich mit ersten Zeigeraktionen nicht
verlässlich bestätigen. Der Auftrag wurde deshalb ohne nachgewiesene Zustimmung
abgewiesen und erzeugte keinen Anbieteraufruf. Sichtbare Tastaturfokusfolge und
Leertaste ermöglichten die eindeutige Zustimmung; erst danach lief genau ein
synthetischer Kontrollauftrag. Nach dem Widerruf blieb der Zähler bei eins.
Kein automatischer Retry und kein Umgehen der Einwilligungssperre.

## E – kurze Ressourcenprobe

| Erwartung | Messung / Ergebnis | Status und Grenze |
|---|---|---|
| Speicher und Handles erfassen | Pausierter Mix: native Familie 701,81 MB RSS, 5735 Handles; laufender Loop 712,44 MB, 5753 Handles | Bestanden als Stichprobe; dezimale MB, summierte Familien-RSS zählt gemeinsame Seiten mehrfach |
| CPU erfassen | Je etwa drei Sekunden: native Familie pausiert 2,08 %, Live-Loop 47,39 % eines CPU-Kerns; Dienst 0,52 % beziehungsweise 0 % | Bestanden als Stichprobe; keine normierte Gesamtmaschinenlast oder Performancefreigabe |
| Kindprozesse prüfen | Native Familie jeweils acht Prozesse, Dienstfamilie drei; keine Inferenzworker in diesen Ruhe-/Playbackproben | Bestanden als Stichprobe; Prozessfamilien statt globaler Zählung |
| wiederholte Starts/Mixwechsel | Originalstart, Pause/Resume, Instrumental/Solo/vier Quellen/Gains/Original und Wiederöffnung nach Neustart tatsächlich bedient | Teilweise; kurze Funktionsfolge, kein Belastungsloop |
| Audio-Ressourcen | Freigabeverträge automatisiert geprüft; keine nativen AudioNode-/Decoderzähler erhoben | Offen für native Ressourcenmessung |
| langfristige Zunahme ausschließen | Weitere native RSS-Snapshots fallen nach dem ersten Laden wieder ab; neue Prozessfamilie am Ende 609,67 MB, 5634 Handles | Nicht nachgewiesen; Werte verschiedener Prozesslebensdauern sind kein Leakvergleich |
| eigener Prozessabschluss | Testhalter, App, Dienste, Anbieter beendet; Ports und Workerbereiche separat kontrolliert | Abschlussnachweis D-integrity; keine fremden Prozesse beendet |

Phase 3 behält die längere und wiederholbare Performance-/Leckprüfung.
Keine Langzeitstabilität, störungsfreie physische Audioausgabe oder garantierte
CPU-/Speicherobergrenze aus dieser kurzen Folge ableiten.

## Bestätigter Fehler und Korrektur

Der Solo-Schnellpfad gab eine vorhandene WAV ohne Sampleprüfung direkt zurück.
Ein Manifest mit gespeicherter `activity` überspringt die erneute Energieberechnung;
damit konnte eine Float-Spur mit NaN ungeprüft ausgeliefert werden. Der neue Test
reproduzierte dies vor der Korrektur: erwarteter ValueError blieb aus.

Der direkte Solo-Pfad prüft jetzt blockweise endliche Samples, bevor er die Datei
zurückgibt. NaN, positive und negative Unendlichkeit werden verworfen. Gültige
Dateien bleiben unverändert; bestehende Mehrspurprüfung und atomarer nativer
Zieldateischutz bleiben erhalten. Kein Refactoring, Schemawechsel oder neuer Adapter.
Zehn gezielte Separationstests bestanden; die native Fehlerprobe mit vorhandener
Zieldatei bestätigt den korrigierten HTTP-/Tauri-Pfad nach Dienstneustart.

## Regressionen, Builds und Datenabschluss

- Vollständige Backendregression nach Korrektur: **399 bestanden**, 38,48 s.
  Vorheriger unveränderter Gesamtlauf: 396 bestanden, 37,85 s.
- Frontend: **156 Tests in 29 Dateien bestanden**, 20,35 s; Frontendcode unverändert.
- Rust: **neun Tests locked/offline bestanden**; Node-Dialogdriver: **fünf bestanden**.
- TypeScript/Vite und Windows-Releasebuild ohne Bundle bestanden. Native
  Releasekompilierung 17,05 s; bekannte Vite-Chunkwarnung und Rust-Kopierfallback.
  Kein Installerlauf und kein neuer lokaler Linux-Build.

Produktive SQLite und Originaldateibestand sind gegen die Ausgangshashes unverändert.
Isolierte SQLite ist intakt; unbenutzte vorverfasste Fixturebesitzer wurden vor der
Neustartbaseline entfernt. Über den vollständigen Neustart sind sämtliche Track-,
Cache- und Besitzerzeilen sowie verwaltete Audio- und Stemhashes identisch.
Das vorhandene Exportziel bleibt sowohl bei Abbruch als auch beim Fehler bytegleich.
Abschließend beide SQLite `integrity_check=ok`, keine verwaisten Cachebesitzer,
keine eigenen temporären Workerbereiche oder temporären Mix-WAVs. Aufgezeichnete
eigene App-/Dienstprozesse beendet, synthetischer Anbieter beendet und beide
Testports frei. Das separate lokale Abschlussprotokoll bestätigt diese Prüfungen.
Rohbelege werden nicht veröffentlicht.

Offen bleiben insbesondere A11, der harte Demucs-Dienstfehlerpfad aus A12,
vollständige native Seeking-/Ausgabesynchronisations- und Audio-Ressourcenmessungen,
längere Wiederholungen, weitere DPI/Plattformen, Installer und Musikqualität.
Phase 2B bleibt unabhängig von diesen Fortschritten teilweise bestanden.

## Nachabnahme 2C.2 vom 20. November 2026

**Entscheidung: weiterhin teilweise bestanden; PR #14 bleibt Draft.**
Kein neuer Anwendungsfehler bestätigt und kein Anwendungscode geändert.
Die Erweiterung besteht aus gezielten Nachweisen und präzisierten Freigabegrenzen.
Rohbelege, Musikausschnitte, Identitäten und lokale Prüftreiber bleiben ignoriert.

### Git, Eingangstest und Prüfumfang

Ausgangsbranch `codex/phase2c-studio-regression`, sauber auf `c9d238c`.
Erneuter Remote-/Connectorabgleich: Main `1717ffd`, #11 `ff585f5` und #12
`5d459f0` offen; #13 Draft auf `b3e4b9c` gegen #12; #14 Draft auf `c9d238c`
gegen #13. Kein Main-Merge, Force-Push oder privater Vorfahr übernommen.
Der bisherige [CI-Lauf 44804376634](https://github.com/FutureKLP/MoodScope-public/actions/runs/44804376634)
ist abgeschlossen: beide Windows-/Ubuntu-Testjobs und beide Native-Buildjobs
erfolgreich. #14 hat keine Reviews und keine Reviewthreads. Das ersetzt kein Review.

Vor weiteren UI-Tests: eindeutiges Tauri-Hauptfenster anhand Prozess und Titel,
Win32-Geometrie und 96 DPI gelesen, separates 16×16-Tao-Hilfsfenster ausgeschlossen,
frische große Screenshotregion gebunden, Hörstudio-Reiter gewählt und sichtbarer
Wechsel bestätigt. Später meldete ein Scrollaufruf erneut 16×16-Grenzen.
Keine blinde Wiederholung: Fenster neu ausgewählt, große Region neu erfasst und
die sichtbare Scrollleiste bildgebunden bedient. Keine numerischen Indexklicks.
Der Werkzeugfehler bleibt ungepatcht; eine vollständige native Abnahme folgt daraus nicht.

Neue tatsächliche Musikprüfung ausschließlich mit quellbenannten lokalen
Zwölf- und Zehn-Sekunden-Ausschnitten aus dem erlaubten Testmusikbestand.
Originale und vorhandene Gewichte nur gelesen. Die native Bibliothek wurde über
HTTP vorbereitet; dies ist kein neuer nativer Importnachweis. Ein separat markierter
leerer Analysecache verhinderte automatische Hauptanalyse. Die automatisch gestartete
Music2Emo-Vergleichsinferenz ist davon getrennt tatsächlich lokal abgeschlossen.
Die Zwei-Sekunden-Exportfixture blieb separat und wurde hier nicht abgespielt.
Keine neuen Links, Modelldownloads, Cloudtransfers oder globalen Audioänderungen.

### Demucs-Fehler- und Crashmatrix

H/I bezeichnet tatsächliche isolierte Windows-Dienste und Offline-Inferenz;
R die separat erneut ausgeführten deterministischen Regressionen.
Der Prüfdienst sperrt Checkpointdownloads ausdrücklich. Fehlgewichtsfälle zeigen
auf eigene isolierte Modellwurzeln; produktive Gewichte werden nicht umbenannt.

| Fall | Ergebnis und Ebene | Grenze |
|---|---|---|
| Fehlende Gewichte | Fehler vor Inferenz, kein fertiger Stemcache · H/I | Lokale Downloadverweigerung des Prüfdiensts; kein nativer Fehlerdialog |
| Unlesbare Gewichte | Checkpointpfad als Verzeichnis erzeugt tatsächlichen Windows-PermissionError, kein Cache · H/I | Kein Eingriff in produktive ACLs |
| Beschädigte Gewichte | Tatsächliche Demucs-Prüfsumme verwirft eigene beschädigte Datei · H/I | Kein deserialisiertes Fremdmodell |
| Ungültiges Trennmodell | HTTP 422 vor Jobannahme · H | Native Auswahl bietet nur erlaubte Modelle |
| Abbruch vor Modellstart | Status cancelled bei Fortschritt 0, kein Ergebnis oder fertiger Cache · H | Separat von Abbruch während Inferenz |
| Abbruch während Berechnung | Echter CPU-Lauf nach Fortschritt 15 abgebrochen, cancelled ohne Cache · H/I | Kooperativ; Modellschritt kann auslaufen |
| Hartes Dienstende | Eigene Dienstfamilie während laufender Trennung beendet, nach Neustart weiterhin kein fertiger Cache · H/I | Start/Kill über Testhalter, kein neuer nativer Crashdialognachweis |
| Wiederherstellung und Neulauf | Neue Dienstfamilie, erneute tatsächliche Vier-Spur-Trennung erfolgreich in 8,26 s · H/I | Zwölf Sekunden Audio, vier Torch-CPU-Threads; keine allgemeine Performancebaseline |
| Vollständiger Cache | Nach weiterem Neustart cached=true, alle Dateien hashgleich · H | Zusätzlich nachfolgender Crashfall |
| Fertiger Cache neben laufender zweiter Trennung | Zweiten Ausschnitt getrennt, Dienst bei Fortschritt 15 hart beendet; erster Cache nach Neustart bereit und vollständig hashgleich, zweiter nicht bereit · H/I | Kein Überschreiben des ersten Caches |
| Unvollständige Ergebnisse | Beide Crashaufträge ohne fertiges Ergebnis; zusätzliche unvollständige-/beschädigte-Stemregressionen bestanden · H/I und R | Kein Nachweis eines Stromausfalls mitten im Dateisystemschreiben |

Demucs läuft im Dienstprozess mit `num_workers=0`; die erfasste Dienstfamilie
enthielt keinen Music2Emo-Inferenzworker. Music2Emo verwendet ausschließlich
seine separat markierten Arbeitsbereiche mit eigenen Sperren. Deren Prozess-/
Recoveryregressionen bestanden erneut. Im ausschließlich für diese Demucs-Dienste
umgeleiteten Tempbereich wurden vor/nach Crash und nach Abschluss keine Dateien
gefunden. Kein tatsächlich nachgewiesener Demucs-Restbesitzer und daher keine neue
Bereinigung implementiert. Die bereits vorgefundenen Modelldateien einschließlich
eines älteren partiellen Downloads blieben unverändert und wurden nicht gelöscht.

### Native Audiobedienung und WebView-Diagnostik

N bezeichnet bildgebundene Eingaben im Releaseclient. W bezeichnet lokale
WebView-Laufzeitdiagnostik im selben Client. Context-/Node-Zähler wurden nur im
isolierten WebView installiert, mit schwachen Contextreferenzen; der Releasecode
blieb unverändert. Diese Instrumentierung ist kein unveränderter Produktionslauf.

Nativ ausgeführt: echten lokalen Ausschnitt öffnen, vorhandene vier Gruppen wählen,
Drums solo, Wiedergabestart, A/B-Punkte, erneuter Start im Loop, Bass hinzufügen,
Bassgain 50 %, Seek im laufenden Mix, Pause/Resume, Live→Original und zurück,
Gesang solo, Hörstudio→Analyse→Bibliothek sowie Songwechsel aus laufendem Mix.
Danach vollständiger App-/Dienstneustart und gespeicherten Ausschnitt erneut geöffnet.
Keine vollständige kartesische oder längere Belastungsmatrix behauptet.

| Zustand | Gemessener Context-/Quellenzustand · W |
|---|---|
| Solo vor Start | Ein suspendierter Context, neun Nodes, vier pausierte Stem-Medienelemente |
| Laufender Solo-/Mehrspurmix | Derselbe laufende Context; Master stumm, vier laufende Stemquellen; Regler-/Seekwechsel erzeugen keinen weiteren Context |
| Pause | Context suspendiert, alle fünf Medienelemente pausiert |
| Originalrückkehr | Erster Context geschlossen, neun Nodes getrennt, keine Stem-Medienelemente, Master wieder hörbar geschaltet; AudioHandlers=0 |
| Zweiter Live-Zyklus / Ansichtswechsel | Zweiter Context läuft, erster gesammelt; weiterhin vier Stemquellen, kein zusätzlicher Context beim Ansichtswechsel |
| Songwechsel | Beide erzeugten Contexts geschlossen/gesammelt, alle 18 Nodes getrennt, keine Stemquellen; neuer Master pausiert bei null, Loop entfernt; AudioHandlers=0 |
| Vollständiger Neustart | Neues WebView ohne Instrumentierung oder alte Stemquellen, AudioHandlers=0, Master ohne Quelle bis zur erneuten Songwahl |

Dies erfasst Medienelemente und Chromium-Audiohandler, nicht unabhängige
Decoderinstanzen des Betriebssystems. Geschlossene Graphen sind nachgewiesen;
sofortige Rückgabe sämtlicher Heap-/Treiberallokationen ist daraus nicht ableitbar.

Vier Prozessstichproben von jeweils etwa drei Sekunden, dezimale MB und summierte
Familien-RSS (gemeinsame Seiten können mehrfach zählen); CPU in Prozent eines Kerns:

| Zustand | Native RSS / Handles / Prozesse / CPU | Dienst RSS / Handles / Prozesse / CPU |
|---|---|---|
| Erster Live-Loop | 663,47 MB / 5306 / 8 / 28,65 % | 690,74 MB / 618 / 3 / 0 % |
| Zweiter Live-Zyklus | 662,88 MB / 5325 / 8 / 32,29 % | 692,54 MB / 623 / 3 / 1,04 % |
| Nach Songwechsel, pausiert | 687,61 MB / 5301 / 8 / 1,56 % | 692,74 MB / 634 / 3 / 0 % |
| Neue Prozessfamilie nach Neustart | 582,78 MB / 5330 / 8 / 2,08 % | 687,91 MB / 630 / 3 / 0 % |

JS-Heapstichproben im ersten WebView: 2,61–7,25 MB. Globale Chromium-Listenerzähler
lagen zwischenzeitlich bei 2038 und nach Songwechsel bei 408. Eine ausdrücklich
separate erzwungene GC-Diagnose im pausierten Live-Mix reduzierte 1851/6,73 MB
auf 428/3,68 MB. Das unterscheidet noch nicht gesammelte von erhaltenen Objekten;
es ist keine automatische Freigabefrist oder Leckfreiheitsgarantie. Keine zusätzlichen
WorkerGlobalScopes in diesen WebView-Stichproben. Phase-3-Langzeitprüfung bleibt offen.

### Synchronisation und tatsächliche Ausgabegrenze

160 lesende Zeitstichproben während nativ gestarteter Wiedergabe, ungefähr alle
100 ms über 16 Sekunden: vier Looprücksprünge von etwa 7,83–7,88 auf 3,04–3,08 s.
Maximaler Player-/Master-Anzeigeunterschied 30,6 ms. Unter den vier Stem-Medienzeiten
maximal 0,155 ms Unterschied; zwischen Stem und Master bis 118,0 ms.
Der Master ist im Live-Modus der stille Transport. Diese Einzelserie erlaubt
keine samplegenaue Ausgabesynchronisations- oder allgemeine Driftaussage.
Die neue Serie enthält keine Lyrics und ersetzt die frühere Lyrics-/Kurvenabnahme nicht.

FFmpeg bietet hier DirectShow/OpenAL-Eingänge, aber keinen WASAPI-Loopbackeingang;
die geprüfte DirectShow-Aufzählung fand kein Audioaufnahmegerät. Kein verlässlich
konfigurierter virtueller Aufnahmeweg wurde nachgewiesen. Daher keine Aufnahme,
kein numerischer Impulsvergleich am tatsächlichen Ausgang und keine Behauptung
über Doppeloutput, Umschaltlücken, DAC-Latenz oder unterbrechungsfreies Hören.
Das gemessene Stummschalten des Masters ist ausschließlich ein Zustandsnachweis.
Keine Geräte installiert, global umkonfiguriert oder Mikrofonaufnahmen angefertigt.

### WAV, Regressionen und Abschluss

Neu bestanden: **399 Backendtests** (41,45 s), **156 Frontendtests** in 29 Dateien
(21,91 s), **neun Rusttests** locked/offline und **fünf Node-Dialogdrivertests**.
TypeScript/Vite und Windows-Releasebuild ohne Bundle bestanden; abschließende
Releasekompilierung 16,08 s. Vite-Chunkwarnung und Rust-Kopierfallback bleiben.
Ein erster Build konnte die laufende Test-EXE nicht ersetzen; nach eigenem
Prozessabschluss erfolgreich wiederholt. Der erste Sandbox-Vorbereitungslauf hing;
beendet, isolierte Vorbereitung mit lokalen Prozess-/Socketrechten erfolgreich.
Kein neuer Installer- oder Linux-Bedienlauf.

Die erneut ausgeführten Tests prüfen NaN und beide Unendlichkeiten im Solo-Pfad,
gültiges Solo, Mehrspur/Gains, ungültige/gekürzte Transfers, Dialogabbruch vor
Dateizugriff und Erhalt bestehender Ziele bei Fehlern. Native WAV-Dialog-/
Zielüberschreib-/Fehlerwiederholungsnachweise aus der Erstabnahme bleiben erhalten;
diese komplette native Dialogserie wurde nicht redundant wiederholt. Im neuen
nativen Lauf wurde kein WAV exportiert; das vorhandene Exportziel blieb bytegleich.
Der kompakte neue Ablauf ist eine ergänzende Ressourcen-/Neustartfolge und keine
neue vollständige D01–D16-Abnahme. Local/API-Schutzregressionen bestanden; kein
Cloudtransfer oder neuer Anbieterauftrag ausgeführt.

Verwendetes Original, produktive SQLite, vorhandene Modellgewichte und verwaltete
Testaudios unverändert. Drei isolierte SQLite-Datenbanken und produktive SQLite
intakt; keine verwaisten Cachebesitzer. Track-, Cache-, Besitzerzeilen, verwaltete
Audios und Stemhashes über den vollständigen nativen Neustart identisch.
Eigene Dienste/App/Worker beendet; Testports frei. Keine temporären Mix-WAVs
oder eigenen aktiven Workerbereiche. Keine unbekannten Verzeichnisse gelöscht.

### Ergänzende native Demucs-Fehlerfolge

Nach dem Dokumentationscheckpoint `e73fcd2` wurden die beiden verbliebenen nativen
Demucs-Fehlerdialoge gezielt nachgeprüft. Eigener weiterer Releaseclient, kopierte
isolierte Testbibliothek und downloadgesperrter Prüfdienst; bestehende vollständige
Stems und vorbereitete Anzeige-Caches separat erhalten. Erneuter Eingangstest mit
frischer Fenster-/Bildbindung, 96 DPI und sichtbarem Bibliothekswechsel bestanden.

1. **Bestanden · N/H/I:** Sechsgruppenmodell nativ gewählt und gestartet; der
   Testloader sucht in der eigenen leeren Modellwurzel. Tatsächlicher
   FileNotFoundError, sichtbare Meldung zur fehlgeschlagenen Quellentrennung mit
   Modell-/Speicher-/Installationshinweis und Fehler-ID. Kein Download und kein
   fertiger Sechsgruppen-Cache. Nach Freigabe der vorhandenen Gewichte erneuter
   nativer Start: echte Sechsgruppen-Trennung erfolgreich in 7,22 s.
2. **Fehlversuch, kein aktiver Crashnachweis:** Der zunächst geplante harte
   Dienstabbruch erfolgte erst nach diesem erfolgreichen Sechsgruppenauftrag.
   Er zählt ausschließlich als Dienstende nach Abschluss; Cache bleibt erhalten.
3. **Bestanden · N/H/I:** Nach Neustart vorhandenes Fine-tuned-Ensemble nativ
   gewählt und gestartet. Sichtbarer Trennfortschritt bei 15 %; unmittelbar vor
   hartem Ende bestätigt der Dienst nochmals status=running. Nur eigene
   Dienstfamilie beendet; Client blieb geöffnet. Sichtbare verständliche Meldung:
   Dienst nicht erreichbar, Dienststatus prüfen/erneut versuchen, gespeicherte
   Analysen bleiben erhalten. Kein fertiger Fine-tuned-Cache nach Neustart.
   Vollständige Vier-/Sechsgruppen-Caches vor/nach Crash hashgleich.
4. **Bestanden · N/H/I:** Ohne Appneustart erneut nativ getrennt. Tatsächlicher
   Fine-tuned-Neulauf erfolgreich in 26,02 s, cached=false; gespeicherte Spuren
   und verwendetes Modell sichtbar. Keine automatische Jobwiederholung.

Zwischenzeitlich lieferte die Automation nur die 16×16-Hilfsregion. Neue
Fensterauswahl plus Aktivierung stellte die große Region wieder her; keine
Eingaben aus den kleinen/veralteten Bildern. Die interne Werkzeugursache bleibt
offen. Unlesbare/beschädigte Gewichte wurden weiterhin auf H/I-Ebene geprüft,
nicht zusätzlich in jedem nativen Dialog und jeder Sprache.

Abschluss dieser Folge: ursprüngliche Track-/Cache-/Besitzerzeilen unverändert,
vorhandene vollständige Stems hashgleich; zusätzliche vollständige Sechsgruppen-
und Fine-tuned-Ausgaben ausschließlich lokal. Alle vier geprüften SQLite intakt,
keine verwaisten Besitzer. Original, Gewichte und produktive Daten unverändert,
eigene Prozesse beendet, Testports frei. Kein neuer Anwendungscode; die oben
genannten Regressionen/Builds prüfen denselben Quellstand. Keine erneute volle
Suite nach dieser rein nativen Zusatzfolge behauptet.

Geschlossen sind die gezielten H/I-Demucs-Fehler-/Crash-/Cacheerhaltfälle, die
native Fehlgewichts-/Dienstverlust-/Wiederholungsfolge und die oben abgegrenzten
N/W-Ressourcenstichproben. Offen bleiben die vollständige
wiederholte native Ressourcen-/Seeking-/Lyrics-Kreuzmatrix und tatsächliche
Audioausgabemessung. Weitere Plattform-/DPI-, Installer-, Langzeit- und
Qualitätsgrenzen gelten fort. **Keine vollständige Phase-2C- oder Kernfreigabe.**
