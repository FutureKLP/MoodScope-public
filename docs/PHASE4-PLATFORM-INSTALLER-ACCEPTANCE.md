# Phase 4.2: Backend-Runtime und Installationsprüfung

Prüfserie 22./23. November 2026. **Teilweise bestanden; keine Endnutzer- oder
öffentliche Binärfreigabe.** Lokale Windows-/Linux-Kandidaten starten jetzt ein
gebündeltes Backend selbst. Der unten erhaltene Phase-4.1-Bericht beschreibt die
vorherigen Clientpakete; dessen Backendlücke gilt nicht für den neuen Runtimebuild.

[Aktueller Status](STATUS.md) · [Runtimearchitektur und Build](BACKEND-RUNTIME.md)
· [Setup](SETUP.md) · [Drittanbieter](THIRD-PARTY.md).

## Architektur und Inhalt

Gewählt: PyInstaller One-folder als feste Tauri-Ressource, zusätzliches Cargo-
Feature `packaged-backend` und eigene Buildkonfiguration. Keine kopierte Entwickler-
venv, kein CUDA-Cache, keine zusätzlichen Renderer-Shellrechte. Der normale
Entwicklungsbuild bleibt beim vorhandenen Windows-/Linux-Projektstarter.
Ein separat eingebettetes Python würde zusätzliche Bootstrap-/Importpfadpflege
verlangen; One-file müsste bei jedem Start entpacken. Modelle bleiben separat.

FastAPI/Uvicorn, Transformers/CLAP/XLM-EMO, PyTorch/Torchaudio, Demucs,
Faster-Whisper/CTranslate2/PyAV, Librosa/SoundFile und ImageIO-FFmpeg sind im
CPU-Umfang gesammelt. Builderinventar, Lizenztexte und SHA256-Dateimanifeste
werden erzeugt; das Inventar der Builderdistributionen ist kein Beweis, dass
jedes Modul eingefroren ist. Windows-Builder: 100 Distributionen. Upstreamtests,
Referenzdaten und Bytecodecaches werden aus dem erzeugten Ordner ausgeschlossen.
Keine Musik, Gewichte oder SQLite in den geprüften Runtime-Dateimanifesten.

| Lokaler Kandidat | Runtimeordner | Paket |
|---|---|---|
| Windows x64 | 1.120.327.053 Bytes, 6.876 Dateien | NSIS 415.900.194 Bytes (396,63 MiB), lokale Zlib-Kompression |
| Linux x86_64 | 1.806.615.685 Bytes, 6.817 Dateien | Debian 616.133.584 Bytes (587,59 MiB) |

Die Kandidaten verwenden eine separate Testkennung. Das Paketverhalten der
normalen Produktkennung auf vorhandenen Benutzerdaten ist damit nicht abgenommen.
Die abschließende Korrektur des Modell-Löschpfads wurde anschließend im Quellstand
mit Regressionen geprüft; native Paketnachweise beziehen sich auf die Kandidaten
davor. Der Windows-Kandidat enthält außerdem nicht die spätere POSIX-spezifische
SO_REUSEADDR-Zeile; sein Windows-Codepfad ist davon nicht betroffen.

## Start, Besitz und Benutzerverzeichnisse

Rust startet nur das feste mitgelieferte Programm und prüft bis zu 120 Sekunden
Status, Version 0.3.0, API 16 und eigene Besitzkennung. Erst danach entsteht das
Hauptfenster. Ein fremder Listener wird weder übernommen noch beendet. Der
Supervisor hält den Loopback-Socket auch über Worker-Neustarts; Windows verwendet
Socket-Sharing/Selector, POSIX einen explizit geerbten Socket mit SO_REUSEADDR.
Stdin-Pipes binden App, Supervisor und Worker aneinander. Es gibt keine PID-Datei
oder Port-basierten Kill. Unerwartete Workerfehler haben höchstens zwei Wiederanläufe;
kein automatischer Anbieterretry. Supervisorverlust beendet den Client mit Exit 1.

`app_local_data_dir` der jeweiligen Appkennung enthält `data` und `models`:
SQLite, verwaltete WAVs, Stems, Profile/Einstellungen, Logs und temporäre
Workerbereiche unter `data`, HF-/Whisper-/Demucs-Gewichte unter `models`.
Der Linux-Installationsbaum blieb im nativen Test schreibgeschützt; dpkg-Dateiprüfung
meldete keine Veränderungen. Windows nutzt die bekannte AppData-Funktion statt
einer geerbten LOCALAPPDATA-Testumleitung. Keine automatische Datenmigration,
keine Verschiebung vorhandener Gewichte oder Originale.

