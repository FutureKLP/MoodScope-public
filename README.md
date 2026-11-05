# MoodScope

MoodScope ist eine lokale Desktop-App für die Frage, wie unterschiedlich Musik und Text eines Songs wirken. Die App spielt einen Song ab und zeigt zwei synchronisierte emotionale Verläufe:

- **Audio Mood:** der geschätzte musikalische Ausdruck.
- **Lyric Mood:** die geschätzte Bedeutung der gesungenen Wörter.
- **Biggest Split:** das Zeitfenster mit dem größten berechneten Unterschied zwischen beiden Verläufen.

React und TypeScript bilden die Oberfläche, Tauri das native Fenster und Python/FastAPI den lokalen Analysedienst. Windows 10/11 und Linux sind die Zielplattformen. Dies ist eine Entwicklungsversion, kein fertig paketierter Endkundeninstaller.

## Funktionen

Neu in Version 0.3: ausführlichere Gesamt- und Zeilendeutung, automatisches Wiederanzeigen gespeicherter KI-Deutungen, lokales Hörstudio mit Demucs, SoundCloud-Suchtreffer-Auswahl, MusicBrainz-Recherche und gemeinsame Anbieterprofile einschließlich Gemini und DeepSeek. Der aktuelle Nachweisstand steht in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

### Hörstudio und Diagnose

Im Reiter **Hörstudio** lassen sich Gesang, Schlagzeug, Bass und übrige Instrumente lokal trennen, solo hören und mischen. Optional bietet das experimentelle Sechs-Spur-Modell zusätzlich Gitarre und Klavier. Alle Sänger bleiben in einer gemeinsamen Gesangsspur. Übersprechen und Artefakte sind möglich; die Emotionskurven gelten weiterhin für den Originalmix.

Vorher die optionale Erweiterung projektlokal installieren: `python -m pip install -r backend/requirements-separation.txt` in der aktivierten venv. Die torchaudio-Version muss zum vorhandenen PyTorch-/CUDA-Build passen. Der erste Trennlauf lädt die offiziellen Demucs-Gewichte nach `models/demucs/`. Ergebnisse liegen unter `data/stems/`.

Unter **Modelle & API** können Gemini, OpenAI, Anthropic, DeepSeek und OpenAI-kompatible Textserver wie Ollama/LM Studio mit Basis-URL und exakter Modell-ID hinzugefügt werden. In **Interpretation** lässt sich das Textmodell unabhängig von der Audioanalyse auswählen. Vor dem Versand ist eine ausdrückliche Zustimmung nötig. Anbieter können kostenpflichtig sein; es gibt keine pauschale Gratiszusage. Profilangaben bleiben lokal gespeichert, Schlüssel nur im Arbeitsspeicher. Diese Adapter sind für Textdeutung vorbereitet, nicht für beliebige Audio- oder Bildmodelle. Unterstützt werden die dokumentierten Chat-Completions- bzw. Messages-Protokolle, nicht automatisch jede proprietäre API.

KI-Deutungen werden automatisch gespeichert und beim erneuten Öffnen angezeigt. **Gesamtdeutung neu erstellen** umgeht ihren Cache; **Analyse-Cache löschen** entfernt auch die KI-Deutungen, erhält aber eigene Notizen und Audio. Getrennte Hörspuren werden separat gespeichert.

Die Diagnoseansicht zeigt lokale Fehlertypen, Codepositionen, Auftragsstatus und Laufzeiten. Jede Fehlermeldung enthält eine Fehler-ID zum Abgleich mit `data/logs/moodscope.log`. Die Logs rotieren bei 2 MB mit drei Sicherungen; Texte, Audio und Zugangsdaten werden nicht protokolliert.

### Öffentliche Aufnahmedaten

