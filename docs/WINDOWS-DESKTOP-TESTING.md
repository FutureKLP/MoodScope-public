# Native Windows-Exportprüfung

Fachlicher Überblick und datierte Nachweise. Aktueller Projekt- und Integrationsstatus:
[STATUS.md](STATUS.md); Navigation: [Dokumentationsübersicht](README.md).

## Voraussetzungen und Abgrenzung

Interaktive, entsperrte Windows-Sitzung, WebView2, eingerichtete Python- und
Node-Umgebung sowie Tauri/MSVC-Buildwerkzeuge. Die native Eingabe verwendet
Computer Use mit `@oai/sky` im vorhandenen JavaScript-Runtime. Kein zusätzliches
Windows-Testframework wird installiert. Ein CI-Build ist keine Desktopabnahme.
Der JS-Driver ist ein beaufsichtigter Ablauf mit getrennten Beobachtungs- und
Eingabeschritten; er ist kein unbeaufsichtigter CLI-End-to-End-Test.

Diese Prüfung verwendet ausschließlich einen erzeugten Stereo-Sinuston
(440 Hz, 48 kHz, PCM16, zwei Sekunden). Eine absichtlich verfasste Cache-Spur
ermöglicht den Export ohne Demucs. Markierte synthetische Analysecaches verhindern
automatische Inferenz beim Öffnen. Das sind Exportfixtures, keine Musik-, Modell-,
Trennqualitäts- oder Wiedergabeabnahme. Originalmusik wird nicht geladen.

## Build und isolierter Start

In der eingerichteten Projektumgebung, mit deren Python und Node im PATH:

```powershell
npm test
node --test tests/windows_dialog_driver.test.mjs
npm run tauri build -- --no-bundle
python -m scripts.windows_desktop_testing prepare
```

`prepare` gibt einen neuen absoluten Arbeitsordner unter `.tools/desktop-*` aus.
Diesen Wert als `$area` übernehmen; vorhandene Ordner werden nicht geleert.

```powershell
$area = '<ausgegebener Arbeitsordner>'
python -m scripts.windows_desktop_testing snapshot --area $area --label before
python -m scripts.windows_desktop_testing run --area $area
```

Der Standardbuild liegt in `src-tauri/target/v03/release/moodscope.exe`.
Bei einem anderen Cargo-Ziel `--binary` mit dem tatsächlich gebauten
Projektbinary angeben. `run` verweigert einen bereits belegten Port 8765,
startet einen eigenen Loopback-Dienst und prüft die isolierte Track-ID vor
Appstart. `MOODSCOPE_DATA` und `WEBVIEW2_USER_DATA_FOLDER` zeigen auf eigene
Unterordner. Anbieterprofile und Zustimmung der produktiven Bibliothek werden
nicht übernommen. Modell-Hub-Zugriffe sind offline geschaltet.

Die Test-App über Alt+F4 schließen; der Halter beendet seine eigenen Prozesse.
Alternativ in einer zweiten Shell eine leere Datei `$area/stop` anlegen.
Für einen weiteren Appstart denselben `run`-Befehl verwenden. Ein Restart-Marker
`$area/restart` startet nur den nativen Testprozess neu; er testet nicht den
produktiven verwalteten Dienstneustart.

## Fenster, DPI und Eingaben

Das Hauptfenster anhand der konkreten ausführbaren Datei und des exakten Titels
`MoodScope 0.3` auswählen. Mehrdeutige Treffer blockieren Eingaben. Der echte
Speicherdialog ist ein separates Fenster desselben Prozesses mit Titel
`WAV exportieren` beziehungsweise `Export WAV` und Windows-Klasse `#32770`.
Hilfs-, IME-, Tooltip- und WebView-Fenster sind keine Dateidialoge.
Der erfasste Dateidialog hatte keinen Win32-Owner; ihn deshalb nicht ausschließlich
über die Owner-Beziehung zum Hauptfenster suchen. Die App deaktiviert ihre
Exportaktionen während des Aufrufs. Die zusätzliche Überschreibbestätigung
erscheint als eigener modaler Teil im Accessibility-Baum und als weitere Bildregion.

```powershell
python -m scripts.windows_desktop_testing geometry --area $area
```

Die ausschließlich lesende Win32-Diagnose erfasst Handles, Titel, Klassen,
Owner, Sichtbarkeit, Minimierung, Vordergrund, Fenster-/Clientrechtecke und DPI.
Rohdaten bleiben ignoriert lokal. Bei 100 % Skalierung wurden 96 DPI gemessen.
Andere Skalierungen und Mehrmonitorwechsel sind nicht abgenommen; keine
Koordinaten zwischen verschiedenen DPI-Konfigurationen übernehmen.

