# MoodScope

Lokale Musik- und Lyrics-Analyse mit React, TypeScript, Tauri und Python/FastAPI. Windows 10/11 und Linux sind die Zielplattformen. Dies ist eine erste Entwicklungsversion, kein fertig paketiertes Endkundenprodukt.

## Windows-Start

```powershell
.\scripts\start.ps1
```

Danach http://127.0.0.1:8765 im Browser öffnen. Der Dienst liefert das gebaute React-Frontend aus. Strg+C beendet ihn. Portable Node-Dateien befinden sich unter `.tools`, Python-Pakete unter `.venv`. Keine globale Node-/Python-Paketinstallation erforderlich.

Nach erfolgreichem nativen Build kann unter Windows auch `Start-MoodScope.cmd` per Doppelklick gestartet werden. Dieser Starter nutzt die projektlokale Python-Umgebung, startet bei Bedarf den Backend-Dienst und öffnet das native Fenster. Ein bereits laufender MoodScope-Dienst wird wiederverwendet.

Für das native Tauri-Fenster (Rust, MSVC und Windows SDK erforderlich):

```powershell
.\scripts\start.ps1 -Desktop
```

Dieser Entwicklungsstarter verwaltet Backend und Tauri zusammen. Eine separat ausgeführte Tauri-EXE benötigt vorerst den laufenden Python-Dienst. Der Installer enthält noch keinen eigenständigen Python-Sidecar.

## Benutzung

1. MP3, WAV oder FLAC importieren oder auf die Songkarte ziehen. Die Analyse startet automatisch. Maximal 250 MB; Dateien werden auf maximal 30 Minuten begrenzt und für kompatible Wiedergabe in Mono-WAV mit 48 kHz umgewandelt.
2. Vorhandene Interpret-/Titel-Tags lösen automatisch eine Lyrics-Suche bei LRCLIB aus. Ohne Tags können Interpret und Titel manuell eingegeben werden. Alternativ synchronisierte `.lrc` importieren oder LRC-Text einfügen und erneut analysieren. Interpret, Titel und Dauer werden zur Lyrics-Suche an LRCLIB gesendet; Audiodateien werden nicht hochgeladen.
3. Optional Whisper aktivieren, wenn keine synchronisierten Lyrics vorliegen. Das funktioniert nach dem ersten Modelldownload offline und läuft standardmäßig auf CPU.
4. Beim ersten Mal werden Modellgewichte von Hugging Face geladen (mehrere GB Speicherplatz einplanen). Anschließend erfolgt die Inferenz lokal. **Song analysieren** berechnet nach Ergänzen/Ändern der Lyrics erneut; die Audioanalyse wird separat aus dem Cache wiederverwendet.
5. Player starten. Kurven, Positionslinie und markierte Lyrics folgen der Audiozeit. Ein Klick in die Kurve, auf eine Textzeile oder auf **Zum Moment springen** sucht die entsprechende Stelle.

Ohne synchronisierte Lyrics bleibt die Textkurve leer und es gibt keinen Biggest Split. Reiner Text wird nicht künstlich mit Zeitstempeln versehen. LRCLIB kann nur unsynchronisierte Texte oder gar keine Ergebnisse liefern. Whisper erkennt Gesang nicht immer zuverlässig; hier wird der gesamte Mix transkribiert, ohne Stem-Separation.

## Was die Kurven bedeuten

