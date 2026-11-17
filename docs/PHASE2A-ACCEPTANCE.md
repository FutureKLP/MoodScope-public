# Phase 2A: native Bibliothek, Player und Lyrics

Prüfung am 17. November 2026 unter Windows 11 Build 26200, WebView2 und 96 DPI.
**Entscheidung: Teilabnahme; Phase 2A nicht vollständig freigegeben.** Native
Dateiimporte bleiben durch eine separate WebView2-Fensterbindung blockiert.
Das ist kein nachgewiesener Importfehler der Anwendung. Keine spätere Phase,
externe Datenbank, allgemeine Musikqualitäts- oder Kernfreigabe.

## Ausgangsstand und Isolation

PR #10 war beim erneuten GitHub-Abgleich offen, nicht gemergt und mergefähig;
Head `aaf5b6fee810b748c942459fc970feec86478717`, alle 13 Check-Runs erfolgreich.
Main war `44320c4d10a5f5e99cc7f2c18e7ac0c5e6568124`. Lokaler Branch und
Arbeitsbaum waren mit dem PR-Head identisch und sauber. Phase 2A verwendet
einen separaten Entwicklungsbranch auf dieser öffentlichen Abstammung.
PR #10 und Main wurden in dieser Prüfung nicht verändert.

Eigener Loopback-Dienst, eigene SQLite, eigenes WebView-Profil und eigener
temporärer Ordner unter `.tools`. Zwei erzeugte Stereo-Sinustöne mit 440/660 Hz,
48 kHz und je 60 Sekunden; zusätzlich die unveränderte Zwei-Sekunden-Fixture
aus Phase 1. Kurven und vier zeitgebundene Textzeilen sind absichtlich verfasste
Anzeige-Fixtures, keine Inferenz. Kein Originalsong wurde importiert oder abgespielt.
Der Originalmusikbestand wurde ausschließlich lesend gehasht.

Vorab gespeicherte synthetische Caches verhindern automatische Inferenz beim
Öffnen. Bis zum Import der geplanten Identitäten besitzen diese Caches noch
keinen Trackeintrag; das ist vorbereiteter Fixturezustand. Nach der Bereitstellung
und im Neustartvergleich bestanden keine verwaisten Cachebesitzer.

## Native Testmatrix

"Bestanden" bezeichnet nur den genannten Umfang. Automatisierte Frontendtests,
HTTP-Fixtureaufbau und SQLite-Prüfungen ersetzen keinen nativen Dateidialog.

