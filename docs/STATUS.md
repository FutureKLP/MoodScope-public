# Tatsächlich geprüfter Stand

Stand: erste MVP-Version; Windows mit NVIDIA-CUDA geprüft.

## Funktioniert und wurde ausgeführt

- React/TypeScript-Produktionsbuild (`npm run build`).
- Nativer Tauri-Windows-Releasebuild (`npm run tauri build -- --no-bundle`); EXE unter `src-tauri/target/release/moodscope.exe`, etwa 8,7 MB. Fenster geöffnet, Oberfläche gerendert, lokale CUDA-Verbindung angezeigt. Der Browser-Ablauf wurde vollständig geprüft; der native Dateidialog wurde geöffnet. Während der nativen Prüfung wurde außerdem ein Song mit Kurve im Fenster sichtbar; die komplette native Bediensequenz wurde nicht als reproduzierbarer UI-Test aufgezeichnet.
- MP3, WAV und FLAC tatsächlich durch FFmpeg dekodiert; Wiedergabe als normalisiertes WAV inklusive HTTP-Range/Seeking.
- Automatischer Analysebeginn nach Import und automatische LRCLIB-Suche anhand von Song-Tags; im Browser mit echter MP3 geprüft.
- LRC-Import/-Parsing, Zeitsynchronisierung, zwei SVG-Kurven, Player, Springen zur Biggest-Split-Stelle. Kalibrierton: Play/Pause und Seeking im Browser geprüft.
- CLAP und XLM-EMO mit tatsächlicher Modellinferenz auf CUDA. Zusätzlich beide Modelle bei `HF_HUB_OFFLINE=1` vollständig aus dem lokalen Cache ausgeführt.
- Vollständiger lokaler MP3-Songtest mit synchronisierten Lyrics und echter CUDA-Inferenz bestanden. Namen, Inhalte und Ergebnisse der privaten Testdateien werden nicht veröffentlicht.
- Analyse-Cachetreffer am echten Song nachgewiesen; kein erneuter Modellaufruf. Audio- und komplette Analyseergebnisse haben separate Cacheeinträge.
- LRCLIB-Liveabfrage mit öffentlichen Testmetadaten: HTTP 200, synchronisierter Text vorhanden.
- faster-whisper `base`: Offline-Inferenz auf CPU. Drei Sekunden Stille erzeugen keine Segmente; ein 20-sekündiger Gesangsausschnitt erzeugt vier zeitlich markierte Segmente. Wortgenauigkeit wurde nicht quantitativ bewertet. Whisper-CUDA wurde nicht getestet.
- **12 Analyse-/API-Tests, 4 Veröffentlichungsprüfungen und 2 Frontend-Tests bestanden**. Backend umfasst echte Formatdekodierung, Tags, Range-Audio, Originschutz, LRC-Instrumentalpausen, Vergleichsberechnung, Cache und Fehlerfälle. Ein Starlette-Testclient-Deprecation-Hinweis ist noch vorhanden; kein Testfehler.
- npm-Sicherheitsprüfung nach Vitest-Update: **0 gemeldete Schwachstellen** zum Prüfzeitpunkt.
- Python-Quelldateien mit compileall geprüft.
- Nativer Windows-Build mit MSVC, Windows SDK und projektlokalem Rust erfolgreich.

Testdaten und vollständige Modell-/Lyrics-Ausgaben bleiben ausschließlich unter dem ignorierten `data/`-Ordner. Nutzermusik unter `for test only music files/` bleibt unverändert und ist von Git ausgeschlossen. Keine Audiodatei wurde an einen Analysedienst hochgeladen.

## Grenzen / noch offen

- CLAP ist ein allgemeines vortrainiertes Audio/Text-Modell mit Zero-Shot-Musikprompts, kein speziell auf musikalische Valenz trainierter Regressor. XLM-EMO ist für Social-Media-Text trainiert. Die Valenzachsen sind heuristisch aus echten Modellwahrscheinlichkeiten projiziert und nicht gegeneinander kalibriert. Die App weist darauf hin.
- Kein fertiger eigenständiger Endkundeninstaller: Native EXE und Projektstarter funktionieren zusammen mit `.venv`, Python-Dienst und Modellcache. Ein gebündelter Python-Sidecar, Installer-Integration, Signierung und Update-Verteilung fehlen.
- Linux-Start-/Setupskripte und Windows/Linux-CI sind vorbereitet. Kein Linux-Build und kein CI-Lauf wurden in dieser Sitzung ausgeführt. Windows 10 wurde nicht separat getestet.
- Whisper transkribiert den gesamten Mix ohne Vocal-Separation; keine garantierte Gesangs- oder Zeitstempelqualität. GPU-Inferenz über CTranslate2 benötigt passende CUDA/cuDNN-Bibliotheken; der funktionierende Standard ist CPU.
- LRCLIB ist ein externer Dienst und kann fehlen, falsche Versionen liefern oder nur unsynchronisierten Text liefern. Keine Treffer werden als Fehler/Hinweis behandelt, ohne Lyrics zu erfinden. Whisper ist bewusst zuschaltbar.
- Kein Videoexport. FFmpeg ist für Import und spätere Exportarbeit verfügbar.
- Kein Abbruchknopf für laufende Analyse, kein Modellmanagement-Dialog und keine dauerhafte Songbibliothek in der Oberfläche. Dateien und Analyseergebnisse werden jedoch persistent gecacht.
- Maximal 250 MB Upload und 30 Minuten dekodierte Laufzeit. Mono-Wiedergabe im MVP.

## Reproduzierbarkeit

JavaScript-Abhängigkeiten: `package-lock.json`. Rust: `src-tauri/Cargo.lock`. Python: `backend/requirements.txt`; zusätzlich `backend/requirements.local-lock.txt` als Snapshot der lokal installierten venv-Pakete. Der Snapshot ist kein plattformübergreifender Komplettlock und enthält nicht die geerbte PyTorch-/NumPy-Installation. Die Emotionsmodelle sind auf konkrete Hugging-Face-Commitrevisionen festgelegt. Cache-Pipelineversionen werden bei semantischen Änderungen angehoben.

