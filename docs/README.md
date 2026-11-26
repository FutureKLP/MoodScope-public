# Dokumentationsübersicht

[Projektstartseite](../README.md) · **[Aktueller Status und nächste Phase](STATUS.md)**

## Einstieg und Entwicklung

- [Installation und lokaler Start](SETUP.md) – Windows, CPU, Linux, Desktop und Modelle.
- [Entwicklungsumgebung](ENVIRONMENT.md) – Laufzeiten und Systembibliotheken.
- [Paketierte Backend-Runtime](BACKEND-RUNTIME.md) – Architektur, Prozessbesitz,
  Benutzerverzeichnisse und Lizenzgrenzen des zusätzlichen Runtimebuilds.
- [Mitwirkung und Projektstruktur](CONTRIBUTING.md) – Einstieg, Tests und Review.
- [Technischer Überblick 0.3](DEVELOPMENT.md) und [Funktionen und Bedienung](USER-GUIDE.md).
- [Designsystem](DESIGN-SYSTEM.md) – Palette, kontinuierliche Bewegung und Synchronisierung.

## Musik und Audio

- [Wiedergabe und Hörstudio](AUDIO-PLAYBACK.md).
- [Audiovergleich und Evaluation](AUDIO-EVALUATION.md).
- [Musikpsychologische Grundlagen](MUSIC-PSYCHOLOGY.md).
- [Menschliche Referenzbewertungen](HUMAN-REFERENCE.md).

## KI und Emotionsanalyse

- [Emotionsmodelle und Grenzen](EMOTION-MODELS.md).
- [Kombinierte Audio-/Textanalyse](COMBINED-ANALYSIS.md).
- [API-Profile, Zustimmung und Datenübertragung](API-PROFILES.md).
- [Backendqualität und Modelllebenszyklus](BACKEND-QUALITY.md).

## Datenintegrität und Sicherheit

- [Originalmusik, Cache, verwaltete Kopien und Wiederherstellung](DATA-INTEGRITY.md).
- [Sicherheitsgrenzen](SECURITY.md).
- [Drittanbieter und Modelllizenzen](THIRD-PARTY.md).

## Desktop- und Regressionstests

- [Testbaseline](TEST-BASELINE.md) – Reproduktion und datierte Prüfläufe.
- [Kernabnahme](CORE-ACCEPTANCE.md) – Kriterien und historische Nachprüfungen.
- [Phase 1: Windows-WAV-Dialoge](WINDOWS-DESKTOP-TESTING.md).
- [Phase 2A: Bibliothek, Player, Lyrics](PHASE2A-ACCEPTANCE.md) – lokaler Branch, definierter synthetischer Umfang.
- [Phase 2B: KI, Modelle, Atmosphäre und API](PHASE2B-ACCEPTANCE.md) – Teilabnahme und offene native Kriterien.
- [Phase 2C: Hörstudio, Mixer und WAV-Export](PHASE2C-ACCEPTANCE.md) – native Teilabnahme, numerische WAV-Prüfung und Gesamtzyklus.
- [Phase 3: Performance und Ressourcen](PHASE3-PERFORMANCE-ACCEPTANCE.md) – wiederholte native Musik-/Mixprüfung, echte Offline-Worker und zentrale Freigabematrix.
- [Phase 4: Installer und Plattformen](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md) – isolierter NSIS-Lauf, Ubuntu/WSLg, Debian-Build und fehlende Backendverteilung.
- [Performancebaseline](PERFORMANCE-BASELINE.md) – historische synthetische Messungen; keine Musikabnahme.

## Release und Veröffentlichung

- [Verbindlicher Veröffentlichungsablauf](PUBLISHING.md).
- [Quelländerungen für 0.3](PUBLIC-RELEASE-NOTES.md).
- [CI-Läufe](https://github.com/FutureKLP/MoodScope-public/actions) und
  [Pull Requests](https://github.com/FutureKLP/MoodScope-public/pulls).

## Technische Nachweise und historische Versionen

- [Version 0.2](RELEASE-0.2.md) ist ein historischer Entwicklungsbericht.
- Datierte Abschnitte in Testbaseline, Kernabnahme und Desktopberichten bleiben
  als Nachweise erhalten. Ihr damaliger Status ersetzt nicht [STATUS.md](STATUS.md).
- Private Sitzungsberichte und Codex-Übergaben bleiben ignoriert lokal; sie sind
  keine öffentlichen Dokumentationslinks. Neue Sitzungen beginnen mit STATUS,
  dieser Übersicht und CONTRIBUTING; lokale Anweisungen zusätzlich lesen.

## Linkpflege

Relative Dateilinks werden gegen den versionierten Dokumentationsbaum geprüft.
DOI- und Verlagslinks können automatisierte Abrufe mit HTTP 403 oder Cookie-
Zwischenseiten beantworten; das ist keine bestätigte Nichtexistenz der Quelle.
Solche stabilen Referenzen bleiben erhalten. Nicht mehr öffentlich erreichbare
Referenzen werden als historisch gekennzeichnet, ohne die damaligen Befunde zu löschen.
