# MoodScope

MoodScope ist eine lokale Desktop-App für die Frage, wie unterschiedlich Musik und Text eines Songs wirken. Die App spielt einen Song ab und zeigt zwei synchronisierte emotionale Verläufe:

- **Audio Mood:** der geschätzte musikalische Ausdruck.
- **Lyric Mood:** die geschätzte Bedeutung der gesungenen Wörter.
- **Biggest Split:** das Zeitfenster mit dem größten berechneten Unterschied zwischen beiden Verläufen.

React und TypeScript bilden die Oberfläche, Tauri das native Fenster und Python/FastAPI den lokalen Analysedienst. Windows 10/11 und Linux sind die Zielplattformen. Dies ist eine Entwicklungsversion, kein fertig paketierter Endkundeninstaller.

## Funktionen

Neu in Version 0.3: ausführlichere Gesamt- und Zeilendeutung, automatisches Wiederanzeigen gespeicherter KI-Deutungen, lokales Hörstudio mit Demucs, SoundCloud-Suchtreffer-Auswahl, automatische Recherche-Fallbacks und gemeinsame Anbieterprofile einschließlich Gemini und DeepSeek. Der aktuelle Nachweisstand steht in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

### Hörstudio und Diagnose

Im Reiter **Hörstudio** lassen sich Gesang, Schlagzeug, Bass und übrige Instrumente lokal trennen, solo hören und mischen. Der automatische Qualitätsmodus verwendet das Fine-tuned-Ensemble, passt Versatzmittelung anhand gemessener Transienten an und korrigiert die Rekonstruktionssumme. Das ist kein Beweis besserer Instrumentisolation auf jedem Song. Optional bietet das experimentelle Sechs-Spur-Modell zusätzlich Gitarre und Klavier. Alle Sänger bleiben in einer gemeinsamen Gesangsspur. Übersprechen und Artefakte sind möglich; die Emotionskurven gelten weiterhin für den Originalmix.

Vorher die optionale Erweiterung projektlokal installieren: `python -m pip install -r backend/requirements-separation.txt` in der aktivierten venv. Die torchaudio-Version muss zum vorhandenen PyTorch-/CUDA-Build passen. Der erste Trennlauf lädt die offiziellen Demucs-Gewichte nach `models/demucs/`. Ergebnisse liegen unter `data/stems/`.

Unter **Modelle & API** können Gemini, OpenAI, Anthropic, DeepSeek und OpenAI-kompatible Textserver wie Ollama/LM Studio mit Basis-URL und exakter Modell-ID hinzugefügt werden. In **Interpretation** lässt sich das Textmodell unabhängig von der Audioanalyse auswählen. Vor dem Versand ist eine ausdrückliche Zustimmung nötig. Anbieter können kostenpflichtig sein; es gibt keine pauschale Gratiszusage. Profilangaben bleiben lokal gespeichert, Schlüssel nur im Arbeitsspeicher. Diese Adapter sind für Textdeutung vorbereitet, nicht für beliebige Audio- oder Bildmodelle. Unterstützt werden die dokumentierten Chat-Completions- bzw. Messages-Protokolle, nicht automatisch jede proprietäre API.

KI-Deutungen werden automatisch gespeichert und beim erneuten Öffnen angezeigt. **Gesamtdeutung neu erstellen** umgeht ihren Cache; **Analyse-Cache löschen** entfernt auch die KI-Deutungen, erhält aber eigene Notizen und Audio. Getrennte Hörspuren werden separat gespeichert.

Die Diagnoseansicht zeigt lokale Fehlertypen, Codepositionen, Auftragsstatus und Laufzeiten. Jede Fehlermeldung enthält eine Fehler-ID zum Abgleich mit `data/logs/moodscope.log`. Die Logs rotieren bei 2 MB mit drei Sicherungen; Texte, Audio und Zugangsdaten werden nicht protokolliert.

### Öffentliche Aufnahmedaten

