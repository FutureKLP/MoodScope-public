# Aktueller Entwicklungs- und Abnahmestand

Stand: 18. November 2026. Dies ist die einzige aktuelle Statusübersicht.
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
  Fehlende Audiomodelldateien werden verständlicher erklärt; der native Testhalter
  erzwingt CPU nun ausdrücklich. Vollständige native Anbieterbearbeitung,
  Reduced Motion und unterbrochene Farb-/Auftragswechsel bleiben offen.
  [Vollständige Matrix und Grenzen](PHASE2B-ACCEPTANCE.md).
- **Phase 2C – Hörstudio und Gesamtregression:** geplant.
- **Phase 3 – Langzeitbetrieb und Performance:** geplant.
- **Phase 4 – Installer und Plattformabnahme:** geplant.
- **Phase 5 – Releaseentscheidung:** geplant; vollständige Kernfreigabe offen.
- **Externe Datenbanken:** bis zur dokumentierten Kernfreigabe gesperrt. SQLite bleibt Standard.

## Weiter offene Grenzen

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
