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
gegen den Phase-2A-Reviewbranch von PR #12. Die native Nachabnahme 2B.4 prüft den
erneut verifizierten öffentlichen Phase-2B-Head `9d11c67`. Dessen vier Windows-/
Ubuntu-Test- und Native-Buildjobs sind erfolgreich. PR #11 und #12 sind weiterhin offen;
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
  erfolgreicher erneuter Inferenz bestanden. Nachabnahme 2B.4: Automations-Eingangstest
  mit frischer Hauptfenster-/Bildbindung und reversiblem Reiterwechsel bestanden;
  anschließend alle zwölf Schritte der nativen Crash-/Einwilligungsfolge bestanden.
  Native Music2Emo-Auslösung, sichtbarer Dienstfehler, automatisches Cleanup,
  erfolgreiche erneute Offline-Inferenz und Checkbox-Rücksetzung nach Dienstneustart
  nachgewiesen. Nativer Transfer ohne neue Zustimmung verweigert, null zusätzliche
  Anbieteraufrufe; neue Zustimmung ermöglicht genau einen synthetischen Loopback-Aufruf.
  [Vollständige Matrix und Grenzen](PHASE2B-ACCEPTANCE.md).
- **Phase 2C – Hörstudio und Gesamtregression:** teilweise bestanden.
  Echter nativer Demucs-Start, regulärer Abbruch und erfolgreicher CPU-Neulauf;
  Live-Mix, Solo, Pegel, gemeinsamer Loop und Ansichtswechsel geprüft.
  32 native Player-/Kurvenstichproben: maximal 23,3 ms Anzeigedifferenz,
  keine Messung der Audioausgabelatenz. Native Solo-/Vier-Spur-/gewichtete WAVs
  numerisch geprüft; Escape, Cancel, vorhandenes Ziel und Export nach Neustart bestanden.
  Reproduzierter Solo-Export nicht endlicher Samples blockweise abgesichert;
  native Fehlerprobe erhält selbst das zum Überschreiben bestätigte Ziel.
  Lokale Analyse, synthetischer Loopback-Auftrag, Widerruf und vollständiger
  App-/Dienstneustart mit identischen SQLite-Zeilen und Audio-/Stemhashes bestanden.
  Nachabnahme 2C.2: isolierte Demucs-Fehlgewichts-/Abbruch-/Crashmatrix und
  erfolgreicher echter Neulauf bestanden; vorhandener vollständiger Cache bleibt
  auch beim Crash einer zweiten Trennung hashgleich. Keine eigenen Tempdateien
  nachgewiesen, daher keine zusätzliche Bereinigung. Zwei instrumentierte native
  Live-Contexts nach Original-/Songwechsel geschlossen, alle 18 Nodes getrennt;
  160 Zeitstichproben zeigen vier Looprücksprünge. Neue Ressourcenproben und
  vollständiger App-/Dienstneustart mit identischen SQLite-/Audio-/Stemständen
  bestanden. Fehlgewichts-/Crashdialoge, vollständige native Wiederholungsmatrix
  und tatsächliche Audioausgabemessung bleiben offen. Keine Leckfreiheit behauptet.
  [Vollständige Matrix und Grenzen](PHASE2C-ACCEPTANCE.md).
- **Phase 3 – Langzeitbetrieb und Performance:** geplant.
- **Phase 4 – Installer und Plattformabnahme:** geplant.
- **Phase 5 – Releaseentscheidung:** geplant; vollständige Kernfreigabe offen.
- **Externe Datenbanken:** bis zur dokumentierten Kernfreigabe gesperrt. SQLite bleibt Standard.

## Weiter offene Grenzen

Phase 2C entwickelt auf `codex/phase2c-studio-regression` von `b3e4b9c`;
die öffentlichen Dokumentations- und Phase-2A-/2B-Linien sind bereits enthalten.
#11 und #12 bleiben offen, #13 bleibt Draft gegen #12. Die vier CI-Jobs
auch des aktuellen #13-Heads sind erfolgreich. Integrationsreihenfolge:
#11, danach #12 gegen den aktualisierten Main prüfen, danach #13 und Phase 2C.
Keine automatischen Main-Merges. Neue lokale Prüfung nach Solo-Korrektur:
399 Backend-, 156 Frontend-, neun Rust- und fünf Node-Tests bestanden;
TypeScript/Vite und Windows-Releasebuild ohne Bundle erfolgreich.
Die kurze Ressourcenprobe ersetzt keine Phase-3-Leckprüfung.

Nachabnahme 2C.2 arbeitet weiter auf demselben Phase-2C-Branch von `c9d238c`;
[PR #14](https://github.com/FutureKLP/MoodScope-public/pull/14) bleibt Draft gegen
den tatsächlichen #13-Head `b3e4b9c`. Dessen gestapelte Basis bleibt #12.
Der bisherige #14-CI-Lauf `44804376634` ist mit allen vier Jobs erfolgreich.
Neu lokal: 399 Backend-, 156 Frontend-, neun Rust- und fünf Node-Tests,
TypeScript/Vite und Windows-Releasebuild ohne Bundle bestanden. Anwendungscode
unverändert; ergänzt sind gezielte Nachweise. Im neuen Musikausschnittslauf
kein zuverlässiger Aufnahmeweg für tatsächliche Ausgangsmessung nachgewiesen.
Details und historische Nachweise: [Phase 2C.2](PHASE2C-ACCEPTANCE.md#nachabnahme-2c2-vom-20-november-2026).

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
