# Aktueller Entwicklungsstand

Entwicklungsversion 0.3. Nachweise und Grenzen werden mit den jeweiligen Prüfungen aktualisiert.

## Implementiert

- Getrennte Anweisungen für Gesamtdeutung und Einzelstelle; ungetakteter Text kann für die Gesamtdeutung verwendet werden. Ohne Text erscheint eine konkrete Anleitung statt erfundener Lyrics.
- Mehr Ausgabetext, sichtbare Hinweise bei Kontext-/Ausgabelimit und separate musikalische Begründung aus tatsächlichen Mess-/Modellwerten.
- Gespeicherte KI-Deutung automatisch laden, bewusst neu erzeugen oder gemeinsam mit Analyse-Cache löschen; eigene Notizen bleiben erhalten.
- Lokales Demucs-Hörstudio mit Solo-/Mix-Knöpfen und zeitlich fortgesetzter Wiedergabe beim Quellenwechsel. Vier oder experimentell sechs Gruppen; keine Trennung einzelner Sänger.
- Lokale Texterkennung per Knopf; Whisper-Fallback bei neuen Analysen standardmäßig aktiviert. Vorhandene Vier-Spur-Gesangstrennung wird bevorzugt. Unverstandener Text wird nicht als gesichert ausgegeben.
- Auswahl von Einzeltracks aus öffentlichen SoundCloud-Suchlinks.
- Kostenlose MusicBrainz-Recherche ohne Key mit bewusst bestätigter Aufnahme und Quellenlink.
- Gemeinsame Profile für Gemini, OpenAI, Anthropic, DeepSeek und kompatible lokale/LAN-Server; Schlüssel nur im Arbeitsspeicher. Kein pauschales Versprechen universeller Anbieter-/Modellkompatibilität.
- Einzelne Songs oder gesamte Bibliothek getrennt vom Analyse-Cache entfernen; Originaldateien und Modelle bleiben erhalten.
- Rotierende lokale Logs mit Fehler-ID, Codepositionen und Auftragslaufzeiten; keine Songtexte oder Zugangsdaten in den Protokollen.

## Bisher ausgeführt

- 81 Python-Tests und 13 Frontend-Tests bestanden, einschließlich gespeicherter Deutungen, Neugenerierung, Cache-Löschung, vollständiger Song-/Bibliotheksentfernung, Anbieterprotokollen, Zustimmung und Fehlerprotokollen.
- Frontend-Produktionsbuild bestanden.
- Offizielle Demucs-Gewichte heruntergeladen; echte Vier- und Sechs-Spur-GPU-Inferenz auf selbst erzeugtem Audio bestanden. Das beweist technische Funktion, keine quantitative Trennqualität für Gesang.
- Echter Offline-Durchlauf auf CUDA mit CLAP, XLM-EMO, Instrumenthinweisen und neuer ausführlicher Zeilendeutung bestanden. Cachetreffer und erzwungene Neuanalyse nachgewiesen.
- Öffentlichen SoundCloud-Suchlink live auf einzelne Songlinks aufgelöst. Den einzigen Treffer lokal heruntergeladen, einen 20-Sekunden-Ausschnitt getrennt und auf der Gesangsspur mit Whisper vier zeitlich begrenzte Segmente erkannt. Keine quantitative Wortgenauigkeitsprüfung.
- Gesamtdeutung mit selbst geschriebenem vollständigem Testtext auf CUDA ausgeführt; nach präzisiertem Prompt ohne erfundene längere Beispielzitate und ohne Kontext-/Ausgabekürzung. Kleine Modelle bleiben sprachlich und inhaltlich begrenzt.
- Browser-Hörstudio: echte lokale Trennung eines öffentlichen Testclips, Gesang und Instrumental-Mix wiedergegeben, Abspielposition beim Wechsel erhalten.
- Nativer Windows-Build 0.3 und Produktionsbuild bestanden; nach letzten UI-Korrekturen wird der Build erneut erstellt.
- MusicBrainz-Livesuche lieferte HTTP 503. Die App behandelt den Ausfall mit Fehler-ID; erfolgreiche Live-Recherche ist damit noch nicht belegt.

## Noch zu prüfen

Weitere quantitative Bewertungen von Textdeutung, Gesangserkennung und Trennqualität stehen aus. Echte OpenAI-/Anthropic-Inferenz ohne Nutzer-Key nicht geprüft; Adapter werden mit Vertragstests validiert. Linux und Windows 10 weiterhin nicht lokal geprüft. Genauigkeits- und Qualitätsgrenzen aus der README gelten unverändert.

## Weiterer Checkpoint: präzisere Bedienung

