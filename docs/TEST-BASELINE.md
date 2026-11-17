# Reproduzierbare Testbaseline

Die automatisierte Prüfung ist von tatsächlichen Musik- und nativen
Bedienabnahmen getrennt. Tests nutzen deterministische, synthetische Fixtures.
Produktive Daten, Modelle, Musik, Lyrics und Prüfausgaben bleiben ausgeschlossen.

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
