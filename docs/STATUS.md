# Aktueller Entwicklungs- und Abnahmestand

Stand: 26. November 2026. Dies ist die einzige aktuelle Statusübersicht.
Prüfberichte halten datierte Nachweise fest; frühere Sitzungsstände sind keine
weiterhin gültigen Arbeitsanweisungen. MoodScope 0.3 bleibt eine Entwicklungsversion.

## Verifizierter öffentlicher und lokaler Stand

Kontrollierte Quellintegration am 26. November 2026. Diese Quelllinie enthält
die bereits geprüften Vorgänger und den Phase-2B-Quellhead `b3e4b9c00abf3f2157d89ff665e9b2b2e1583b8e`.
Die datierten Nachweise unten beschreiben ihren jeweiligen Testumfang;
sie sind keine Installer-, Distributions- oder Endnutzerfreigabe.
Ausgangs-Main `886d05542d2a306a60959571ed57915ab13fa382` enthält die regulär
gemergten PRs #11 und #12. Ihre PR-Pflichtchecks waren erfolgreich; neue
Main-Prüfungen werden unabhängig vom jeweils geprüften Quellhead ausgewertet.
Veröffentlichungsbranch und Regeln: [PUBLISHING.md](PUBLISHING.md).

## Entwicklungsphasen

- **Phase 1 – native WAV-Abbruchprüfung:** erfolgreich im definierten synthetischen
  Windows-Prüfumfang bei 96 DPI abgenommen. Kein Anwendungsfehler beim Abbruch
  nachgewiesen; Automationsfehleingaben eingegrenzt.
  [Nachweis und Grenzen](WINDOWS-DESKTOP-TESTING.md).
- **Phase 2A – Bibliothek, Player und Lyrics:** erfolgreich im definierten synthetischen
  Windows-Prüfumfang abgenommen; Desktoptests am 17., Abschluss am 18. November.
  Alle zuvor blockierten Importfälle geschlossen. Der zugehörige Code gehört
  zu dieser Quelllinie; breitere Plattform- und Releasegates bleiben offen.
  [27-Fälle-Abnahme](PHASE2A-ACCEPTANCE.md).
- **Phase 2B – KI, Modelle, Atmosphäre und API:** teilweise bestanden.
  Echte Offline-Inferenz und kontrollierte API-Verträge, native Modellauswahl,
  Local/API/Local, Sprache, Atmosphäre sowie App-/Dienstneustart geprüft.
  Nachabnahme 2B.2: native Profilanlage, Bearbeitung, Löschung, Routing,
  Einwilligung, kontrollierte Anbieterfehler und Dienstwiederherstellung geprüft.
  Echte lokale Musikaufträge, Sperren, Abbruch und Wiederholung bestanden;
  fehlende CLAP-Dateien nativ auf Deutsch und Englisch mit Wiederherstellung geprüft.
  Zeitstichproben belegen sichtbare Farbverläufe bei Wiedergabe, Seek, Song- und
  Modellwechsel; Reduced Motion wurde in einer eigenen nativen Sitzung geprüft.
  Ein zweites echtes Textemotionsmodell fehlt weiterhin. Die vollständige
  Kreuzmatrix bleibt offen. Stabilisierung 2B.3 ergänzt eigene Workerbesitzmarker,
  Prozesssperren und automatische Crashbereinigung beim Dienststart sowie die
  Invalidierung sichtbarer Zustimmung bei Verbindungs-/Sitzungswechsel.
  Echter isolierter Music2Emo-Crash-/Neustartlauf mit automatischem Cleanup und
  erfolgreicher erneuter Inferenz bestanden. Nachabnahme 2B.4: Automations-Eingangstest
  mit frischer Hauptfenster-/Bildbindung und reversiblem Reiterwechsel bestanden;
  anschließend alle zwölf Schritte der nativen Crash-/Einwilligungsfolge bestanden.
  Native Music2Emo-Auslösung, sichtbarer Dienstfehler, automatisches Cleanup,
  erfolgreiche erneute Offline-Inferenz und Checkbox-Rücksetzung nach Dienstneustart
  nachgewiesen. Nativer Transfer ohne neue Zustimmung verweigert, null zusätzliche
  Anbieteraufrufe; neue Zustimmung ermöglicht genau einen synthetischen Loopback-Aufruf.
  [Vollständige Matrix und Grenzen](PHASE2B-ACCEPTANCE.md).
