# Reproduzierbare Testbaseline

Fachlicher Überblick und datierte Nachweise. Aktueller Projekt- und Integrationsstatus:
[STATUS.md](STATUS.md); Navigation: [Dokumentationsübersicht](README.md).

Die automatisierte Prüfung ist von tatsächlichen Musik- und nativen
Bedienabnahmen getrennt. Tests nutzen deterministische, synthetische Fixtures.
Produktive Daten, Modelle, Musik, Lyrics und Prüfausgaben bleiben ausgeschlossen.

## Phase 2C am 20. November 2026

Nach bestätigter Solo-Exportkorrektur 399 Backendtests bestanden (38,48 s),
zehn gezielte Separationstests einschließlich NaN und beider Unendlichkeiten.
Vor der Korrektur reproduzierte der neue NaN-Test den Fehler zuverlässig.
Unverändertes Frontend: 156 Tests in 29 Dateien bestanden (20,35 s).
Neun Rusttests locked/offline, fünf Node-Dialogdrivertests, TypeScript/Vite und
Windows-Releasebuild ohne Bundle erfolgreich; Releasekompilierung 17,05 s.
Bekannte Chunkwarnung und Rust-Kopierfallback bleiben. Kein Installerlauf.

Die separate native Prüfung verwendet synthetische Quellen und echte vorhandene
Demucs-Gewichte: Start, Abbruch, erfolgreicher CPU-Neulauf, Mix/Loop, drei numerisch
geprüfte Exporte, Escape/Cancel, tatsächlicher Exportfehler und erneuter Export
nach vollständigem App-/Dienstneustart. Fünf tatsächliche Dienstmixvarianten und
fünf getrennte kontrollierte Vier-Spur-Sollvergleiche bestanden. Letztere sind
deterministische Fixtures, keine Demucs- oder Musikqualitätsabnahme.
Ressourcenstichproben und Anzeigezeitvergleich ersetzen keine Audioausgangs-/
Langzeit-Leckprüfung. [Vollständiger Nachweis](PHASE2C-ACCEPTANCE.md).

## Befehle