Am 17. November 2026 war ein sichtbares, titelloses `Tao Thread Event Target`
mit Fensterrechteck `[0,0,16,16]` und leerem Clientbereich nachweisbar. Gleichzeitig
hatte das echte Tauri-Fenster einen Clientbereich von 1440 × 980. Computer Use
lieferte zeitweise das Hilfsfenster als erste Screenshotregion und die echte
Oberfläche als weitere Region. Ein minimiertes Hauptfenster hatte dagegen
negative Windows-Parkkoordinaten. Die 16 × 16 waren somit keine tatsächliche
Verkleinerung der App und bei diesem Lauf kein DPI-Skalierungsfehler.

Zusätzlich aktivierte `click(element_index)` im Dateidialog wiederholt Speichern,
obwohl der aktuelle Baum den Index als `Cancel`, ID `2`, bezeichnete. Bei einer
vorhandenen Fixture wurde dadurch `Confirm Save As` geöffnet. Die Bestätigung
wurde verworfen; die Datei blieb erhalten. Das belegt einen falschen
Automations-Eingabeweg. Die interne Ursache der Indexzuordnung im Werkzeug ist
nicht untersucht. Kein Anwendungsfehler aus diesen Versuchen ableiten.

Darum im Dateidialog keine numerischen Accessibility-Klicks verwenden. Das
Dateinamensfeld wird über das beobachtete Edit mit ID `1001` gesetzt und danach
im Baum geprüft. Cancel/Save werden anhand des frischen Dialogbilds mit dessen
`screenshotId` aktiviert. Niemals pauschal `screenshots[0]` auswählen. Kleine
Hilfsregionen verwerfen; bei zusätzlichen Modalen die richtige Region prüfen.
Nach Fokus-, Größen-, Scroll- oder Dialogwechsel neu beobachten. Keine
Eingabe nach unbekanntem Ausgang blind wiederholen. Bei fehlender Geometrie
Fensterbindung erneuern und gegebenenfalls das Hauptfenster wiederherstellen.

## Beaufsichtigter Automationsdriver

`scripts/windows_dialog_driver.mjs` exportiert `createDesktopDriver` ohne neue
Abhängigkeiten. Im Computer-Use-JavaScript-Runtime zuerst `@oai/sky` initialisieren,
mit `list_windows()` die konkrete App auswählen und dann das lokale Modul laden:

```javascript
var {sky} = await import('@oai/sky');
var {pathToFileURL} = await import('node:url');
var {createDesktopDriver} = await import(pathToFileURL(
  nodeRepl.cwd + '/scripts/windows_dialog_driver.mjs').href);
// appId stammt aus dem eindeutig ausgewählten list_windows()-Treffer.
// exportDirectory ist der absolute exports-Unterordner des neuen Arbeitsbereichs.
var driver = createDesktopDriver(sky, {app: appId, exportDirectory});
var observation = await driver.observe('dialog');
nodeRepl.write(observation);
```

Bild und Baum prüfen und die Zelle beenden. Erst in der folgenden Zelle eine
einzelne Aktion ausführen. Beispiele für jeweils eigenständige Schritte:

```javascript
observation = await driver.setFilename({token: observation.token,
  path: exportDirectory + '/filename-cancel.wav'});
// Nach erneuter Bildprüfung: die tatsächlich sichtbare Cancel-Position angeben.
observation = await driver.clickAt({token: observation.token,
  screenshotId: selectedScreenshotId, x: observedCancelX, y: observedCancelY,
  next: 'main'});
// In einem neu geöffneten, beobachteten Dialog alternativ:
observation = await driver.escape({token: observation.token});
```

Positionen werden aus dem jeweiligen Bild gewählt, nicht als globale
Bildschirmkoordinaten gespeichert. Die verwendete Dialogregion war im Prüflauf
946 × 533; dies ist keine übertragbare Layoutgarantie. Der Driver verwirft alte
Tokens, Hilfsgeometrie, Pfade außerhalb des Exportordners und automatische
Wiederholungen fehlgeschlagener Eingaben. Er wartet begrenzt auf Fensterzustände
und auf Dialogschluss, statt feste lange Wartezeiten einzusetzen.

## Prüffälle und Nachweise

Vor jeder Cancel-Serie einen Hashsnapshot erfassen. Alle Dateinamen vor Eingaben
auf den isolierten Exportordner setzen, auch wenn Windows einen anderen letzten
Ordner vorschlägt. Nach dem Test Dialogschluss, wieder bedienbare App und
ausbleibende Erfolgsmeldung prüfen; anschließend:

