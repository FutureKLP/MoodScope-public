# Phase 2A: native Bibliothek, Player und Lyrics

Datierter Nachweis des Phase-2A-Quellstands. Die zugehörigen Importfunktionen,
Testhalter und Regressionen gehören zu dieser Quelllinie; ihr aktueller
Integrationsstatus steht in [STATUS.md](STATUS.md). Die historischen Teststände
und Abnahmegrenzen unten bleiben erhalten.

**Entscheidung: Phase 2A im festgelegten synthetischen Windows-Prüfumfang vollständig bestanden.**
Die vier zunächst blockierten Importfälle wurden in Phase 2A.2 tatsächlich nativ
abgeschlossen. Desktopprüfung am 17. November 2026, Dokumentationsabschluss am
18. November 2026. Windows 11 Build 26200, WebView2, 96 DPI. Keine allgemeine
Kern-, Musikqualitäts-, Langzeit-, Installer- oder andere Plattformfreigabe.

## Projektstand und Isolation

Ausgangspunkt war der unveränderte lokale Commit `82c760c` auf
`codex/phase2a-native-library-player-lyrics`, mit geprüftem Phase-1-Head
`aaf5b6fee810b748c942459fc970feec86478717` als Vorfahr. PR #10 war beim Testbeginn
offen und mergefähig, alle 13 Check-Runs erfolgreich; Main damals `44320c4`.
Beim Abschlussabgleich am 18. November war PR #10 bereits regulär gemergt:
Merge und tatsächlicher Main `1717ffd074041dd5db4e129f9f3aed3fb1a072dc`.
Dieser Main ist in den lokalen Entwicklungsbranch übernommen. Kein automatischer
öffentlicher Main-Merge und kein öffentlicher Push dieser Phase.

Eigener Loopback-Dienst, eigene SQLite, eigenes WebView-Profil und eigener
ignorierter Arbeitsbereich unter `.tools`. Zwei erzeugte Stereo-Sinustöne
(440/660 Hz, 48 kHz, je 60 Sekunden), eine Zwei-Sekunden-Seedfixture und eine
absichtlich ungültige WAV-Quelle. Nur die kurze Seedfixture wurde beim Aufbau
über HTTP importiert; beide 60-Sekunden-Dateien wurden tatsächlich im nativen
Dialog ausgewählt und bestätigt. Vorbereitete, ausdrücklich synthetische Caches
verhinderten automatische Inferenz beim ersten Öffnen und zählen nicht als
Importnachweis oder wissenschaftliche Modellbewertung.

Eine separat verfasste LRC-Datei unterscheidet sich von den vorab gespeicherten
Zeilen. Nach nativer Dateiauswahl wurden ihre unveränderten Zeitmarken im Editor
geprüft, die vorhandene lokale Analyse über die UI gestartet und die drei neuen
Zeilen angezeigt. Vorhandene lokale Gewichte, offline geschaltete Modell-Hubs;
keine externe KI- oder Musikdatenübertragung. Die dabei angezeigten Schätzwerte
sind kein Qualitätsnachweis. Der ursprüngliche Musikbestand wurde nur lesend
gehasht und nie in dieser Prüfung importiert oder abgespielt.

## Ursache und Lösung

Die bisherigen HTML-Dateiinputs öffnen einen echten Windows-Dialog der Klasse
`#32770` in einem WebView2-Kindprozess. Das Fenster war sichtbar, im Vordergrund,
mit normaler Geometrie und 96 DPI. Es fehlte als eigenständiges Ziel in der
Fensterliste des Automationswerkzeugs. Eingaben über das Tauri-Hauptfenster
scheiterten an der anderen Prozessidentität; der dortige Accessibility-Baum
blieb beim HTML-Importknopf. Das ist eine belegte Bindungsgrenze des Werkzeugs,
kein nachgewiesener Defekt des bisherigen Imports und kein DPI-Fehler.