| Fall | Erwartung und tatsächlicher Nachweis | Ergebnis |
| --- | --- | --- |
| N01 | Exakter Prozesspfad und Titel, eindeutiges Hauptfenster, frische Bildregion; 16×16-Hilfsregion nach Neustart verworfen | Bestanden |
| N02 | Audioimport öffnet echten Windows-Dialog | Bestanden: Öffnen des Dialogs |
| N03 | Synthetische Audiodatei auswählen und bestätigen | Blockiert: WebView2-Dialog nicht als Zielfenster angeboten |
| N04 | Dieselbe Datei nativ erneut importieren, Identität/Cache erhalten | Blockiert durch N03 |
| N05 | Beschädigte Quelldatei nativ importieren und Dekodierfehler prüfen | Blockiert durch N03; Backendregression separat bestanden |
| N06 | Gespeicherte Songs aus Bibliothek öffnen, Cache und Lyrics laden | Bestanden mit vorbereiteten synthetischen Einträgen |
| N07 | Wiedergabe starten, Zeit läuft, Pause verfügbar | Bestanden; erneute Wiedergabe auch im korrigierten Build |
| N08 | Pause hält Position stabil | Bestanden in zwei getrennten Beobachtungen |
| N09 | Positionsregler spult; Kurve übernimmt denselben Zeitstand | Bestanden: 30,90 s in beiden Reglern |
| N10 | Lyrics-Zeile mit gebrochenem Zeitstempel springt exakt | Bestanden: 10,25 s in Player und Kurve |
| N11 | Lyrics-Anzeige und aktive Zeile folgen Position | Bestanden bei 0, 10,25, 25 und etwa 30,90 s |
| N12 | A/B-Punkte in Player und Kurve gemeinsam sichtbar | Bestanden: A=10,25 s, B=25 s |
| N13 | Wiedergabe springt bei B nach A zurück | Bestanden: Rücksprung in 62 nativen Zeitstichproben erfasst |
| N14 | Player und Kurve während Loop synchron angezeigt | Bestanden im beobachteten Umfang: maximale Wertdifferenz 0,02451 s |
| N15 | Songwechsel während aktivem Loop stoppt alte Wiedergabe und setzt Zeit/Loop zurück | Bestanden: neuer Song pausiert bei 0, kein alter Loop |
| N16 | App und eigener Dienst vollständig beenden und neu starten | Bestanden: neue Prozess- und Fensterkennungen |
| N17 | Bibliothek, Cache, verwaltete Audiohashes und SQLite nach Neustart erhalten | Bestanden: Zeilen-/Hashvergleich gleich, integrity_check=ok |
| N18 | Gespeicherten Song nach Neustart erneut nativ öffnen | Bestanden: Kurve und Lyrics vorhanden |
| N19 | Fehlende verwaltete Audiokopie sinnvoll erklären | Zunächst fehlgeschlagen: nur generischer Playerfehler. Nach Korrektur nativ bestanden, Deutsch/Englisch |
| N20 | Beschädigte verwaltete Audiokopie sinnvoll erklären | Zunächst fehlgeschlagen: nur generischer Playerfehler. Nach Korrektur nativ bestanden, Englisch; gemeinsame deutsche Meldung bei N19 geprüft |
| N21 | Nach Wiederherstellung der isolierten Kopien wieder öffnen und abspielen | Bestanden im korrigierten Build; Wiederherstellung aus Fixturebackup, kein nativer Wiederimportnachweis |
| N22 | LRC-Dateiauswahl öffnen und importieren | Öffnen bestanden; Dateiauswahl/Bestätigung blockiert wie N03 |
| N23 | Originaldateien, Fixturequellen und produktive SQLite unverändert | Bestanden: vollständiger Vor-/Nachvergleich, isolierte Bibliothek ebenfalls gleich |
| N24 | Eigene App-/Dienstprozesse nach Prüfung beenden | Bestanden: Testhalter beendet, keine eigenen App-/Dienstprozesse im Abschlusssnapshot |

N14 ist eine Stichprobe von Accessibility-Anzeigewerten, keine Messung der
Audioausgabelatenz oder samplegenauer Synchronität. Die verwendeten Kurven haben
keine wissenschaftliche Bedeutung. Langzeit-, andere DPI-, Mehrmonitor-,
Installer- und andere Plattformprüfungen gehören nicht zu dieser Teilabnahme.

## Blocker und korrigierter Fehler

Der Audio-/LRC-Öffnendialog gehört zu `msedgewebview2.exe`. Er wird als zusätzliche
946×533-Bildregion erfasst, fehlt aber in `list_windows()` und `list_apps()` als
adressierbares Fenster. Ein bildgebundener Klick über das Tauri-Hauptfenster wurde
mit einer Prozessabweichung abgelehnt. Nach Aktivierung, frischem Bild und einer
einzigen Wiederholung dasselbe Ergebnis. Keine numerischen Accessibility-Klicks
im Dateidialog, keine blinden Wiederholungen, keine Eingabe eines Dateipfads in
ein unbestätigtes Ziel. Escape schloss den Dialog. LRC zeigte denselben Fenstertyp.
Die sichere Phase-1-Erkennung für den Tauri-WAV-Speicherdialog löst diese andere
Prozesszuordnung nicht automatisch.

Für die verbleibende native Matrix wurden die synthetischen Dateien ausdrücklich
als Fixtureaufbau über den eigenen HTTP-Dienst importiert. Dies zählt weder als
N03 noch als N04. Import/Wiederimport und Reparatur sind separat automatisiert
abgesichert; die native Abschlussbestätigung bleibt offen.