Unter **Songdetails** können Interpret und Titel bei MusicBrainz recherchiert werden. Suchtreffer werden erst nach Auswahl einer konkreten Aufnahme übernommen; verfügbare Mitwirkende, Instrumentangaben, Genres und Veröffentlichungen werden mit Quellenlink gezeigt. Fehlende Angaben werden nicht durch die KI erfunden. MusicBrainz benötigt für diese Abfragen keinen Key; private, nichtkommerzielle Nutzung ist kostenlos. Der Dienst kann zeitweise nicht erreichbar sein. Quellen: [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API), [Demucs](https://github.com/facebookresearch/demucs), [OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), [Anthropic Messages](https://platform.claude.com/docs/en/api/messages), [Ollama-Kompatibilität](https://docs.ollama.com/api/openai-compatibility).

### Verlauf

- Import von MP3, WAV und FLAC sowie einzelnen öffentlichen YouTube- und SoundCloud-Songlinks.
- Stereo-Wiedergabe, Lautstärke, Positionsregler und Sprünge in beide Richtungen.
- Audio- und Textkurven folgen der Wiedergabezeit; Textzeilen und Kurve können angesprungen werden.
- Automatische Lyrics-Suche bei LRCLIB anhand vorhandener Interpret-/Titel-Tags.
- Import synchronisierter LRC-Dateien oder Einfügen eigener zeitmarkierter Lyrics.
- Lokale Whisper-Transkription als zuschaltbarer Fallback.
- Anzeige von Modelltrennschärfe und Unsicherheit; diese sind keine kalibrierte Genauigkeit.

### Bibliothek

Importierte Songs, Analysen und eigene Notizen werden lokal in SQLite gespeichert. Identische Dateien werden auch bei geändertem Dateinamen erkannt. Bei unterschiedlichen Dateien mit gleichen Interpret-/Titel-Tags werden zusätzlich Laufzeit und zeitlich ausgerichtete akustische Signaturen verglichen. Metadaten alleine reichen nicht aus: Ein Remix, anderes Mastering oder eine andere Aufnahme soll keine unpassenden Zeitkurven erhalten.

Vorhandene Ergebnisse werden beim Import geladen, ohne erneut KI-Inferenz auszuführen. Bei geänderter Modellversion wird eine ältere Analyse als solche gekennzeichnet. **Neu analysieren** erzwingt eine neue Berechnung und umgeht Audio- und Gesamtanalyse-Cache. **Analyse-Cache löschen** entfernt gespeicherte Analyse-/KI-Deutungsergebnisse; eigene Notizen und die lokale Wiedergabedatei bleiben erhalten.

**Song vollständig entfernen** löscht einen Bibliothekseintrag einschließlich zugehöriger Analysen, KI-Deutungen, eigener Notizen, normalisierter Wiedergabekopie und Hörspuren. Gleich erkannte Importvarianten werden gemeinsam entfernt. **Gesamte Bibliothek entfernen** löscht alle verwalteten Songs und zugehörigen Daten. Beide Aktionen verlangen eine Bestätigung in der App. Ursprüngliche Musikdateien, heruntergeladene Modelle und Anbieterprofile bleiben erhalten.

### Songdetails

- Geschätztes Tempo mit librosa, Energie und spektrale Helligkeit.
- Relative CLAP-Ähnlichkeiten für mögliche Instrumente in mehreren Audioausschnitten.
- Eigene Angaben zu Genre, BPM, Instrumenten und Mitwirkenden.

Instrumenthinweise sind keine gesicherte Instrumentenliste. Eine tatsächliche Besetzung kann nicht zuverlässig allein aus einem Audiomix festgestellt werden. Manuelle Angaben sind als solche getrennt.

### Interpretation

Eine lokale Sprach-KI kann den Songtext oder eine ausgewählte Textzeile in ihrem Kontext deuten: mögliche Bedeutung, Verlust, Hoffnung, Widersprüche und alternative Lesarten. Dazu gibt es getrennte Audiohinweise aus vorhandenen Mess- und Modellwerten. Ein Sprachmodell darf nicht behaupten, selbst Audio gehört zu haben, wenn es nur Text erhalten hat.

Die KI-Deutung und **Meine eigene Interpretation** sind getrennte Bereiche. Eigene Notizen werden lokal gespeichert und nicht zur Online-KI gesendet. Interpretationen können trotz dieser Begrenzung falsch sein; sie sind keine gesicherten Aussagen über die Absicht eines Künstlers.

### Modelle & API

Die App erklärt im Modellbereich Zweck, ungefähre Downloadgröße und Speicherbedarf. Angeboten werden:

- CLAP kompakt oder CLAP Fusion für Audio Mood und Instrumenthinweise.
- XLM-EMO für mehrsprachige Textemotionen.
- Whisper Base oder Small für lokale Transkription.
- Qwen 1.5B oder 3B für lokale Song-/Zeilendeutung.

Downloads erfolgen nur aus einem kuratierten Katalog. Fremde Modell-Python-Skripte werden nicht ausgeführt. Größere Modelle sind nicht automatisch nachweislich genauer. Qwen 3B hat eigene Research-Lizenzbedingungen; vor einer Weiterverwendung prüfen. Downloadgrößen und VRAM-Angaben sind Richtwerte.

**Lokale KI bleibt der Standard, auch bei Internetverbindung.** Optional kann später ein eigener Gemini-Key eingetragen werden. Er bleibt nur im Arbeitsspeicher des lokalen Backends und wird nicht in SQLite, Git oder Browser-LocalStorage gespeichert. Ohne Key erfolgt keine Online-Inferenz.

## Voraussetzungen

- Python 3.10 oder neuer.
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

Danach [http://127.0.0.1:8765](http://127.0.0.1:8765) im Browser öffnen. Der Dienst liefert das gebaute Frontend aus. Strg+C beendet ihn.

Für das native Fenster:

```powershell
npm run tauri build -- --no-bundle
.\scripts\start.ps1 -Desktop
```

Nach einem nativen Build kann auch **Start-MoodScope.cmd** per Doppelklick verwendet werden. Der Starter verwendet die projektlokale Python-Umgebung und startet den lokalen Backend-Dienst bei Bedarf. Eine separat gestartete EXE braucht diesen Dienst ebenfalls.

Auf einem bereits eingerichteten Entwicklungsrechner kann ein separater Build unter `src-tauri/target/v03/release/` oder `src-tauri/target/v02/release/` liegen. Der Projektstarter wählt die neuere EXE aus diesen Ordnern und `src-tauri/target/release/`. Eine bereits geöffnete ältere App und ihr Backend müssen für Version 0.3 neu gestartet werden; ein älterer Dienst wird vom Starter erkannt.

## Installation und Start unter Linux

Nach Einrichtung der oben genannten Systemvoraussetzungen:

```bash
bash scripts/setup.sh
bash scripts/start.sh
# Native Entwicklung:
bash scripts/start.sh --desktop
# Nativer Build:
npm run tauri build -- --no-bundle
```

Windows- und Linux-Builds müssen auf ihren jeweiligen Zielsystemen geprüft werden. Ein erfolgreicher Windows-Build bestätigt keinen Linux-Build.

## YouTube- und SoundCloud-Links

Einmal das offizielle portable Downloadwerkzeug projektlokal einrichten:

```powershell
.venv\Scripts\python.exe scripts\setup_links.py
```

Unter Linux entsprechend `.venv/bin/python scripts/setup_links.py`. Der Installer lädt die offizielle yt-dlp-Standalone-Datei nach `.tools/yt-dlp/` und vergleicht deren SHA256 mit der offiziellen Release-Prüfsumme. Für YouTube benötigt yt-dlp zusätzlich eine unterstützte JavaScript-Laufzeit; MoodScope nutzt vorhandenes Node.js.

Im Linkfeld wird ein einzelner HTTPS-Songlink eingefügt. Playlists und SoundCloud-Kurzlinks werden nicht angenommen. Private, gelöschte oder gesperrte Inhalte können nicht importiert werden. Es werden keine Browser-Cookies oder Anmeldedaten übernommen. Bei einem Plattformfehler kann derselbe Song weiterhin als lokale Datei importiert werden. Nur Inhalte verwenden, die heruntergeladen und analysiert werden dürfen.

## Lokale Modelle einrichten

Im Reiter **Modelle & API** das gewünschte Modell herunterladen und auswählen. Beim ersten Analyselauf können benötigte Standardmodelle ebenfalls geladen werden. Gewichte liegen standardmäßig unter `models/`; die Auswahl und bekannte Download-Snapshots werden lokal unter `data/` gespeichert.

Die Interpretation entlädt vorher die Emotionsmodelle, um GPU-Speicher freizugeben. Beim nächsten Analyseauftrag werden diese wieder geladen. Ein kleineres Interpretationsmodell ist schneller, kann aber stärker vereinfachen oder Anweisungen missverstehen.

## Optionale Anbieterprofile

Unter **Modelle & API** stehen Gemini, OpenAI/ChatGPT, Anthropic Claude, DeepSeek, Ollama und LM Studio in einer gemeinsamen Profilverwaltung. Basis-URL, Protokoll und genaue Modell-ID können angepasst werden. Die Modell-ID muss beim gewählten Anbieter verfügbar sein; die App wählt keine unbekannten Ersatzmodelle. Gemini nutzt GenerateContent, Claude Messages und die anderen Vorlagen Chat Completions. [DeepSeek-Dokumentation](https://api-docs.deepseek.com/).

1. Anbieter vorbereiten, genaue Modell-ID und gegebenenfalls eigenen API-Key direkt in der App eingeben. Kein Key gehört in Quellcode, Issues oder Chatnachrichten.
2. Für Textdeutungen das Profil im Reiter **Interpretation** wählen und den Versand des Songtexts ausdrücklich erlauben. Die Audioanalyse kann dabei lokal bleiben.
3. Nur ein entsprechend eingerichtetes Gemini-Profil kann derzeit zusätzlich für **Audio-API verwenden** aktiviert werden. Danach den Audio-API-Modus ausdrücklich auswählen und Audio-/Lyrics-Versand erlauben. Textadapter für Claude, OpenAI, DeepSeek oder kompatible Server werden nicht als Audiomodelle ausgegeben.

OpenAI, Claude und DeepSeek können kostenpflichtig sein. Ein Chat-Abonnement ersetzt keinen API-Zugang. Es gibt keine Zusage kostenloser oder unbegrenzter API-Nutzung. Für die vorbereitete Gemini-Audiofunktion verlangt die App ein bestätigtes Projekt ohne aktivierte Abrechnung, kann den Abrechnungsstatus aber nicht selbst feststellen. Gratislimits und Datenverwendung können sich ändern. [Gemini-Preise](https://ai.google.dev/gemini-api/docs/pricing), [Audio-Dokumentation](https://ai.google.dev/gemini-api/docs/audio).

Profilname, Adresse und Modellwahl bleiben lokal gespeichert; API-Keys nur im Arbeitsspeicher bis zum Backend-Neustart. Profil entfernen entfernt seinen Sitzungs-Key. Lokale/LAN-Server können ohne Key arbeiten, können ihrerseits aber Cloud-Modelle verwenden. Kein automatischer Anbieterwechsel und keine automatischen kostenpflichtigen Wiederholungen. Im Audio-API-Modus wird kein lokales Whisper gestartet. Ohne Nutzer-Keys wurden echte Cloud-Inferenz und deren Kosten nicht live geprüft; Vertragstests ersetzen diesen Nachweis nicht.

## Analyseverfahren und Grenzen

Audio Mood nutzt ein vortrainiertes CLAP-Modell mit mehreren musikalischen Beschreibungen pro Emotionsklasse. Fünf-Sekunden-Anzeigefenster werden anhand von bis zu zehn Sekunden zentriertem Audiokontext geschätzt. Die Anzeige ist keine Messung mit Fünf-Sekunden-Genauigkeitsgarantie.

Lyric Mood nutzt XLM-EMO. Die Vorhersage für eine Textzeile wird mit ihrer unmittelbaren sprachlichen Umgebung kombiniert. LRC-Leerzeilen beenden den Textspan für Instrumentalpausen. Ungeschnittener Text ohne Zeitstempel wird nicht künstlich synchronisiert.

Biggest Split vergleicht die Audio-Valenz mit der nach Überlappungsdauer gemittelten Textvalenz. Ein Fenster benötigt mindestens 50 % Lyrics-Abdeckung. Prozent = absoluter Abstand / 2 × 100; das ist keine Sicherheit oder Trefferquote.

CLAP ist ein allgemeines Audio/Text-Modell, XLM-EMO wurde für Social-Media-Text trainiert. Die gemeinsame Valenzachse, Kontextmischung und Trennschärfe sind nicht wissenschaftlich gegeneinander kalibriert. Sarkasmus, mehrdeutige Zeilen, Gesang und ungewöhnliche Produktionen bleiben schwierig. BPM, Energie oder spektrale Helligkeit beweisen alleine keine Emotion.

Ein Diagnose-Set mit zwölf selbst geschriebenen deutschen und englischen Fällen ergab bisher für Einzelzeilen und Kontext jeweils 75 % richtige Valenzrichtung. Das ist ein kleiner Regressionstest und belegt keinen allgemeinen Genauigkeitsgewinn für Songs. Es werden keine Zufallskurven oder vorgetäuschten KI-Ergebnisse als Analyse ausgegeben.

## Tests und Entwicklung

```powershell
.venv\Scripts\python.exe -m pytest -q
npm test
npm run build
# Optionale echte Modellprüfungen:
.venv\Scripts\python.exe -m scripts.smoke_models
.venv\Scripts\python.exe -m scripts.evaluate_local
.venv\Scripts\python.exe -m scripts.smoke_pipeline
.venv\Scripts\python.exe -m scripts.smoke_interpretation
```

Echte Modelltests können Gewichte laden und GPU-Zeit benötigen. Normale Unit-/API-/DOM-Tests verwenden für gezielte Fehler- und UI-Fälle Mocks; solche Testwerte erscheinen nicht in der produktiven App. Die laufend aktualisierten Nachweise und Grenzen stehen in [docs/STATUS.md](docs/STATUS.md) und [docs/RELEASE-0.2.md](docs/RELEASE-0.2.md).

Für die Oberfläche `npm run dev` und für das Backend separat `.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765` starten. `VITE_API_URL` kann für eine getrennte Testumgebung gesetzt werden. `MOODSCOPE_DATA` wählt einen separaten Datenordner. Der Dienst ist nur für lokale Nutzung vorgesehen.

## Datenschutz und Veröffentlichung

Audio, Lyrics, Analysen, persönliche Notizen, API-Keys, Modelle und Testmusik werden nicht in Git aufgenommen. Auch lokale Werkzeuge, virtuelle Umgebungen, Installer und Screenshots sind ausgeschlossen. Standardmäßig bleiben Audio und Inferenz lokal; LRCLIB erhält nur bei Lyrics-Suche Interpret, Titel und Dauer. Linkimport greift auf die gewählte Plattform zu. Der ausdrücklich gewählte API-Modus sendet die dafür genannten Daten an Google.

Vor jedem Fortschritts-Commit und Upload prüft `scripts/check_publication.py` die ausgewählten Dateien. Mit `--ref HEAD` werden auch ältere erreichbare Dateiversionen und Commit-E-Mail-Adressen geprüft. Ein später gelöschtes Geheimnis bleibt ein Sperrgrund. Das ersetzt kein zusätzliches Lesen der Änderungen. Einzelheiten: [Veröffentlichungsablauf](docs/PUBLISHING.md).

## Noch offen

Eigenständige Installer mit eingebettetem Python-Backend, Signierung, Update-Verteilung und FFmpeg-Videoexport fehlen. Weitere Modellvarianten und Zielsysteme benötigen eigene Live- und Qualitätsprüfungen. Modellgewichte haben eigene Lizenzbedingungen und werden nicht mit dem Quellcode weiterverteilt.