Die Desktop-App verwendet für Audio/LRC nun das bereits vorhandene Tauri-
Dialogplugin mit explizitem Hauptfenster als Parent. Der echte Windows-Picker
gehört dadurch zum Appprozess. Wenn er nur im Baum des deaktivierten Parents
erscheint, verlangt der Driver genau einen passenden Dialogtitel. Doppelte
Darstellungen desselben Baumknotens werden zusammengefasst; unterschiedliche
Dialoge, fremde Prozesse und unbekannte Modale blockieren die Bindung.
16×16-Hilfsregionen werden weiterhin verworfen. Auswahl und Bestätigung erfolgen
an frischen, überprüften Dialogbildern, ohne numerische Accessibility-Klicks.
Das Import-Dateinamensfeld ID 1148 lieferte ebenfalls veraltete Indexbindungen;
indizierte Import-Edits sind deshalb ausdrücklich gesperrt. Bildbasierte
Dateiauswahl oder bildbestätigter Fokus mit wörtlicher Eingabe und anschließender
Feldprüfung bleiben erforderlich. Ein gemischt formatierter Pfad wurde zunächst
von Windows zurückgewiesen; nach neuer Beobachtung und korrekten Windows-
Trennzeichen gelang die Auswahl. Dieser Fehlversuch zählt nicht als Import.

Der Renderer übergibt keine Dateipfade oder Zielhosts an Rust. Nur die Auswahl
aus dem Picker wird gelesen: Audio begrenzt und gestreamt an denselben festen
Loopback-Importendpunkt, ohne Proxy oder Weiterleitungen; LRC/TXT begrenzt als
UTF-8 wie bisher an den Editor. Abbruch endet vor Datei-/Netzwerkzugriff.
Der Browser verwendet weiterhin die vorhandenen HTML-Dateiinputs. Oberfläche,
Designsystem, Analyseformeln und Deutsch/Englisch bleiben erhalten.

## Vollständige native Testmatrix

Bestanden gilt ausschließlich für den beschriebenen Umfang. N07–N15 stammen
aus der vorausgehenden nativen Phase-2A-Prüfung; sie wurden nicht unnötig neu
implementiert. N03–N05, N21–N22 und N25–N27 sind neue echte Desktopnachweise.
HTTP-Aufbau, Unit-Tests und SQLite-Leseprüfungen ersetzen keinen Dateidialog.

