# Tatsächlich geprüfter Stand

Entwicklungsversion 0.3; aktuelle Erweiterungen und Prüfungen: [Entwicklungsstand](DEVELOPMENT.md). Vorherige MVP-Nachweise: Windows mit NVIDIA-CUDA geprüft. Funktionsumfang und Startanleitung stehen in der [README](../README.md), weitere Nachweise in den [Versionshinweisen](RELEASE-0.2.md).

## Ausgeführte Prüfungen

- Aktuell 81 Python-Tests und 13 Frontend-Tests bestanden. Ein Starlette-Testclient-Deprecation-Hinweis bleibt vorhanden.
- React/TypeScript-Produktionsbuild und nativer Tauri-Windows-Releasebuild bestanden. Neuer Build unter `src-tauri/target/v02/release/moodscope.exe`; der Starter berücksichtigt auch den normalen Releaseordner.
- MP3, WAV und FLAC durch FFmpeg dekodiert; Stereo-WAV-Wiedergabe mit Range-Anfragen und Seeking. Player, Lautstärke, zwei Kurven, Lyrics-Synchronisierung und Biggest-Split-Sprung wurden geprüft.
- Echte lokale CLAP- und XLM-EMO-Inferenz auf CUDA, auch vollständig offline. Private Songtests und ihre Ergebnisse werden nicht veröffentlicht.
- Vollständiger isolierter Offline-Modelltest mit selbst erzeugtem Kalibrieraudio und selbst geschriebenen Lyrics: Analyse, Cache-Wiederverwendung ohne neue Audioinferenz, Songdetails, Instrumenthinweise, Qwen-Zeilendeutung, Cache-Löschung bei erhaltenen eigenen Notizen und erzwungene Neuanalyse bestanden. Reproduzierbar mit `python -m scripts.smoke_pipeline` nach Einrichtung der Modelle.
- Automatische Wiedererkennung, konservativer Metadaten-/Audiovergleich, getrennte Modellversionen, gezielte Cache-Löschung und Notizenspeicherung durch API-Tests geprüft.
- Öffentliche YouTube- und SoundCloud-Einzeltracks tatsächlich importiert. Ein öffentlicher YouTube-Track wurde zusätzlich über die Browseroberfläche importiert und lokal auf CUDA analysiert. Bibliotheksöffnung lud den Cache; eine eigene Notiz überstand vollständiges Neuladen.
- LRCLIB-Liveabfrage erfolgreich. faster-whisper `base` offline auf CPU: Stille ohne Segmente und kurzer Gesangsausschnitt mit vier zeitmarkierten Segmenten; keine quantitative Wortgenauigkeitsprüfung.
- Zwölf selbst geschriebene deutsche/englische Textfälle: Einzelzeilen- und Kontextmodell jeweils 75 % richtige Valenzrichtung. Kein Nachweis allgemein höherer Song-Genauigkeit.
- Veröffentlichungsschutz prüft ausgewählten Quellcode und erreichbare Git-Historie auf ausgeschlossene Daten, typische Geheimnisse, persönliche Pfade/E-Mail-Adressen und dekorative Emojis. Private Musik, Lyrics, Modellantworten und Schlüssel gehören nicht ins Repository.

Der Browser lehnte den lokalen Kalibrierdatei-Upload trotz anschließender Nutzerfreigabe weiterhin ab. Dieser Bedienpfad wurde in der aktuellen Browserrunde ausgelassen. Die separate isolierte Modellprüfung und der öffentliche Linkimport ersetzen keinen erneuten Browser-Dateidialogtest. Ein früherer MVP-Dateiimport war erfolgreich geprüft worden.

## Grenzen

- CLAP ist ein allgemeines vortrainiertes Audio/Text-Modell; XLM-EMO wurde auf Social-Media-Text trainiert. Valenzprojektion, Kontextmischung und Trennschärfe sind keine wissenschaftlich kalibrierte Song-Emotionsmessung.
- Qwen 1.5B wurde tatsächlich lokal ausgeführt. Textdeutungen können falsch sein; akustische Begründungen werden separat aus vorhandenen Mess-/Modellwerten formuliert. Nicht alle angebotenen Modellvarianten wurden heruntergeladen oder qualitativ verglichen.
- Optionales Gemini wurde ohne eigenen Schlüssel nicht live ausgeführt. Vertragstests prüfen Adapter und Einwilligung; kostenlose Kontingente und Abrechnungsstatus sind keine Garantie der App. Standard bleibt lokale KI, auch online.
- Windows 10 und Linux wurden nicht lokal ausgeführt. Startskripte und CI-Konfiguration sind vorbereitet; daraus folgt kein bestandener Zielsystem- oder CI-Lauf.
- Whisper läuft standardmäßig auf CPU. Gesang und Zeitstempel sind nicht garantiert; keine Vocal-Separation. Whisper-CUDA wurde nicht geprüft.
- LRCLIB kann falsche, unvollständige oder keine Lyrics liefern; ungetakteter Text wird nicht künstlich synchronisiert. Linkplattformen können einzelne Inhalte sperren oder löschen.
- Kein eigenständiger Installer mit Python-Sidecar, keine Signierung/Updates und kein Videoexport. Die native EXE benötigt die eingerichtete Projektumgebung samt Backend.
- Kein Abbruch laufender Analyse. Maximal 250 MB Import und 30 Minuten dekodierte Laufzeit; API-Audio maximal zehn Minuten.

## Reproduzierbarkeit

JavaScript: `package-lock.json`; Rust: `src-tauri/Cargo.lock`; Python: `backend/requirements.txt` plus lokaler Paketsnapshot `backend/requirements.local-lock.txt`. Der Snapshot enthält nicht die geerbte PyTorch-/NumPy-Installation und ist kein universeller Plattformlock. Standard-Emotionsmodelle sind auf Hugging-Face-Revisionen festgelegt. Modellwahl und Pipelineversion fließen in Analyse-Cacheschlüssel ein.
