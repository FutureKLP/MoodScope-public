# Aktueller Entwicklungs- und Abnahmestand

Stand: 20. November 2026. Dies ist die einzige aktuelle Statusübersicht.
Prüfberichte halten datierte Nachweise fest; frühere Sitzungsstände sind keine
weiterhin gültigen Arbeitsanweisungen. MoodScope 0.3 bleibt eine Entwicklungsversion.

## Verifizierter öffentlicher und lokaler Stand

Öffentlicher Main: `1717ffd074041dd5db4e129f9f3aed3fb1a072dc`,
[PR #10](https://github.com/FutureKLP/MoodScope-public/pull/10) gemergt.
Die Phase-2A-Änderungen sind noch nicht öffentlich in Main integriert.
Ihr erhaltener lokaler Branch ist `codex/phase2a-native-library-player-lyrics`:
`9b7e4f3` (Importpicker), `9d44a4a` (Main-Integration), `c539444` (Abnahme).
Phase 2A ist separat als [PR #12](https://github.com/FutureKLP/MoodScope-public/pull/12)
auf `codex/phase2a-public-review` veröffentlicht (`5d459f0`), noch nicht gemergt.
Die vier CI-Jobs dieses PRs sind erfolgreich. [PR #11](https://github.com/FutureKLP/MoodScope-public/pull/11)
bleibt separat offen. Der lokale Phase-2B-Branch `codex/phase2b-native-ai`
integriert beide öffentlichen Quell-/Dokumentationslinien ohne private Vorfahren.
[PR #13](https://github.com/FutureKLP/MoodScope-public/pull/13) bleibt ein Draft
gegen den Phase-2A-Reviewbranch von PR #12. Die Stabilisierung 2B.3 baut auf dem
erneut verifizierten öffentlichen Phase-2B-Head `b6b2c88` auf. PR #11 und #12 sind weiterhin offen;
Main wurde nicht gemergt oder überschrieben.
Veröffentlichungsbranch und Regeln: [PUBLISHING.md](PUBLISHING.md).

## Entwicklungsphasen

- **Phase 1 – native WAV-Abbruchprüfung:** erfolgreich im definierten synthetischen
  Windows-Prüfumfang bei 96 DPI abgenommen. Kein Anwendungsfehler beim Abbruch
  nachgewiesen; Automationsfehleingaben eingegrenzt.
  [Nachweis und Grenzen](WINDOWS-DESKTOP-TESTING.md).
- **Phase 2A – Bibliothek, Player und Lyrics:** erfolgreich im definierten synthetischen
  Windows-Prüfumfang abgenommen; Desktoptests am 17., Abschluss am 18. November.
  Alle zuvor blockierten Importfälle geschlossen. Dies gilt für den lokalen
  Phase-2A-Branch, nicht als Behauptung über den öffentlichen Main.
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
  erfolgreicher erneuter Inferenz bestanden. Die neue zwölfteilige native Bedienfolge
  ist wegen fehlerhafter Testwerkzeuggeometrie nicht vollständig nachgewiesen.
  [Vollständige Matrix und Grenzen](PHASE2B-ACCEPTANCE.md).
- **Phase 2C – Hörstudio und Gesamtregression:** geplant.
- **Phase 3 – Langzeitbetrieb und Performance:** geplant.
- **Phase 4 – Installer und Plattformabnahme:** geplant.
- **Phase 5 – Releaseentscheidung:** geplant; vollständige Kernfreigabe offen.
- **Externe Datenbanken:** bis zur dokumentierten Kernfreigabe gesperrt. SQLite bleibt Standard.

## Weiter offene Grenzen

Aktuelle Regression: 396 Backendtests, vollständige Frontendsuite mit 154 Tests
und zusätzlich separat geprüfter englischer Checkboxfall, 9 Rust- und 5 Node-Tests
bestanden; TypeScript/Vite und Windows-Releasebuild ohne Bundle erfolgreich.
Die Korrekturen aus 2B.2 bleiben erhalten. Neu: nur eindeutig eigene inaktive
Music2Emo-Bereiche bereinigen und Zustimmung nach Verbindungs-/Sitzungswechsel
verwerfen; Routingversion vor Transfer erneut prüfen. Kein automatischer Transferretry.

Der frühere 2B.2-Lauf hinterließ zwei vom Halter entfernte Crashbereiche.
Der neue 2B.3-Dienstlauf belegt automatische Bereinigung eines markierten eigenen
Bereichs nach hartem Dienstende. Aktive oder nicht zuordenbare Bereiche bleiben
erhalten; alte Bereiche ohne Besitzmarker werden nicht nachträglich übernommen.
Veraltete und fehlende API-Zustimmung werden am tatsächlichen Dienst ohne
Loopback-Anbieteraufruf abgewiesen; neue Zustimmung erfolgreich mit synthetischen
Daten geprüft. Der native Checkbox-Sichtnachweis nach Dienstneustart bleibt offen.
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