| Fall | Erwartung und Nachweis | Ergebnis |
| --- | --- | --- |
| N01 | Prozess, Titel und frische Bildregion eindeutig; Hilfsfenster verworfen; neue Kennungen nach Neustart | Bestanden |
| N02 | Echter Audio-Öffnendialog, eindeutiger Parent und passender Titel | Bestanden im neuen Build |
| N03 | Beide synthetischen WAVs nativ auswählen/bestätigen; richtige Identitäten, Bibliothek und verwaltete Audiodaten | Bestanden; kein HTTP-Ersatzimport |
| N04 | Dieselbe Quelle erneut importieren; Identität, Notiz und Analyse erhalten | Bestanden in beiden Reparaturfällen |
| N05 | Ungültige Quelle nativ auswählen; verständlicher Dekodierfehler; Datenbank unverändert | Bestanden: HTTP 422, sämtliche SQLite-Zeilen und Audiohashes davor/danach gleich |
| N06 | Gespeicherte Songs aus Bibliothek öffnen, Analyse und Lyrics laden | Bestanden; erneut nach Neustart im neuen Build |
| N07 | Wiedergabe startet und Zeit läuft | Bestanden; erneut nach Neustart im neuen Build |
| N08 | Pause hält Position | Bestanden; Pause auch im neuen Build geprüft |
| N09 | Seeking übernimmt dieselbe Position in Kurve und Player | Bestanden: zuvor 30,90 s; neu importierte Lyrics zusätzlich bei 10,25 s |
| N10 | Gebrochener Lyrics-Zeitstempel navigiert exakt | Bestanden: 10,25 s vor und nach Neustart |
| N11 | Lyrics-Anzeige und aktive Zeile folgen Position | Bestanden; neue importierte Zeile zusätzlich sichtbar aktiv |
| N12 | Gemeinsame A/B-Punkte in Player und Kurve | Bestanden: A=10,25 s, B=25 s |
| N13 | Wiedergabe springt bei B zurück nach A | Bestanden: Rücksprung in 62 nativen Zeitstichproben |
| N14 | Player- und Kurvenposition während Loop synchron | Bestanden im Stichprobenumfang: maximale Differenz 0,02451 s |
| N15 | Songwechsel stoppt alte Wiedergabe und setzt Position/Loop zurück | Bestanden: neuer Song pausiert bei 0, kein alter Loop |
| N16 | App und eigener Dienst vollständig beenden/neu starten | Bestanden, erneut in Phase 2A.2; neue Prozesse/Fenster |
| N17 | SQLite-Zeilen, Cachezuordnungen und verwaltete Audiohashes über Neustart erhalten | Bestanden: exakter Vergleich gleich, integrity_check=ok, keine verwaisten Cachebesitzer |
| N18 | Nativ importierten Song nach Neustart öffnen | Bestanden: neue Lyrics, Kurve und gespeicherte Analyse ohne erneute Inferenz |
| N19 | Fehlende verwaltete Kopie mit Wiederimporthinweis erklären | Erstfall fehlgeschlagen; korrigierter Build bestanden, Deutsch/Englisch; erneut vor nativer Reparatur geprüft |
| N20 | Beschädigte verwaltete Kopie sinnvoll erklären | Erstfall fehlgeschlagen; korrigierter Build bestanden; Reparatur jetzt nativ nachgewiesen |
| N21 | Fehlende und beschädigte Kopie über denselben nativen Quellimport reparieren | Bestanden, getrennte Versuche: identische Track-ID, ursprünglicher Audiohash wiederhergestellt; Notiz-/Analysezeilen bytegleich |
| N22 | Neue LRC nativ auswählen/bestätigen; Inhalt und Zeitstempel übernehmen | Bestanden: 1,25 / 10,25 / 25 s; leere Endmarke bei 45 s erhalten |
| N23 | Originalbestand, synthetische Quellen und produktive SQLite schützen | Bestanden: vollständiger Vor-/Nachhashvergleich; produktive und isolierte SQLite intakt |
| N24 | Eigene App-/Dienstprozesse beenden | Bestanden; Testhalter beendet, Abschlusssnapshot ohne eigene Prozesse |
| N25 | Audio-Dateidialog abbrechen ohne Änderung | Bestanden: bildgebundenes Cancel; sämtliche SQLite-Zeilen und Audiohashes gleich |
| N26 | LRC-Dateidialog abbrechen ohne Änderung | Bestanden: Escape vor und nach Neustart; Editorinhalt gleich, abschließend auch sämtliche SQLite-Zeilen und Audiohashes gleich |
| N27 | Tatsächlich neu importierte Lyrics verarbeiten, anzeigen und navigieren; nach Neustart erhalten | Bestanden: lokale Analyse über UI abgeschlossen; neue Zeile setzt beide Regler auf 10,25 s; nach Neustart gleicher gespeicherter Inhalt |

## Fehlgeschlagene und blockierte Fälle getrennt

Historische Erstfehler N19/N20: generischer Medienfehler statt Reparaturhinweis;
mit dem vorhandenen übersetzten Hinweis korrigiert und nativ nachgeprüft.
Die vorherigen N03/N04/N05/N22 waren durch die WebView2-Prozessbindung blockiert;
Phase 2A.2 hat sie mit dem neuen Desktop-Picker vollständig nativ geschlossen.
Die Werkzeuggrenzen selbst wurden nicht gepatcht. Fehlgeschlagene Indexeingabe,
ungültige Pfadformatierung und ein außerhalb des sichtbaren Bereichs liegender
Lyrics-Klick bleiben lokale Automationsfehlversuche; jeweils neu beobachtet,
kein Erfolg daraus abgeleitet.

