# MoodScope

MoodScope ist eine lokale Desktop-App für die Frage, wie unterschiedlich Musik und Text eines Songs wirken. Die App spielt einen Song ab und zeigt zwei synchronisierte emotionale Verläufe:

- **Audio Mood:** der geschätzte musikalische Ausdruck.
- **Lyric Mood:** die geschätzte Bedeutung der gesungenen Wörter.
- **Biggest Split:** das Zeitfenster mit dem größten berechneten Unterschied zwischen beiden Verläufen.

React und TypeScript bilden die Oberfläche, Tauri das native Fenster und Python/FastAPI den lokalen Analysedienst. Windows 10/11 und Linux sind die Zielplattformen. Dies ist eine Entwicklungsversion, kein fertig paketierter Endkundeninstaller.

Der eigene Projektcode steht unter der [MIT-Lizenz](LICENSE). Bibliotheken,
Modelle und Datensätze behalten ihre jeweiligen Lizenzen; insbesondere stehen
die optionalen MERT-Gewichte nicht unter MIT. Details und geprüfte Alternativen:
[Emotionsmodelle](docs/EMOTION-MODELS.md).

Die CLAP-Valenz ist eine Projektion von Beschreibungsähnlichkeiten mit festen
Gewichten. Ein hoher Ärger-Score bestätigt kein empfundenes Gefühl. Auch der
optionale Music2Emo-Verlauf ist experimentell: Der bisherige dynamische
Referenzvergleich belegt noch keine präzise Erkennung von Stimmungswechseln.

## Funktionen

Neu in Version 0.3: ausführlichere Gesamt- und Zeilendeutung, automatisches Wiederanzeigen gespeicherter KI-Deutungen, lokales Hörstudio mit Demucs, SoundCloud-Suchtreffer-Auswahl, automatische Recherche-Fallbacks und gemeinsame Anbieterprofile einschließlich Gemini und DeepSeek. Der aktuelle Nachweisstand steht in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

### Hörstudio und Diagnose

Im Reiter **Hörstudio** lassen sich Gesang, Schlagzeug, Bass und übrige Instrumente lokal trennen, solo hören und mischen. Der automatische Qualitätsmodus verwendet das Fine-tuned-Ensemble, passt Versatzmittelung anhand gemessener Transienten an und korrigiert die Rekonstruktionssumme. Das ist kein Beweis besserer Instrumentisolation auf jedem Song. Optional bietet das experimentelle Sechs-Spur-Modell zusätzlich Gitarre und Klavier. Alle Sänger bleiben in einer gemeinsamen Gesangsspur. Übersprechen und Artefakte sind möglich; die Emotionskurven gelten weiterhin für den Originalmix.

Vorher die optionale Erweiterung projektlokal installieren: `python -m pip install -r backend/requirements-separation.txt` in der aktivierten venv. Die torchaudio-Version muss zum vorhandenen PyTorch-/CUDA-Build passen. Der erste Trennlauf lädt die offiziellen Demucs-Gewichte nach `models/demucs/`. Ergebnisse liegen unter `data/stems/`.

Unter **Modelle & API** können Gemini, OpenAI, Anthropic, DeepSeek und OpenAI-kompatible Textserver wie Ollama/LM Studio mit Basis-URL und exakter Modell-ID hinzugefügt werden. In **Interpretation** lässt sich das Textmodell unabhängig von der Audioanalyse auswählen. Vor dem Versand ist eine ausdrückliche Zustimmung nötig. Anbieter können kostenpflichtig sein; es gibt keine pauschale Gratiszusage. Profilangaben bleiben lokal gespeichert, Schlüssel nur im Arbeitsspeicher. Diese Adapter sind für Textdeutung vorbereitet, nicht für beliebige Audio- oder Bildmodelle. Unterstützt werden die dokumentierten Chat-Completions- bzw. Messages-Protokolle, nicht automatisch jede proprietäre API.

KI-Deutungen werden automatisch gespeichert und beim erneuten Öffnen angezeigt. Gesamt- und Zeilendeutung werden getrennt aufbewahrt; eine Zeilendeutung überschreibt die Gesamtdeutung nicht. **Gesamtdeutung neu erstellen** umgeht ihren Cache; **Analyse-Cache löschen** entfernt auch die KI-Deutungen, erhält aber eigene Notizen und Audio. Getrennte Hörspuren werden separat gespeichert.