- 85 Python-Tests, 13 Frontend-Tests und Produktionsbuild bestanden. Neu: überlappende Transkriptionsfenster, manuelle Audiofilter und Recherche-Fallback.
- Whisper-CUDA mit vorhandenen PyTorch-cuDNN-/cuBLAS-Bibliotheken tatsächlich ausgeführt. Large-v3-Turbo projektlokal heruntergeladen und auf einem vollständigen öffentlichen Song gegen Base und gegen eine getrennte Gesangsspur getestet. Zeitabdeckung und Wortanzahl unterscheiden sich; ohne Referenztranskript ist damit kein Genauigkeitsgewinn bewiesen. Unsichere Zeilen werden zur Korrektur sichtbar gehalten.
- Zwei-Sekunden-Anzeigeraster zusätzlich zum Fünf-Sekunden-Raster implementiert; der Audiokontext bleibt zehn Sekunden. Feinere Anzeige ist keine höhere Messgenauigkeit.
- Manueller Zeit-/Frequenz-/Stereo-Fokus als Hörhilfe implementiert und mit tatsächlicher Filterung geprüft. Keine Trennung nach Sängeridentität.
- Katalogsuche bei MusicBrainz und Apple samt Detailabruf live erfolgreich. Beide Dienste bleiben externe Abhängigkeiten; keine erfundenen Daten beim Ausfall.
- Einzelne Songs und gesamte Bibliothek lassen sich getrennt vom Cache entfernen. Auf dem zuvor laufenden Dienst fehlten diese Endpunkte noch; dieser veraltete Dienst wurde ersetzt. Versionsprüfung und Freigabe der Player-Datei vor dem Löschen ergänzt.

Automatische Metadatenrecherche, vollständiges Ersetzen recherchierter Angaben, Instrument-Ausblendung, Neustart-/Beenden-Steuerung und die abschließende Brave-Prüfung werden noch vervollständigt. Der native Build wird nach diesen weiteren Oberflächenänderungen erneut erstellt.

## Native Bedienprüfung und Dienststeuerung

- Automatische Recherche, erzwungenes Ersetzen recherchierter Metadaten und deren gezielte Cache-Löschung implementiert und durch Regressionstests geprüft. Import-Tags und Originalformatwerte werden separat angezeigt.
- Überwachter Backend-Starter ergänzt. Neustart und Beenden betreffen nur MoodScope und seine eigenen Unterprozesse. Ein direkt gestartetes Uvicorn aktiviert diese Bedienfunktionen nicht.
- Neuer nativer Windows-Build mit Dienststeuerung erfolgreich erstellt und tatsächlich geöffnet. MP3 und FLAC über den nativen Dateidialog importiert, echte CUDA-Analysen und zwei Kurven angezeigt. Wiedergabe, Pause und Biggest-Split-Sprung geprüft. Lokale Instrumenthinweise und Metadaten-Neurecherche bedient.
- Neustart über den Knopf im nativen Fenster tatsächlich ausgeführt. Bibliothek blieb erhalten; Wiederöffnung lud eine gespeicherte Analyse ohne neue Modellinferenz.
- Bei der nativen Gesamtdeutung erzeugte Qwen 1.5B ein unbelegtes Zitat. Die Belegprüfung hat die Antwort korrekt verworfen. Ein begrenzter zweiter lokaler Formulierungsversuch mit unveränderter Belegprüfung wurde ergänzt; 91 Python-Tests bestanden. Derselbe native Fall wurde danach erfolgreich mit einer Gesamtdeutung abgeschlossen. Es gibt keine automatische kostenpflichtige Anbieter-Wiederholung.
- Native Hörstudio-Prüfung und Brave-Prüfung bleiben in dieser Runde noch offen. Private Testtitel, Lyrics und Bildschirmaufnahmen werden nicht veröffentlicht.

## Weitere sichtbare Prüfung

- Native Hörstudio-Prüfung abgeschlossen: echte Quellentrennung, hörbare Gesangs-/Instrumentalwiedergabe, Positionsübernahme und manuelle Frequenzfokussierung bedient. Die Filter sind keine Trennung einzelner Sänger.
- Brave tatsächlich am PC bedient: öffentlichen SoundCloud-Einzeltrack importiert, zwei Kurven angezeigt und präzise Turbo-Erkennung des vollständigen Songs auf der getrennten Gesangsspur abgeschlossen. Gesamtdeutung erfolgreich abgeschlossen.
- Sichtbare Whisper-Auswahl und automatischen Import angeglichen; automatische Erkennung verwendet nun dieselbe Auswahl. Standardquelle ist vorhandene Gesangsspur oder Originalmix, damit ein fehlendes optionales Demucs den normalen Import nicht blockiert. 14 Frontend-Tests und Produktionsbuild bestanden; 91 Python-Tests zuletzt bestanden.
- Private MP3-/FLAC-Titel, Lyrics, Ergebnisse und Bildschirmaufnahmen bleiben außerhalb des Repositorys. Die Prüfung der Löschlogik erfolgte mit isolierten Testdaten; keine vollständige Nutzungsbibliothek wurde zur Bedienprüfung geleert.