**Aktuell keine blockierten oder fehlgeschlagenen Pflichtfälle der Phase 2A.**
Andere DPI-/Mehrmonitor-Konfigurationen, Langzeitverhalten, Installer, Windows 10,
Linux und musikalische Modellqualität sind nicht Teil dieser Abnahme. N14 misst
Accessibility-Anzeigewerte, keine samplegenaue Audioausgabelatenz. Die breitere
Kernfreigabe und das externe Datenbank-Gate bleiben offen.

## Reproduktion und lokale Nachweise

Build und sichere Beobachtungs-/Eingabeschleife aus
[WINDOWS-DESKTOP-TESTING.md](WINDOWS-DESKTOP-TESTING.md) verwenden.

```powershell
python -m scripts.windows_library_testing prepare
$area = '<neu ausgegebener isolierter Arbeitsordner>'
python -m scripts.windows_desktop_testing run --area $area
```

`prepare` legt klar gekennzeichnete Anzeige-Caches für die geplanten synthetischen
Identitäten an, damit beim ersten Öffnen keine automatische Inferenz beginnt. In der UI beide 60-Sekunden-Quellen nativ importieren; `seed` ist
nur alternativer Fixtureaufbau und zählt nicht als Abnahme. Für Reparaturfälle
zuerst die verwaltete Testkopie sichern, ausschließlich diese verschieben oder
beschädigen, nativ öffnen und Hinweis prüfen, dann dieselbe unveränderte Quelle
nativ erneut auswählen. Vor-/Nachvergleich über alle Track-/Cache-/Ownerzeilen;
Notiz und Analyse vor beiden Reparaturen sichern und unverändert vergleichen.
Die Reparatur erfolgte durch den echten Import, nicht durch Backup-Rückkopieren.

Die ungültige Quelle getrennt nativ importieren und sämtliche Datenbankzeilen
vor/nach HTTP 422 vergleichen. Audio-Cancel und LRC-Escape getrennt prüfen.
LRC-Quelle mit anderen Zeilen als im Cache auswählen, Editor prüfen, lokale
Analyse über die UI starten und neue Zeilenanzeige samt 10,25-s-Navigation prüfen.

```powershell
python -m scripts.windows_library_testing snapshot --area $area --label before-restart
# Test-App mit Alt+F4 schließen; Halter beendet den eigenen Dienst.
python -m scripts.windows_desktop_testing run --area $area
# Bibliothek öffnen, importierten Song auswählen, neue Lyrics prüfen.
python -m scripts.windows_library_testing snapshot --area $area --label after-restart --baseline before-restart
# Test-App beenden; danach abschließenden Snapshot aufnehmen.
```

Rohbilder, Accessibility-Bäume, Prozess-/Ownerdiagnosen, Quellen, Fehlerbackups,
SQLite-Auszüge, komplette Originalhashmanifeste und fallbezogene Prüfskripte
bleiben ignoriert lokal. Der Testhalter aktualisiert nur bekannte synthetische
Identitäten für den nächsten Start; fremde Einträge werden abgewiesen.

## Automatisierte Regressionen

Getrennt von der Desktopmatrix bestanden: 378 Backendtests (34,82 s),
146 Frontendtests in 28 Dateien, neun Rusttests offline mit Lockfile und fünf
Node-Drivertests. TypeScript/Vite und Windows-Releasebuild ohne Bundle bestanden.
Die bestehende Chunkgrößenwarnung bleibt. Kein neuer Installerlauf.

Neu abgesichert: Browser-/Desktop-Importentscheidung, Cancel ohne Fallback,
leere LRC-Datei, Zeitstempel und IPC-Sprache, Dekodier-/Dateifehler, ungültige
Antwortdaten, begrenztes Lesen, Multipart-Dateiname sowie eindeutige Parent-
Dialogbindung und Verbot indizierter Import-Edits. Bestehende echte SQLite-
Integrationsregressionen sichern Wiederimport, Reparatur, Notizerhalt und
Datenintegrität weiterhin ab. [Testbaseline](TEST-BASELINE.md).
