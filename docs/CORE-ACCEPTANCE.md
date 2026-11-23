# Kernabnahme und Freigabegrenzen

Fachlicher Überblick und datierte Nachweise. Aktueller Projekt- und Integrationsstatus:
[STATUS.md](STATUS.md); Navigation: [Dokumentationsübersicht](README.md).

## Entscheidung

Die Anwendung bleibt eine Entwicklungsversion. Die Veröffentlichung geprüfter
Quellverbesserungen bedeutet keine vollständige Kern-, Plattform- oder
Qualitätsfreigabe. Die externe Datenbankphase ist weiterhin gesperrt; SQLite
bleibt Standard. Kein MariaDB-, Supabase- oder Firebase-Adapter wurde ergänzt.

## Phase 4.3 am 23. November 2026

**Weiterhin teilweise bestanden.** Neue Windows-/Linux-Kandidaten aus
`25b4dc0` enthalten den autonomen Backendstand einschließlich der finalen
Modellpfadkorrektur und einer verständlichen Offline-Whisper-Fehlgewichtshilfe.
Beide installierten APIs bestehen die Modellpfadregression mit eigenen
Wegwerfmarkern. Keine echte installierte Modellinferenz behauptet.

Windows startet ohne Python im PATH, trotz ungültiger Python-Overrides und
schreibgeschützter Runtime. Nativer Musikimport, Wiedergabefortschritt,
samplegleicher WAV-Export und reguläres Ende sind bestätigt. Worker-/Client-
Crash, Neustart und Supervisorverlust mit Exit 1 sind im getrennten finalen
Lauf bestanden. Eine überlappende Reinstallation war ein ungültiger
Testhalterversuch; die sequenzielle Wiederholung erhält zehn Datendateien.

Linux-Debian ist einschließlich GStreamer-bad in einer isolierten Kopie der
Ubuntu-Systemdateien vollständig konfiguriert. Hostpakete unverändert.
Schreibgeschützter autonomer Start als UID 1000, GTK-Musikimport, samplegleicher
WAV-Export und Alt-F4 mit vollständigem Cleanup sind bestätigt. Die neue
Audiowiederholung bleibt offen: zunächst unpassende Temp-Rechte im Testhalter,
beim späteren Nachlauf verweigert der WSLg-PulseAudio-Server die Verbindung.
Frühere Monitormessungen sind kein Nachweis für diesen Kandidaten. Auch die
finale installierte Linux-Crash-/Neustart-/Supervisorverlustmatrix als UID 1000
ist bestanden. Beide eigenen Testinstallationen sind entfernt; Benutzerdateien,
Exporte und fremde Sentineldateien blieben erhalten.

409 Backendtests plus ein POSIX-Skip auf Windows, 410 unter Linux; jeweils
156 Frontend-, zehn Rust- und fünf Node-Tests, Web-/Release-/Paketbuilds.
Binärlizenzen/Quellbereitstellung, glib-Advisory, CPU-Distributionslocks,
versionswechselndes Update, installierte Modell-/Lyricsmatrix, Windows 10,
unabhängiger Linux-Desktop und frühere Ressourcen-/Qualitätsgrenzen bleiben
offen. Die folgenden Phase-4.1-Aussagen sind historische Clientpaketnachweise.
[Aktuelle Paketmatrix und Grenzen](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).

## Historischer Phase-4.1-Stand am 21./22. November 2026

**Teilweise bestanden.** Isolierter Windows-NSIS-Installations-/Deinstallationslauf
mit Datenerhalt und nativen WAV-Dialogen; tatsächlicher Ubuntu-WSL2-Build samt
Debian-Paket und WSLg-GUI mit GTK-Dateidialogen, Seeking/Loop/Pause, numerisch
geprüftem WAV-Export und Signal am WSLg-Ausgabemonitor. Eigene Bibliotheken nach
beaufsichtigten Neustarts identisch, geschützte Produktionsdateien unverändert.

Beide Installationspakete enthalten nur den Client. Eigenständiger Backendstart
ohne Entwicklungsumgebung bleibt blockiert; externe Prüfdienste schließen diese
Lücke nicht. Echte Linux-Paketinstallation, regulärer Linux-Quitpfad, physische
Audioausgabe, vollständige Lyrics-/Modellmatrix und weitere Plattform-/DPI-Fälle
offen. Frühere Ressourcen-, Proactor- und Qualitätsbefunde bleiben erhalten.
[Getrennte Plattformmatrix und Nachweise](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).