## Sprache und Bestätigungsdialoge

- Deutsch/Englisch in der Kopfzeile, lokal gespeicherte Auswahl, übersetzte Bedienelemente, Hilfen und Statusmeldungen. Eigene Notizen, importierte Tags und Original-Lyrics bleiben unverändert.
- Neustart-/Beenden-Bestätigungen im dunklen App-Design mit Tastaturfokus, Escape, Fokusbegrenzung und expliziter Bestätigung vor dem Dienstaufruf.
- Lokale und optionale Server-Deutungen erhalten eine ausdrückliche Ausgabesprache. Deutsche und englische Deutungen haben getrennte Cache-Einträge; Cache-Löschung entfernt beide.
- Kein erneuter sichtbarer PC-Test in dieser Runde. Neue Abläufe werden durch Komponenten- und API-Regressionstests geprüft.

- Ergebnis dieser Runde: 99 Backend- und 19 Frontend-Tests bestanden (nach Korrekturen nur die betroffenen Fälle wiederholt). TypeScript-/Produktionsbuild und nativer Windows-Releasebuild erfolgreich. Eine tatsächliche Qwen-Gesamtdeutung selbst geschriebener englischer Testzeilen lief offline auf CUDA und lieferte englischen Text; keine erfundene Live-API-Prüfung ohne Schlüssel.
- Sieben Hilfsbibliotheken projektlokal aktualisiert; aktueller Python-Sicherheitsstand einschließlich offener Modellbibliotheksmeldungen in SECURITY.md. Keine systemweite Paketänderung. Kein neuer sichtbarer Desktop-Durchlauf dieser Sprachversion.

## Korrektur des nativen Starts

Der direkte Cargo-Releaseaufruf der Sprachrunde hatte das Tauri-Feature `custom-protocol` nicht aktiviert. Die EXE erwartete deshalb den später beendeten Vite-Server. Ein erfolgreicher Compilerlauf war hier kein ausreichender Startnachweis. Der korrigierte Build bettet die Oberfläche ein; build.rs verwirft künftig Release-Builds im Entwicklungsmodus. Der Worker übernimmt außerdem die Standardausgabekanäle des Supervisors ausdrücklich, damit native Startfehler im Backend-Protokoll landen.

Korrigierter Windows-Releasebuild erfolgreich. Vier gezielte Starter-/Systemtests bestanden; separater tatsächlicher Supervisor-Test bestätigte API-Revision 4, geschriebenes Startprotokoll und sauberes Beenden. Kein erneuter Song- oder sichtbarer Bedienlauf.

## Hörstudio und nachvollziehbare Bewertung

- Explizites Wiederherstellen manuell versteckter und automatisch leiser Gruppen mit persistenter Sichtbarkeit. Pegel für echte Quellenspuren, deterministischer Mix-Cache und Schutz vor gleichzeitigen Schreibzugriffen.
- Zentralisierte unveränderte CLAP-Prompts und Valenzgewichte; Methodenprotokoll pro Analyse. Bekannte ältere Pipelineversionen werden ausdrücklich als rekonstruiert gekennzeichnet; unbekannte/Provider-Analysen erhalten keine erfundene CLAP-Formel.
- Gemeinsamer Dialog mit Tastatur-/Fokussteuerung für Neustart, Beenden und Bibliotheksaktionen. Optionaler sphärischer Atmosphärenplayer ohne Eingriff in den Audiographen.
- 23 Frontend- und 30 betroffene Backend-Tests bestanden; weiterer Recherche-Ausbau, neuer nativer Build und zusätzliche Integration folgen im nächsten Checkpoint. Fine-tuned ist auswählbar; tatsächlicher neuer Modelldurchlauf wird separat geprüft.

## Recherche-Fallbacks und geprüfter Integrationsstand