## Tatsächlich geprüfte Plattformfälle

| Fall | Windows NSIS | Linux Debian / WSLg |
|---|---|---|
| Installation | Eigener Zielpfad und Registrierung, Exit 0 | Isolierter dpkg-Root mit kopiertem Paketstatus; anfängliche Installation und Reinstallation erfolgreich |
| Finaler Paketstatus | Installiert und getestet | Finaler Kandidat korrekt unkonfiguriert: deklarierte Abhängigkeit `gstreamer1.0-plugins-bad` fehlt; kein force-depends |
| Eigenständiger Erststart | Mit Python-freiem PATH und absichtlich ungültigem PYTHONHOME/PYTHONPATH; Rust entfernt Overrides, eigene Prozessfamilie/Health bestätigt | System-Python im Testnamespace maskiert, Installation nur lesbar, kein Projektserver; eigene Runtime/Health bestätigt |
| Import und Wiedergabe | Nativer WAV-Dialog, Track sichtbar, Player bis 0:02 | GTK-Import; 1,999979 s Signal am WSLg-Ausgabemonitor, 440,004583 Hz, Peak 0,195343 |
| Hörstudio und WAV-Export | Native Zielauswahl; Stereo/48 kHz/96.000 Frames, maximaler Samplefehler 0 | GTK-Zielauswahl; gleiche Audioeigenschaften und maximaler Samplefehler 0 |
| Dienstneustart / Workercrash | Eingefrorener Protokolllauf: neuer Worker, neue Sitzung; installierter Workercrash erholt sich | Eingefrorener Protokolllauf: Neustart, Workercrash und Wiederherstellung |
| Nativer Appneustart | UI-Neustart mit neuer Client-PID und Besitzkennung bestätigt | Mehrfache getrennte native Starts und eingefrorener Dienstneustart; vollständige native UI-Neustartfolge offen |
| Reguläres Ende | Beenden und Bestätigung: Exit 0, keine eigenen Backendkinder/Listener | Alt-F4 über WSLg-Fenster: Exit 0, keine eigene Backendfamilie/Listener |
| Harter Clientabbruch | Eigene Backendfamilie endet, Daten hashgleich und SQLite ok; erneuter Start funktioniert | Eigene Familie/Port frei, Daten hashgleich und SQLite ok |
| Supervisorverlust | Client Exit 1, keine eigene Familie/Listener | Pipe-EOF im eingefrorenen Protokolllauf geprüft; identische installierte Fehlermatrix noch offen |
| Unbekannter Listener | Native Fehleranzeige; keine Backendkinder oder HTTP-Anfragen; Listener bleibt erhalten | Socketregression / Protokoll; native Fehlermatrix offen |
| Fehlende Runtime | Native Fehleranzeige, mit OK beendet; Testdatei wiederhergestellt | Native Fehlerprobe offen |
| Update | Gleichversions-Reinstallation erhält acht Datendateien | Reinstallation im isolierten Root; final fehlende Abhängigkeit bleibt sichtbar |
| Deinstallation | Eigene EXE/Registrierung entfernt; Bibliothek/Profile/Exporte und fremde Sentineldatei erhalten | Eigenes Paket mit dpkg -r entfernt; 180 Dateien im Benutzerprofil unverändert |

Die Quellen sind selbst verfasste synthetische Stereo-WAVs mit 440 Hz, 0–2 s.
Für Hörstudioexporte wurde ein ausdrücklich synthetischer Einspurcache vorbereitet;
das ist kein Demucs-Inferenznachweis. Es wurde keine Originalmusik verwendet und
kein Anbieterauftrag ausgelöst. Windows hat keinen neuen physischen Ausgangsnachweis;
der Linux-Pulse-Monitor liegt vor dem Windows-Audiogerät. Leere Modellordner führen
zu sichtbaren Fehlgewichtsfehlern, nicht zu behaupteter erfolgreicher Inferenz.

Die zusätzliche Nur-Lese-Testumgebung benötigte schreibbares `/var/tmp` neben
`/tmp`; damit funktioniert Audio auch in der stärkeren Isolation. Die fehlende
GStreamer-Pluginbibliothek wurde nur extrahiert und per lokalem Pluginpfad verwendet,
nicht im Host installiert. Das ersetzt keine vollständige konfigurierte Debian-
Installation. Host-`libc-bin` bleibt unverändert halb konfiguriert. WSL lief als Root;
Normalbenutzerrechte und unabhängiger Ubuntu-Desktop bleiben offen.

