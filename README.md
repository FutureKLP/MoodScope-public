# MoodScope

MoodScope vergleicht den geschätzten emotionalen Ausdruck von Musik und Lyrics.
Die lokale Desktop-App zeigt beide Verläufe synchron zur Wiedergabe und markiert
mit **Biggest Split** ihren größten berechneten Unterschied. React/TypeScript,
Tauri und Python/FastAPI bilden Oberfläche, Desktopfenster und Analysedienst.

## Funktionen

- Lokale Audioimporte, berechtigte Linkimporte und eine SQLite-Bibliothek.
- Player mit Seeking, A/B-Loops und synchronisierten Lyrics; LRC-Import und optionale Whisper-Erkennung.
- Audio-/Textanalysen, beleggebundene Gesamt- und Zeilendeutungen sowie eigene Notizen.
- Hörstudio mit Demucs-Spuren, Live-Mix und WAV-Export.
- Lokale Modelle und optionale Anbieterprofile mit ausdrücklicher Übertragungszustimmung.
- Deutsche/englische Oberfläche und fließende Atmosphäre mit reduzierter Bewegung.

[Ausführliche Funktionen und Bedienung](docs/USER-GUIDE.md).
Modellschätzungen bestätigen weder Gefühle noch vollständige Worterkennung,
Sängerisolation oder Instrumentanwesenheit.

## Voraussetzungen

Python ab 3.11, Node.js ab 22.12 mit npm und mehrere GB Platz für Modelle.
Das Windows-Setup richtet Python 3.13 projektlokal ein. Native Builds benötigen
Rust und die jeweiligen [Tauri-Systemvoraussetzungen](https://v2.tauri.app/start/prerequisites/),
unter Windows insbesondere MSVC, Windows SDK und WebView2. CUDA ist optional.
[Umgebung und Hardwaregrenzen](docs/ENVIRONMENT.md).

## Installation und lokaler Start

Im ausgecheckten Projektordner unter Windows:

```powershell
.\scripts\setup.ps1
.\scripts\start.ps1
```

Im Browser anschließend [MoodScope öffnen](http://127.0.0.1:8765).
Das Windows-Standardsetup verwendet einen CUDA-PyTorch-Build; CPU-Einrichtung,
Linux, native Builds, Modelle und Linkimport stehen in der
[Installationsanleitung](docs/SETUP.md).

Der zusätzliche [Runtimebuild](docs/BACKEND-RUNTIME.md) bündelt ein eigenes
CPU-Python-/FastAPI-Backend. Lokale NSIS-/Debian-Testkandidaten starten es selbst;
der normale Entwicklungsbuild verwendet weiterhin den Projektstarter.
Lizenzen, vollständige Modellprüfung und weitere Plattformfälle bleiben offen.
Keine Endnutzer-Installerfreigabe.
[Plattformabnahme und Grenzen](docs/PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).

## Entwicklungsstatus

Version 0.3 ist eine Entwicklungsversion. Maßgeblich für abgeschlossene Phasen,
öffentlichen Integrationsstand, verbleibende Abnahmen und die nächste Phase ist
**[docs/STATUS.md](docs/STATUS.md)**. Builds und synthetische Prüfungen sind keine
vollständige Kern-, Musikqualitäts-, Installer- oder Plattformfreigabe.

## Dokumentation

Die **[Dokumentationsübersicht](docs/README.md)** führt zu Entwicklung, Audio,
KI-Verfahren, Datenintegrität, Tests und Veröffentlichung.

## Tests und Qualität

[Reproduzierbare Befehle und datierte Ergebnisse](docs/TEST-BASELINE.md),
[Kernabnahmekriterien](docs/CORE-ACCEPTANCE.md) und
[GitHub-CI](https://github.com/FutureKLP/MoodScope-public/actions).
Automatisierte Regressionen, native Bedienung und tatsächliche Musiktests werden
getrennt dokumentiert. Einstieg für Beiträge: [CONTRIBUTING.md](docs/CONTRIBUTING.md).

## Datenschutz und Sicherheit

Lokale Verarbeitung ist der Standard. Optionale Recherche-, Linkimport- und
API-Funktionen greifen auf die gewählten Dienste zu; Anbieteranalysen benötigen
Zustimmung. Schlüssel bleiben im Backend-Arbeitsspeicher. Originaldateien bleiben
von verwalteten Kopien, Analyse-Caches und persönlichen Notizen getrennt.
Nur Musik mit den erforderlichen Nutzungsrechten importieren und bearbeiten.
[Sicherheitsgrenzen](docs/SECURITY.md), [Datenintegrität](docs/DATA-INTEGRITY.md)
und [API-Datenübertragung](docs/API-PROFILES.md).

## Lizenzen und Mitwirkung

Projektcode: [MIT](LICENSE). Abhängigkeiten und Modelle haben eigene Bedingungen:
[Drittanbieter und Modelllizenzen](docs/THIRD-PARTY.md).
Beiträge folgen [CONTRIBUTING.md](docs/CONTRIBUTING.md) und dem maßgeblichen
[Veröffentlichungsablauf](docs/PUBLISHING.md).
