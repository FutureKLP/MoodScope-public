# Phase 4.4: Distributions- und Sicherheitsnachprüfung

Prüfserie vom 23./24. November 2026. **Phase 4 weiterhin teilweise bestanden;
öffentliche Binärverteilung blockiert, keine Endnutzerfreigabe.** Die folgenden
Nachweise ergänzen die vollständig erhaltenen historischen Berichte darunter.

## Git- und Kandidatenbindung

Ausgangshead `4c5ff2cd18d4f532cc272a254fa9329d1135f0b3` erneut gegen origin und
Draft-PR #17 geprüft. Main unverändert `1717ffd074041dd5db4e129f9f3aed3fb1a072dc`.
Beide zugehörigen CI-Läufe erfolgreich; keine offenen Inline-Reviewthreads.
Kein Merge, Force-Push, PR-Schließen oder Binärrelease.

Die erhaltenen Phase-4.3-Pakete haben weiterhin die unten dokumentierten SHA256.
Die vollständigen Runtime-Manifeste wurden erneut abgeglichen; 377 Windows-PE-
und 393 Linux-ELF-Dateien zusätzlich auf Versionsressourcen/Verknüpfung untersucht.
Die neuen lokalen Lizenz-Testpakete verwenden unveränderte eingefrorene
Anwendungs-/Abhängigkeitsbinaries des Anwendungscheckpoints `25b4dc0`, ergänzte
Lizenzdateien und neu gebaute Tauri-Clients mit eigener Testkennung. Keine neue
Abhängigkeitsauflösung, kein frischer PyInstaller-Neubau, kein Versionsupgrade.

| Neuer lokaler Kandidat | Paketbytes | SHA256 |
|---|---|---|
| Windows x64 / NSIS | 415.970.356 | `b0627d0ea95bb631a406bc2f0f99165227cbe47a4324552e07c75a601fd68116` |
| Linux x86_64 / Debian | 602.684.864 | `37eaac031afdeb7bfc6fc013d3688841bd3be47a9f70da71c4c7369e938acd11` |

Linux enthält 6.788 Runtime-Dateien mit 1.763.136.381 Bytes.
Windows enthält 6.885 Runtime-Dateien mit 1.120.381.759 Bytes; die neun zusätzlichen
Dateien sind Lizenztexte und deren Zuordnung, alle ursprünglichen Runtime-Dateien
hashgleich. Der NSIS-Kandidat ist mit eigener Registrierung installiert; sieben
Originaltexte im installierten Paket gegen den Katalog geprüft. Ein erster
Installationsversuch vor dem fertigen Paket wurde vor Ausführung abgewiesen und
zählt nicht als Installation. Finale Windows-/Linux-Nachtests werden getrennt
von den erhaltenen Phase-4.3-Kandidaten geführt.

## Abschließender GPL-Lizenznachlauf

Die obige Tabelle hält die Zwischenkandidaten mit sieben Zusatztexten fest.
Der abschließende Kandidat enthält zusätzlich den unveränderten GPLv3-Text
für die konkret hashgebundenen ImageIO-FFmpeg-Programme: acht Zusatztexte,
keine Änderung ursprünglicher eingefrorener Runtime-Dateien.

| Finaler Kandidat | Paketbytes | SHA256 |
|---|---|---|
| Windows NSIS | 415.982.909 | `2d1f35877eb85e85edd8755eeeb21b715005b3afd5cb3fb62e8cb52461534cc3` |
| Linux Debian | 602.697.760 | `0539faf2a350a47c7ae09392a6cfaba3ab6f0b42a0997a9bd65d266f2570cbe0` |

Finale Runtime: Windows 6.886 Dateien / 1.120.418.422 Bytes,
Linux 6.789 Dateien / 1.763.173.015 Bytes. Beide Pakete regulär in die eigenen
Testinstallationen übernommen; vollständige installierte Runtimehashes und
acht Zusatztexte geprüft, Debian-Audit leer, dpkg-Dateiprüfung sauber,
Host-Paketstatus unverändert. Keine öffentliche Binärverteilung.

Abschließend beide eigenen Testinstallationen regulär deinstalliert: 77 Windows-
und 514 Linux-Benutzerdateien einschließlich Modellkopien hashgleich erhalten,
unabhängige Sentineldateien erhalten, eigene Anwendungsdateien/Registrierung
entfernt. SQLite-Prüfungen intakt, Linux-Hostpaketstatus unverändert. Eigene
Anwendungsprozesse beendet und Testport frei.

Die Originaltexte bleiben einschließlich Upstream-Leerzeichen und Zeilenenden
unverändert. Git-Zeilenendenkonvertierung ist ausschließlich für den
Lizenzassetordner deaktiviert; alle acht Hashes auch direkt aus dem Index
bestätigt. Eigene Build- und Provenienzdaten ersetzen keine Rechtsfreigabe.