## Phase 3 am 20./21. November 2026

**Teilweise bestanden.** Zehn wiederholte native Original-/Live-Mixzyklen
sowie ein zusätzlicher Ansichts-/Songwechselgraph geben elf Contexts,
99 Nodes und acht Mixerlistener frei. Echte lokale CLAP-, XLM-EMO-,
Music2Emo- und Demucs-Wiederholungen, gezielte Abbrüche/Neuläufe und Cacheaufrufe
sind von den automatisierten Regressionen getrennt dokumentiert.

Die [zentrale Freigabematrix](PHASE3-PERFORMANCE-ACCEPTANCE.md#zentrale-freigabematrix)
führt offene Phase-2B-/2C-Kriterien fort. Zweites echtes Textemotionsmodell,
vollständige native Kreuzmatrix, tatsächliche Audioausgabe und breitere
Langzeit-/Musiklast bleiben offen; weitere DPI-/Plattform-/Installerprüfungen
gehören zu Phase 4, abschließende Qualität und Releaseentscheidung zu Phase 5.
Historische Berichte werden dadurch nicht rückwirkend umgeschrieben.

## Phase 2C am 20. November 2026

Teilweise bestanden: echte native Demucs-Trennung mit Abbruch/Neulauf, Live-Mix,
gemeinsamer Loop, numerisch geprüfte native Exporte und sichere Dialogabbrüche.
Ein Solo-Schnellpfad lieferte nicht endliche Float-Samples ungeprüft aus;
blockweise Prüfung ergänzt und nativ mit erhaltenem vorhandenen Exportziel bestätigt.
Kombinierter Ablauf einschließlich echter lokaler Analyse, kontrollierter Loopback-API,
Widerruf und App-/Dienstneustart mit unveränderten SQLite-/Audio-/Stemständen geprüft.
32 Player-/Kurvenpaare: maximal 23,3 ms Anzeigeunterschied, keine Ausgabelatenzmessung.
Fehlgewichte, harter Demucs-Dienstfehler und vollständige native Audio-Ressourcen-/
Seeking-/Ausgabesynchronisationsmatrix offen. Phase 2B bleibt teilweise bestanden.
[Vollständige Phase-2C-Matrix](PHASE2C-ACCEPTANCE.md). Keine Kernfreigabe.

## Phase 2B am 18. November 2026

Teilweise bestanden: echte Offline- und kontrollierte Loopback-Anbietertests,
native Auswahl und Local/API/Local sowie Neustart-/Datenintegrität geprüft.
Reproduzierter Music2Emo-Gerätekonflikt im Testhalter korrigiert; historische
Ursache ohne damaligen Workerlog bleibt unbestätigt. Native Reduced-Motion-,
unterbrochene Übergangs- und vollständige Profil-/Auftragsmatrix noch offen.
[Vollständige Matrix](PHASE2B-ACCEPTANCE.md). Keine vollständige Kernfreigabe.

## Abgesicherte Bereiche

- Zielgebundene Übertragungszustimmung und Aufgaben-/Profil-/Key-Snapshots.
- Journalisierte Bibliothekslöschung, Wiederimport und SQLite-Transaktionen.
- Gemeinsame Medienzeit, Stemstart, Ressourcenfreigabe und WAV-Transferprüfung.
- Schutz vor verspäteten Songdetails und veralteten Notizspeicherantworten.
- Endliche Modellwerte, kooperative Abbrüche und Belegpflicht für Textdeutungen.
- Deutsch/Englisch, gemeinsame Palette und reduzierte Bewegung.

## Noch erforderliche Abnahmen

### Phase 2A und Phase 2A.2 am 17./18. November 2026

**Phase 2A im festgelegten synthetischen Windows-Prüfumfang vollständig bestanden.**
Die zunächst blockierten Audio-, Wieder-, Fehlquell- und LRC-Dateiimporte wurden
mit dem neu gebauten Windows-Programm tatsächlich nativ ausgeführt. Der bestehende
Tauri-Dialog ist nun explizit an das Hauptfenster gebunden; bildgebundene Eingaben
vermeiden die nachgewiesene WebView2-Prozess- und Accessibility-Indexgrenze.
Browserimporte verwenden weiterhin die bisherigen HTML-Dateiinputs.

Beide Reparaturfälle erhalten Trackidentität, Analyse und Notiz; ungültige Quellen
zeigen den Dekodierhinweis ohne SQLite-Änderung. Audio-/LRC-Abbruch, neu importierte
Lyrics mit 10,25-s-Navigation in Player und Kurve sowie vollständiger App-/Dienst-
neustart mit unveränderten Bibliothekszeilen und Audiohashes bestanden. Frühere
Wiedergabe-, Seeking-, Songwechsel- und A/B-Nachweise bleiben getrennt erhalten.
Originalbestand, synthetische Quellen und produktive SQLite unverändert; eigene
Prüfprozesse beendet. Nur synthetische Signale und verfasste Texte; keine neue
Musikqualitätsabnahme. Eine lokale Verarbeitung der importierten LRC wurde über
die UI ausgeführt, danach aus gespeichertem Ergebnis wieder geöffnet.

Desktoptests am 17., Abschluss am 18. November. PR #10 war beim Testbeginn offen,
ist beim Abschlussabgleich bereits gemergt; tatsächlicher Main `1717ffd` in den
Entwicklungsbranch übernommen. Kein automatischer öffentlicher Main-Merge.
Die breitere Kernfreigabe und das externe Datenbank-Gate bleiben offen.
[Vollständige 27-Fälle-Matrix, historische Fehler und Grenzen](PHASE2A-ACCEPTANCE.md).

### Windows-Exportprüfung am 17. November 2026

Die gezielte Phase-1-Prüfung hat keinen Anwendungsfehler beim Abbruch des
Speicherdialogs nachgewiesen. Die 16 × 16 stammen von einem separaten sichtbaren
`Tao Thread Event Target` mit leerem Clientbereich. Das Hauptfenster war normal
groß und hatte 96 DPI. Ein als Cancel adressierter Accessibility-Indexklick
aktivierte tatsächlich Speichern; bei bestehendem Ziel erschien die
Überschreibbestätigung. Diese Eingabefehler erklären die im neuen Lauf erzeugten
synthetischen WAVs. Die historische Sequenz lässt sich ohne damaligen
Eingabetrace nicht rückwirkend vollständig beweisen.

Mit frischen, bildgebundenen Dialogeingaben bestanden Escape, Cancel-Schaltfläche,
Dateinameneingabe mit Abbruch, Erhalt einer vorhandenen Zieldatei, wiederholte
Abbrüche und bestätigter Export vor und nach App-/Dienstneustart. Beide bestätigten
Exporte sind gültige Stereo-WAVs mit 48 kHz, zwei Sekunden und identischem
Quellhash. Produktive SQLite bytegleich, isolierte SQLite intakt, eigene
Prüfprozesse beendet. Ausschließlich synthetische Exportfixtures; keine neue
tatsächliche Musik- oder Modellqualitätsabnahme.

Entscheidung: **Kein Anwendungsfehler nachgewiesen, Automationsproblem behoben**
durch den dokumentierten Eingabeweg. Der Werkzeugfehler selbst ist nicht gepatcht.
Andere DPI-Stufen und längere Ressourcenläufe bleiben unbestätigt. Die breitere
Kernfreigabe und das Datenbank-Gate bleiben unverändert offen.
[Verfahren, vollständige Testmatrix und Grenzen](WINDOWS-DESKTOP-TESTING.md).

### Nachprüfung am 16. November 2026

Die native Windows-App wurde mit neu gebauter Oberfläche und einer isolierten
Kopie der freigegebenen lokalen Testbibliothek bedient. Bibliothek, gespeicherte
Analyse, Vier-Stem-Modell und deutscher WAV-Speicherdialog waren erreichbar.
Zwei Abbrüche mit Escape ließen den beobachteten Exportordner unverändert.
Ein vorheriger Versuch mit automatischer Dateinamensänderung und anschließendem
Cancel-Klick erzeugte hingegen eine WAV; dieser Versuch ist kein Abbruchnachweis.
Direkte Cancel-Klicks blieben wegen erneut gemeldeter 16-mal-16-Fenstergrenzen
unbestätigt. Die widersprüchliche Eingabesequenz ist noch zu klären.

Local/API/Local wurde ohne Anbieteranalyse sichtbar gewechselt: API ohne Cache
wurde neutral, die lokale Rückkehr stellte die Modellfarbe wieder her.
Deutsch/Englisch, Originalmix-Wiedergabe bis zum Abschnittsende und der mit der
Atmosphäre gestaltete Neustartdialog wurden nativ geprüft. App und Dienst
starteten anschließend neu; englische Sprache und Atmosphäreneinstellung blieben
erhalten. Dies deckt nicht die gesamte Profil-/Song-/Modell-/Dialogfehlermatrix ab.
Nach dem Neustart stimmen Tracks und Metadaten der isolierten SQLite mit der
kopierten Ausgangsbibliothek überein; sechs gespeicherte Ergebnisse bleiben
vorhanden und die Datenbankintegrität ist in Ordnung.

Wiederholte tatsächliche Music2Emo-Läufe mit bestehenden lokalen Gewichten
bestanden auf CPU, GPU und erneut CPU. Workerlogs wurden lokal erhalten.
Die korrigierte Wiederholung bestätigte unveränderte Originaldatei und produktive
SQLite. Erfolgreiche Wiederholungen erklären den früheren sporadischen Fehler
weiterhin nicht. Keine neue Qualitäts-, Langzeit- oder Plattformfreigabe.

MariaDB, Supabase und Firebase/Firestore sowie Migration und Rückmigration
sind nicht implementiert. Dafür wurden keine Emulatoren, Mocks oder Liveziele
als erfolgreiche Anwendungstests ausgegeben; keine externe Verbindung geöffnet.
Die folgenden offenen Kriterien gelten mit diesen begrenzten Ergänzungen weiter.

1. Den nun belegten Windows-Dialogablauf bei weiteren DPI-Konfigurationen und
   in längeren Läufen prüfen. Der frühere unklare Versuch bleibt historisch;
   die neue synthetische Abnahme ist oben getrennt dokumentiert.
2. Native Local/API/Local-, Song-/Modellwechsel-, Dialogfehler- und gemeinsame
   App-/Dienstneustartmatrix bei zuverlässigem Fensterzugriff vervollständigen.
3. Sporadischen Music2Emo-Prüfdienstfehler bei Wiederholung mit erhaltenem
   Workerlog aufklären. Erfolgreiche Wiederholungen sind keine Ursachenklärung.
4. Längere Wiedergabe-/Mix-/Speicherprüfung und verfügbare Zielplattformen
   getrennt abnehmen. Windows 10, Linux und Installation bleiben unbestätigt;
   ein erfolgreicher Windows-NSIS-Paketbuild ist keine Installationsabnahme.
5. Grenzen von Worterkennung, Deutungswahrheit, Sängertrennung und zeitlichen
   Emotionsverläufen erhalten. Modellschätzungen sind keine bestätigten Fakten.

[Automatisierte Prüfungen](TEST-BASELINE.md) und [Sicherheitsgrenzen](SECURITY.md).

## Begrenzte Ergänzung Phase 3.2 am 21. November 2026

Das einzelne 20-Minuten-Ziel ist mit einem ununterbrochenen nativen Windows-Lauf
von 20 Minuten 54,51 Sekunden und 251 Ressourcenproben im engen lokalen
Musikumfang geschlossen. Zehn Contexts/90 Nodes freigegeben. Zusätzlicher nativer
Speicherverbleib nach Wiederholungen und die genaue Proactor-Ursache bleiben offen;
keine Kern- oder Releasefreigabe. Physische Audioausgabe, zweites echtes
Textemotionsmodell, vollständige native Lyrics-/API-/Audiokreuzmatrix, weitere
DPI/Mehrmonitor, Windows 10/Linux, Installation/Update/Deinstallation und
Musik-/Modellqualität unverändert offen. [Nachweis und Phase-4-Übergabe](PHASE3-PERFORMANCE-ACCEPTANCE.md#phase-32-ununterbrochener-nachlauf-und-speicherdiagnose).