Unter **Songdetails** läuft die Suche automatisch über MusicBrainz, Apple iTunes und Deezer. Leere Suchen versuchen bereinigte Plattformtitel und eine Suche ohne Interpret. Ausgefallene Quellen werden sichtbar angezeigt. Passende Interpret-/Titel-/Versionsangaben werden anhand der Songlänge geordnet. Die automatische Auswahl prüft bis zu drei kompatible Treffer auf Instrumentcredits; mehrdeutige Treffer müssen ausgewählt werden. Für Instrumentcredits werden verknüpfte **Discogs-Veröffentlichungen** und ergänzende **Wikidata-Werkdaten** abgefragt. Discogs-Releaseabrufe funktionieren hier ohne Key; eine anmeldepflichtige Discogs-Such-API wird nicht verwendet. Tonartangaben können zusätzlich aus verknüpften MusicBrainz-Werken und [Wikidata P826](https://www.wikidata.org/wiki/Property:P826) stammen; sie bestätigen nicht automatisch die Tonart eines Remixes. Song-, Album- und Werkangaben bleiben getrennt und tragen Quellenlinks. Nicht jede Aufnahme hat vollständige Credits, insbesondere Mashups. Quellen: [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API), [Discogs API-Client](https://github.com/discogs/discogs_client/blob/master/docs/quickstart.md), [Wikidata Instrumentierung](https://www.wikidata.org/wiki/Property:P870), [Demucs](https://github.com/facebookresearch/demucs).

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

- Lokale Tonart-Kandidaten, zeitliche Dur-/Moll-Dreiklangschätzungen, Tempo, Beat-Regelmäßigkeit, Energie, spektrale Helligkeit und Dynamik. Unter **Methode & Werte** sind Messung, Unsicherheit und tatsächliche Rechenbeiträge einsehbar.
- Die Endvalenz ergänzt CLAP um eine explizite Merkmalskorrektur (maximal ±0,12); Dynamik beeinflusst die Aktivierung. Diese Regeln sind heuristisch, keine wissenschaftlich kalibrierte Emotionsmessung. Septakkorde, Umkehrungen und Modulationen werden nicht zuverlässig transkribiert.
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

Unter **Modelle & API** gibt es zusätzlich **Eigenes Modell hinzufügen**. Unterstützt werden öffentliche Hugging-Face-Modellseiten mit kompatibler Architektur: CLAP für Audio, BERT/RoBERTa/XLM-RoBERTa mit exakt den vier erwarteten Emotionslabels für Lyrics, unterstützte Transformers-Instruct-Modelle mit Chat-Template für Interpretation sowie konvertiertes CTranslate2-Whisper. Die App erklärt die Anforderungen am Linkfeld, prüft Konfiguration und Format und fixiert eine unveränderliche Revision. Eigene Transformers-Modelle benötigen Safetensors, eigener Python-Code ist ausgeschlossen. GGUF/Ollama wird über Serverprofile eingebunden. Ein erfolgreicher Architekturcheck garantiert noch keine Qualität oder passende Speicherausstattung.

**Entfernen** löscht verwaltete lokale Modellgewichte; bei eigenen Modellen auch den Eintrag. Aktive Auswahl fällt auf den Standard zurück. Songs, gespeicherte Analysen und Notizen bleiben erhalten. Der Standard kann beim nächsten Analyselauf erneut geladen werden. Abgebrochene Downloads werden nicht als installierte Modelle angeboten; teilweise geladene Dateien können beim erneuten Download wiederverwendet werden. Größere Modelle sind nicht automatisch genauer; Modelllizenzen prüfen.

**Lokale KI bleibt der Standard, auch bei Internetverbindung.** Eigene Anbieterprofile können für optionale Serverdeutungen eingerichtet werden. Schlüssel bleiben nur im Arbeitsspeicher des lokalen Backends. Ohne explizite Wahl und Zustimmung erfolgt keine Online-Inferenz.

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
.venv-modern\Scripts\python.exe scripts\setup_links.py
```

Unter Linux entsprechend `.venv-modern/bin/python scripts/setup_links.py`. Der Installer lädt die offizielle yt-dlp-Standalone-Datei nach `.tools/yt-dlp/` und vergleicht deren SHA256 mit der offiziellen Release-Prüfsumme. Für YouTube benötigt yt-dlp zusätzlich eine unterstützte JavaScript-Laufzeit; MoodScope nutzt vorhandenes Node.js.

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

**Neustarten / Beenden:** Die Knöpfe steuern den eigenen MoodScope-Dienst und dessen Modellprozesse. Sie benötigen den Projektstarter oder `python -m scripts.service --port 8765`. Ein direkt gestartetes Uvicorn bietet diese Steuerung bewusst nicht an. Beim Neustart wird die Wiedergabe beendet, der Backend-Prozess ersetzt und die Oberfläche neu geladen; gespeicherte Daten bleiben erhalten. Beenden schließt zusätzlich das native Fenster. Im Browser bleibt eine Beendet-Seite stehen; andere Browser-Tabs werden nicht geschlossen.

Songdetails enthalten zusätzlich verfügbare Originalformat-/Tagangaben. Öffentliche Katalogdaten werden beim Import anhand geeigneter Song-Tags gesucht; mehrdeutige Aufnahmen müssen bestätigt werden. **Metadaten neu recherchieren** fragt die Dienste erneut ab und ersetzt die bisherigen Recherchewerte; **Ausgewählte Aufnahme neu recherchieren** aktualisiert die bestätigte Aufnahme. Eigene Angaben bleiben getrennt. Der Analyse-Cache umfasst auch recherchierte Aufnahmeinformationen und die gespeicherte Auswahl.

Im Hörstudio werden nahezu leere Modellspuren anhand ihrer relativen Energie ausgeblendet. Das ist kein Nachweis realer Instrumentanwesenheit. Falsch zugeordnete Gruppen lassen sich manuell ausblenden und wieder anzeigen.

```powershell
.venv-modern\Scripts\python.exe -m pytest -q
npm test
npm run build
# Optionale echte Modellprüfungen:
.venv-modern\Scripts\python.exe -m scripts.smoke_models
.venv-modern\Scripts\python.exe -m scripts.evaluate_local
.venv-modern\Scripts\python.exe -m scripts.smoke_pipeline
.venv-modern\Scripts\python.exe -m scripts.smoke_interpretation
```

Echte Modelltests können Gewichte laden und GPU-Zeit benötigen. Normale Unit-/API-/DOM-Tests verwenden für gezielte Fehler- und UI-Fälle Mocks; solche Testwerte erscheinen nicht in der produktiven App. Die laufend aktualisierten Nachweise und Grenzen stehen in [docs/STATUS.md](docs/STATUS.md) und [docs/RELEASE-0.2.md](docs/RELEASE-0.2.md).

Für die Oberfläche `npm run dev` und für das Backend separat `.venv-modern\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765` starten. `VITE_API_URL` kann für eine getrennte Testumgebung gesetzt werden. `MOODSCOPE_DATA` wählt einen separaten Datenordner. Der Dienst ist nur für lokale Nutzung vorgesehen.

## Datenschutz und Veröffentlichung

Audio, Lyrics, Analysen, persönliche Notizen, API-Keys, Modelle und Testmusik werden nicht in Git aufgenommen. Auch lokale Werkzeuge, virtuelle Umgebungen, Installer und Screenshots sind ausgeschlossen. Standardmäßig bleiben Audio und Inferenz lokal; LRCLIB erhält nur bei Lyrics-Suche Interpret, Titel und Dauer. Linkimport greift auf die gewählte Plattform zu. Der ausdrücklich gewählte API-Modus sendet die dafür genannten Daten an Google.

Vor jedem Fortschritts-Commit und Upload prüft `scripts/check_publication.py` die ausgewählten Dateien. Mit `--ref HEAD` werden auch ältere erreichbare Dateiversionen und Commit-E-Mail-Adressen geprüft. Ein später gelöschtes Geheimnis bleibt ein Sperrgrund. Das ersetzt kein zusätzliches Lesen der Änderungen. Einzelheiten: [Veröffentlichungsablauf](docs/PUBLISHING.md).

## Noch offen

Eigenständige Installer mit eingebettetem Python-Backend, Signierung, Update-Verteilung und FFmpeg-Videoexport fehlen. Weitere Modellvarianten und Zielsysteme benötigen eigene Live- und Qualitätsprüfungen. Modellgewichte haben eigene Lizenzbedingungen und werden nicht mit dem Quellcode weiterverteilt.

## Sprache und Bedienung

In der Kopfzeile zwischen **Deutsch** und **English** wechseln. Die Auswahl bleibt auf diesem Rechner gespeichert. Englisch gilt auch für neue KI-Gesamtdeutungen, Zeilendeutungen und musikalische Begründungen. Vorhandene Deutungen werden pro Sprache gespeichert; beim Sprachwechsel eine neue Deutung starten, wenn noch keine vorliegt. Original-Lyrics, Metadaten und eigene Notizen werden nicht automatisch übersetzt. Die Texterkennungssprache ist davon unabhängig.

Neustart und Beenden verwenden einen Bestätigungsdialog im App-Design. **Abbrechen** oder Escape schließt ihn ohne Dienstaufruf. Ein bestätigter Neustart beendet laufende Aufträge; gespeicherte Songs bleiben erhalten.

Vibe-coded mit Codex. Modellschätzungen und generierte Interpretationen bleiben überprüfungsbedürftig.

Bekannte Sicherheitsgrenzen und noch offene Bibliotheksmeldungen: [Sicherheitsstand](docs/SECURITY.md).

Native Release-Builds müssen die Oberfläche einbetten. `npm run tauri build -- --no-bundle` übernimmt dies; ein direkter Cargo-Aufruf benötigt `--features tauri/custom-protocol`. Ein Build-Schutz verhindert Release-Dateien, die versehentlich den Entwicklungsserver benötigen.

## Hörstudio, Analysebericht und Atmosphäre

Ausgeblendete Spuren bleiben im Bereich **Ausgeblendete Spuren** direkt wiederherstellbar. Das gilt auch für automatisch als leise eingestufte Gruppen. Pro erzeugter Spur lassen sich Pegel setzen und mit **Mix anwenden** gemeinsam anhören. **Demucs Fine-tuned** bietet ein aufwendigeres Vier-Gruppen-Ensemble; die Sechs-Gruppen-Variante ergänzt experimentelle Gitarre/Klavier. Katalogeinträge erzeugen keine zusätzlichen Audiospuren.

**Methode & Werte** zeigt pro Song und Abschnitt die gespeicherten Ähnlichkeiten, Kontextfenster, Gewichtung und Valenzrechnung. Messwerte wie BPM und spektrale Helligkeit sind getrennt von dieser Formel. **Atmosphäre** im Player schaltet ein sphärisches Visual ein; Farben folgen den Mood-Werten, Bewegung der Wiedergabe und gespeicherten RMS-Energie. Kein Live-Frequenzspektrum. Reduzierte Bewegung wird respektiert.

Die Bestätigungen für Bibliotheks-/Cache-Aktionen und Anbieterprofile verwenden denselben Dialog wie Neustart/Beenden. Ein fehlgeschlagener Bibliotheks-Refresh nach erfolgreichem Löschen stellt keine gelöschte Audioadresse mehr her. Modelldownloads für Demucs haben Zeit-/Größenlimits, atomare Dateien und die Prüfsummen des Herausgebers; das Laden erzwingt `weights_only=True` mit einer engen Typfreigabe für die kuratierten HTDemucs-Pakete.

Die optionale **Atmosphäre** färbt das gesamte Layout anhand der analysierten Stimmung. Nebel-/Wasserbewegungen folgen Wiedergabe, geschätztem Tempo und gespeicherter Energie, keinem Live-Frequenzspektrum. Pausieren hält sie an; reduzierte Bewegung wird respektiert. F11 schaltet im nativen Fenster Vollbild um; im Browser gilt dessen Vollbildfunktion.

**Bedienweg:** Bibliothek → Songdetails → Stimmungsverlauf → Methode & Werte → Hörstudio → Interpretation. **Modelle & API** ist ein eigener Hauptbereich links unter **Song-Analyse**. Der letzte Song-Reiter und die Wiedergabe bleiben beim Wechsel erhalten.

**Aufträge abbrechen:** Im globalen Auftragsbanner kann ein laufender Download, Import oder Analyseauftrag abgebrochen werden. Die App wartet gegebenenfalls auf einen aktuellen GPU-Schritt oder Netzwerkaufruf. Bereits abgeschlossene Zwischencaches dürfen wiederverwendbar bleiben; eine unvollständige neue Gesamtanalyse wird nicht als fertig ausgegeben. Synchrone Metadatenabfragen sind zeitlich begrenzt, haben aber noch keinen eigenen Auftragsabbruch.

**Neustart bei veraltetem Dienst:** Neustarten ersetzt den Backend-Prozess; im nativen Modus wird auch das Fenster über den Projektstarter neu geöffnet und die neueste vorhandene EXE gewählt. Im Browser wird die Oberfläche neu geladen. Eine bereits beendete Sitzung zeigt einen eigenen Abschlussbildschirm.

### Live-Mix, Export und A/B-Loop

Im Hörstudio steuert **Live-Mix** die Pegel der tatsächlichen Audiospuren direkt per Web Audio. Solo, Spurwahl und Regler benötigen keine neu gerenderte Mixdatei; Pause, Positionssprünge und Abhörlautstärke folgen dem Hauptplayer. Die Spuren werden lokal gestreamt. Bei Browser-/Audioproblemen lässt sich Live-Mix ausschalten und der dateibasierte Mix verwenden.

Jede erzeugte Spur lässt sich als WAV exportieren. **Mix als WAV exportieren** rendert die gewählten Spuren mit ihren eingestellten Pegeln; die Abhörlautstärke beeinflusst den Export nicht. Bei Übersteuerung wird der gesamte Mix gleichmäßig abgesenkt. Originaldateien werden nicht verändert. Exportformat ist derzeit WAV, keine MP3-/FLAC-Ausgabe und kein gespeichertes Mix-Preset.

Rechtsklick auf die untere Positionsleiste setzt zuerst A, dann B. Der Bereich wird bei Wiedergabe wiederholt; ein dritter Rechtsklick entfernt beide Markierungen. Zwei Punkte in umgekehrter Reihenfolge werden geordnet. Die A/B-Schaltfläche oder Shift+F10 setzen den Punkt an der aktuellen Position. Neben **Song importieren** steht zusätzlich **Song neu analysieren**.

Dropdowns verwenden in aktuellen Chromium-/WebView2-Browsern ein gestaltetes natives Auswahlmenü; Tastatur- und Fokussteuerung bleiben erhalten. Ältere Browser behalten die dunkel gestaltete Standardauswahl. Animationen respektieren die Betriebssystemoption für reduzierte Bewegung.