- Automatische Suche bei MusicBrainz, Apple iTunes und Deezer; Titelbereinigung und Suche ohne Interpret bei leeren Ergebnissen. Teilfehler lassen Suchtreffer nutzbar, fehlgeschlagene automatische Recherche bleibt sichtbar. Eindeutige passende Aufnahmen aus mehreren Quellen blockieren sich nicht mehr gegenseitig.
- Instrumentcredits zusätzlich aus verknüpften Discogs-Releases und Wikidata P870. Trackbezogene Credits, Albumangaben und verknüpfte Werkangaben bleiben getrennt. Ein öffentlicher Discogs-Releaseabruf ohne Schlüssel lieferte acht trackbezogene Instrumentcredits und 64 Albumcredits; diese konkreten Inhalte werden nicht veröffentlicht.
- Tatsächlicher CUDA-Test von Demucs Fine-tuned mit selbst erzeugtem Signal bestanden: vier finite, vier Sekunden lange Quellen. Neuer begrenzter Downloadpfad und enges Safe-Globals-Laden beheben den beobachteten PyTorch-Weights-only-Kompatibilitätsfehler.
- Echter CLAP-/XLM-EMO-Durchlauf im isolierten Dienst: gespeichertes Methodenprotokoll und Rechenweg im Hintergrund-Browser geprüft. Atmosphärenvisual und Löschdialog visuell geprüft, Löschdialog abgebrochen. Keine erneute Analyse privater Testmusik.
- Same-Origin-Auslieferung funktioniert auch auf einem isolierten lokalen Backend-Port; andere nicht freigegebene Ursprünge bleiben gesperrt. Die Browseroberfläche verwendet bei lokaler Backend-Auslieferung denselben Ursprung; native App und Vite behalten ihren konfigurierten Dienst.
- Frontend: 24 Tests bestanden, TypeScript-/Produktionsbuild erfolgreich. Backend: Volltest mit 110 Fällen bestanden; nach den letzten Ergänzungen 39 betroffene API-/Recherche-/Download-/Startertests bestanden. Der Testumfang umfasst jetzt 113 Fälle. Ein Starlette-Testclient-Deprecation-Hinweis bleibt. Neuer nativer Windows-Releasebuild erfolgreich.
- Sicherheitsrest: Eine getrennte aktuelle Python-/CUDA-Umgebung wird projektlokal vorbereitet. Die produktive ältere Umgebung ist noch nicht umgestellt; verbleibende Meldungen stehen in SECURITY.md. Linux und Windows 10 wurden nicht lokal ausgeführt.

## Isolierte aktuelle Modellumgebung

- Projektlokales Python 3.13, PyTorch 2.15/CUDA 13.2 und Transformers 5.22.1 ohne geerbte Systempakete. Startskripte bevorzugen die Umgebung erst mit Validierungsmarker. API-Revision 6 und Umgebungskennung verhindern die stille Wiederverwendung eines älteren Dienstes.
- Tatsächliche CUDA-Ausführung von CLAP, XLM-EMO, Qwen (Deutsch/Englisch), Demucs Fine-tuned und Whisper mit selbst erzeugtem Testmaterial. Whisper benötigt zusätzlich projektlokale CUDA-12-Bibliotheken; nach dem beobachteten DLL-Fehler wurde genau dieser Pfad korrigiert und erneut erfolgreich geprüft.
- 113 Backend-Tests im neuen Volltest bestanden, anschließend neun gezielte Start-/CUDA-Pfadtests bestanden (aktueller Umfang 117). Isolierter tatsächlicher Supervisor-Start über den alten Interpreter bestätigte API 6, Startprotokoll und sauberes Beenden. PowerShell-Setup-/Startskripte syntaktisch geprüft. Windows-Releasebuild aktualisiert.
- pip check ohne Konflikte; OSV-Abgleich von 92 Python-Paketen ohne Befund. Offene Rust-/Linux-Hinweise bleiben in SECURITY.md dokumentiert. Keine erneuten privaten Songtests oder zusätzlichen sichtbaren Desktopprüfungen.

## Harmonie, Merkmalsbeiträge und appweite Atmosphäre

- Lokales harmonisches STFT-Chroma, explizite Tonartprofile und Dur-/Moll-Dreiklänge auf Sekundenraster. Speicherbegrenzte Spektralblöcke, mehrdeutige Akkorde leer; kein Genauigkeitsnachweis für beliebige Musik.
- CLAP-Rohwerte bleiben erhalten. Neue Pipeline ergänzt protokollierte heuristische Tonart-/Dreiklang-/Tempo-/Helligkeitsbeiträge mit insgesamt maximal ±0,12 Valenz. Relative Energie beeinflusst separat Aktivierung. Neue Cacheschlüssel, alte Analysen bleiben abrufbar; neue Messungen erfordern Neuanalyse.
- Appweite optionale Farb-/Nebel-/Wasseratmosphäre ohne Eingriff in den Audiographen; Pause und reduzierte Bewegung berücksichtigt. F11 im nativen Fenster vorbereitet.
- Aufnahmevorschläge nach kompatibler Identität und Laufzeit sortiert; bis zu drei automatische Credit-Fallbacks. Online-Werktonarten über MusicBrainz und Wikidata getrennt von gemessener Aufnahmetonart.
- 42 betroffene Backend-Tests bestanden, einschließlich echter Analyse eines synthetischen C-Dur-Akkords. Frontend- und nativer Abschlussnachweis folgen nach den restlichen Hörstudioverbesserungen. Kein neuer privater Songdurchlauf.
