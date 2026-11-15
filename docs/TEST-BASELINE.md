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

## Kandidatenprüfung

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
