# Installation und lokaler Start

[Dokumentationsübersicht](README.md) · [Entwicklungsumgebung](ENVIRONMENT.md)

Die Befehle werden im Repository-Hauptverzeichnis ausgeführt. Zielplattformen und
Installationsfreigabe sind getrennt im [aktuellen Status](STATUS.md) eingeordnet.

## Voraussetzungen

- Python 3.11 oder neuer unter Linux; das Windows-Setup richtet Python 3.13 projektlokal ein.
- Node.js 22.12 oder neuer mit npm.
- Für das native Fenster: Rust und die [Tauri-Systemvoraussetzungen](https://v2.tauri.app/start/prerequisites/).
- Windows: MSVC C++ Build Tools, Windows SDK und WebView2.
- Linux: unter anderem WebKitGTK 4.1, GTK 3, OpenSSL und native Build-Werkzeuge gemäß Tauri-Dokumentation.
- Optional: NVIDIA-GPU mit kompatiblem PyTorch-CUDA-Build. CPU ist als Fallback möglich.
- Mehrere GB freier Speicher für Modellgewichte; lokale Interpretation benötigt zusätzlich RAM bzw. VRAM.

Die Setupskripte installieren Python-/Node-Pakete projektlokal. Betriebssystempakete werden nicht automatisch installiert. Ein GPU-Treiber und ein für die GPU-Architektur geeigneter PyTorch-Build sind unabhängig davon erforderlich.

## Installation und Start unter Windows

Repository lokal auschecken und im Projektordner ausführen:

```powershell
.\scripts\setup.ps1
.\scripts\start.ps1
```

Das Windows-Setup lädt ein prüfsummengeprüftes offizielles Python-Paket und richtet `.venv-modern` ohne geerbte Systempakete ein. Standard ist PyTorch mit CUDA 13.2; Treiber und GPU müssen dazu passen. Für CPU: zuerst `scripts/setup_runtime.ps1 -Cpu`, anschließend `npm ci` und `npm run build`. Ältere GTX-Karten benötigen gegebenenfalls einen anderen geeigneten PyTorch-Build. Es werden weder System-Python noch Treiber installiert. Der Starter bevorzugt diese Umgebung erst nach erfolgreicher Import-/Kernelprüfung.

Danach [http://127.0.0.1:8765](http://127.0.0.1:8765) im Browser öffnen. Der Dienst liefert das gebaute Frontend aus. Strg+C beendet ihn.

Für das native Fenster:

```powershell
npm run tauri build -- --no-bundle
.\scripts\start.ps1 -Desktop
```

Nach einem nativen Build kann auch **Start-MoodScope.cmd** per Doppelklick verwendet werden. Der Starter verwendet die projektlokale Python-Umgebung und startet den lokalen Backend-Dienst bei Bedarf. Eine separat gestartete EXE braucht diesen Dienst ebenfalls.

Auf einem bereits eingerichteten Entwicklungsrechner kann ein separater Build unter `src-tauri/target/v03/release/` oder `src-tauri/target/v02/release/` liegen. Der Projektstarter wählt die neuere EXE aus diesen Ordnern und `src-tauri/target/release/`. Eine bereits geöffnete ältere App und ihr Backend müssen für Version 0.3 neu gestartet werden; ein älterer Dienst wird vom Starter erkannt.

## Stand der Installationspakete

Phase 4.2 ergänzt einen gesonderten Entwicklungsbuild mit CPU-Python-Backend als
Tauri-Ressource. Bau, Benutzerverzeichnisse und Grenzen stehen unter
[Backend-Runtime](BACKEND-RUNTIME.md). Lokale NSIS-/Debian-Kandidaten wurden mit
eigener Testkennung installiert, ohne Projektserver gestartet und mit Datenerhalt
deinstalliert. Phase 4.3 baut beide Kandidaten nach der finalen Modellpfadkorrektur
neu; das Debianpaket ist mit vollständigen GStreamer-Abhängigkeiten in einer
isolierten Systemkopie konfiguriert. Modellgewichte sind nicht enthalten.
Phase 4.4 ergänzt versionsgebundene Original-Lizenztexte und echte installierte
Windows-/Linux-CPU-Inferenz mit vorhandenen Testgewichten. Die synthetische WSLg-Monitorprobe
ist erneut gelungen; sie ersetzt keine physische Audioabnahme. Unabhängige
Linux-Desktopabnahme, vollständige Modellmatrix, Distributionsquellen/-rechte
und weitere Releasegates bleiben offen; keine Endnutzer-/Releasefreigabe.
Die früheren Phase-4.1-Pakete und der Standardbuild enthalten weiterhin nur den
Client und benötigen den eingerichteten Projektstarter beziehungsweise Dienst.
[Nachweise und Grenzen](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).

## Installation und Start unter Linux

Nach Einrichtung der oben genannten Systemvoraussetzungen:

```bash
bash scripts/setup.sh
# Explizite CPU-Umgebung, auch Torchaudio ohne CUDA:
# bash scripts/setup.sh --cpu
bash scripts/start.sh
# Native Entwicklung:
bash scripts/start.sh --desktop
# Nativer Build:
npm run tauri build -- --no-bundle
```

Windows- und Linux-Builds müssen auf ihren jeweiligen Zielsystemen geprüft werden. Ein erfolgreicher Windows-Build bestätigt keinen Linux-Build.

`--cpu` wählt Torch und Torchaudio vom selben CPU-Paketindex. Beide müssen zur
gewählten Umgebung passen; ein CUDA-Torchaudio neben CPU-Torch kann bereits den
CLAP-Import verhindern. Das Setup prüft diese Importe, bevor es die Umgebung als
validiert markiert. Bei einem fehlgeschlagenen Setup bleibt kein alter
Validierungsmarker bestehen.

Unter WSL2 zuerst die tatsächliche Ubuntu-Version, Werkzeuge und WSLg-Sockets
prüfen. Eine separate Quellkopie im Linux-Dateisystem verwenden; Windows-venv,
produktive SQLite, private Musik und Modelle nicht ungeprüft kopieren. Die
Tauri-Systempakete werden nicht vom Setupskript installiert. Die Phase-4-Prüfung
verwendete Ubuntu 24.04.4 LTS, GTK 3 und WebKitGTK 4.1. WSLg-Anzeige und PulseAudio-
Anschluss ersetzen keine Abnahme an einem eigenständigen Ubuntu-Desktop.

## YouTube- und SoundCloud-Links

Einmal das offizielle portable Downloadwerkzeug projektlokal einrichten:

```powershell
.venv-modern\Scripts\python.exe scripts\setup_links.py
```

Unter Linux entsprechend `.venv-modern/bin/python scripts/setup_links.py`. Der Installer lädt die offizielle yt-dlp-Standalone-Datei nach `.tools/yt-dlp/` und vergleicht deren SHA256 mit der offiziellen Release-Prüfsumme. Für YouTube benötigt yt-dlp zusätzlich eine unterstützte JavaScript-Laufzeit; MoodScope nutzt vorhandenes Node.js.

Im Linkfeld wird ein einzelner HTTPS-Songlink eingefügt. Playlists und SoundCloud-Kurzlinks werden nicht angenommen. Private, gelöschte oder gesperrte Inhalte können nicht importiert werden. Es werden keine Browser-Cookies oder Anmeldedaten übernommen. Bei einem Plattformfehler kann derselbe Song weiterhin als lokale Datei importiert werden. Nur Inhalte verwenden, die heruntergeladen und analysiert werden dürfen.

## Lokale Modelle einrichten

Im Reiter **Modelle & API** das gewünschte Modell herunterladen und auswählen. Beim ersten Analyselauf können benötigte Standardmodelle ebenfalls geladen werden. Gewichte liegen standardmäßig unter `models/`; die Auswahl und bekannte Download-Snapshots werden lokal unter `data/` gespeichert.

Die Interpretation entlädt vorher die Emotionsmodelle, um GPU-Speicher freizugeben. Beim nächsten Analyseauftrag werden diese wieder geladen. Ein kleineres Interpretationsmodell ist schneller, kann aber stärker vereinfachen oder Anweisungen missverstehen.

## Optionale Anbieterprofile

Unter **Modelle & API** stehen Gemini, OpenAI/ChatGPT, Mistral/Voxtral, Anthropic Claude, DeepSeek, Ollama und LM Studio in einer gemeinsamen Profilverwaltung. Basis-URL, Protokoll und genaue Modell-ID können angepasst werden. Die Modell-ID muss beim gewählten Anbieter verfügbar sein; die App wählt keine unbekannten Ersatzmodelle. Gemini nutzt GenerateContent, Claude Messages und die anderen Vorlagen Chat Completions. [DeepSeek-Dokumentation](https://api-docs.deepseek.com/).

1. Anbieter vorbereiten, genaue Modell-ID und gegebenenfalls eigenen API-Key direkt in der App eingeben. Kein Key gehört in Quellcode, Issues oder Chatnachrichten.
2. Für Textdeutungen das Profil im Reiter **Interpretation** wählen und den Versand des Songtexts ausdrücklich erlauben. Die Audioanalyse kann dabei lokal bleiben.
3. Ein entsprechend eingerichtetes Gemini-Profil oder ein ausdrücklich audiotaugliches OpenAI-kompatibles Profil kann für **Audio-API verwenden** aktiviert werden. Dazu gehören geeignete OpenAI-, Mistral/Voxtral- und eigene Audiomodelle. Danach den API-Modus ausdrücklich auswählen und der Übertragung zustimmen. Reine Textprofile werden nicht als Audiomodelle ausgegeben.

OpenAI, Claude und DeepSeek können kostenpflichtig sein. Ein Chat-Abonnement ersetzt keinen API-Zugang. Es gibt keine Zusage kostenloser oder unbegrenzter API-Nutzung. Für die vorbereitete Gemini-Audiofunktion verlangt die App ein bestätigtes Projekt ohne aktivierte Abrechnung, kann den Abrechnungsstatus aber nicht selbst feststellen. Gratislimits und Datenverwendung können sich ändern. [Gemini-Preise](https://ai.google.dev/gemini-api/docs/pricing), [Audio-Dokumentation](https://ai.google.dev/gemini-api/docs/audio).

Profilname, Adresse und Modellwahl bleiben lokal gespeichert; API-Keys nur im Arbeitsspeicher bis zum Backend-Neustart. Profil entfernen entfernt seinen Sitzungs-Key. Lokale/LAN-Server können ohne Key arbeiten, können ihrerseits aber Cloud-Modelle verwenden. Kein automatischer Anbieterwechsel und keine automatischen kostenpflichtigen Wiederholungen. Im Audio-API-Modus wird kein lokales Whisper gestartet. Ohne Nutzer-Keys wurden echte Cloud-Inferenz und deren Kosten nicht live geprüft; Vertragstests ersetzen diesen Nachweis nicht.