Testhaltergrenzen: X11 `windowclose` zerstört das Fenster und zählt nicht als
reguläres Ende. Frühere Starts während laufender Paketextraktion und einzelne
Probestatusrennen wurden korrigiert wiederholt. Der NSIS-Wrapper kehrt vor seiner
abgetrennten Aufräumphase zurück; die erste Registrierungsprüfung war zu früh,
die abschließende Prüfung bestätigt deren Entfernung. Kein Testhaltercleanup als
nativen Quiterfolg gewertet.

## Regression, Integrität und öffentliche Übernahme

Windows: **407 Backendtests bestanden, ein POSIX-Skip**. Linux: **408 bestanden**.
Beide Plattformen: **156 Frontend-, zehn Rust- und fünf Node-Tests**, TypeScript/
Vite, native Release- und jeweilige Paketbuilds. Prozessbesitz, Portkonflikt,
TIME_WAIT, Benutzerpfade und fehlende Kompatibilitätsruntime haben Regressionen.
Der letzte Modellpfadtest trennt Ressourcen und Benutzergewichte ausdrücklich.
Vite-Chunkwarnung bleibt; Buildtests beweisen keine vollständige Kernfreigabe.

Alle **10.071** geschützten Produktionsdaten-, Gewichts- und Musikdateien sind
vor/nach der Serie hashgleich, produktive SQLite lesend intakt. Eigene Dienste
sind beendet. Rohbelege, Installer, Manifeste und lokale Übergaben bleiben ignoriert.
Vor öffentlichem Quellpush sind exakter Index, erreichbare Historie und Diff zu
prüfen; Ergebnisse und neuer CI-Stand werden im Draft-PR festgehalten.

Am 23. November unverändert: Main `1717ffd`, #11 `ff585f5`, #12 `5d459f0`,
#13 `b3e4b9c`, #14/#15 `723b8c2`, #16 `7df500e`; alle offen, #13/#14/#16 Draft,
jeweilige Head-Workflows erfolgreich. #17 bleibt Draft gegen Phase 3; sein früherer
Head `f4bf651` hat erfolgreiche CI, keine Reviews/Reviewthreads. Neuer Quellstand
benötigt eigene CI. Keine Merges, Schließungen oder Force-Pushes. #15 bleibt eine
alternative Sammelintegration, kein zusätzlicher Schritt in der gestapelten Kette.

## Offene Freigabegrenzen

Music2Emo benötigt eine separate ältere Python-/Torch-Kompatibilitätsumgebung;
im eingefrorenen Paket wird es selbst bei vorhandenen Gewichten als nicht verfügbar
gemeldet. Entwicklungspfad und Crash-Recovery bleiben erhalten. Ein separater
Kompatibilitätsinstaller ist noch nicht freigegeben.

Binärlizenzen sind **nicht vollständig freigegeben**: GPLv3-FFmpeg benötigt passende
Quellen/Buildangaben und Weiterverteilung; native Notices (unter anderem PyAV,
libsndfile, CTranslate2, Torch und C/C++-Runtime) müssen final zusammengeführt werden.
Bei ctranslate2, flatbuffers, sentencepiece, tokenizers und tqdm enthält das geprüfte
Wheel keine gesammelten Lizenztextdateien, nur Metadaten. Plattformübergreifend
gesperrte CPU-Distributionslocks fehlen. Keine öffentlichen Binaries hochgeladen.