- **Phase 2C – Hörstudio und Gesamtregression:** geplant.
- **Phase 3 – Langzeitbetrieb und Performance:** geplant.
- **Phase 4 – Installer und Plattformabnahme:** geplant.
- **Phase 5 – Releaseentscheidung:** geplant; vollständige Kernfreigabe offen.
- **Externe Datenbanken:** bis zur dokumentierten Kernfreigabe gesperrt. SQLite bleibt Standard.

## Weiter offene Grenzen

Vollständige lokale Regression aus 2B.3: 396 Backend-, 156 Frontend-, 9 Rust- und
5 Node-Tests bestanden; TypeScript/Vite und Windows-Releasebuild ohne Bundle erfolgreich.
In 2B.4 zusätzlich gezielt 63 Backend- und 51 Frontendtests bestanden. Anwendungscode
unverändert; kein neuer vollständiger lokaler Suite-/Buildlauf. Remote-CI des geprüften
Quellheads mit beiden Windows-/Ubuntu-Testjobs und beiden nativen Builds erfolgreich.
Die Korrekturen aus 2B.2 bleiben erhalten. Neu: nur eindeutig eigene inaktive
Music2Emo-Bereiche bereinigen und Zustimmung nach Verbindungs-/Sitzungswechsel
verwerfen; Routingversion vor erlaubtem Transfer erneut prüfen. Rein lokale Aufträge
bleiben unabhängig vom Anbieterstatus. Kein automatischer Transferretry.

Der frühere 2B.2-Lauf hinterließ zwei vom Halter entfernte Crashbereiche.
Der neue 2B.3-Dienstlauf belegt automatische Bereinigung eines markierten eigenen
Bereichs nach hartem Dienstende. Aktive oder nicht zuordenbare Bereiche bleiben
erhalten; alte Bereiche ohne Besitzmarker werden nicht nachträglich übernommen.
Veraltete und fehlende API-Zustimmung werden am tatsächlichen Dienst ohne
Loopback-Anbieteraufruf abgewiesen; neue Zustimmung erfolgreich mit synthetischen
Daten geprüft. Der native Checkbox-Sichtnachweis nach Dienstneustart und die
zwölfteilige Folge sind in 2B.4 geschlossen. Geometriefehler nicht erneut aufgetreten;
die interne Ursache einer historischen veralteten Bildbindung bleibt unbeweisbar.
Ein separates 16-Pixel-Tao-Hilfsfenster ist nachgewiesen und wurde ausgeschlossen.
Beide verwendeten Originale, übernommene WAV-Kopien und produktive SQLite unverändert;
beide SQLite intakt, keine verwaisten Cachebesitzer/Workerbereiche, eigene Testprozesse
beendet und Testports frei. Frühere Abnahmegrenzen bleiben erhalten.
Keine echten Cloudschlüssel/-aufrufe, neuen Gewichte oder Änderungen produktiver Datenbanken.

Ein Music2Emo-Prüfdienstfehler wurde mit Workerlog reproduziert: CUDA-Ziel
bei fehlender sichtbarer Worker-GPU. Der Testhalter setzt nun explizit CPU.
Wiederholungen und Abbruch/Wiederaufnahme bestehen. Die historische Störung
ohne Workerlog ist dadurch nicht abschließend zugeordnet. Langzeitbetrieb, weitere DPI-Stufen, Mehrmonitorbetrieb,
Windows 10 und Linux benötigen eigene Abnahmen. Der erfolgreiche NSIS-Paketbuild
bestätigt keine Installation, Deinstallation oder eigenständige Backendverteilung.
Installer weiterhin nicht vollständig abgenommen.

Zeitliche Emotionsgenauigkeit, vollständige Whisper-Worterkennung, Sängerisolation
und bestätigte Instrumentpräsenz sind nicht belegt. Synthetische Signale und
vorbereitete Anzeige-Caches sind keine tatsächlichen Musikqualitätsnachweise.
Die neuere Teilabnahme ersetzt keine vollständige native Kernmatrix.

[Kernabnahme und datierte Historie](CORE-ACCEPTANCE.md),
[Testbefehle und historische Läufe](TEST-BASELINE.md),
[Dokumentationsübersicht](README.md).