In der eingerichteten Projektumgebung:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:CUDA_VISIBLE_DEVICES = ''
$env:MOODSCOPE_DATA = "$PWD/.tools/verification/data"
python -m pytest tests -q --basetemp=.tools/verification/temp --tb=short
npm test
npm run build
cargo test --locked --offline --manifest-path src-tauri/Cargo.toml
npm run tauri build -- --no-bundle
```

Den ignorierten Elternordner zuvor anlegen und für jeden Lauf einen eigenen
kurzen Testbereich verwenden. Pytest leert seinen Basistestordner; niemals
produktive Daten oder vorhandene Ergebnisse als `--basetemp` verwenden.
Lokale Testsockets und die plattformspezifischen Tauri-Buildwerkzeuge werden
benötigt. Node 22.16.0 ist die hier verwendete Version. Ein Windows/CUDA-
Paketsnapshot ist kein universeller Plattformlock. Offline-Rust benötigt
bereits vorhandene Pakete. Native Kompilierung ist keine Bedienabnahme.

## Phase 2A.2: native Importnachprüfung, Abschluss am 18. November 2026

Am 17. November neu bestanden: 378 Backendtests (34,82 s), 146 Frontendtests in
28 Dateien (26,39 s), neun Rusttests offline mit Lockfile, fünf Node-Drivertests,
TypeScript/Vite und Windows-Releasebuild ohne Bundle. Vier neue Frontendtests
prüfen native Importentscheidung, Cancel, LRC und Fehler; drei neue Rusttests
prüfen die Abbruchgrenze, begrenztes Lesen und sichere Multipart-Dateinamen.
Zwei zusätzliche Drivertests sichern die Parentbindung, doppelt dargestellte
Baumknoten sowie Ablehnung fremder/mehrdeutiger Modale und indizierter Import-Edits.
Die vorhandenen echten SQLite-Integrationsregressionen für Reparatur, Wiederimport
und Datenerhalt bleiben erfolgreich. Ein lokaler Skriptaufruf benötigte den
Projektpfad im PYTHONPATH; nach Korrektur bestanden die Fallvergleiche.

Die Desktopmatrix schließt alle vier zuvor blockierten nativen Importfälle und
beide Abbruchpfade, lokale Verarbeitung tatsächlich importierter LRC sowie
App-/Dienstneustart ein. SQLite-Zeilen-/Audiohashvergleich gleich, Originalbestand
und produktive SQLite unverändert. Native Desktopnachweise sind von Tests und
vorbereiteten Anzeige-Fixtures getrennt. [Abnahme](PHASE2A-ACCEPTANCE.md).

Bekannte Vite-Chunkwarnung bei 503,34 kB bleibt; kein Installer-, anderer DPI-,
Langzeit- oder Plattformlauf. Der am 18. November eingelesene Main `1717ffd` hat
denselben Quellbaum wie der geprüfte Phase-1-Head; seine lokale Integration
ändert den getesteten Anwendungscode nicht. Kein erneuter CI-Lauf dieser lokalen
Phase behauptet. Die folgenden Abschnitte sind historische Prüfstände.

## Phase 2A am 17. November 2026

Vollständig erneut bestanden: 378 Backendtests (40,98 s), 142 Frontendtests in
27 Dateien (17,06 s), drei separate Node-Drivertests, TypeScript/Vite und nativer
Windows-Releasebuild ohne Bundle. Sechs neue Frontendregressionen betreffen
Wiederimport, LRC-Editorübernahme und Wiedergabefehler; drei neue Backendtests
sichern den Testhalter einschließlich echter SQLite-Zeilenvergleiche.
Ein erster Snapshot-Test scheiterte an Tupel-/JSON-Listenvergleich; korrigiert.
Die echte Desktopprüfung deckte anschließend einen falschen Spaltennamen im
neuen Testhalter auf; korrigiert und Test auf echtes Anwendungsschema umgestellt.
Erste neue Frontendtests benötigten die DOM-Umgebung und eine vorhandene
Assertionform; der oben genannte finale Gesamtlauf besteht.

Windows-Neubau erfolgreich, bestehende Chunkwarnung bei 502,18 kB. Kein erneuter
separater Rusttest, Installer- oder anderer Plattformlauf. Die synthetische native
Teilabnahme und ihre verbleibenden Importblocker sind getrennt in
[PHASE2A-ACCEPTANCE.md](PHASE2A-ACCEPTANCE.md) dokumentiert.

## Gezielte Windows-Exportphase am 17. November 2026

Neu ausgeführt: vollständige vorhandene Backendsuite mit 371 Tests (35,77 s),
136 Frontendtests in 26 Dateien (17,21 s), sechs Rusttests offline mit Lockfile
und Windows-Releasebuild einschließlich TypeScript/Vite. Danach vier neue
Schutztests für den Desktop-Testhalter gezielt bestanden (0,16 s) und drei
separate Node-Tests des Dialogdrivers bestanden. Keine zweite vollständige
Backendsuite nach Ergänzung der vier Testhaltertests behauptet.

```powershell
node --test tests/windows_dialog_driver.test.mjs
python -m pytest tests/test_windows_desktop_testing.py -q
```

Rust-Cancel-Gate und Frontend-IPC-Verträge werden getrennt vom echten
Windows-Dialog geprüft. Der native Lauf deckte die synthetische A-J-Matrix
bei 96 DPI ab, einschließlich Dateinamenabbruch, vorhandener Zieldatei,
bestätigtem Export, Wiederholungen und Neustart. Andere DPI-Stufen wurden
nicht ausgeführt. Fehlgeschlagene Accessibility-Klicks wurden als
Automationsfehler erhalten und nicht als Cancel-Erfolge gezählt.
[Reproduzierbares Verfahren und Grenzen](WINDOWS-DESKTOP-TESTING.md).

Produktive SQLite während der nativen Phase bytegleich, synthetische Quelle
unverändert, isolierte SQLite-Integrität ok. Die Testhaltervorbereitung und
Backendsuite benötigten für lokale Testsockets eine Ausführung außerhalb der
Sandbox; der hängende erste Vorbereitungslauf wurde beendet. Bekannte
Vite-Chunkwarnung und Rust-Hardlink-Kopierfallback bleiben bestehen. Kein
erneuter NSIS-Build, Installerlauf oder anderer Plattformtest in dieser Phase.

## Wiederholungsprüfung am 16. November 2026

Auf dem öffentlichen Entwicklungsstand mit begrenzter LRC-/Katalogbereinigung
erneut bestanden: 371 Backendtests (35,37 s), 133 Frontendtests in 25 Dateien
(20,08 s), vier Rusttests offline mit Lockfile sowie TypeScript/Webbuild.
Der Backendlauf erfasste 74 strikt isolierte SQLite-Ziele; die produktive
SQLite blieb bytegleich. Ein erster Sandboxlauf hing ohne Fortschritt und wurde
abgebrochen; die isolierte Wiederholung außerhalb bestand.

Die Windows-Releasekompilierung mit eingebetteter Oberfläche bestand über
`npm run tauri build -- --no-bundle` mit offline geschaltetem Cargo.
Die Vite-Größenwarnung bei 501,48 kB und der Rust-Hardlink-Kopierfallback
bleiben bestehen. Zusätzlich bestand der Windows-NSIS-Paketbuild über
`npm run tauri build -- --bundles nsis --ci`. Der erste Paketversuch scheiterte
am Netzwerkzugriff auf das fehlende NSIS-Werkzeug; die Wiederholung mit Zugriff
auf die offiziellen Werkzeuge und deren Tauri-Hashprüfung bestand. Der Installer
wurde nicht ausgeführt oder veröffentlicht. Keine Installations-/Deinstallations-
oder andere Zielplattformabnahme daraus ableiten.
Der englische Katalog enthält 990 Einträge; die zusätzliche Quelltextprüfung
fand keine fehlende deutsche Zeichenkette unter den erfassten Übersetzungsaufrufen.

Unit-/Vertragstests verwenden deterministische Fixtures und teilweise Mocks.
SQLite-Transaktions- und Prozessabbruchtests verwenden echte lokale SQLite.
Das sind keine Emulator- oder Liveprüfungen externer Datenbanken. MariaDB-,
Supabase- und Firestore-Adapter sowie Migration/Rückmigration fehlen weiterhin;
dafür gibt es weder bestandene Mock-, Emulator- noch Live-Abnahmen.

Native Bedienung und tatsächliche lokale Modellläufe werden getrennt in
[CORE-ACCEPTANCE.md](CORE-ACCEPTANCE.md) eingeordnet. Die folgenden Werte
beschreiben den früheren Kandidatenstand.

## Frühere Kandidatenprüfung

Am 15. November 2026 auf der kuratierten öffentlichen Quellkopie bestanden:

- 360 Backendtests (erneuter Lauf nach CI-Anpassung: 31,50 s), 74 strikt isolierte SQLite-Ziele; produktive
  SQLite während des isolierten Laufs bytegleich.
- 133 Frontendtests in 25 Dateien unter Node 22.16.0 (18,72 s).
- TypeScript und Vite-Produktionsbuild: 62 Module, 0,869 s. Bestehende
  Größenwarnung bei 501,48 kB JavaScript, kein Buildfehler.
- Vier Rusttests mit Lockfile offline; separater Testbuild 1 Minute 2 Sekunden.
- Separate Windows-Releasekompilierung offline mit eingebetteter Oberfläche
  (`cargo build --release --locked --offline --features tauri/custom-protocol
  --manifest-path src-tauri/Cargo.toml`), 1 Minute 32 Sekunden; kein Installer.

Ein Fresh-Checkout-Fehler des Benchmark-Sicherheitstests wurde vor dem finalen
Gesamtlauf korrigiert: Der Test legt seinen ignorierten Elternordner selbst an
und verlangt den tatsächlichen FileExistsError bei vorhandener Ausgabe.
Anwendungsquellen und Abhängigkeiten wurden für diese Testkorrektur nicht geändert.

Keine neue tatsächliche Musikprüfung, Modellinferenz, native Bedienabnahme,
Installer-, Linux-, Windows-10- oder vollständige Advisoryprüfung in diesem Lauf.
Ein erfolgreicher entfernter CI-Lauf wird nicht behauptet. Abnahmegrenzen bleiben
in [CORE-ACCEPTANCE.md](CORE-ACCEPTANCE.md) erhalten.
## Phase 2B am 18. November 2026

381 Backendtests (36,21 s), 146 Frontendtests in 28 Dateien (17,15 s),
neun Rusttests locked/offline und fünf Node-Drivertests bestanden. TypeScript/Vite
und Windows-Releasebuild ohne Bundle erfolgreich; bekannte Chunkwarnung bleibt.
Die erste Buildwiederholung traf eine noch laufende EXE; nach Beendigung erfolgreich.
Aktuelle Python-3.13-Projektumgebung verwenden: der ältere Python-3.10-Testhalterlauf
scheiterte an sechs `hashlib.file_digest`-Aufrufen, die Wiederholung bestand.

Neue Regressionen prüfen fehlende CLAP-Prozessor-/Gewichtsdateien ohne halbe
Engineaktivierung und ausdrücklichen CPU-Modus des Desktop-Testhalters.
Tatsächliche Offline-Inferenz, kontrollierte lokale API-Fehler, Dienstabbruch,
Neustart und native Bedienung sind getrennt in [Phase 2B](PHASE2B-ACCEPTANCE.md)
ausgewiesen. Die native Gesamtmatrix bleibt teilweise offen; keine vollständige
Kernfreigabe. Keine neuen echten Anbieter-, Installer- oder anderen Plattformtests.

## Phase 2B.3 am 20. November 2026

396 Backendtests bestanden (57,40 s), finale vollständige Frontendsuite mit 156 Tests
(18,14 s), einschließlich englischer Checkbox und lokaler Analyse bei ungültigem
Anbieterstatus. Der vorherige vollständige 154-Fälle-Lauf und der zusätzliche
39-Fälle-App-Lauf sind als Zwischenprüfungen erhalten. Neun Rusttests locked/offline, fünf Node-Dialogdrivertests,
TypeScript/Vite und native Windows-Releasekompilierung ohne Bundle erfolgreich.
Bekannte Chunkwarnung bleibt; kein Installer-/Plattformtest.

Neue Regressionen: normale und unterbrochene Workerlebensdauer, echter Prozesskill,
aktive Workersperre, FastAPI-Startup-Recovery, ungültige Besitzmarker und verlinkte
Dateien; sichtbare Zustimmung nach Sitzungs-/Routing-/Verbindungswechsel, erneute
Versionsprüfung vor Transfer sowie Dienstinstanzheader und Listenerbereinigung.
Keine Modellinferenz in diesen deterministischen Regressionen.

Der erste Backend-Gesamtlauf hatte 391 Erfolge und einen Langpfadfehler aufgrund
des zu langen Testhalter-Tempverzeichnisses. Wiederholung mit kurzem isoliertem
`--basetemp` bestand; abschließender Lauf nach ergänzten Regressionen wie oben.
Die Prozessregressionen benötigen lokale Prozess-/Socketrechte; ein anfänglicher
Sandboxlauf blieb ohne Fortschritt. Fehlerhafte erste Windows-Fixtures und die
korrigierte Prozesszuordnung des realen Testhalters bleiben als Fehlversuche erhalten.

Echter Music2Emo-Crash-/Neustartlauf und Loopback-API-Prüfung bestanden getrennt
von den Regressionen. Native App gestartet und sichtbar; Bedienfolge wegen
Testwerkzeug-Geometriefehler unvollständig. Exakte Einordnung, Datenabschluss und
offene Kriterien: [Phase 2B.3](PHASE2B-ACCEPTANCE.md#nachabnahme-2b3-vom-20-november-2026).