Die Diagnoseansicht zeigt lokale Fehlertypen, Codepositionen, Auftragsstatus und Laufzeiten. Jede Fehlermeldung enthält eine Fehler-ID zum Abgleich mit `data/logs/moodscope.log`. Die Logs rotieren bei 2 MB mit drei Sicherungen; Texte, Audio und Zugangsdaten werden nicht protokolliert.

### Öffentliche Aufnahmedaten

Unter **Songdetails** läuft die Suche automatisch über MusicBrainz, Apple iTunes und Deezer. Leere Suchen versuchen bereinigte Plattformtitel und eine Suche ohne Interpret. Ausgefallene Quellen werden sichtbar angezeigt. Passende Interpret-/Titel-/Versionsangaben werden anhand der Songlänge geordnet. Die automatische Auswahl prüft bis zu drei kompatible Treffer auf Instrumentcredits; mehrdeutige Treffer müssen ausgewählt werden. Für Instrumentcredits werden verknüpfte **Discogs-Veröffentlichungen** und ergänzende **Wikidata-Werkdaten** abgefragt. Discogs-Releaseabrufe funktionieren hier ohne Key; eine anmeldepflichtige Discogs-Such-API wird nicht verwendet. Tonartangaben können zusätzlich aus verknüpften MusicBrainz-Werken und [Wikidata P826](https://www.wikidata.org/wiki/Property:P826) stammen; sie bestätigen nicht automatisch die Tonart eines Remixes. Song-, Album- und Werkangaben bleiben getrennt und tragen Quellenlinks. Nicht jede Aufnahme hat vollständige Credits, insbesondere Mashups. Quellen: [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API), [Discogs API-Client](https://github.com/discogs/discogs_client/blob/master/docs/quickstart.md), [Wikidata Instrumentierung](https://www.wikidata.org/wiki/Property:P870), [Demucs](https://github.com/facebookresearch/demucs).

### Verlauf

- Import von MP3, WAV und FLAC sowie einzelnen öffentlichen YouTube- und SoundCloud-Songlinks.
- Stereo-Wiedergabe, Lautstärke, Positionsregler und Sprünge in beide Richtungen.
- Audio- und Textkurven folgen der Wiedergabezeit; Textzeilen können angesprungen und die Position in der Kurve gezogen werden. A/B-Loops werden per Rechtsklick in Kurve oder Player gemeinsam gesetzt und mit dem dritten Rechtsklick entfernt.
- Automatische Lyrics-Suche bei LRCLIB anhand vorhandener Interpret-/Titel-Tags.
- Import synchronisierter LRC-Dateien oder Einfügen eigener zeitmarkierter Lyrics.
- Lokale Whisper-Transkription als zuschaltbarer Fallback.
- Anzeige von Modelltrennschärfe und Formulierungssensitivität; diese sind keine kalibrierte Genauigkeit.
- Gemeinsame Einordnung von Musik und Text direkt an der bestehenden Kurve: zeitliche Übereinstimmung, Kontrast und unzureichende oder unsichere Belege. Die kombinierte Interpretation verwendet dieselbe ausgewählte Musikquelle. [Methode und Nachweisgrenzen](docs/COMBINED-ANALYSIS.md).
- Die vorhandenen Emotionsbalken folgen fließend der Wiedergabe; der Rechenweg darunter zeigt die gespeicherten Abschnittswerte. Musikalische Hinweise und persönliche Gefühlsreaktionen werden erläutert. [Forschungsgrundlage](docs/MUSIC-PSYCHOLOGY.md).
- Im Atmosphärenmodus prägt die führende Audio-Kategorie die Grundfarbe; kleinere Farbanteile mischen sich dezent darunter. Textfarben bleiben im Hintergrund zurückhaltend. Die Farbmischung verändert keine Analysewerte.
- Lokale Emotionskurve v7: konstanter Analysepegel je Kontext, keine festen Emotionszuschläge durch musikalische Merkmale und keine zusätzliche Dreipunktglättung. Original-RMS und Wiedergabe bleiben erhalten. Bestehende Analysen verwenden weiterhin ihre gespeicherte Methode; Neu analysieren verwendet v7.

### Bewertungsmodell der Audio-/Lyrics-Kurve

Direkt unter der vorhandenen Kurve lässt sich **Audio-Bewertungsmodell** öffnen.
Die Audioquelle bleibt beim Wechsel zwischen Stimmungsverlauf und Methode & Werte aktiv.
Eine sichtbare Modellauswahl steht in beiden Ansichten bereit. Im Abschnittsbericht
stehen Kraft und Energie separat unter Klangcharakter; sie werden nicht in Aerger
umgerechnet. Vor-/Zurueck-Tasten waehlen gemessene Abschnitte.

**Music2Emo verwenden** setzt einen aktuellen gespeicherten Vergleich in dieselbe
Audio-/Lyrics-Kurve ein. **Music2Emo berechnen und verwenden** startet die lokale
Berechnung. Die Audio-Kennzahl und **Biggest Split** folgen der Auswahl; Lyrics
bleiben ihre eigenen Textschätzungen. **CLAP verwenden** stellt die bisherige
Audio-Bewertung wieder her. Die Wahl wird lokal gemerkt. Ohne ausdrückliche CLAP-Wahl wird die eingerichtete
lokale Music2Emo-Erweiterung bevorzugt: Ein aktueller Cache wird geladen, ein
fehlender oder veralteter Verlauf einmalig lokal berechnet. Es gibt keinen
automatischen Modelldownload.

Music2Emo verwendet bis zu 30 Sekunden Kontext und 5-Sekunden-Schritte. Es trifft
auf dem bisherigen Referenzsatz das allgemeine Niveau besser, schnelle Übergänge
sind weiter unzureichend validiert. Bei Music2Emo verwenden die vorhandenen Gefühlsbalken echte gelernte Hinweise:
Freude, Ruhe, Trauer, Melancholie, Zuversicht, Romantik, Kraft, Energie und
Entspannung. Die unabhängigen Scores laufen von 0 bis 1 und addieren sich nicht
zu 100 Prozent. Kurve, Balken und Atmosphärenfarben verwenden dieselbe Quelle;
Kraft wird nicht automatisch als Ärger interpretiert. Bei CLAP bleiben seine
sechs ursprünglichen Beschreibungsanteile und die gespeicherte Rechnung sichtbar.
Zusätzliche Vergleichsdiagramme werden nicht eingeblendet.

Die Erweiterung wird nicht automatisch heruntergeladen. Lokale Einrichtung,
getrennte Basisumgebung und Lizenzbedingungen stehen in
[docs/EMOTION-MODELS.md](docs/EMOTION-MODELS.md). Abbruch beendet den separaten
Modellprozess. Vergleichsdaten werden mit dem Analyse-Cache entfernt.

### Bibliothek

Importierte Songs, Analysen und eigene Notizen werden lokal in SQLite gespeichert. Identische Dateien werden auch bei geändertem Dateinamen erkannt. Bei unterschiedlichen Dateien mit gleichen Interpret-/Titel-Tags werden zusätzlich Laufzeit und zeitlich ausgerichtete akustische Signaturen verglichen. Metadaten alleine reichen nicht aus: Ein Remix, anderes Mastering oder eine andere Aufnahme soll keine unpassenden Zeitkurven erhalten.

Vorhandene Ergebnisse werden beim Import geladen, ohne erneut KI-Inferenz auszuführen. Bei geänderter Modellversion wird eine ältere Analyse als solche gekennzeichnet. **Neu analysieren** erzwingt eine neue Berechnung und umgeht Audio- und Gesamtanalyse-Cache. **Analyse-Cache löschen** entfernt gespeicherte Analysen, KI-Deutungen und Recherchewerte. Eigene Notizen, Wiedergabekopie und erzeugte Hörspuren bleiben erhalten; ausgeblendete Spuren werden zurückgesetzt. Beim Öffnen eines Songs aus der Bibliothek wird ein vorhandener Analyse-Cache geladen. Fehlt er, startet automatisch derselbe Recherche-, Lyrics- und Analyseablauf wie beim ersten Import. Das Löschen allein startet noch keine neue Analyse. **Song neu analysieren** erzwingt jederzeit eine neue Berechnung.

**Song vollständig entfernen** löscht einen Bibliothekseintrag einschließlich zugehöriger Analysen, KI-Deutungen, eigener Notizen, normalisierter Wiedergabekopie und Hörspuren. Gleich erkannte Importvarianten werden gemeinsam entfernt. **Gesamte Bibliothek entfernen** löscht alle verwalteten Songs und zugehörigen Daten. Beide Aktionen verlangen eine Bestätigung in der App. Ursprüngliche Musikdateien, heruntergeladene Modelle und Anbieterprofile bleiben erhalten.

### Songdetails

- Lokale Tonart-Kandidaten, zeitliche Akkordkandidaten einschließlich Sept-, verminderten, übermäßigen und sus-Akkorden, Tempo, Beat-Regelmäßigkeit, Energie, spektrale Helligkeit und Dynamik. Unter **Methode & Werte** sind Messung, Unsicherheit und tatsächliche Rechenbeiträge einsehbar.
- Neue Analysen verwenden die pegelkontrollierte CLAP-Projektion v7 ohne feste Valenzzuschläge oder nachträgliche Dreipunktglättung. Tonart, Akkorde und Dynamik bleiben getrennte Musikbelege. Ältere Analysen zeigen weiterhin ihre damals verwendeten heuristischen Beiträge.
- Relative CLAP-Ähnlichkeiten für mögliche Instrumente in mehreren Audioausschnitten.
- Eigene Angaben zu Genre, BPM, Instrumenten und Mitwirkenden.

Instrumenthinweise sind keine gesicherte Instrumentenliste. Eine tatsächliche Besetzung kann nicht zuverlässig allein aus einem Audiomix festgestellt werden. Manuelle Angaben sind als solche getrennt.

### Interpretation

Eine lokale Sprach-KI kann den Songtext oder eine ausgewählte Textzeile in ihrem Kontext deuten: mögliche Bedeutung, Verlust, Hoffnung, Widersprüche und alternative Lesarten. Dazu gibt es getrennte Audiohinweise aus vorhandenen Mess- und Modellwerten. Ein Sprachmodell darf nicht behaupten, selbst Audio gehört zu haben, wenn es nur Text erhalten hat.

Die zunächst ausgeschaltete Option **Musikbelege einbeziehen** ergänzt einen
experimentellen Vergleich von Text und Musikbeobachtungen. Das Modell erhält
zeitlich zugeordnete Energie-, Tempo- und Harmoniekandidaten mit Belegreferenzen.
Die genauen Messwerte erscheinen separat; hohe Energie wird keinem bestimmten
Gefühl gleichgesetzt. Textdeutung und Musikvergleich werden getrennt gespeichert.
Kleine lokale Modelle können dabei weiterhin scheitern oder unplausibel deuten;
unbelegte Antworten werden verworfen. Es erfolgt kein automatischer Anbieterwechsel.

Der [Vergleich spezialisierter Musikmodelle](docs/EMOTION-MODELS.md) dokumentiert
Music2Emo, Moody und AudioMuse sowie das neue getrennte Offline-Vergleichswerkzeug.

Der [externe Vergleich mit menschlichen Musikbewertungen](docs/HUMAN-REFERENCE.md)
beschreibt die verwendeten Referenzen und ihre Grenzen. Die neue lokale Methode v7 kontrolliert den Analysepegel und verzichtet auf feste
Valenzzuschlaege durch Tempo, Helligkeit und Harmonie. Das ist noch kein Nachweis
einer genaueren Emotionserkennung. Insbesondere sind ausgelöste Gefühle und wahrgenommener Ausdruck
unterschiedliche Bewertungsziele.

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

Unter **Modelle & API** stehen Gemini, OpenAI/ChatGPT, Mistral/Voxtral, Anthropic Claude, DeepSeek, Ollama und LM Studio in einer gemeinsamen Profilverwaltung. Basis-URL, Protokoll und genaue Modell-ID können angepasst werden. Die Modell-ID muss beim gewählten Anbieter verfügbar sein; die App wählt keine unbekannten Ersatzmodelle. Gemini nutzt GenerateContent, Claude Messages und die anderen Vorlagen Chat Completions. [DeepSeek-Dokumentation](https://api-docs.deepseek.com/).

1. Anbieter vorbereiten, genaue Modell-ID und gegebenenfalls eigenen API-Key direkt in der App eingeben. Kein Key gehört in Quellcode, Issues oder Chatnachrichten.
2. Für Textdeutungen das Profil im Reiter **Interpretation** wählen und den Versand des Songtexts ausdrücklich erlauben. Die Audioanalyse kann dabei lokal bleiben.
3. Ein entsprechend eingerichtetes Gemini-Profil oder ein ausdrücklich audiotaugliches OpenAI-kompatibles Profil kann für **Audio-API verwenden** aktiviert werden. Dazu gehören geeignete OpenAI-, Mistral/Voxtral- und eigene Audiomodelle. Danach den API-Modus ausdrücklich auswählen und der Übertragung zustimmen. Reine Textprofile werden nicht als Audiomodelle ausgegeben.

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

Für die kontrollierte Untersuchung der musikalischen Emotionsanalyse gibt es ein
[Vergleichs- und Bewertungskonzept](docs/AUDIO-EVALUATION.md) und das separate
Werkzeug `python -m scripts.audio_evaluation --help`. Es vergleicht Prompts,
Pegelkontrollen und unabhängige Ausdrucksabfragen ausschließlich mit einem
vorhandenen lokalen CLAP-Snapshot. Private Ergebnisse und Hörausschnitte bleiben
in ignorierten Testordnern; App, Bibliothek und produktive Analysemethode werden
nicht verändert. Ohne unabhängige menschliche Bewertungen wird keine verbesserte
Emotionserkennung behauptet.

Für die Oberfläche `npm run dev` und für das Backend separat `.venv-modern\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765` starten. `VITE_API_URL` kann für eine getrennte Testumgebung gesetzt werden. `MOODSCOPE_DATA` wählt einen separaten Datenordner. Der Dienst ist nur für lokale Nutzung vorgesehen.

## Datenschutz und Veröffentlichung

Audio, Lyrics, Analysen, persönliche Notizen, API-Keys, Modelle und Testmusik werden nicht in Git aufgenommen. Auch lokale Werkzeuge, virtuelle Umgebungen, Installer und Screenshots sind ausgeschlossen. Standardmäßig bleiben Audio und Inferenz lokal; LRCLIB erhält nur bei Lyrics-Suche Interpret, Titel und Dauer. Linkimport greift auf die gewählte Plattform zu. Der ausdrücklich gewählte API-Modus sendet die dafür genannten Daten an Google.

Vor jedem Fortschritts-Commit und Upload prüft `scripts/check_publication.py` die ausgewählten Dateien. Öffentliche Übernahmen verwenden einen eigenen Veröffentlichungscommit; mit `--ref codex/public-release` werden auch dessen erreichbare Dateiversionen und Commit-E-Mail-Adressen geprüft. Ein später gelöschtes Geheimnis bleibt ein Sperrgrund. Das ersetzt kein zusätzliches Lesen der Änderungen. Einzelheiten: [Veröffentlichungsablauf](docs/PUBLISHING.md).

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

**Methode & Werte** zeigt pro Song und Abschnitt die gespeicherten Ähnlichkeiten, Kontextfenster, Gewichtung und Valenzrechnung. Die neue Pipeline weist Analyse-Pegelkorrektur und Formulierungssensitivität aus. Feste Valenzzuschläge und nachträgliche Dreipunktglättung werden nicht mehr angewendet; ältere Rechenwege bleiben nachvollziehbar. **Atmosphäre** im Player schaltet ein sphärisches Visual ein; Farben folgen den Mood-Werten, Bewegung der Wiedergabe und gespeicherten RMS-Energie. Kein Live-Frequenzspektrum. Reduzierte Bewegung wird respektiert.

Die Bestätigungen für Bibliotheks-/Cache-Aktionen und Anbieterprofile verwenden denselben Dialog wie Neustart/Beenden. Ein fehlgeschlagener Bibliotheks-Refresh nach erfolgreichem Löschen stellt keine gelöschte Audioadresse mehr her. Modelldownloads für Demucs haben Zeit-/Größenlimits, atomare Dateien und die Prüfsummen des Herausgebers; das Laden erzwingt `weights_only=True` mit einer engen Typfreigabe für die kuratierten HTDemucs-Pakete.

Die optionale **Atmosphäre** färbt das gesamte Layout anhand der analysierten Stimmung. Nebel-/Wasserbewegungen folgen Wiedergabe, geschätztem Tempo und gespeicherter Energie, keinem Live-Frequenzspektrum. Pausieren hält sie an; reduzierte Bewegung wird respektiert. F11 schaltet im nativen Fenster Vollbild um; im Browser gilt dessen Vollbildfunktion.

**Bedienweg:** Bibliothek → Songdetails → Stimmungsverlauf → Methode & Werte → Hörstudio → Interpretation. **Modelle & API** ist ein eigener Hauptbereich links unter **Song-Analyse**. Der letzte Song-Reiter und die Wiedergabe bleiben beim Wechsel erhalten.

**Aufträge abbrechen:** Im globalen Auftragsbanner kann ein laufender Download, Import oder Analyseauftrag abgebrochen werden. Die App wartet gegebenenfalls auf einen aktuellen GPU-Schritt oder Netzwerkaufruf. Bereits abgeschlossene Zwischencaches dürfen wiederverwendbar bleiben; eine unvollständige neue Gesamtanalyse wird nicht als fertig ausgegeben. Synchrone Metadatenabfragen sind zeitlich begrenzt, haben aber noch keinen eigenen Auftragsabbruch.

**Neustart bei veraltetem Dienst:** Neustarten ersetzt den Backend-Prozess; im nativen Modus wird auch das Fenster über den Projektstarter neu geöffnet und die neueste vorhandene EXE gewählt. Im Browser wird die Oberfläche neu geladen. Eine bereits beendete Sitzung zeigt einen eigenen Abschlussbildschirm.

### Live-Mix, Export und A/B-Loop

Im Hörstudio steuert **Live-Mix** die Pegel der tatsächlichen Audiospuren direkt per Web Audio. Solo, Spurwahl und Regler benötigen keine neu gerenderte Mixdatei; Pause, Positionssprünge und Abhörlautstärke folgen dem Hauptplayer. Die Spuren werden lokal gestreamt. Bei Browser-/Audioproblemen lässt sich Live-Mix ausschalten und der dateibasierte Mix verwenden.

Jede erzeugte Spur lässt sich als WAV exportieren. Die Desktop-App öffnet einen nativen Speichern-unter-Dialog mit Songtitel und gewählten Spurgruppen als Dateinamenvorschlag. Im Browser wird die Dateiauswahl verwendet, sofern unterstützt; sonst gilt dessen Download-Einstellung. Ein Abbruch erzeugt keine Exportdatei. **Mix als WAV exportieren** rendert die gewählten Spuren mit ihren eingestellten Pegeln; die Abhörlautstärke beeinflusst den Export nicht. Bei Übersteuerung wird der gesamte Mix gleichmäßig abgesenkt. Originaldateien werden nicht verändert. Exportformat ist derzeit WAV, keine MP3-/FLAC-Ausgabe und kein gespeichertes Mix-Preset.

Rechtsklick auf die Stimmungskurve oder die untere Positionsleiste setzt zuerst A, dann B; beide Ansichten teilen dieselben Markierungen. Der Bereich wird bei Wiedergabe wiederholt; ein dritter Rechtsklick entfernt beide Markierungen. Zwei Punkte in umgekehrter Reihenfolge werden geordnet. Die A/B-Schaltfläche setzt den Punkt an der aktuellen Position und ist auch per Tab und Enter/Leertaste erreichbar. Neben **Song importieren** steht zusätzlich **Song neu analysieren**.

Dropdowns verwenden in aktuellen Chromium-/WebView2-Browsern ein gestaltetes natives Auswahlmenü; Tastatur- und Fokussteuerung bleiben erhalten. Ältere Browser behalten die dunkel gestaltete Standardauswahl. Animationen respektieren die Betriebssystemoption für reduzierte Bewegung.

## Importierte Audiodaten und Nutzungsrechte

Datei- und Linkimporte behalten eine verwaltete lokale Wiedergabekopie und gegebenenfalls getrennte Hörspuren. Analysen und Deutungen werden getrennt zwischengespeichert. Der Analyse-Cache löscht keine Audiodateien; **Song vollständig entfernen** entfernt auch die verwalteten Kopien. Externe Originaldateien bleiben erhalten.

Ein öffentlich abspielbarer Link ist keine pauschale Download- oder Bearbeitungserlaubnis. Import, Trennung und Export nur mit den erforderlichen Rechten und unter Beachtung der Plattformbedingungen verwenden. Auch vorübergehende Speicherung ersetzt keine erforderliche Erlaubnis. Die App kann die Rechtslage eines einzelnen Songs nicht verlässlich feststellen. Sie umgeht keine Anmeldung oder DRM-Sperre. Orientierung für Deutschland: [§ 53 UrhG](https://www.gesetze-im-internet.de/urhg/__53.html); zusätzlich gelten die Bedingungen der jeweiligen Quelle.

## Prompts, Geräte und fließende Detailansicht

Links unter **Modelle & API** liegt **Prompts**. Für Audio Mood lassen sich die zwölf CLAP-Klangbeschreibungen bearbeiten, für Instrumenthinweise neun Beschreibungen. Gesamt- und Zeilendeutung haben getrennte deutsche und englische Arbeitsaufträge. Eigene Varianten können gespeichert, ausdrücklich aktiviert, aktualisiert oder entfernt werden. **Standard wiederherstellen** aktiviert die Vorgabe und erhält eigene Vorlagen. Feste Regeln zu Textbelegen und Unsicherheit bleiben aktiv. XLM-EMO und Whisper verwenden hier keinen frei editierbaren Chat-Prompt. Änderungen trainieren kein Modell und garantieren keine bessere Bewertung.

Unter **Modelle & API** lässt sich für Audio Mood, Lyric Mood, Texterkennung, Interpretation und Spurentrennung jeweils Automatik, CPU oder eine erkannte NVIDIA-GPU wählen. Die Einstellung gilt für neue Berechnungen; vorhandene Songcaches bleiben erhalten. Ausgewählte GPUs werden geprüft. API-Server bestimmen ihre Hardware selbst. Whisper benötigt zusätzlich passende CUDA-Laufzeitbibliotheken; CPU kann deutlich langsamer sein.

Die Detailbalken unter **Methode & Werte** interpolieren während der Wiedergabe zwischen Messpunkten. Die angezeigte Rechnung behält die exakten gespeicherten Abschnittswerte. Offene Abschnittsmenüs bleiben beim Weiterlaufen stabil. Lyrics und Akkordfolge folgen der aktiven Stelle innerhalb ihres eigenen Bereichs; manuelles Scrollen pausiert das Folgen. Hover- und Tastaturhilfen verwenden gestaltete Tooltips.

Die Modusauswahl **Lokal / API** ist in der gemeinsamen Kopfzeile auch in **Modelle & API** und **Prompts** erreichbar. In der Modellverwaltung zeigt der lokale Modus Geräte und Modelle, der API-Modus die Serverprofile. Prompts für Textdeutungen gelten für beide Wege; CLAP-Beschreibungen werden im API-Modus nicht als anwendbare Prompts angeboten. Ein Moduswechsel sendet noch keine Audiodaten. Die Kopfzeile bleibt beim Scrollen als schmale matte Glasleiste stehen. Sie schließt ohne Rand mit dem Inhaltsbereich ab und läuft nach unten transparent aus; die Song-Aktionen stehen rechts. Modus, Sprache und App-Steuerung liegen in einer Zeile, Song-Aktionen und Linkimport in einer zweiten. Am Seitenanfang stehen Modus, Sprache, Info, Dienststatus und App-Steuerung ganz oben. Darunter liegen die große Überschrift und die Song-Aktionen. Beim Scrollen gleitet und verblasst die Überschrift kontinuierlich; die Song-Aktionen schließen weich unter der oberen Einstellungszeile zum kompakten Header auf. Der Übergang folgt direkt dem Scrollweg, ohne den Dokumentfluss umzubauen. Song-Reiter scrollen normal mit.

Unten links steht der gewählte Modus mit lokalem Gerätenamen beziehungsweise API-Modell. Für eine ausdrücklich gewählte Textserver-Deutung zeigt die Interpretation deren Profil und Modell. Die Detailbalken verwenden weich animierte Transformationen; reduzierte Bewegung bleibt berücksichtigt. Maus-Tooltips folgen dem Cursor, Tastaturhilfen bleiben am fokussierten Element. Der A/B-Knopf ersetzt den zuvor angekündigten Shift+F10-Weg.

Die Desktop-App startet maximiert mit normalem Fensterrahmen (kein exklusives Vollbild). F11 bleibt als Vollbildumschaltung verfügbar. Songkarte und Player zeigen ein aus dem Songtitel abgeleitetes Kürzel; ohne geladenen Song bleibt MS als Platzhalter.

Die Atmosphäre tönt auch die matte Kopfzeile sehr zurückhaltend. Ihre leichte Lichtbewegung folgt nur laufender Wiedergabe; Pause und reduzierte Bewegung werden respektiert. Ein laufendes Windows-Fenster darf beim Bauen geöffnet bleiben: geprüfte neue ausführbare Dateien können neben der gesperrten Datei liegen und werden vom Projektstarter beim nächsten Neustart ausgewählt.

Bestätigungs- sowie Neustart-/Beendenfenster übernehmen bei aktiver Atmosphäre deren Farbgebung. Sie liegen außerhalb des Header-Darstellungskontexts über der ganzen Oberfläche; damit wird auch die Kopfzeile einheitlich unscharf und abgedunkelt.


Die manuelle Hörhilfe verwendet das oben ausgewählte Trennmodell. Als Quelle stehen der Originalmix und ausschließlich bereits erzeugte Spuren dieses Modells zur Verfügung. Bei einem Modellwechsel fällt die Hörhilfe auf den Originalmix zurück; fehlende Spuren müssen zuerst getrennt werden.

Die Atmosphärenfarben mischen sich aus den relativen Anteilen von Freude, Ruhe, Trauer, Ärger, Anspannung/Angst und Zärtlichkeit. Die weichen Farbübergänge verändern keine Analysewerte; die Farbzuordnung ist eine Designentscheidung. Fehler erscheinen in einer schließbaren Meldungsleiste über dem Player und außerhalb der fixierten Kopfzeile.

Beim Löschen verwirft die App noch laufende Rechercheantworten, statt gelöschte Werte wieder zu speichern. Ein bestätigter Neustart beendet auch offene Recherche- und Streaming-Verbindungen; der Dienst startet als neuer Prozess. Reguläres Herunterfahren hat eine begrenzte Wartezeit.

Im Atmosphärenmodus verwenden Hintergrund, Panels, Sidebar, Header und Player wieder dunkle, durchscheinende Farbflächen. Die Farbsättigung der Darstellung wird angehoben, damit gemischte Emotionsanteile sichtbar bleiben. Das verändert weder die Emotionswerte noch die Palette oder die Übergangszeiten. Browser ohne relative OKLCH-Farben verwenden die bisherige Farbdarstellung als Fallback.


Der Live-Mix verwendet einen lokal erzeugten stummen Wiedergabetakt und bis zu sechs echte Audiospuren. Steueranfragen nutzen den jeweils anderen Loopback-Namen auf demselben Port, damit volle Audiostream-Verbindungen die Bibliothek und Bedienung nicht blockieren. Ein Songwechsel beendet die alten Decoder und startet mit einem frischen Player. Misslingt der Live-Start oder antwortet eine Quelle nicht innerhalb von 20 Sekunden, wird der Originalmix mit Fehlermeldung wiederhergestellt.

**Gespeicherte Spuren laden** liest vorhandene Ergebnisse direkt ein und zeigt eine Bereitschaftsmeldung. Dafür wird kein neuer Trennauftrag gestartet. Fehlende Spuren werden weiterhin durch einen echten lokalen Trennauftrag erzeugt.

Bei einem anhand Metadaten und Audio erkannten Wiederimport findet das Hörstudio auch die vorhandenen Trennspuren der bestätigten Aufnahme. Bereits separat erzeugte Spuren einer älteren Importvariante bleiben verfügbar. Das gilt auch für Quellenmix, Export und manuellen Hörfokus. Monospuren werden für den Hörfokus auf beide Wiedergabekanäle gelegt.

Der Atmosphaerenmodus faerbt den Hintergrund sichtbar nach den aktuellen
Balkenfarben: die staerkste Kategorie praegt die Flaeche, kleinere Anteile
mischen sich dezent darunter. Balken und Hintergrund verwenden dieselbe Palette.
Die Farben orientieren sich an verbreiteten psychologischen Assoziationen;
die konkrete Gestaltung ist keine weitere Emotionsmessung.

KI-Anbieterprofile und API-Key-Felder stehen unter **Modelle & API** sowohl
im lokalen als auch im API-Modus bereit. Die obere Auswahl bezeichnet den
API-Modus allgemein; die App zeigt die tatsaechliche Unterstuetzung getrennt:
aktivierte Audioprofile fuer Audiokurven, Gesangserkennung und Instrumenthinweise; eingetragene Textprofile fuer Deutungen. Der Moduswechsel
startet keine Anbieteranfrage. API-Keys bleiben nur im Backend-Arbeitsspeicher.

Audio-API-Profile unterstuetzen jetzt zusaetzlich zu Gemini geeignete OpenAI-,
Mistral/Voxtral- und eigene kompatible Audiomodelle. Sie koennen Emotionskurve,
Textbewertung, optionale Gesangserkennung und separat angeforderte
Instrumenthinweise uebernehmen. Reine Textanbieter bleiben fuer Deutungen nutzbar.
Einrichtung, Datenuebertragung und Grenzen stehen in [API-PROFILES.md](docs/API-PROFILES.md).
