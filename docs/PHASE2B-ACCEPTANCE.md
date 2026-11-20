# Phase 2B: KI, Modelle, Atmosphäre und API

Datierte Erstabnahme vom 18. November 2026 mit Nachabnahme 2B.2 vom
20. November 2026. Aktueller Status: [STATUS.md](STATUS.md).

**Entscheidung: teilweise bestanden.** Native Bedienung, echte lokale Inferenz,
kontrollierte Anbieterverträge und Regressionen sind getrennt ausgewiesen.
Offene native Kriterien sind keine bestandenen Tests. Keine Kern-, Modellqualitäts-,
Langzeit-, Installer- oder weitere Plattformfreigabe.

Die folgenden 52 Fälle A01–F08 bewahren den Stand und die Fehlversuche der
Erstabnahme. Die [Nachabnahme 2B.2](#nachabnahme-2b2-vom-20-november-2026)
aktualisiert die bezeichneten Fälle mit zusätzlichen nativen Nachweisen.
Historische Aussagen über offene native Prüfungen gelten nur für den damaligen Lauf.

## Git und Abhängigkeiten

Öffentlicher Main beim Abgleich: `1717ffd074041dd5db4e129f9f3aed3fb1a072dc`.
[PR #11](https://github.com/FutureKLP/MoodScope-public/pull/11), Head `ff585f5`,
bleibt offen und wurde nicht gemergt. Phase 2A ist noch nicht in Main integriert.
Der ursprüngliche lokale Branch und seine Nachweise bleiben unverändert erhalten.
Die drei relevanten Quell-/Abnahmecommits wurden auf öffentlichem Main getrennt
übernommen: `10a72f9`, `489b2ec`, `5d459f0`. Ergebnis ist
[PR #12](https://github.com/FutureKLP/MoodScope-public/pull/12); seine vier
Windows-/Ubuntu-Test-/Native-Buildjobs sind erfolgreich. Keine Main-Merges.
Phase 2B arbeitet auf `codex/phase2b-native-ai`; der lokale Integrationscheckpoint
`89bd4a8` verbindet Phase 2A mit der öffentlichen Dokumentationslinie.
Keine private Archivhistorie wurde übernommen.

GitHub meldet weiterhin eine moderate Dependabot-Warnung, Alert 2.
Die Detail-API und die Alertseite werden vom verfügbaren Connector nicht unterstützt.
Paket, betroffene Version, Erreichbarkeit und Abhilfe sind deshalb hier nicht
verifiziert. Kein Upgrade, Schließen oder Herabstufen des Alerts.

## Testebenen, Umgebungen und Belege

- **N/W:** echte native Windows-11-App, Build 26200, WebView2, 96 DPI;
  eigene SQLite, eigener Loopback-Dienst und eigenes WebView-Profil.
- **I/W:** tatsächliche Offline-Inferenz mit vorhandenen lokalen Gewichten;
  CLAP/XLM-EMO im aktuellen Dienst, Music2Emo im vorhandenen separaten Worker.
- **H/M:** echter isolierter HTTP-Dienst mit kontrolliertem Anbieter auf Loopback;
  synthetische Antworten, kein Modellqualitätsnachweis.
- **R/T:** deterministische Python-, React-, Rust- und Node-Regressionen in
  getrennten temporären Datenbereichen. Kein Ersatz für N/W.

Quellen: eigens erzeugter Zwei-Sekunden-Sinuston und zwei 60-Sekunden-Sinustöne,
eigens verfasste zeitgestempelte Zeilen. Vorbereitete Anzeige-Caches sind als
synthetisch markiert. Der HTTP-Fixtureaufbau der beiden langen Tracks zählt
nicht als nativer Import. Originalmusik wird ausschließlich lesend gehasht;
keine Originaldatei wird als Fixture geöffnet oder geändert. Keine Testlinks,
keine Downloads und keine echten API-Schlüssel.

Rohbelege bleiben ignoriert lokal: nummerierte native Zustandsbilder/-texte,
Workerlogs, HTTP-Fallprotokolle, SQLite-Vergleiche und Originalhashmanifeste.
Die Belegkennungen unten verweisen auf diese lokal erhaltenen Prüfserien;
Quellregressionen sind zusätzlich unter `tests/` und `src/` reproduzierbar.

## A – KI-Modellauswahl

- **A01 · bestanden · N/W.** Erwartet: lokale Verwaltung erreichbar und aktive
  Auswahl erkennbar. Ist: CLAP, XLM-EMO, Whisper und Qwen mit Installations-/
  Auswahlzustand sichtbar. Beleg: native Serie 01–07. Grenze: keine Qualitätsprüfung.
- **A02 · bestanden · N/W und I/W.** Erwartet: Audioauswahl wechselt explizit.
  Ist: CLAP Fusion nativ ausgewählt und gespeichert; Music2Emo separat nativ
  gestartet, CLAP/XLM tatsächlich offline gerechnet. Beleg: 06–07, 19–20,
  32–33 und Inferenzprotokolle. Grenze: Fusion nicht lokal installiert;
  keine erfolgreiche Fusion-Inferenz behauptet.
- **A03 · blockiert · N/W.** Erwartet: zwischen zwei verfügbaren Textemotionsmodellen
  wechseln. Ist: nur XLM-EMO als installierte passende Auswahl vorhanden.
  Beleg: Modellkarten. Grenze: keine weiteren Gewichte heruntergeladen;
  Qwen ist Interpretation, kein zweites Textemotionsmodell.
- **A04 · bestanden · N/W und H/M.** Erwartet: Auswahl über Neustart erhalten.
  Ist: gespeichertes CLAP Fusion und übrige Auswahl nach vollständigem Neustart
  unverändert; später ausdrücklich CLAP wiederhergestellt. Beleg: Neustartserie.
- **A05 · bestanden · N/W und H/M.** Erwartet: nicht installierte Modelle klar
  unterscheiden. Ist: Fusion mit Downloadaktion, installierte Modelle getrennt.
  Offlineauftrag scheitert ohne Download. Beleg: 04–07 und Fehlgewichtsprobe.
- **A06 · bestanden · H/M und R/T.** Erwartet: fehlende Dateien verständlich erklären,
  alte Analysen erhalten. Ist: reproduzierte technische Loaderfehlermeldung
  korrigiert; deutscher und englischer tatsächlicher Dienstlauf geben jetzt
  Installations-/Modellwechselhinweis. Beleg: Fehlgewichtsproben und zwei neue
  `test_engine_lifecycle.py`-Fälle. Grenze: korrigierter Fehlerdialog nicht zusätzlich nativ ausgelöst.
- **A07 · bestanden · N/W.** Erwartet: Aktivierungs-/Ladezustände passen zum Auftrag.
  Ist: aktive Karten, gesperrte Aktionen und Auftragsbanner während Music2Emo;
  nach Abschluss wieder bedienbar. Beleg: 07, 19, 32–33.
- **A08 · bestanden · R/T.** Erwartet: fehlgeschlagenes Laden hinterlässt keinen
  halben CLAP-Zustand. Ist: Prozessor und Modell werden erst zusammen aktiviert;
  beide Fehlerstufen geprüft. Beleg: `test_engine_lifecycle.py`.

## B – Analyse und Cache

- **B01 · bestanden · I/W und N/W.** Erwartet: synthetischer Track wird wirklich
  analysiert. Ist: echte CLAP-/XLM-EMO-Analyse und native Music2Emo-CPU-Inferenz
  abgeschlossen. Beleg: lokale Inferenz und native Serie 32–33. Grenze:
  Sinuston-/Textfunktionstest, keine Musik- oder Emotionsqualität.
- **B02 · bestanden · N/W und H/M.** Erwartet: vorhandener Cache wird wiederverwendet.
  Ist: gespeicherten Track nativ geöffnet; HTTP-API-Cache ohne weiteren Mockaufruf
  und Music2Emo-Cache mit `cached=true`. Beleg: 15, 28, 44, API-/Dienstmatrix.
- **B03 · bestanden · N/W und I/W.** Erwartet: erneute Analyse startet neue Berechnung.
  Ist: erzwungene CPU-Dienstläufe und native Neuberechnung abgeschlossen.
  Beleg: Dienstserie CPU 1–3 und 32–33.
- **B04 · bestanden · I/W und H/M.** Erwartet: Abbruch beendet Worker ohne neues Ergebnis.
  Ist: direkter Workerabbruch und Dienstabbruch nach etwa zwei Sekunden;
  Status cancelled, temporäre Workerbereiche entfernt. Beleg: Worker-/Dienstserie.
  Grenze: Abbruchaktion hier HTTP, nicht nativer Cancel-Klick.
- **B05 · bestanden · R/T; nativ nicht ausgeführt.** Erwartet: Songwechsel während
  Auftrag übernimmt keine alte Antwort. Ist: verzögerte Antwortregressionen
  erfolgreich. Beleg: `App.test.tsx`. Grenze: keine native Wechselaktion während Auftrag.
- **B06 · bestanden · R/T und N/W.** Erwartet: Modus-/Songzustände zeigen keine
  fremden Ergebnisse. Ist: verspätete Cacheantworten regressionsgeprüft;
  Local/API/Local nativ mit getrennter lokaler/API-Farbe. Beleg: 35–41 und `App.test.tsx`.
- **B07 · bestanden · H/M und R/T.** Erwartet: ungültige/unvollständige Antworten
  verwerfen. Ist: ungültige Werte und fehlendes Segment erzeugen Fehler statt
  Ersatzwerten; Wiederaufnahme erfolgreich. Beleg: Anbietermatrix und Cloud-/Music2Emo-Regressionen.
- **B08 · bestanden · H/M und N/W.** Erwartet: Datenintegrität über Neustart.
  Ist: sämtliche Cache-/Track-/Ownerzeilen und verwaltete Audiohashes beim
  ersten Neustart identisch; später abgebrochene Antwort nicht gespeichert.
  Beleg: Vor-/Nach-SQLite-Vergleich und Lebenszyklusserie. Grenze: spätere
  erfolgreiche Analysen ändern den Testcache erwartungsgemäß.

## C – Music2Emo

- **C01 · bestanden · I/W.** Erwartet: Workerstart und Prozessende reproduzierbar.
  Ist: fünf direkte erfolgreiche Läufe (dreimal CPU, zweimal GPU), zusätzlicher
  direkter Abbruch, danach erfolgreicher CPU-Lauf im aufgeführten Umfang enthalten.
  Beleg: sechs Einträge der direkten Workerserie. Grenze: kurzer synthetischer Kontext.
- **C02 · bestanden nach Korrektur · N/W und I/W.** Erwartet: CPU-Testdienst startet
  CPU-Worker. Ist: anfänglich CUDA-Ziel trotz fehlender sichtbarer Worker-GPU;
  nach explizitem CPU-Routing drei erfolgreiche Dienstläufe, Cache, Abbruch,
  Wiederaufnahme und erfolgreicher nativer Neulauf. Beleg: gesicherter Fehlerlog,
  Dienstserie und 32–33.
- **C03 · bestanden · I/W.** Erwartet: vorhandene GPU explizit verwendbar.
  Ist: zwei tatsächliche Workerläufe mit sichtbarer Karte und `cuda:0` erfolgreich.
  Beleg: direkte Workerserie. Grenze: kein nativer GPU-Auswahl-/Langzeitlauf.
- **C04 · bestanden · I/W.** Erwartet: CPU/GPU/CPU/GPU-Wechsel erhalten Funktionsfähigkeit.
  Ist: vier aufeinanderfolgende Läufe erfolgreich. Beleg: direkte Workerserie.
  Grenze: keine langfristige VRAM-/Handletrendmessung.
- **C05 · bestanden · I/W und R/T.** Erwartet: Abbruch räumt Worker/Scratch auf.
  Ist: direkter und Dienstabbruch erfolgreich, jeweils kein Scratchrest;
  anschließende Inferenz erfolgreich. Beleg: beide Workerserien und `test_expression_compare.py`.
- **C06 · bestanden · R/T; real nicht ausgeführt.** Erwartet: Timeout beendet auch
  widerspenstigen Worker. Ist: vorhandene deterministische Timeout-/Killregression
  erfolgreich. Grenze: kein tatsächlicher 30-Minuten-Inferenztimeout abgewartet.
- **C07 · bestanden · N/W und I/W.** Erwartet: Fehler mit erhaltener Loglage erklären.
  Ist: aktueller Fehler reproduziert; Workerlog zeigt CUDA-Deserialisierung bei
  null sichtbaren Geräten. Beleg: native Fehlerserie 19–20 und gesicherter Workerlog.
  Grenze: keine endgültige Zuordnung der historischen Störung ohne damaligen Log.
- **C08 · bestanden · H/M.** Erwartet: Dienstneustart während Auftrag beschädigt nichts.
  Ist: verzögerte Mockanalyse beim Dienstabbruch aktiv, Cache unverändert;
  nach Neustart alte Job-ID unbekannt, neue Analyse erfolgreich. Beleg: Lebenszyklusserie.
  Grenze: API-Auftrag, kein absichtlich abgebrochener Music2Emo-Neustartlauf.

## D – Atmosphäre und Farbzustände

- **D01 · bestanden · N/W.** Erwartet: Atmosphäre ein-/ausschaltbar. Ist: ausgehend
  ausgeschaltete und anschließend aktivierte Atmosphäre sichtbar, abschließend
  wieder nativ deaktiviert. Beleg: 28–30 und 52.
- **D02 · bestanden · N/W und R/T.** Erwartet: gleiche Kategoriequelle für Balken
  und Hintergrund. Ist: lokale Music2Emo-Tags gegenüber API-Mockscores getrennt;
  gemeinsame Palette regressionsgeprüft. Beleg: 30, 36, 41 und Atmosphere-/App-Tests.
  Grenze: keine psychologische Validierung der Farbzuordnung.
- **D03 · nicht ausgeführt · N/W.** Erwartet: unterbrochene Übergänge setzen
  kontinuierlich am aktuellen Bildzustand an. Ist: einzelne Anfangs-/Endbilder,
  kein zeitlich ausreichend dichter nativer Unterbrechungstrace. Kein Erfolg behauptet.
- **D04 · nicht ausgeführt · N/W.** Erwartet: reduzierte Bewegung im tatsächlich
  aktiven nativen Präferenzmodus. Ist: bestehende CSS-Regeln erhalten; kein
  vollständiger nativer Reduced-Motion-Lauf. Quellprüfung ersetzt diesen nicht.
- **D05 · bestanden · N/W.** Erwartet: Local/API/Local wechselt zur passenden Quelle.
  Ist: API-Cache warmgelb, lokale Music2Emo-Rückkehr blaugrün; Zustimmung beim
  API-Wechsel leer. Beleg: 35–41. Grenze: API-Werte vorbereitet, keine Anbieterqualität.
- **D06 · bestanden · N/W.** Erwartet: Atmosphären-/Spracheinstellung über Neustart
  erhalten. Ist: finaler Build startet mit englischer Sprache und aktivierter,
  zunächst neutraler Atmosphäre ohne geöffneten Song. Beleg: 42.
- **D07 · bestanden nach Korrektur · N/W und Build.** Erwartet: Deutsch/Englisch
  konsistent. Ist: beide Oberflächen nativ bedient; fehlende Übersetzung
  `Lokales Modell` ergänzt. Beleg: 37–41 und finaler Build. Keine Neugestaltung.
- **D08 · bestanden · R/T; nativ ergänzend geprüft.** Erwartet: Modellwechsel
  verändert dieselbe Farbquelle. Ist: CLAP-/Music2Emo-Zuordnung und spätere
  Cacheantworten regressionsgeprüft; native Modellauswahl/-anzeige erreichbar.
  Native CLAP-/Music2Emo-Umschaltung im finalen Build: Serie 46–48.
  Grenze: vollständiger zeitlicher Farbtrace offen wie D03.
- **D09 · bestanden · N/W.** Erwartet: Song ohne Kategoriescores übernimmt keine
  frühere Modellfarbe. Ist: Wechsel vom real analysierten Zwei-Sekunden-Track
  zum vorbereiteten 60-Sekunden-Track; neue Identität, Position null und neutraler
  Zielzustand. Beleg: 49–51. Grenze: vorbereiteter Anzeige-Cache, keine zweite Modellinferenz.

## E – API und Anbieterprofile

- **E01 · bestanden · H/M.** Erwartet: Profil erstellen, ändern und entfernen.
  Ist: synthetisches Loopback-Profil erstellt, Modell-ID geändert, separates
  Wegwerfprofil entfernt. Beleg: Anbietermatrix. Grenze: keine native Editorabnahme.
- **E02 · bestanden · H/M und N/W.** Erwartet: Anbieter-/Modellwahl und Aufgaben
  explizit. Ist: lokale Modellliste gelesen, ausschließlich Audio dem Loopbackprofil
  zugeordnet, restliche Aufgaben lokal; nativ sichtbare Zusammenfassung. Beleg: 35–38.
- **E03 · bestanden · H/M und N/W.** Erwartet: ohne Zustimmung kein Transfer.
  Ist: verweigerte und veraltete Zustimmung HTTP 422, Aufrufzähler unverändert;
  native Zustimmung nach Modus-/Neustartwechsel leer. Beleg: Anbietermatrix, 35–38.
- **E04 · bestanden · R/T.** Erwartet: erforderliche fehlende Zugangsdaten blockieren
  ohne Fallback. Ist: vorhandene Routingregressionen erfolgreich. Grenze:
  lokaler Mock erlaubt absichtlich keylose lokale Server; kein echter Cloud-Keytest.
- **E05 · bestanden · H/M.** Erwartet: fehlerhafte Zugangsdaten verständlich behandeln.
  Ist: kontrolliertes HTTP 401 führt zum Fehler, keine automatische Wiederholung.
  Beleg: Anbietermatrix. Grenze: simulierte Zurückweisung, kein echter Anbieter.
- **E06 · bestanden · H/M.** Erwartet: Providerfehler und Netzwerkabbruch sicher.
  Ist: HTTP 503 und Verbindungsabbruch abgefangen, anschließender Erfolg.
  Beleg: Anbietermatrix. Grenze: tatsächlicher 180-Sekunden-Timeout nicht ausgeführt.
- **E07 · bestanden · H/M und R/T.** Erwartet: ungültige Antworten nicht speichern.
  Ist: fehlende IDs und ungültige Werte verworfen; Vertragstests erfolgreich.
  Beleg: API-/Cloudtests. Keine Qualitätsaussage aus Mock-Ergebnissen.
- **E08 · bestanden · H/M.** Erwartet: Profile/Aufgaben erhalten, Keys/Zustimmung
  nach Dienstneustart verloren. Ist: alle vier Eigenschaften tatsächlich geprüft.
  Beleg: Neustartserie; alte Zustimmung HTTP 422.
- **E09 · bestanden · H/M.** Erwartet: keine Geheimnisse persistieren.
  Ist: ausschließlich erfundener Sitzungsschlüssel, Byteprüfung aller isolierten
  Datendateien ohne Schlüsselvorkommen; Profile nach Neustart ohne Sitzungsschlüssel.
  Beleg: Anbietermatrix und Neustartserie. Keine echten Secrets verwendet.
- **E10 · bestanden · H/M und N/W.** Erwartet: Moduswahl löst keinen unkontrollierten
  Transfer aus. Ist: ausschließlich Loopback-Anbieteraufrufe mit synthetischem
  Audio; verweigerte Zustimmung ohne Aufruf. Native API-Ansicht mit leerer Zustimmung.
  Grenze: kein allgemeiner Netzwerk-Mitschnitt aller Windows-Prozesse.
- **E11 · nicht ausgeführt · N/W.** Erwartet: gesamte Profil-/Routing-/Key-/
  Fehlerbearbeitung über native Bedienelemente. Ist: Oberfläche gelesen, Datenänderungen
  über echte isolierte HTTP-Verträge geprüft. Dieser Umfang ersetzt keine native Editiermatrix.

## F – Fehler- und Lebenszyklusmatrix

- **F01 · bestanden · R/T; nativ nicht ausgeführt.** Erwartet: laufender Auftrag
  plus Songwechsel liefert kein altes Ergebnis. Ist: React-Regressionen erfolgreich;
  vollständige native Parallelbedienung bleibt offen. Beleg: `App.test.tsx`.
- **F02 · bestanden · R/T; nativ nicht ausgeführt.** Erwartet: Modell-/Profiländerung
  während Auftrag ist gesperrt oder korrekt gebunden. Ist: HTTP-Aufnahmesnapshots
  und Mutation-Locks regressionsgeprüft. Beleg: `test_provider_routing.py`.
- **F03 · bestanden · N/W und R/T.** Erwartet: API-Rückkehr verändert nicht die lokale
  Quelle. Ist: native Local/API/Local-Ansicht und verspätete-Antwort-Regressionen bestanden.
- **F04 · bestanden · H/M.** Erwartet: Dienstabbruch mitten im Auftrag speichert
  kein halbes Ergebnis. Ist: Cache zeilengleich, SQLite intakt, alte Job-ID nicht
  wiederbelebt, neue Analyse erfolgreich. Beleg: tatsächliche Lebenszyklusserie.
- **F05 · bestanden · H/M.** Erwartet: ungültige Antwort und Netzwerkfehler sind
  wiederherstellbar. Ist: beide Fehlerklassen und anschließender Erfolg geprüft.
  Beleg: Anbietermatrix. Native Fehlerdarstellung separat nur bei Music2Emo gesehen.
- **F06 · bestanden · I/W und R/T.** Erwartet: Workerressourcen nach Abbruch frei.
  Ist: Prozessablauf beendet, Scratch leer und Folgeauftrag erfolgreich;
  deterministische Kill-/Cleanup-Tests erfolgreich. Grenze: keine Langzeittrendmessung.
- **F07 · bestanden nach Korrektur · H/M und R/T.** Erwartet: verständlicher lokaler
  Ladefehler. Ist: neuer DE-/EN-Installationshinweis tatsächlich im Dienst,
  Teilinitialisierung regressionsgeprüft. Grenze: native Nachprüfung des neuen Dialogtexts offen.
- **F08 · nicht ausgeführt · N/W.** Erwartet: vollständige native Kreuzmatrix aller
  Song-/Modell-/Modus-/Fehlerwechsel einschließlich reduzierter Bewegung.
  Ist: Teilfolgen geprüft, Gesamtumfang offen. Keine Gesamtfreigabe.

## Bestätigte Fehler und begrenzte Korrekturen

1. Fehlende CLAP-Dateien erzeugten eine technische Loaderausnahme. Jetzt gezielter
   DE-/EN-Wiederherstellungshinweis; Prozessor und Modell werden erst nach vollständigem
   Laden gemeinsam aktiviert. Zwei neue Regressionen prüfen beide Fehlerstufen.
2. Der native Testhalter wollte CPU allein über eine leere CUDA-Sichtbarkeit
   erzwingen. Im geprüften Prozessmix wählte der Dienst trotzdem CUDA, während der
   Worker null sichtbare Karten hatte. Der Halter setzt jetzt ausdrücklich
   `MOODSCOPE_DEVICE=cpu` und `CUDA_VISIBLE_DEVICES=-1`. GPU-Prüfungen bleiben getrennt.
3. Die native englische API-Zusammenfassung enthielt `Lokales Modell` auf Deutsch.
   Fehlenden Katalogeintrag ergänzt. Keine UI-Struktur-/Paletteänderung.

Die frühere sporadische Music2Emo-Störung ist ohne damaligen Workerlog nicht
rückwirkend bewiesen. Der aktuelle Fehler ist dagegen mit Startumgebung,
Workerlog und Korrekturwiederholung belegt. Direkte CPU/GPU-Läufe dauerten etwa
9–15 Sekunden; daraus folgt keine Langzeit- oder Musikleistungsbaseline.

## Tests, Builds und Fehlversuche

- Finale Backendsuite: **381 bestanden**, 36,21 Sekunden, explizite CPU,
  eigene Datenbereiche. Zwei neue Loader- und eine neue Testhalterregression.
- Finale Frontendsuite: **146 bestanden in 28 Dateien**, 17,15 Sekunden.
- Node-Dialogdriver: **5 bestanden**. Rust: **9 bestanden**, locked/offline.
- TypeScript/Vite und finaler Windows-Releasebuild ohne Bundle: bestanden.
  Bekannte Vite-Chunkwarnung bleibt. Kein neuer Installerlauf.
- Separat: tatsächliche native Windows-Bedienung und oben bezeichnete Offline-/
  HTTP-Proben. CI ist kein Ersatz für Desktopbedienung.

Der erste Lauf verwendete irrtümlich die ältere Python-3.10-Rückfallumgebung;
sechs Testhalterfälle und Vorbereitung scheiterten am dort fehlenden
`hashlib.file_digest`. Wiederholung in der dokumentierten aktuellen Umgebung
bestand. Keine pauschale Python-3.10-Kompatibilität der Testhalter behauptet.
Der erste Mockparser verarbeitete den angehängten Schematteil nicht; korrigierte
Wiederholung bestand. Zwei lokale Prüftreiber mussten Abbruch ohne Ergebnisobjekt
richtig protokollieren. Diese Werkzeugfehler sind keine Appfehler.
Ein Buildversuch konnte die noch laufende EXE nicht ersetzen; Wiederholung nach
Beendigung der eigenen App erfolgreich. Frühe Geometrie-/Indexeingaben banden
an die 16-mal-16-Hilfsregion. Frische große Bildregion und lesende Win32-Diagnose
ermöglichten die weiteren Eingaben. Keine falschen Klicks als Testerfolg ausgegeben.

## Daten und verbleibende Freigabegrenzen

Produktive SQLite und Originalbestand werden über vollständige Vor-/Nachhashes
geprüft. Der isolierte Cache darf sich ausschließlich durch die beauftragten
synthetischen Analysen ändern. Vorbereitete Caches für noch nicht importierte
Identitäten erklären anfängliche Owner ohne Track; sie sind Fixtureaufbau,
keine beobachtete Datenbankbeschädigung. Nach dem späteren Fixtureimport werden
alle geplanten Identitäten vorhanden geprüft.

Ausstehend bleiben insbesondere native Reduced Motion, unterbrochene Farbtraces,
vollständige native Profilbearbeitung und parallel bediente Auftragswechsel.
Zweites installiertes Textemotionsmodell fehlt; kein Download zur Umgehung dieser
Grenze. Wirkliche Anbieter-/Music2Emo-Timeoutdauer, Langzeitbetrieb, weitere DPI,
Mehrmonitor, Windows 10, Linux-Bedienung und Installation nicht neu abgenommen.
Originalmusikqualität, Worterkennung, Sängerisolation und Instrumentpräsenz werden
nicht aus Sinustönen oder vorbereiteten Antworten bestätigt. Externe Datenbanken
bleiben gesperrt; SQLite bleibt Standard.

Abschließender Datenvergleich bestanden: vollständiger Originaldateibestand,
produktive SQLite und synthetische Quelldateien unverändert; produktive und
isolierte SQLite `integrity_check=ok`. Drei erwartete Trackidentitäten, keine
verwaisten Cachebesitzer nach abgeschlossenem Fixtureaufbau. Eigene native App
und Dienste beendet; abschließender Prozesssnapshot leer. Die vorhandene
Exportzieldatei blieb unverändert. 140 relative Dokumentationslinks in 29
Markdown-Dateien geprüft, kein Link-/Ankerfehler.

## Nachabnahme 2B.2 vom 20. November 2026

**Entscheidung weiterhin teilweise bestanden.** N/W bezeichnet hier die echte
Windows-App mit isolierter SQLite, WebView2 und CPU-Prüfdienst. Für lokale
Inferenz und Wiedergabe wurden zwei quellbenannte 90-Sekunden-Ausschnitte aus
dem erlaubten lokalen Musikbestand verwendet. Originale blieben unverändert.
Ihr vorbereitender HTTP-Import ist kein neuer nativer Importnachweis.
API-Tests verwendeten ausschließlich die separate synthetische Quelle und
einen kontrollierten Loopback-Anbieter; keine Übertragung echter Musik an Anbieter.
Vorbereitete leere Anzeige-Caches zählen nicht als Inferenz.

### Ergänzende Fälle und Fortschreibung der 52-Fälle-Matrix

- **N01 → E01, E11 · bestanden · N/W.** Profil im Formular angelegt, Endpunkt
  und Modell geändert, gespeichert und wieder gelesen; zusätzliches Testprofil
  mit nativer Bestätigung gelöscht. Bibliothek blieb erhalten. Ein früher
  indexbasierter Bedienfehler erzeugte ein Duplikat statt einer Bearbeitung;
  dieser Fehlversuch zählt nicht als Erfolg. Wiederholung mit frischem Bildbezug bestanden.
- **N02 → E02 · bestanden · N/W und H/M.** Audio- und Textaufgabe dem Testprofil
  zugewiesen und gespeichert. Tatsächliche Aufträge erreichten dessen ausgewähltes
  Modell. Übrige voreingestellte Cloudziele wurden nicht aufgerufen.
- **N03 → E03, E10 · bestanden · N/W und H/M.** Ohne Einwilligung wurde der Auftrag
  verständlich verweigert und kein Anbieter-POST erzeugt. Nach ausdrücklicher
  Freigabe liefen Audio und Text erfolgreich. Nach Widerruf erneut verweigert,
  Anzahl der Anbieteraufrufe unverändert. Keine reale Musik in diesen API-Proben.
- **N04 → E05, E06, E11, D07 · bestanden nach Korrektur · N/W und R/T.**
  Kontrollierte HTTP-401-/503-Antworten nativ ausgelöst. Zusätzlich ein absichtlich
  abgelehnter Sitzungswert mit tatsächlich gesetztem Authentifizierungsheader
  geprüft. Fehlende Übersetzungsfragmente korrigiert; finaler 401-Hinweis und
  laufender DE-/EN-Sprachwechsel einschließlich Fehler-ID nativ geprüft.
  Backendregressionen decken beide Statuscodes ab. Keine echten Cloudschlüssel,
  keine echte Kontingent-/Cloudabnahme und kein vollständiger 180-Sekunden-Timeoutlauf.
- **N05 → E08, E09 · bestanden im beschriebenen Umfang · N/W und H/M.**
  Nur den eigenen Dienst bei offener App neu gestartet. Ein alter Einwilligungsstand
  konnte zunächst noch angehakt aussehen; der Start wurde jedoch wegen geänderter
  Aufgabenzuordnung mit HTTP 422 abgewiesen, ohne Anbietertransfer. Nach Prüfung
  der Ziele und erneuter Einwilligung Erfolg. Kein automatischer visueller Reset
  vor dem Start behauptet. Der Test-Sitzungsschlüssel war abschließend nicht persistiert.
- **N06 → B01, B05, F01, F02, F03 · bestanden im geprüften Ablauf · N/W und I/W.**
  Echte Music2Emo-Inferenz gestartet. Währenddessen Moduswechsel, Öffnen anderer
  Songs, Modellwahl sowie persistierende Profil-/Routing-/Geräteaktionen nativ
  gesperrt. Keine neue Songidentität oder Zuordnung wirksam. Nach Abschluss/Abbruch
  wieder bedienbar. Editierbare Formularentwürfe waren keine gespeicherten Änderungen.
- **N07 → B04, F06 · bestanden für regulären Abbruch · N/W und I/W.**
  Echten Music2Emo-Auftrag nach sichtbarem Fortschritt nativ abgebrochen;
  Status abgebrochen, kein Ergebnis, Workerbereich aufgeräumt und Folgeauftrag möglich.
  Das ersetzt keine Abnahme jedes Zeitpunkts im Auftrag.
- **N08 → B07, B08, F04, F05 · bestanden für geprüfte Störung · N/W, I/W und H/M.**
  Eigenen Dienst während echter lokaler Analyse beendet und neu gestartet.
  Vollständige Tabellen für Tracks, Cache und Besitzer vor/nach Restart identisch,
  SQLite intakt. Im finalen Build verständlicher DE-/EN-Diensthinweis statt
  rohem Fetchfehler; erneute native Analyse erfolgreich. Music2Emo ebenfalls
  nach Störung erfolgreich wiederholt. Ungültige Anbieterantwort nativ geprüft:
  kein Teilcache, altes vollständiges Ergebnis erhalten, anschließender API-Erfolg.
  Harte Prozessabbrüche hinterließen zwei isolierte Workerbereiche. Der Halter
  sicherte sie als Beleg und entfernte sie; automatische Crashbereinigung bleibt offen.
- **N09 → A06, A08, F07 · bestanden · N/W, I/W und R/T.** Nicht installiertes
  CLAP Fusion offline ausgewählt und Analyse nativ gestartet: verständlicher
  Installations-/Wechselhinweis auf Deutsch und Englisch, keine Downloads oder
  Änderungen produktiver Gewichte. Alte Analysen erhalten. Nach Auswahl des
  installierten kompakten CLAP echte native Analyse erfolgreich. Atomare
  Aktivierung von Prozessor und Modell zusätzlich regressionsgeprüft.
- **N10 → D01, D02, D03, D05, D08, D09 · bestanden im Stichprobenumfang · N/W.**
  Tatsächliche Musik abgespielt, pausiert und zehn Sekunden weitergesprungen;
  lokaler Modellwechsel zwischen vorhandenen Ergebnissen, Songwechsel und
  Local/API/Local nativ geprüft. Zeitreihen erfassen den sichtbaren Aufbau
  von neutral zu lokaler Farbe sowie Modell-/Songübergänge. Seek während
  laufender Wiedergabe unterbrach den fortlaufend neu angesteuerten Farbverlauf
  ohne beobachteten neutralen Reset. Nach Neustart neutral ohne ausgewählten Song.
  DE-/EN-Oberflächen geprüft. Keine Aussage über Emotionsrichtigkeit.
- **N11 → D04, D06, D07 · bestanden im Stichprobenumfang · N/W.** Neue native
  Sitzung mit WebView2-Präferenz für reduzierte Bewegung; `matchMedia` bestätigte
  den Zustand. Echte Wiedergabe, Modellwechsel, Pause und Local/API/Local mit
  verweigerter Übertragung geprüft. Sichtbare ruhige Zustände und lesende
  Laufzeitdiagnose: dekorative Animationen und Übergänge aus. Kein globaler
  Windows-Eingriff; kein Beweis sämtlicher Betriebssystem-/DPI-Konfigurationen.
- **N12 → A03 · echte Zwei-Modell-Inferenz weiterhin blockiert; R/T bestanden.**
  Nur XLM-EMO fachlich passend lokal installiert. Qwen bleibt Interpretationsmodell;
  keine zusätzlichen Gewichte geladen. Kontrollierte A/B/A-Pipeline prüft
  tatsächlichen Auswahlpfad, Entladen, neue Quelle und unterschiedliche Ergebnisse.
  Leere Testmodellordner und Doubles sind ausdrücklich kein zweites reales Modell.
- **N13 → F08 · teilweise bestanden · N/W.** Die oben genannten nativen Abläufe
  ergänzen die bisherige Kreuzmatrix. Eine vollständige kartesische Kombination
  aller Songs, Modelle, Modi, Fehler und Bewegungspräferenzen ist nicht ausgeführt.
  Keine vollständige Kernfreigabe.

### Zeitliche Belege und Messgrenzen

45 native Bildstichproben mit tatsächlichen Zeitstempeln lokal gesichert.
Dichte Folgen für lokale Rückkehr, Wiedergabe, Seek, Modell- und Songwechsel
reichen ungefähr von 0,2 bis 2,3 Sekunden nach der Aktion; reduzierte Wiedergabe
bis etwa 3,1 Sekunden. Farbproben einer freien Hintergrundregion bestätigen
zusammen mit den Bildern fortlaufende Änderungen ohne beobachteten Neutralreset
beim Seek. Lesende Laufzeitdiagnose bestätigt während Wiedergabe laufende,
neu angesteuerte Farbübergänge. Keine Bildraten- oder lückenlose Einzelbildmessung.

Der erste Versuch eines schnellen Local/API/Local-Wechsels lag wegen
Werkzeuglatenz rund sieben Sekunden auseinander. Er belegt keinen unterbrochenen
Zwei-Sekunden-Übergang. Der gültige Unterbrechungsnachweis ist die Seek-Folge
während tatsächlicher Wiedergabe. Einzelne schnelle Bildaufnahmen enthielten
unvollständig erfasste Schrift; daraus folgt weder ein bestätigter Darstellungsfehler
noch eine Garantie perfekter Einzelbilder. Rohbilder, Lyrics und Messdateien bleiben lokal.

### Korrekturen, Regression und Datenabschluss

Ergänzte DE-/EN-Fragmente für Anbieterfehler und deren Rückübersetzung bei
laufendem Sprachwechsel. Verbindungsfehler zum lokalen Dienst zeigen einen
verständlichen Hinweis mit manueller Wiederholung; kein automatischer Retry.
Explizite Abbruchsignale und `AbortError` bleiben erhalten. Drei neue Backendfälle,
ein neuer Sprachtest und zwei neue Frontend-Netzwerkfälle ergänzen die Regression.

- Backend: **384 bestanden**, 31,97 Sekunden.
- Frontend: **149 bestanden in 29 Dateien**, 17,44 Sekunden.
- Rust: **9 bestanden**, locked/offline. Node-Dialogdriver: **5 bestanden**.
- TypeScript/Vite und finaler Windows-Releasebuild ohne Bundle: bestanden.
  Bestehende Chunk-/Hardlink-Fallbackwarnungen; kein neuer Installerlauf.

Fehlversuche bleiben erhalten: Sandbox-Socket-/Teststarts mussten außerhalb
der Sandbox wiederholt werden; erster Sprachtest benötigte die jsdom-Umgebung;
ein erster Abbruchtest zeigte den ungeeigneten `instanceof Error`-Vergleich für
DOMException. Korrigierte finale Läufe bestanden. Eine Bildauswertung scheiterte
zunächst am fehlenden Pillow der aktuellen Umgebung und wurde mit vorhandener
Pillow-Umgebung wiederholt. Diese Halterfehler sind keine Appfehler.

Abschließender Vergleich: beide tatsächlich benutzten Originale und produktive
SQLite unverändert; produktive und isolierte SQLite `integrity_check=ok`, keine
verwaisten Cachebesitzer. Kein Anspruch auf erneutes Hashen des ganzen Musikbestands.
Eigene App, Dienst, Worker und Anbieter beendet; geprüfte Loopbackports frei.
Regulärer Abbruch automatisch bereinigt; harte Abbruchbereiche nach Belegsicherung
vom Halter entfernt. Musik, Ausschnitte, Analysen, Testschlüssel und Rohbelege
bleiben ignoriert lokal. Keine Links genutzt, keine Downloads, keine echten Schlüssel.

Git-Abgleich: Main `1717ffd`, #11 `ff585f5` und #12 `5d459f0` unverändert offen;
#13 bleibt Draft gegen #12. Beide offenen Quellen sind bereits Vorfahren des
Phase-2B-Branches. Keine automatischen Main-Merges, keine private Abstammung,
keine Änderung der Dokumentationsstruktur. Weitere Grenzen aus der Erstabnahme
gelten fort: echte zweite Textmodell-Inferenz, Langzeitbetrieb, weitere DPI/
Plattformen, vollständige Timeoutdauer, Installation und Musikqualitätsabnahme.