```powershell
python -m scripts.windows_desktop_testing snapshot --area $area --label after --baseline before
python -m scripts.windows_desktop_testing validate --area $area --filename confirmed.wav
```

Der Snapshot vergleicht vollständigen Dateibestand und SHA-256-Hashes im
Exportordner, Quelle und produktive SQLite-Dateien, prüft die isolierte
SQLite-Integrität und erfasst eigene Prozessfamilien, RSS und Handles.
`validate` verlangt für diese Fixture gültiges RIFF/WAVE samt Größenfeld,
Stereo/48 kHz/96.000 Frames, endliche Werte, 440-Hz-Hauptkomponente und denselben
Quellhash. Fehlernachweise werden vor einer fehlgeschlagenen Assertion gesichert.
Ein Snapshot vor bestätigtem Dialogschluss reicht nicht als Abbruchnachweis.

Am 17. November 2026 mit Releasebuild 0.3 und Windows 11 Build 26200 geprüft:

- A/B: Öffnen und Escape-Abbruch bestanden, keine Erfolgsmeldung oder Datei.
- C: Cancel-Schaltfläche über bildgebundene Eingabe bestanden. Vorherige
  Accessibility-Indexklicks fehlgeschlagen; sie betätigten den Speicherweg.
- D: Eindeutigen Dateinamen setzen, danach bildgebunden abbrechen bestanden;
  zusätzlich mit dem gespeicherten Driver am echten Dialog wiederholt.
- E: Vorhandene synthetische WAV nach Abbruch bytegleich. Auch das Verwerfen
  einer durch den falschen Eingabeweg ausgelösten Überschreibbestätigung geprüft.
- F/H: Bestätigter Export nach vorherigem Abbruch bestanden und technisch
  validiert: 384.044 Bytes, zwei Sekunden, bytegleich zur Quelle.
- G: Drei zusätzliche Abbrüche in Folge (Escape, Schaltfläche, Escape) bestanden.
  Kein neuer Export, keine hängenden Dialoge, sieben native Kindprozesse vorher
  und nachher. Prozessfamilien-RSS etwa 596,69 zu 596,65 MB; Handles 5691 zu 5708.
  Das ist eine kurze Ressourcenprobe, kein Langzeit-Leaknachweis.
- I: App und eigener Dienst beendet und neu gestartet; erneuter Export gültig
  und bytegleich. Neue Prozess- und Fensterhandles bestätigt, SQLite intakt.
- J: Normale/maximierte Darstellung, separate Modale, Fokus, Minimieren und
  Wiederherstellen bei 96 DPI geprüft. Andere DPI-Stufen nicht ausgeführt.

Die fehlerhaften Indexklick-Versuche erzeugten zwei synthetische WAVs. Eine lag
zunächst außerhalb des Exportordners im gemerkten Windows-Dialogordner; sie wurde
nach Hashprüfung in den ignorierten Diagnosebereich verschoben. Die andere blieb
als Fehlversuchsartefakt erhalten. Beide Versuche werden ausdrücklich nicht als
bestandene Abbrüche gezählt. Korrigierte Abbrüche erzeugten keine weiteren Dateien.

## Grenzen und Testebenen

Rust prüft den echten Abbruch-Gate vor Download/Dateizugriff. Frontendtests prüfen
IPC-Argumente und Cancel-/Fehlerweitergabe mit gemocktem Invoke. Die drei
Driver-Schutztests verwenden ein Werkzeugdouble; die vier Python-Schutztests
prüfen Pfad-/Hash-/SQLite-Nachweise. Diese Tests ersetzen keine native Bedienung.
Der echte Windows-Lauf verwendete den gebauten Client, reale Tauri-IPC, den
nativen Dialog, den isolierten FastAPI-Dienst und tatsächliche WAV-Dateien.

Cancel vor Dateiauswahl bedeutet: kein HTTP-Mixabruf und kein Exportstart.
Erst bestätigte Auswahl führt zur HTTP-Anfrage, vollständigen WAV-Prüfung,
temporären Zieldatei und atomaren Ersetzung. Ein Abbruch nach bestätigtem Start
ist ein anderer Fall; ein eigener laufender Export-Cancel wird nicht behauptet.

Keine neue NSIS-/Installations-, Linux-, Windows-10-, Langzeit-, Musikqualitäts-
oder vollständige Kernabnahme. Keine neue Anbieter- oder Datenbankphase.
Rohlogs und Screenshots können lokale Pfade enthalten und bleiben ausschließlich
im ignorierten Arbeitsbereich. Nur bereinigte Nachweise veröffentlichen.