Die bestehende moderate Dependabot-Warnung wurde im angemeldeten Browser konkret
geprüft: `glib 0.18.5`, transitiv über GTK/Tauri, `GHSA-wrw7-89jp-8q8g`, betroffen
ab 0.15 bis vor 0.20, gepatcht ab 0.20.0. Keine ungeprüfte GTK-Hauptversionsänderung;
Warnung weder behoben noch als sicher abgehakt.
[Advisory](https://github.com/advisories/GHSA-wrw7-89jp-8q8g).

Weiter offen: finaler Paketnachlauf nach Modellpfadkorrektur, vollständig konfigurierte
Debianinstallation, verzögerter und inkompatibler Dienst als native Fehlerfälle
(Version/Besitz bisher Vertragstest), versionswechselndes Update, echte installierte
Modell-/Lyricsmatrix, Normalbenutzer/Linux außerhalb WSL, Windows 10, weitere DPI/
Mehrmonitor und frühere Phase-2B-/2C-/3-Grenzen. **Phase 4 bleibt teilweise bestanden.**

---

# Historischer Prüfstand Phase 4.1: Clientpakete

Prüfserie vom 21./22. November 2026. **Teilweise bestanden.** Windows-NSIS,
isolierte Windows-Installation/Deinstallation, Ubuntu-Build, Debian-Paketbuild
und eine echte Linux-GUI unter WSLg sind nachgewiesen. **Eigenständig nutzbare
Installationspakete sind nicht freigegeben:** Beide Pakete enthalten den
Desktopclient, aber keinen Python-Analysedienst. Kein Endnutzer-Release.

[Aktueller Status](STATUS.md) · [Setup](SETUP.md) · [Kernabnahme](CORE-ACCEPTANCE.md).

## Git, Review und Teststand

Branch `codex/phase4-platform-installer`, direkt vom öffentlichen Phase-3-Head
`7df500e31016876d297fb32d59758c614fc44ff1`. Öffentlicher Main nach erneutem
Fetch am 22. November weiterhin `1717ffd074041dd5db4e129f9f3aed3fb1a072dc`.
Keine private Entwicklungshistorie übernommen, kein Main-Merge, kein Force-Push
und keine PR-Schließung.

Beim GitHub-Abgleich am 21. November waren #11/#12/#15 offen und #13/#14/#16
Draft. Für jeden Head waren Windows-/Ubuntu-Test und Native-Build erfolgreich;
keine eingereichten Reviews oder Reviewthreads. Heads: #11 `ff585f5`,
#12 `5d459f0`, #13 `b3e4b9c`, #14/#15 `723b8c2`, #16 `7df500e`.
Diese datierten Checks ersetzen weder Review noch CI für einen neuen Phase-4-Head.
Spätere Integration: **#11 → #12 → #13 → #14 → #16 → Phase 4**, jeweils Basis,
Restdiff, Diskussionen und Pflichtchecks erneut prüfen. #15 ist die alternative
Sammellinie mit demselben Head wie #14 und wird nicht zusätzlich integriert.

App-Code, Tauri-Konfiguration und Frontend blieben in dieser Phase unverändert.
Gezielt korrigiert wurden Linux-CPU-Setup und plattformgerechte Git-Auswahl des
Publikationsprüfers. Synthetische Regressionen, native Eingaben, HTTP-Prüfungen
und Audio-Monitormessungen sind unterschiedliche Nachweise. Vorverfasste
Analyse-/Stemfixtures sind ausdrücklich keine Inferenz oder Musikqualitätsabnahme.
Rohbelege, Paketdateien, Testdaten und Hashmanifeste bleiben ignoriert lokal.

## Installer- und Backendarchitektur

Tauri 2 mit Rust hostet das gebaute React-/TypeScript-Frontend. `tauri.conf.json`
konfiguriert NSIS, Debian und AppImage. `frontendDist` wird eingebettet; ein
Vite-Entwicklungsserver ist beim Releaseclient nicht erforderlich. Es gibt
keine konfigurierten Backendressourcen und kein `externalBin` für Python.

FastAPI wird durch `scripts.service` auf **127.0.0.1** gestartet. Der Dienst
supervisiert seinen Worker und bereinigt eigene Modellkinder. Der Windows-
Projektstarter `scripts.launch` wählt die validierte Projekt-Pythonumgebung,
startet nötigenfalls den Dienst und beendet nur den von ihm erzeugten Dienst.
Er kann bei Exitcode 75 den neuesten Client erneut wählen. Der Linux-
Entwicklungsstarter verwendet ebenfalls eine separate Pythonumgebung.

Eine direkt gestartete installierte EXE bzw. Linux-Binärdatei führt diesen
Projektstarter nicht aus. Sie besitzt keinen Backend-Kindprozess. Die vorhandene
Neustartvereinbarung mit dem Projektstarter ist daher keine nachgewiesene
autonome Installer-Neustartfunktion. Das wurde nicht durch eine spekulative
Änderung der funktionierenden Entwicklungsarchitektur verdeckt.

SQLite, verwaltete WAVs, Stems, Sitzungsdiagnosen und lokale Einstellungen liegen
im Backend-Datenordner, standardmäßig projektbezogen unter `data/`, über
`MOODSCOPE_DATA` umleitbar. Hugging-Face-Gewichte verwenden `HF_HOME`, standardmäßig
`models/`. Weitere Modellpfade sind projektspezifisch; daraus folgt noch kein
vollständiges Datenverzeichniskonzept für einen schreibgeschützten Installationsort.
Die Tests setzen eigene Daten-, Modell-, Temp- und WebView-/XDG-Verzeichnisse.

**Bestätigte Lücke:** Ein Runtimepaket, dessen Abhängigkeiten/Lizenzen und
Dateiinhalte geprüft sind, fehlt auf beiden Plattformen. Ebenso fehlen eine
installierte Backend-Start-/Besitzvereinbarung und deren Crash-/Updateabnahme.
Eine vorhandene Entwicklungsvenv samt CUDA-Bibliotheken und lokalen Caches
ungeprüft zu bündeln wäre keine sichere minimale Lösung. In dieser Phase wurde
deshalb kein solches Paket erzeugt. Nächster Umsetzungsschritt ist ein getrennt
prüfbarer Backend-Runtimeumfang mit Benutzerverzeichnissen und ausschließlich
eigenen Prozesslebensdauern; danach müssen beide Installer erneut abgenommen werden.

## Windows 11

Windows 11 Build 26200.9974, vorhandenes MSVC/SDK/WebView2, Node 22.16.0 und
projektlokale Python-/Rust-Werkzeuge. Kein frisches Windows ohne Entwicklungstools;
insbesondere keine bestandene Installation auf einem Rechner ohne Python behauptet.

| Fall | Status und tatsächliches Ergebnis | Nachweis und Einschränkung |
|---|---|---|
| Release und NSIS bauen | Bestanden; Releasekompilierung 21,76 s, NSIS 2,37 MiB | Locked/offline Cargo; Tauri-Bundletool verwendet vorhandene Werkzeuge. Vite-Chunkwarnung bleibt |
| Paketinhalt | Bestanden im geprüften Clientumfang | Erzeugtes NSIS-Skript und tatsächliche Installation: ausschließlich App-EXE und Uninstaller, Frontend in EXE; keine Pythonressourcen, Musik, SQLite oder Gewichte |
| Isoliert installieren | Bestanden, Exitcode 0 | Separate Testidentität `MoodScopePhase4Test` / `dev.moodscope.phase4test`, eigener geprüfter Zielpfad, eigene Registrierung/Profile, keine Startmenü-/Desktopverknüpfungen |
| Erster Start ohne Entwicklungsserver | Bestanden für das Fenster | Installierte EXE aus ihrem Installationsordner gestartet; kein Vite-Dienst |
| Backend autonom starten | **Fehlgeschlagen** | Client läuft, Port 8765 bleibt geschlossen; kein Backend im Paket |
| Fehlender Dienst | Teilweise bestanden | Sichtbar „Backend offline“; kein autonomer Reparatur-/Einrichtungspfad geprüft |
| Externer eigener Backenddienst | Bestanden, getrennte Testbedingung | Loopback-Healthcheck Version 0.3.0/API 16/CPU; eigener Dienst mit eigener SQLite. Kein Nachweis für mitgeliefertes Backend |
| Nativer WAV-Import | Bestanden mit externem Prüfdienst | Tauri-Dateidialog, synthetische Zwei-Sekunden-WAV gewählt, Track sichtbar. Vorverfasster Cache verhindert automatische Inferenz |
| Wiedergabe und Hörstudio | Bestanden im kurzen synthetischen Umfang | Player läuft bis 0:02, gespeicherte synthetische Spur im Hörstudio geöffnet. Kein neuer physischer Ausgangsnachweis |
| Nativer WAV-Export | Bestanden | Speicherdialog tatsächlich bestätigt; Stereo, 48 kHz, 96.000 Frames, 384.044 Bytes und bytegleich zur Quelle |
| App-/Dienstneustart | Bestanden mit externem Testhalter | Neue eigene Prozesse, Bibliothek sichtbar wieder geöffnet; Tracks/Cache-/Besitzerzeilen und Audiohashes identisch, SQLite intakt |
| Deinstallation | Bestanden im isolierten Standardpfad | Eigenen tatsächlichen Installationspfad und Registrierung erneut geprüft; Exitcode 0, EXE und Uninstallregistrierung entfernt |
| Benutzerdaten erhalten | Bestanden im geprüften Standardpfad | Testbibliothek, Profil und Exporte außerhalb des Installationsziels hashgleich; absichtlich fremde Datei im Ziel erhalten. Option „Appdaten löschen“ nicht betätigt/geprüft |
| Lyrics und echte Inferenz im installierten Client | Offen | Kein erneuter vollständiger Lyricslauf und kein neuer tatsächlicher Modelllauf dieser Phase; frühere Projektabnahmen werden nicht als Installerabnahme übernommen |

Die Produktions-NSIS-Datei wurde gebaut; die tatsächliche Installation verwendet
denselben Anwendungscode mit ausschließlich abweichender Produkt-/Bundlekennung.
Das ist ein echter isolierter Installationstest dieser Variante, keine globale
Produktionsinstallation oder vollständige Upgrade-/Downgradeabnahme.

Die bekannte 16×16-Tao-Hilfsregion trat erneut auf. Verworfen wurden Eingaben
aus falscher/fehlender Bildbindung; das große Hauptfenster und modale Dialoge
wurden frisch gewählt. Eine Save-Mausprobe schloss den Dialog nicht zuverlässig;
erst die anschließende beobachtete Tastaturbestätigung und erzeugte Zieldatei
zählen als Exportnachweis. Zwischenzeitliche Benutzereingaben wurden respektiert.
Kein neuer Appfehler aus diesen Automationsgrenzen abgeleitet.

## Ubuntu unter WSL2

Tatsächlich erkannt: **Ubuntu 24.04.4 LTS, x86_64**, WSL 2.4.13.0,
Kernel 5.15.167.4-1, WSLg 1.0.65. Die Distribution `Ubuntu` wird ausdrücklich
gewählt; `docker-desktop` blieb unberührt. Die vorhandene Ubuntu-Standardanmeldung
ist root; daraus wird keine Abnahme als gewöhnlicher Desktopbenutzer abgeleitet.

Anfangs fehlten Cargo/Rust, Node/npm, Compiler, pkg-config, pip/venv-Unterstützung,
WebKitGTK und weitere Laufzeitpakete. Nach ausdrücklicher Nutzerzustimmung wurden
in Ubuntu die Tauri-Buildpakete, Python-venv, Soundfile-/PulseAudio-/ALSA- und
GStreamer-Laufzeitpakete eingerichtet. Der Paketmanager meldete 244 neue und
63 aktualisierte Pakete mit ungefähr 565 MB zusätzlichem Platz; die genaue
Pakettransaktion bleibt im lokalen Setupbeleg.

Bei der späteren Git-Nachrüstung meldete Ubuntu zunächst eine automatische
Paketsperre, danach eine unvollständige `libc-bin`-Konfiguration. Keine fremden
Updater beendet, keine Sperrdateien entfernt, kein `dpkg --configure -a` ausgeführt.
Git und die X11-Prüfwerkzeuge wurden stattdessen nur in der Testumgebung entpackt.
Die offene Systempaketkonfiguration ist vor einer echten Paketinstallation separat
zu klären; der erfolgreiche Build behebt sie nicht.

Die Quellkopie stammt aus `git archive` des öffentlichen Phase-3-Heads, im
Linux-Dateisystem außerhalb des Windows-Projektbaums. Nur die gezielten
Phase-4-Quellkorrekturen wurden danach übertragen. Keine Musik-, Datenbank-,
Gewichts-, Windows-venv- oder private Git-Verzeichnisse kopiert. Für Gitregressionen
wurde eine eigene lokale Testhistorie erstellt; das ist keine Veröffentlichung.

Linux-Werkzeuge: Python 3.12.3, Node 22.16.0, Rust/Cargo 1.100.0, GTK 3.24.41,
WebKitGTK 2.52.6 und OpenSSL 3.0.13. Pythonpakete liegen in einer eigenen venv;
Torch 2.15.0+cpu und Torchaudio 2.11.1+cpu. Keine Modellgewichte heruntergeladen.

| Fall | Status und tatsächliches Ergebnis | Nachweis und Einschränkung |
|---|---|---|
| Linux-Backend starten | Bestanden | Eigener Linux-Prozess, Loopback-Healthcheck erfolgreich; kein Windows-Ergebnis umgedeutet |
| Linux-Backendsuite | Bestanden nach Korrekturen | Erster Lauf 387 bestanden/12 fehlgeschlagen; korrigierter vollständiger Lauf **402 bestanden, 37,02 s** |
| Frontend/Node/Web | Bestanden | **156 Frontendtests**, **fünf Node-Tests**, TypeScript/Vite auf Linux |
| Rusttests | Bestanden | **Neun Tests**, Lockfile, tatsächliches Linux-Toolchainziel |
| Linux-Release und Debian | Bestanden | Tauri-Release und `.deb` 3,60 MiB unter Ubuntu gebaut |
| Linux-Pfade und SQLite | Bestanden im Testumfang | Eigene Linux-Datenverzeichnisse, SQLite `integrity_check=ok`; gleiche Zeilen und Medienhashes nach Exportabbruch und Neustart |
| Linux-Paketinhalt | Bestanden für Clientumfang | `dpkg-deb` zeigt ausführbare App und Desktopdatei; Abhängigkeiten `libwebkit2gtk-4.1-0`, `libgtk-3-0`; Backend/Python fehlen |
| Entpacktes Linux-Paket starten | Bestanden für Clientprozess, Backend fehlt | Separat entpackt, `ldd` ohne fehlende Bibliotheken; Client läuft ohne Entwicklungsserver, Port 8765 bleibt ohne Dienst. Keine registrierte Paketinstallation |
| Linux-Paketinstallation/-deinstallation | **Blockiert/offen** | Kein globales `dpkg -i`, keine vollständige isolierte Betriebssysteminstallation. Paketbuild und Inhaltsprüfung sind kein Installationstest |
| AppImage | Offen | Konfiguriert, aber nicht zusätzlich gebaut oder installiert |

### Bestätigte Korrekturen

1. Der Publikationsprüfer bevorzugte überall `git.exe`. WSL erbte den Windows-PATH
   und verwendete dadurch Git für Windows für Linux-Verzeichnisse. Vier reale
   Gitregressionen scheiterten. Auf POSIX wird jetzt ausschließlich natives `git`
   gewählt; Windows behält seine bisherige EXE-Auswahl. Drei neue Regressionen
   prüfen beide Plattformen einschließlich fehlendem Linux-Git.
2. Das erste CPU-Testsetup installierte Torch vom CPU-Index, Torchaudio über die
   allgemeinen Separation-Abhängigkeiten. Dessen CUDA-Bibliothek benötigte
   `libcudart.so.13`; acht Modell-Lifecycletests scheiterten bereits beim Import.
   `setup.sh --cpu` wählt nun beide Pakete vom CPU-Index und prüft auch Torchaudio,
   CLAP und die Transformer-Pipeline vor dem Validierungsmarker. Der Marker wird
   vor Paketänderungen entfernt. Kein globaler CUDA-Workaround und kein Abschalten
   von Sicherheitsprüfungen. Das vollständige CPU-Setup wurde unter Ubuntu ausgeführt.

## Echte Linux-GUI und Audio unter WSLg

`DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`,
`PULSE_SERVER=unix:/mnt/wslg/PulseServer`. X11-/Wayland-Sockets vorhanden.
Bei einer frühen kurzlebigen Probe fehlte der Pulse-Socket bzw. die Verbindung
wurde verweigert. Während der laufenden GUI antwortete PulseAudio zuverlässig
mit `RDPSink` und dessen `RDPSink.monitor`. Gesetzte Variablen allein wurden nicht
als Audioabnahme gewertet.

| Fall | Status und tatsächliches Ergebnis | Nachweis und Einschränkung |
|---|---|---|
| Echtes Linux-Fenster | Bestanden | Linux-ELF läuft in Ubuntu, Fenster „MoodScope 0.3 (Ubuntu)“ auf Windows sichtbar; Frontend eingebettet |
| Maus und Tastatur | Bestanden im kurzen Umfang | Bibliothekswechsel durch native X11-Eingaben, GTK-Pfadfeld mit Ctrl+L, Pfad und Return bedient |
| Bibliothek/Analyse/Hörstudio/Modelle & API | Teilweise bestanden | Bibliothek und vorverfasste Analyse geladen, Hörstudio und Modelle-/API-Ansicht sichtbar; keine echte Linux-Modellinferenz oder neue Anbieterübertragung |
| Nativer Linux-Import | Bestanden | GTK-Dateidialog, eigener synthetischer WAV-Pfad bestätigt; verwalteter Track sichtbar |
| Wiedergabe | Bestanden am WSLg-Monitor | Zwei-Sekunden-Fixture: 1,99994 s aktiver Signalbereich, dominante Frequenz 440,014 Hz; kein Mikrofoneingang benutzt |
| Seeking/A/B/Pause | Bestanden im kurzen synthetischen Umfang | Pausiert auf ungefähr 0,5 und 1,5 s gesucht, A/B gesetzt, laufender Loop und anschließende Pause sichtbar; Monitor enthält rund 3,994 s fortdauerndes Signal bei zweisekündiger Quelle |
| WAV-Export | Bestanden | GTK-Speicherdialog bestätigt; Stereo/48 kHz/96.000 Frames, bytegleich zur Quelle; Linux-Zieldatei mit Modus 0600 |
| WAV-Zieldateischutz | Bestanden im Abbruchfall | GTK-Überschreibwarnung für eigenes bestehendes Ziel sichtbar, verworfen und Speicherdialog abgebrochen; alle Testdateien und DB-Zeilen hashgleich |
| Beaufsichtigter App-/Backendneustart | Bestanden | Eigene Prozesse durch Testhalter beendet und neu gestartet; neue PIDs, erfolgreicher Healthcheck, SQLite-/Medien-/Exportstand identisch |
| Reguläres Alt-F4-Ende | Offen | Linux-seitige Tastenkombination schloss die App nicht nachweisbar; früher zweiter Testhalter verweigerte Start am belegten Port. Testhaltercleanup ist kein bestandener nativer Quitpfad |
| Physische Ausgabe, Lyrics-/Langzeitmatrix | Offen | Pulse-Monitor ist vor der tatsächlichen Windows-Geräteausgabe. Keine DAC-/Lautsprecheraufnahme oder vollständige Lyrics-/Seeking-/Mehrspurmatrix |

Windows-seitige Eingaben im weitergereichten WSLg-Fenster bewirkten anfangs
keinen verlässlich bestätigten Wechsel. Erst Linux-seitige X11-Eingaben mit
frischer Bildkontrolle zählen. Eine Scroll-/Klickprobe blendete die synthetische
Spur aus; sie wurde sichtbar wieder eingeblendet und der Export danach separat
ausgeführt. Keine unbestätigte Eingabe als Erfolg gezählt.

EGL meldete DRI2-/DRI3-Warnungen; der WSLg-Fenstertitel meldete zeitweise Copy Mode.
Die Anwendung lief und erzeugte Audio, aber Hardwarebeschleunigung und flüssige
Animationen unter Linux sind damit nicht abgenommen. Keine Sandbox, Audio- oder
Grafiksicherheit abgeschaltet, keine globalen Geräteeinstellungen verändert.
WSLg ist ein echter Linux-Anwendungstest, kein vollständiger Ubuntu-Desktopersatz.

## DPI, weitere Plattformen und Sicherheit

**Windows 96 DPI: bestanden im oben begrenzten Umfang.** Win32 liest
1440×980 Clientpixel; der zusätzliche sichtbare Tao-Helfer besitzt keinen
Clientbereich. Zwei Monitore wurden tatsächlich erkannt, aber kein kontrollierter
Monitorwechsel oder weiterer Skalierungswert abgenommen. **Windows 10: offen**,
kein geeignetes Testsystem. Ubuntu außerhalb WSL: offen.

Loopbackbindung und vorhandene Host-/Originprüfungen blieben unverändert.
Das ist keine separate Authentisierung anderer gleichberechtigter lokaler
Prozesse. Anbieterzustimmung und Sitzungs-Keys wurden nicht abgeschwächt; in
dieser Phase keine private Musik übertragen, keine Keys eingegeben und keine
Modelldownloads gestartet. Vollständige native Consent-/Worker-Crashmatrix aus
früheren Phasen wurde nicht pauschal erneut als bestanden markiert.

Windows-Vor-/Nachvergleich: **10.071 geschützte Dateien unverändert**, keine
hinzugefügten Dateien im beobachteten Produktions-/Modell-/Musikbestand;
produktive SQLite lesend intakt. Isolierte Windows- und Linux-SQLite intakt,
Track-/Cache-/Besitzerzeilen und WAV-/Stem-/Exporthashes bei den beschriebenen
Neustarts identisch. Originale, vorhandene Gewichte und produktive Daten wurden
nicht als Testziele verwendet. Eigene Prozessfamilien werden vom Testhalter
beendet; keine fremden Prozesse oder Docker-Distributionen beendet.

## Verbleibende Freigabegrenzen

Phase 4 ist **teilweise bestanden**, der autonome Installationsbetrieb bleibt
blockiert. Erforderlich sind geprüfte Backend-Runtimepakete, installierte
Benutzerverzeichnisse und Prozessbesitz, Start ohne Entwicklungsumgebung,
Update-/Crash-/Quitprüfung und echte Linux-Paketinstallation/-deinstallation.

Offen bleiben außerdem zweites echtes Textemotionsmodell und vollständige native
Phase-2B-Kreuzmatrix, physische Audioausgabe und vollständige Lyrics-/Seeking-
Matrix aus Phase 2C, nativer Speicherrestbedarf und Windows-Proactor-Ursache aus
Phase 3, breitere Langzeit-/Modellqualität, weitere DPI-/Mehrmonitorfälle,
Windows 10 und unabhängiger Linux-Desktop. Keine Kern- oder Releasefreigabe und
keine Freigabe der externen Datenbankphase.