Bei beschädigten/fehlenden verwalteten Kopien lieferte der Dienst bereits HTTP 409
mit Reparaturhinweis, das Mediaelement verdeckte diesen aber. Der Player prüft
nach einem Medienfehler jetzt ausschließlich seinen verwalteten Originalaudio-
Endpunkt mit einer begrenzten Range-Anfrage. Erfolgreiche Antwortkörper werden
geschlossen, keine vollständige Audiodatei für die Diagnose geladen. HTTP 409
zeigt den vorhandenen übersetzten Wiederimport-Hinweis. Andere Fehler behalten
die allgemeine Meldung. Fremde URLs, Blob- und Stemquellen werden nicht abgefragt.
Verspätete Ergebnisse nach Song-/Quellenwechsel oder neuem Wiedergabeversuch
werden verworfen. Keine neue Designsprache oder Übersetzung erforderlich.

## Reproduktion und Nachweise

Voraussetzungen und beaufsichtigte Eingabeschleife aus
[WINDOWS-DESKTOP-TESTING.md](WINDOWS-DESKTOP-TESTING.md) verwenden. Beobachtung
und Eingabe bleiben getrennt; nach einer Aktion erst den stabilen Folgezustand
beurteilen. Ein unmittelbar erfasster Accessibility-Baum kann noch den vorherigen
Renderstand zeigen.

```powershell
python -m scripts.windows_library_testing prepare
# Den als PHASE2A_AREA ausgegebenen neuen Ordner übernehmen:
$area = '<neuer isolierter Arbeitsordner>'
python -m scripts.windows_desktop_testing snapshot --area $area --label before
python -m scripts.windows_desktop_testing run --area $area
```

In einer weiteren Shell nach verifizierter Dienstbereitschaft, falls N03 weiterhin
blockiert ist, ausschließlich den gekennzeichneten Fixtureaufbau verwenden:

```powershell
python -m scripts.windows_library_testing seed --area $area
python -m scripts.windows_library_testing snapshot --area $area --label before-restart
# Test-App mit Alt+F4 schließen; Halter beendet seinen Dienst.
python -m scripts.windows_desktop_testing run --area $area
python -m scripts.windows_library_testing snapshot --area $area --label after-restart --baseline before-restart
```

`seed` ist ausdrücklich kein nativer Importtest. Snapshot nach erfolgreichen
nativen Importen oder Fixtureaufbau aktualisiert die erlaubten synthetischen
Track-IDs für den nächsten Start. Unbekannte Identitäten werden abgewiesen.
Vor Fehlerpräparation Backups der isolierten verwalteten Kopien sichern; nie die
Quellen verändern. Fehlende/beschädigte Kopien getrennt öffnen, Meldung und
Backendstatus erfassen, anschließend aus Backups wiederherstellen und vergleichen.
Rohbilder, Accessibility-Beobachtungen, Zeitstichproben, Fehlerpräparation und
Hashmanifeste bleiben ignoriert lokal. Keine persönlichen Fensterdaten publizieren.

Neu bestanden: 378 Backendtests, 142 Frontendtests in 27 Dateien, drei separate
Node-Drivertests, TypeScript/Vite und Windows-Releasebuild ohne Bundle.
Die bestehende Chunkgrößenwarnung bleibt. Rustcode wurde nicht geändert und in
Phase 2A nicht erneut separat getestet; keine Installerprüfung.
Neue Regressionen sichern Wiederwahl derselben Datei, LRC-Editorübernahme,
Diagnosegrenzen/Deutsch/Englisch, verspätete Antworten und echte SQLite-Snapshots.

Nächster erforderlicher Schritt innerhalb Phase 2A: den WebView2-Dateidialog über
ein korrekt angebotenes eigenes Fenster bedienen und N03/N04/N05/N22 vollständig
nativ wiederholen. Bis dahin keine vollständige Phase-2A-Abnahme.