## Lizenzen und FFmpeg

Die konkrete [Distributionsmatrix](THIRD-PARTY.md#distributionsnachprüfung-phase-44-23-november-2026)
belegt acht ergänzte Originaltexte für sechs Paketversionen, einschließlich des
GPLv3-Textes der konkreten FFmpeg-Binaries. Der Builder erkennt jetzt auch
`LICENCE`; drei neue Regressionen sichern Sammlung, Versions-/Texthashbindung
und plattformspezifische native Binärbindung.
Native Notices, exakte Wheel-/Vendorherkunft und Corresponding Source bleiben
unvollständig. GPLv3-ImageIO-FFmpeg und die widersprüchliche LGPL-/x264-/x265-
Selbstauskunft der separaten PyAV-Bibliotheken sind nicht rechtlich freigegeben.
Eine konkrete Liste benötigter Quellen, Buildskripte und Verteilungsnachweise
steht in der Matrix. Keine pauschale Rechtsfreigabe aus vorhandenen Lizenztexten.

## glib-Sicherheitsbewertung

[GHSA-wrw7-89jp-8q8g](https://github.com/advisories/GHSA-wrw7-89jp-8q8g) und
[RUSTSEC-2024-0429](https://rustsec.org/advisories/RUSTSEC-2024-0429.html)
erneut gelesen; kein zugeordnetes CVE. Betroffen sind `VariantStrIter::next`,
`next_back`, `nth`, `nth_back` und `last` in glib >=0.15.0,<0.20.0. Ein C-Aufruf
schreibt durch `&p` in einen als unveränderlich referenzierten Nullzeiger.
Optimierung kann den Schreibzugriff verwerfen; `CStr::from_ptr(NULL)` führt zu
undefiniertem Verhalten und möglichen Abstürzen. Der Upstreamfix verwendet
`let mut p` und `&mut p`. Ein Angriffsweg in MoodScope ist damit noch nicht belegt;
der generische Netzwerk-CVSS-Wert beweist keine fernausnutzbare MoodScope-Lücke.

Der exakte Linux-Lockgraph enthält Tauri 2.12.5, GTK 0.18.2, WebKitGTK-Rust 2.0.2,
Wry 0.57.1, tauri-runtime-wry 2.12.3 und glib 0.18.5. GTK und weitere Bindings
verlangen die 0.18-Linie. Auch der geprüfte aktuelle Tauri-Upstreamstand 2.12.7
verwendet GTK 0.18; Wry 0.57.3 verlangt weiterhin GTK 0.18/WebKitGTK 2.0.2.
Ein unterstütztes einzelnes Update auf glib >=0.20 ist damit nicht nachgewiesen.
Der geprüfte Upstreambranch 0.18 enthält weiterhin die fehlerhafte Stelle.

Die lesende Suche in den lokal vorhandenen Rust-Abhängigkeitsquellen findet
`VariantStrIter`/`array_iter_str` ausschließlich in glib selbst, dessen Tests
und Dokumentation; keine Verwendung im MoodScope-Quellcode oder den übrigen
vorhandenen Abhängigkeiten. Dies begrenzt den belegten Aufrufumfang, ist kein
formaler Nachweis der Nichterreichbarkeit im optimierten ausgelieferten ELF.
Das Paket bleibt aufgrund seiner aufgelösten Version advisory-betroffen.

Ein eigener kleiner Backport ist technisch denkbar, aber kein nachgewiesener
gewarteter 0.18-Release. Er würde überprüfte Vendorquellen, Patchpflege,
optimierte Iteratorregressionen und vollständige Linux-/Tauri-/Paketabnahme
erfordern. Kein ungeprüfter Fork, kein inkompatibles Override und keine
Warnungsunterdrückung eingebaut. Dependabot #2 im angemeldeten Brave erneut
bestätigt: offen, 0.18.5 maximal auflösbar, Fix ab 0.20.0; genau ein offener
Dependabot-Alert in der gelesenen Übersicht. Keine Warnung ausgeblendet.

Vorläufig: keine neuen betroffenen Iteratoraufrufe einführen, lokale
Desktop-/Loopback-Grenze erhalten und keine öffentliche Binärfreigabe erteilen.
Für die Releaseentscheidung fehlen ein unterstützter Fix oder ein vollständig
geprüfter kompatibler Backport sowie die dokumentierte Restrisikobewertung.
Quellen: [Tauri](https://github.com/tauri-apps/tauri/blob/dev/crates/tauri/Cargo.toml),
[Wry](https://github.com/tauri-apps/wry/blob/dev/Cargo.toml),
[Upstreamfix](https://github.com/gtk-rs/gtk-rs-core/pull/1343).

## Echte installierte CPU-Inferenz unter Linux

Tatsächlich installierter, unveränderter Phase-4.3-Debian-Client in einer neuen
isolierten Kopie der vollständig konfigurierten Testsystemwurzel, UID 1000,
schreibgeschützte Installation, maskiertes System-Python, eigener autonomer
Backendprozess. Modelle liegen in Kopien im eigenen Benutzer-Datenverzeichnis;
kein Download, keine produktiven Gewichtsänderungen und keine Cloudaufrufe.

| Modell/Fall | Tatsächlicher Nachweis |
|---|---|
| CLAP + XLM-EMO / CPU | Frischer Auftrag mit lokalem 20-s-Musikexcerpt und zwei ausdrücklich selbst verfassten Testtextzeilen: vier Audio-/zwei Textsegmente, `cached=False`, 23,38 s; nativ nach Appneustart geöffnet |
| Demucs / CPU | `htdemucs` mit vorhandenen Original-Checkpointkopien: echter Auftrag abgeschlossen, vier erzeugte Quellen; keine vorbereiteten Stemfixtures verwendet |
| Faster-Whisper Base / CPU | Vorhandener vollständiger 145.217.532-Byte-Checkpoint separat materialisiert und kopiert; echte Offline-Transkription/Analyse abgeschlossen. Keine Behauptung vollständiger oder korrekter Worterkennung |
| Abbruch | Neuer echter Analyseauftrag: `cancelled`, „Auftrag abgebrochen“, kein Ersatzresultat |
| Fehlende Gewichte | Vor Bereitstellung der Whisper-Kopie verständliche Installationshilfe im nativen Client sichtbar; kein Download oder fingiertes Ergebnis |
| Reguläres Ende | Zugeordnetes WSLg-Fenster regulär geschlossen: Exit 0, keine eigenen Kinder, Testport frei; eigene Daten danach hashgleich |
| Music2Emo | Weiterhin ausdrücklich nicht verfügbar; kein Kompatibilitätsbundle ergänzt |

Der erste Testhalter erreichte nach erfolgreicher Inferenz seine 900-s-Grenze.
Sein Cleanup zählt nicht als reguläres Beenden. Der anschließende echte Neustart
öffnete das gespeicherte CLAP-/XLM-EMO-Ergebnis nativ; der getrennte spätere
reguläre Exit 0 ist der Beenden-Nachweis. Native Detail-/Spurauswahl und endgültige
Neustartmatrix werden nicht aus HTTP-Erfolgen allein abgeleitet.

## Linux-Negativmatrix im installierten Client

Eigene Phase-4.4-Systemkopie mit dem hashgeprüften ursprünglichen installierten
Phase-4.3-Client. Pro Fall separates Benutzerprofil. API-/Besitz-/Verzögerungs-
proben verwenden ausschließlich das selbst verfasste Health-Protokollprogramm;
sie sind keine Analyse- oder Modelltests. Nach jedem Fall ist die echte
Runtime hashgleich wiederhergestellt. Native Fehlerdialoge wurden aufgenommen.

| Fall | Ergebnis |
|---|---|
| API 15 statt 16 | Kein Hauptfenster, native Startfehlermeldung nach 121,04 s, Exit 1 |
| Falsche Besitzkennung | Kein Hauptfenster, native Startfehlermeldung nach 120,90 s, Exit 1 |
| Fehlende Runtime | Native Fehlermeldung nach 0,27 s, Exit 1; Datei unverändert wiederhergestellt |
| Eigener fremder Testlistener | Native Fehlermeldung, Exit 1; Listener erhalten, null HTTP-Nutzdaten empfangen |
| Kontrolliert fünf Sekunden verzögert | Hauptfenster nach 5,40 s; reguläres Alt-F4, Exit 0 |
| Echter Neustart nach Fehlern | Echte unveränderte Runtime startet nach 2,84 s wieder; reguläres Schließen über das Fensterkreuz, Exit 0 |

Keine fremden Listener beendet und keine globale Linux-Paketreparatur.
Die Prüfung gilt für diese WSLg-/hostbasierte isolierte Installation, nicht für
einen unabhängigen Linux-Desktop. Windows-Negativnachweise bleiben separat.

## Finaler Installationsnachlauf vom 24. November

Der neue Debian-Kandidat wurde nach der Unterbrechung in derselben eigenen
Systemkopie regulär erneut installiert, anschließend `dpkg --audit` leer und
`dpkg --verify` ohne Abweichung. Nach dem abschließenden GPL-Nachlauf passen alle
6.789 installierten Runtime-Dateien zum Manifest; acht Zusatztexte enthalten,
Host-Paketstatus hashgleich.
Ein vorher abgebrochener Halterlauf zählt nicht als vollständiger Nachweis.
Die alten eigenen Linux-Testdaten/-modelle wurden für die neue Kennung kopiert;
das ist keine Migration oder Prüfung eines tatsächlichen Versionsupdates.

Der final installierte Windows-Client startet ohne Python im PATH und mit
ungültigen geerbten Pythonpfaden seinen eigenen CPU-Dienst. Alle **6.886**
installierten Runtime-Dateien sind hashgeprüft. Modellkopien liegen außerhalb
der Installation im eigenen Testbenutzerverzeichnis. Echte Inferenz über die
installierte API, getrennt von nativer UI-Abnahme:

| Windows-Fall | Ergebnis |
|---|---|
| CLAP + XLM-EMO / CPU | Vier Audio-/zwei Textsegmente aus freigegebener Testmusik und selbst verfasstem Text, `cached=False`, 48,55 s |
| Demucs htdemucs / CPU | Tatsächlicher Auftrag abgeschlossen, vier neue Quellen, `cached=False` |
| Faster-Whisper Base / CPU | Modell geladen und echte lokale Berechnung abgeschlossen; **null erkannte Textsegmente**, kein Worterkennungsnachweis |
| Echter Abbruch | Neuer Analyseauftrag `cancelled`, kein Ersatzresultat |
| App schließen und neu starten | Reguläres Alt-F4, Exit 0; neuer autonomer Backendbesitzer und neue Instanzkennung |
| Gespeicherte Ergebnisse nach Neustart | Installierte API liest Analyse und echte Demucs-Spuren wieder; neun Benutzerdatendateien hashgleich, SQLite intakt |
| Native Ergebnisanzeige/-wiederöffnung | Nach Auswahl des vollständigen Fensterbildes bedienbar: neuer CLAP-/XLM-EMO-Auftrag nativ gestartet, `cached=False`, zehn Audio-/zwei Textsegmente in 14,24 s; Kurven und beide selbst verfassten Textzeilen sichtbar. Nach regulärem Schließen und Neustart erneut nativ als „CPU · AUS CACHE“ geöffnet |

Die zunächst reproduzierte 16×16-/fehlende Werkzeuggeometrie ist durch explizite
Auswahl des vollständigen Fensterbildes gelöst; keine App- oder Werkzeugquellen
gepatcht. Unter Windows wurde anschließend im nativen Hörstudio „Demucs · 4
Gruppen“ ausgewählt; `htdemucs` und gespeicherte Spurbedienelemente sichtbar.
Neun eigene Datendateien nach Neustart hashgleich, SQLite intakt, abschließendes
Alt-F4 mit Exit 0 und freiem Port. Unter Linux im finalen Achttextpaket ebenfalls
Kurven und zwei Testtextzeilen nach Neustart geöffnet, ausdrücklich Demucs statt
Auto ausgewählt und „Gespeicherte Spuren sind bereit“ für `htdemucs` angezeigt.
Regulärer Exit 0, keine eigenen Kinder oder Listener. Ein zwischenzeitlich
unterbrochener Halter zählt nicht als regulärer Exit; der getrennte abschließende
Lauf liefert diesen Nachweis. Der ursprüngliche Linux-Whisper-Lauf ergab ebenfalls
null Textsegmente: echte Inferenz ohne Beleg erfolgreicher Worterkennung.

## Finale Linux-Audioprobe

Die erste lesende `pactl info`-Probe meldete erneut `Connection refused`.
Später war derselbe WSLg-Server ohne Konfigurationsänderung wieder erreichbar,
`RDPSink.monitor` vorhanden. Der installierte Client importierte das ausdrücklich
synthetische Stereo-/48-kHz-/2-s-/440-Hz-Signal über seinen nativen GTK-Dialog.
Ausgabemonitor: 127.174 Frames, Spitzenpegel 0,15872, 63.939 aktive Samples,
aktive Spanne 1,38998 s, dominante Frequenz 440,294 Hz. Dies belegt ein Signal
am WSLg-Monitor, keine vollständige zweisekündige verlustfreie Erfassung und
keine physische Windows-Geräteausgabe. Keine WSL-/Audioeinstellung erzwungen,
kein fremder Audiodienst beendet. Ein zunächst unvollständig eingetragener
Dialogpfad wurde am Screenshot korrigiert und erst danach bestätigt.

## Distributionslocks, Updates und Regressionen

[CPU-Lockgrenze](BACKEND-RUNTIME.md#nachprüfung-phase-44): offizielle Artefakthashes
lesend geprüft, aber kein vollständiger plattformweiser Hashlock mit frischer
Installations-/Buildregression abgeschlossen. Insbesondere CPU-Index und
Demucs-Sourcebuild getrennt behandeln. Keine ungeprüften Dependency-Upgrades.
Keine zwei geeigneten unterschiedlichen Installationsversionen vorhanden;
versionswechselndes Update bleibt auf beiden Plattformen offen. Ein
Gleichversions-/Lizenzpaketnachlauf schließt dieses Gate nicht.

Windows: **412 Backendtests bestanden, ein POSIX-Skip**; Linux: **413 bestanden**.
Je Plattform 156 Frontend-, zehn Rust- und fünf Node-Tests sowie TypeScript/Vite
bestanden. Native Release-/NSIS-/Debian-Builds erfolgreich. Bekannte Vite-
Chunkwarnung und Windows-Hardlinkwarnung im Rustcache ohne Testfehler.
Der eingeschränkte erste Windows-Backendlauf lieferte keinen belastbaren
Abschluss; der vollständige Lauf außerhalb der Sandbox zählt. Ein neuer Test
hatte zunächst eine plattformabhängige Pfaderwartung; nach Korrektur beide
vollständigen Suiten erfolgreich. Keine Produktionsdaten für Tests verwendet.

Vor-/Nachvergleich: alle **10.071** geschützten Musik-, Modell- und produktiven
Datendateien hashgleich; produktive SQLite lesend `integrity_check=ok`.
Rohinventare, Modellkopien, Musik, Texte und Identifikatoren bleiben ignoriert
lokal. Keine externen Datenbankadapter oder echten Anbieteraufrufe.

Weiterhin offen: vollständige native Modell-/Lyrics-/Plattformkreuzmatrix,
versionswechselnde Updates, CPU-Hashlocks, unabhängiger Linux-Desktop,
Windows 10, DPI/Mehrmonitor, physische Ausgabe, die früheren Ressourcen-/
Qualitätsgrenzen sowie glib und vollständige native Distributionsrechte.
**Phase 4 teilweise bestanden; Binärfreigabe blockiert.**

---

# Phase 4.3: Finaler Paketnachlauf

Prüfserie vom 23. November 2026. **Weiterhin teilweise bestanden; keine
Endnutzerfreigabe und keine Veröffentlichung von Installationsbinaries.**
Die unten erhaltenen Phase-4.2- und Phase-4.1-Berichte gelten ausschließlich
für ihre damaligen Kandidaten. Die folgenden Pakete wurden neu gebaut.

## Exakte Quell- und Paketbindung

Anwendungscheckpoint: `25b4dc06211d7f4d925d426b8011b39e764be6aa` auf
`codex/phase4-platform-installer`, auf öffentlicher Abstammung. Ausgangshead
`2f89689` erneut mit origin und Draft-PR #17 abgeglichen; alle vier PR-Jobs
erfolgreich. Main beim Abgleich unverändert `1717ffd`. Keine Übernahme von #15,
kein Merge, Force-Push, PR-Schließen oder Endnutzer-Release.

Der Nachlauf fand eine rohe englische Whisper-Offline-Fehlmeldung. Die gezielte
Korrektur erklärt fehlende Gewichte und die Modellverwaltung auf Deutsch und
Englisch, ohne Retry oder Ersatzwerte. Unbenutzte Torch-Testprogramme und deren
Testarchive werden beim Runtimebau entfernt; notwendige Helfer bleiben erhalten.
Beide Änderungen haben eigene Regressionen. Die zunächst aus `2f89689` gebauten
Zwischenpakete gelten nicht als Nachweis für den korrigierten Kandidaten.

Frische PyInstaller-Analysen aus den separaten CPU-Buildern, jeweils erfolgreiches
`pip check`, aufgelöste Paketinventare, Lizenzsammlung und vollständige SHA256-
Dateimanifeste. 239 Quell-Dateihashes binden die Linux-Kopie an den Checkpoint;
installierte Runtime-Dateien wurden gegen die neuen Manifeste verglichen.
Keine Musik, Lyrics, SQLite oder Modellgewichte im finalen Runtime-Dateiinventar.
Kein Nachweis bitidentischer Wiederholungsbuilds; CPU-Distributionslocks bleiben offen.

| Kandidat | Runtime | Installationspaket | SHA256 des Pakets |
|---|---|---|---|
| Windows x64 / NSIS | 6.876 Dateien, 1.120.328.268 Bytes | 415.900.755 Bytes | `30e0bd71e008e1d7a2ee8db85bfdf710c22a63c2727ba766e1552c85f43fd9ed` |
| Linux x86_64 / Debian | 6.779 Dateien, 1.763.082.947 Bytes | 602.680.696 Bytes | `5916a255a3b97d5f3c4e092ccfdbeb5443681cd3bbf7048a6de231dc6b279ee0` |

Beide Pakete verwenden ausschließlich eine eigene Testkennung. Produktive
Einstellungen oder Gewichte wurden nicht übernommen. Ein fehlender NSIS-
Cache-/DNS-Zugriff im Sandbox-Build wurde durch einen regulären Build mit
Zugriff auf die vorhandenen offiziellen Werkzeuge behoben.

## Tatsächliche finale Installationsnachweise

| Fall | Windows NSIS | Linux Debian / WSLg |
|---|---|---|
| Installation | Eigener Zielpfad und Registrierung, Exit 0; finale Runtimehashes stimmen | Vollständig konfigurierte isolierte Systemkopie, reguläres dpkg-Installieren, Exit 0, leeres `dpkg --audit`; Runtimehashes stimmen |
| Autonomer Start | Python-freier PATH, ungültige PYTHONHOME/PYTHONPATH; Overrides im eigenen Worker entfernt | System-Python maskiert, ungültige Python-Overrides, eigene Runtime und Health bestätigt |
| Schreibschutz | Eigener Runtimeordner per gesicherter ACL schreibgeschützt; Schreibprobe abgewiesen, ursprüngliche ACL anschließend wiederhergestellt | Gesamte installierte Systemkopie nur lesbar eingebunden; eigenes Profil schreibbar |
| Health / Besitz | Version 0.3.0, API 16, eigene Besitzkennung und Prozessfamilie bestätigt | Entsprechender Healthcheck und Prozessfamilie; Client und Backend als UID 1000 |
| Musikimport | Nativer WAV-Dateidialog mit lokalem 20-s-Testmusikausschnitt | Nativer GTK-Dateidialog mit demselben lokalen Ausschnitt |
| Wiedergabe | Native Anzeige bis 11,45 s, danach Songende; keine physische Ausgabemessung | Finale Wiederholung offen; unten abgegrenzte Testumgebungs-/WSLg-Störung |
| WAV-Export | Nativer Speicherdialog; Stereo, 48 kHz, 960.000 Frames, maximaler Samplefehler 0 | GTK-Speicherdialog; dieselben Eigenschaften und maximaler Samplefehler 0 |
| Modellpfade | Installierte API: eigener verwalteter Testmarker entfernt, fremder Pfad abgewiesen, Auswahlrückfall und Fehlerwiederholung bestanden | Entsprechende installierte API-Regressionsfolge bestanden |
| Fehlende Gewichte | Neue verständliche Whisper-Installationshilfe nativ sichtbar | Entsprechende neue Hilfe nativ sichtbar |
| Reguläres Ende | UI-Beenden und Bestätigung, Exit 0, keine eigenen Kinder oder Listener | Alt-F4, Exit 0, keine eigene Backendfamilie oder Listener |
| Worker-/Clientcrash und Neustart | Finale installierte Prozessmatrix bestanden, Benutzerdaten hashgleich und SQLite intakt | Finale installierte Matrix als UID 1000 bestanden; Daten hashgleich, SQLite intakt, eigene Kinder/Port freigegeben |
| Supervisorverlust | Finale Wiederholung: Client Exit 1, keine eigenen Kinder oder Listener | Finale installierte Wiederholung: Exit 1, keine eigenen Kinder oder Listener |
| Inkompatible API | Eigenes künstliches Testbackend mit API 15: kein Hauptfenster; 120-s-Readinessgrenze und native Fehlermeldung | Finale native Fehlerprobe offen |
| Falsche Besitzkennung | Eigenes künstliches Testbackend: kein Hauptfenster, Readiness-Timeout, Client Exit 1; echte Runtime danach hashgleich | Finale native Fehlerprobe offen |
| Belegter Port | Eigener fremder Testlistener bleibt erhalten; keine Backendkinder, keine HTTP-Nutzdaten | Finale native Fehlerprobe offen |
| Fehlende Runtime-Datei | Native Neuinstallationshilfe, Client Exit 1; Originaldatei hashgleich wiederhergestellt | Finale native Fehlerprobe offen |
| Verzögerter Start | Kontrollierte fünf Sekunden Verzögerung des eigenen Health-Testbackends; Hauptfenster erscheint, Alt-F4 Exit 0 | Finale native Fehlerprobe offen |
| Wiederholung nach Dienstfehler | Anschließend echte unveränderte Runtime erneut mit eigener Familie gestartet; „Dienst bereit“, Alt-F4 Exit 0 ohne Kinder oder Listener | Finale native Fehlerprobe offen |
| Gleichversions-Reinstallation | Getrennter sequenzieller Lauf, Exit 0; zehn Benutzerdatendateien erhalten | Reguläre Ersetzung durch das korrigierte Paket in der konfigurierten Testwurzel |
| Versionswechsel | Offen: keine zwei sicher verwendbaren unterschiedlichen Installationsversionen | Offen |
| Deinstallation | Eigene Anwendung und Registrierung entfernt; 16 Benutzer-/Profil-/Exportdateien hashgleich, fremde Sentineldatei erhalten | Eigene Anwendung regulär mit dpkg entfernt; 190 Benutzerdateien hashgleich, SQLite intakt, fremde Sentineldatei und Hoststatus erhalten |

Die Exporte prüfen den realen WAV-/Dialogweg mit einem ausdrücklich markierten
Cache aus dem lokalen Originalmix. Sie sind **keine Demucs-Trennung oder
Modellinferenz**. Musik- und Quelldateinamen, WAVs und Rohbelege bleiben lokal.
Die zusätzlich angeforderte synthetische Linux-Monitorprobe ist vorbereitet,
aber für dieses Paket noch nicht erfolgreich gemessen. Historische synthetische
Messungen unten ersetzen diese finale Probe nicht.

Die API-/Besitz-/Verzögerungsproben ersetzen vorübergehend ausschließlich die
eigene Test-Runtime durch ein selbst verfasstes lokales Protokollprogramm.
Sie prüfen Tauris native Startgrenze, nicht einen vollständigen Analysedienst.
Die echte Runtime wurde nach jeder Probe anhand ihres Ausgangshashes
wiederhergestellt; ein erfolgreicher echter Neustart schließt die Folge ab.
Portkonflikt und fehlende Datei verwenden den tatsächlichen installierten
Client. Der unbekannte Listener erhielt nur geschlossene TCP-Verbindungen
ohne HTTP-Nutzdaten und wurde vom Client weder übernommen noch beendet.

Die erste Linux-Benutzerisolation erzeugte Temp-Dateisysteme mit Root-Rechten;
ein Diagnosesocket belegte den fehlenden Schreibzugriff für UID 1000. Nur im
Testnamespace auf übliche Rechte korrigiert. Eine eigene D-Bus-Sitzung zeigte
außerdem die zunächst fehlende UID-Auflösung; der gesperrte Testbenutzer wurde
ausschließlich in der Systemkopie ergänzt. Beim späteren Nachlauf verweigert
der WSLg-PulseAudio-Server die Verbindung (`Connection refused`), auch mit
separater begrenzter `pactl`-Prüfung. Kein fremder Audiodienst beendet oder WSL
zurückgesetzt. Finale Audiomessung bleibt offen; kein bewiesener Appfehler aus
dieser Testumgebungsgrenze abgeleitet.

Eine Windows-Reinstallation überlappte versehentlich mit einer Crashprobe;
dieser Versuch ist ungültig. Getrennte Wiederholungen bestanden vollständig.
Weitere Halterkorrekturen: Mountpunkte vor schreibgeschütztem Einbinden anlegen,
Hostpfade auf den Linux-Testnamespace abbilden und native Dialoge vor Eingaben
erneut eindeutig auswählen. Haltercleanup zählt nicht als reguläres Beenden.

Ein zu früh während des Debian-Bundlings gestarteter Nachinstallationslauf
hatte alte dpkg-Kontrollsummen bei bereits aktuellen Nutzdateien behalten.
Der Vergleich mit dem fertig gebauten Paket bestätigt unveränderte korrekte
Paket- und Nutzdatenhashes. Installation nach vollständigem Buildende regulär
wiederholt; anschließend `dpkg --verify` ohne Abweichung und `dpkg --audit`
leer. Erst danach wurde die erfolgreiche Deinstallation gewertet. Kein
Paketmanagerzustand des Hosts betroffen und keine Force-Reparatur verwendet.

## Debian-Abhängigkeit und Isolationsgrenzen

`gstreamer1.0-plugins-bad` ist im endgültigen Debianpaket korrekt deklariert.
WebKits GStreamer-Medienpfad benötigt unter anderem dessen `fakevideosink` aus
`libgstdebugutilsbad.so`. Basis-/Good-Plugins, Audiosink, WAV-Parser und weitere
benötigte Elemente wurden in derselben Benutzerisolation gefunden; PulseAudio
war bei der ersten Diagnose erreichbar. Kein lokaler Plugin-Suchpfad ersetzt
die Paketinstallation.

Nach lesender Vorprüfung wurde ausschließlich eine eigene Kopie der Ubuntu-
Systemdateien und Paketdatenbanken angelegt. Darin ließ sich `libc-bin` regulär
konfigurieren; eine apt-Simulation wurde vor der normalen Installation geprüft.
87 GStreamer-Pakete wurden nur dort zusätzlich installiert, danach der finale
MoodScope-Kandidat mit normalem dpkg konfiguriert. Keine Force-Option, gelöschte
Sperre, beendeter Paketprozess oder globale Abhängigkeitsinstallation.
Host-Paketstatus blieb hashgleich und dessen halb konfiguriertes `libc-bin`
unverändert. Das ist eine vollständig konfigurierte **hostbasierte isolierte
Installation**, kein frischer oder unabhängiger Ubuntu-Desktop.

## Regressionen und Freigabegrenzen

Korrigierter Quellcheckpoint: Windows **409 Backendtests bestanden, ein POSIX-
Skip**; Linux **410 bestanden**. Je Plattform **156 Frontend-, zehn Rust- und
fünf Node-Tests**, TypeScript/Vite sowie native Release-/Paketbuilds bestanden.
Der erste Linux-Testlauf hatte nur ein fehlendes Git-Verzeichnis in der neuen
Quellkopie als Fehler; der vollständige korrigierte Lauf bestand. Die bekannte
Vite-Chunkwarnung bleibt. Diese Prüfungen ersetzen keine installierte Modellmatrix.

Music2Emo ist im installierten Paket weiterhin zuverlässig nicht verfügbar.
Keine ungefragten Downloads, produktiven Modellkopien, echten Cloudaufträge,
Anbieterwechsel oder Änderungen der Consent-Logik. Echte installierte Inferenz
bleibt ohne gesondert freigegebene Testgewichte unbestätigt. Die technische
Empfehlung für eine spätere getrennte Kompatibilitätsruntime steht unter
[Backend-Runtime](BACKEND-RUNTIME.md).

Der Vor-/Nachvergleich aller 10.071 geschützten Musik-, Modell- und produktiven
Datendateien ist hashgleich; produktive SQLite wurde lesend mit
`integrity_check=ok` geprüft. Die eigene Windows-Crashmatrix erhält die
Testdatenhashes und bestätigt ebenfalls SQLite-Integrität. Es wurden keine
Originaldateien, produktiven Gewichte oder Einstellungen für die Installation
verschoben oder verändert. Rohbelege und Dateimanifeste bleiben ignoriert lokal.
Die Linux-Crash-/Deinstallationsprüfungen bestätigen ebenfalls SQLite-Integrität.
Der abschließende Prozess-/Portabgleich auf beiden Plattformen findet keine
eigene native Testfamilie und keinen Listener auf dem Testport.

Binärfreigabe blockiert: fehlende Lizenztexte in fünf Distributionen, exakte
GPL-FFmpeg-Quellen/Buildherkunft und vollständige native Notices/Weiterverteilungs-
nachweise. Die konkrete Versions-/Lizenzmatrix steht unter
[Drittanbieter](THIRD-PARTY.md#konkrete-distributionsprüfung-phase-43).

Dependabot-Alert #2 und `GHSA-wrw7-89jp-8q8g` erneut im angemeldeten Browser
geprüft. Der aktuelle Linux-Rustgraph führt `glib 0.18.5` über GTK 0.18.2,
WebKitGTK und Tauri 2.12.5. GTK verlangt `glib = 0.18`; GitHub bestätigt 0.18.5
als höchste auflösbare Version, die Advisory nennt 0.20.0 als erste gepatchte
Version. Ein direktes Update wäre keine kompatible Einzelkorrektur. Keine
ungeprüfte GTK-Migration, kein selbst behaupteter Fix und keine Ausblendung
der Warnung. [Advisory](https://github.com/advisories/GHSA-wrw7-89jp-8q8g).

Weiter offen: restliche native Fehlerfälle, versionswechselndes Update, CPU-
Distributionslocks, finale Linux-Audioprobe, vollständige installierte Modell-/
Lyricsmatrix, unabhängiger Linux-Desktop, Windows 10, weitere DPI/Mehrmonitor,
physische Windows-Ausgabe, zweites echtes Textemotionsmodell, Phase-3-
Speicherrestbedarf/Proactor-Ursache und Musik-/Modellqualität. **Phase 4 bleibt
teilweise bestanden; keine Endnutzer- oder öffentliche Binärfreigabe.**

---

# Historischer Phase-4.2-Stand: Backend-Runtime und Installationsprüfung

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

Der erste neue CI-Pushlauf fand ein Rennen im Testhalter: Der beendete Nachkomme
kann zwischen `is_running()` und `status()` verschwinden. Der parallele PR-Lauf
bestand. Die Regression akzeptiert nun `NoSuchProcess` als abgeschlossenen
Prozess; keine Änderung am Anwendungscleanup und kein bloßer Wiederholungslauf.

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
