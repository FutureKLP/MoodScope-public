# Mitwirkung an MoodScope

## Einstieg und Entwicklungsumgebung

Zuerst [Status und nächste Phase](STATUS.md), [Dokumentationsübersicht](README.md)
und [verbindlichen Veröffentlichungsablauf](PUBLISHING.md) lesen.
[Setup](SETUP.md) und [Umgebung](ENVIRONMENT.md) beschreiben die Voraussetzungen.
Lokale, ignorierte Anweisungen und Übergaben zusätzlich beachten und nicht veröffentlichen.

## Projektstruktur

- `src/`: React/TypeScript-Oberfläche, Audiozustand und benachbarte Vitest-Dateien.
- `backend/`: FastAPI, Analysen, Anbieter, Persistenz und Sprachkataloge.
- `src-tauri/`: Rust-Desktopintegration, Konfiguration und native Unit-Tests.
- `tests/`: Pythonregressionen und separate Node-Tests des Windows-Dialogdrivers.
- `scripts/`: Setup, Start, Prüfungen und Evaluationswerkzeuge.
- `.github/workflows/checks.yml`: unabhängige Windows-/Ubuntu-Test- und Native-Buildjobs.
- `docs/`: Fachwissen und datierte Nachweise; `STATUS.md` ist die aktuelle Statusquelle.

Frontendentwicklung: `npm run dev`. Backend separat in der validierten Projektumgebung:

```powershell
.venv-modern\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765
```

Dieser direkte Uvicorn-Aufruf bietet keine Dienst-Neustart-/Beendensteuerung;
dafür den [Projektstarter](SETUP.md) verwenden. `VITE_API_URL` wählt einen
getrennten Testdienst, `MOODSCOPE_DATA` einen isolierten Datenordner.

## Tests und Abnahme

Verbindliche Reproduktion, Isolation und Warnungen: [Testbaseline](TEST-BASELINE.md).
Die wesentlichen Befehle in der eingerichteten und isolierten Testumgebung sind:

```text
python -m pytest tests -q
npm test
node --test tests/windows_dialog_driver.test.mjs
npm run build
cargo test --locked --manifest-path src-tauri/Cargo.toml
npm run tauri build -- --no-bundle
```

Nur für die Änderung relevante Prüfungen ausführen und tatsächlich ausgeführte
Befehle/Ergebnisse dokumentieren. Bei reinen Dokumentationsänderungen Links,
Diff und Publikationssicherheit prüfen. Unit-Tests, Builds, native Bedienung,
tatsächliche Musiktests und Modellqualität sind getrennte Nachweise.
[Kernabnahmekriterien](CORE-ACCEPTANCE.md) bleiben maßgeblich.

## Branches, Pull Requests und Veröffentlichung

Es gelten ausschließlich die Git-Regeln aus [PUBLISHING.md](PUBLISHING.md):
öffentliche Abstammung, Veröffentlichungsbranch `codex/public-release`, geprüfte
PRs und Pflichtchecks für Main. Keine private Archivhistorie übernehmen,
Branches löschen, Historie umschreiben oder Branchschutz umgehen.
Funktionsänderungen und Dokumentationsorganisation nachvollziehbar trennen.
Keine automatischen Main-Merges aus einem Dokumentationsauftrag ableiten.

Vor Veröffentlichung den exakt vorgemerkten Baum und nach dem Commit die
vollständige erreichbare Veröffentlichungshistorie prüfen:

```text
python scripts/check_publication.py
python scripts/check_publication.py --ref codex/public-release
```

Scans ersetzen nicht das Lesen des Diffs. Bei unklarer Publikationssicherheit
nicht veröffentlichen. Commitnachrichten beschreiben konkrete Änderungen.
PRs nennen Verhalten, Umfang, ausgeführte Prüfungen und verbleibende Grenzen.

## Private Testdaten und Originalmusik

Musik, Lyrics, Stems, Analysen, persönliche Notizen, SQLite-Dateien, Gewichte,
Screenshots, Logs und lokale Werkzeuge bleiben ignoriert lokal. Originalmusik
niemals verändern. Testdienste und Testspeicher von produktiven Daten isolieren.
Deterministische synthetische Regressionen sind keine tatsächliche Musikabnahme.
Für tatsächliche Musiktests die lokal autorisierten Quellen verwenden;
Plattformlinks vor Verwendung mit vollständiger URL, Datum und Zweck im lokalen
ignorierten Linklog des Testmusikordners erfassen. Keine solchen Links oder
identifizierenden Testergebnisse in öffentliche Berichte übernehmen.

## Dokumentationsregeln

README bleibt die kurze Projektstartseite; Fachdetails gehören in die
[Dokumentationsübersicht](README.md). Aktuellen Status ausschließlich in
[STATUS.md](STATUS.md) pflegen. Datierte Abnahmen mit Quelle, Plattform,
Prüfumfang und Grenzen erhalten; historische Aussagen als solche kennzeichnen.
Relative Links prüfen, keine persönlichen Rechnerpfade oder dekorativen Emojis.
Unsichere Modellschätzungen nicht als bestätigte Fakten beschreiben.