- **Audio Mood:** Das vortrainierte Audio/Text-Modell [LAION CLAP](https://huggingface.co/laion/clap-htsat-unfused) vergleicht echte Audiofenster mit vier musikalischen Beschreibungen (fröhlich, ruhig, traurig, wütend). Aus Softmax-Ähnlichkeiten entsteht eine gewichtete Valenz von −1 bis +1. Fensterlänge 10 s, Abstand 5 s. CLAP ist ein allgemeines Audio/Text-Modell, kein auf Valenz kalibrierter Musik-Emotionsregressor. Stimmen und Textinhalt können die Audiovorhersage beeinflussen.
- **Lyric Mood:** [XLM-EMO](https://huggingface.co/MilaNLProc/xlm-emo-t) liefert die Wahrscheinlichkeiten für joy, sadness, anger und fear je synchronisierter Zeile. Valenz = joy − sadness − 0,7 × anger − 0,7 × fear. Das Modell wurde für Social-Media-Text trainiert, nicht speziell für Songtexte.
- **Biggest Split:** Für jedes Audiofenster wird die zeitlich überlappende Textvalenz nach Überlappungsdauer gemittelt. Der größte absolute Unterschied wird markiert. Angezeigte Prozentwerte sind Abstand / 2 × 100, keine statistische Sicherheit.
- **librosa:** Misst echte RMS-Energie als zusätzliches akustisches Merkmal. RMS wird ausdrücklich nicht als KI-Emotion ausgegeben.

Die Zuordnung zu einer gemeinsamen Valenzachse ist eine transparente MVP-Designentscheidung. Die Werte sind subjektive Modellschätzungen und nicht wissenschaftlich gegeneinander kalibriert. Es gibt keine Zufallskurven, Demo-KI-Ergebnisse oder heuristischen Ersatz, wenn Modellinferenz scheitert. Fehlermeldungen bleiben sichtbar.

## Umgebung und Installation

Python 3.10+, Node.js 22.12+ und npm. Native Builds zusätzlich Rust und plattformspezifische [Tauri-Voraussetzungen](https://v2.tauri.app/start/prerequisites/). Windows: MSVC C++ Build Tools, Windows SDK und WebView2. Linux: z. B. WebKitGTK 4.1, GTK 3, librsvg, patchelf und Build-Werkzeuge laut Tauri-Dokumentation. Die Skripte installieren keine Betriebssystempakete automatisch.

```powershell
.\scripts\setup.ps1
```

```bash
bash scripts/setup.sh
bash scripts/start.sh
# Native Entwicklung:
bash scripts/start.sh --desktop
```

Neue Installationen verwenden eine isolierte venv. Eine vorhandene kompatible PyTorch-Installation kann bei Bedarf über eine venv mit `--system-site-packages` wiederverwendet werden. TensorFlow/Flax sind für Transformers deaktiviert. Auf anderen Systemen die passende CUDA-PyTorch-Version gemäß [PyTorch](https://pytorch.org/get-started/locally/) installieren. RTX-50-GPUs benötigen einen Build mit Unterstützung ihrer CUDA-Architektur. Ein tatsächlicher CUDA-Kerneltest entscheidet über GPU-Nutzung; CPU ist der automatische Fallback.

Konfiguration über Umgebungsvariablen:

- `MOODSCOPE_DEVICE=cpu|cuda|auto` (Standard auto)
- `MOODSCOPE_WHISPER_DEVICE=cpu|cuda` (Standard cpu; CUDA für CTranslate2 benötigt passende CUDA/cuDNN-Bibliotheken und ist hier nicht vorausgesetzt)
- `MOODSCOPE_DATA`: Daten-/SQLite-Ordner (Standard `data/` im Projekt)
- `HF_HOME`: Modellcache (Standard `models/` im Projekt)
- `HF_HUB_OFFLINE=1`: keinerlei Hugging-Face-Netzanfragen nach vollständigem Download

Die Audio-/Textmodelle werden nacheinander durch einen einzelnen Hintergrundarbeiter angesprochen. SQLite speichert dekodierte Track-Metadaten und Analyseergebnisse nach Dateiinhalt, Pipelineversion, Lyrics und Whisper-Einstellung. LRCLIB-Antworten werden ebenfalls gespeichert. Audiodateien und Gewichte werden nicht in Git aufgenommen. Zum Freigeben von Speicher kann man bei beendeter App `data/` beziehungsweise `models/` manuell löschen. Analysejobs selbst sind flüchtig; nach Backend-Neustart erneut analysieren, dann wird der Cache verwendet.

## Entwicklung und Tests

```powershell
.venv\Scripts\python.exe -m pytest -q
npm test
npm run build
# Optional: Downloads und echte Modellinferenz (keine Mocks):
.venv\Scripts\python.exe -m scripts.smoke_models
```

`scripts.smoke_models` testet einen ausdrücklich synthetischen Kalibrierton und einen selbst geschriebenen Satz. Dies bestätigt technischen Modellbetrieb, nicht die emotionale Genauigkeit für Songs. Unit-/API-Tests ersetzen nur im Cachetest die Modellaufrufe; solche Testdaten erscheinen nicht in der App.

Frontend-Entwicklung: Backend starten und separat `npm run dev` (127.0.0.1:1420). Produktion: `npm run build`, Backend neu starten, dann 127.0.0.1:8765. Der Dienst bindet nur an Loopback und prüft Host/Origin. Er ist nicht als öffentlich erreichbarer Mehrbenutzerserver gedacht.

Native Builds auf dem jeweiligen Betriebssystem:

```bash
npm run tauri build -- --no-bundle
# Erst nach Integration eines paketierten Python-Backends Endkunden-Installer bauen.
```

Windows und Linux müssen separat gebaut/getestet werden; ein Windows-Build bestätigt keinen Linux-Build. Die Linux-Skripte und Tauri-Konfiguration sind vorbereitet. Videoexport ist noch nicht implementiert; das projektlokale FFmpeg wird bereits zur Audiodekodierung genutzt.

## Struktur

`src/` React-Player, SVG-Kurven und Oberfläche · `backend/` API, Modelle, Timing und SQLite · `src-tauri/` native Hülle · `scripts/` Start/Setup/Integration · `tests/` Backend-Tests · `docs/` Prüfstatus.

Modellgewichte haben eigene Nutzungsbedingungen; insbesondere verweist XLM-EMO auf die Lizenzen der Trainingsdaten. Vor einer Weiterverteilung mit eingebetteten Gewichten diese prüfen. Es werden standardmäßig keine Gewichte mit der App weiterverteilt.

## Veröffentlichung

Vor jeder Veröffentlichung `python scripts/check_publication.py` für vorgemerkte Dateien und `python scripts/check_publication.py --ref HEAD` für den Commit ausführen. Die Prüfung meldet nur Dateinamen und Fundkategorien, keine mutmaßlichen Geheimnisse. Details stehen in `docs/PUBLISHING.md`.
