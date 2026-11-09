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

## Adaptive Trennung, Auftragsabbruch und eigene Modelle

- Automatischer Trennmodus mit Fine-tuned-Ensemble, gemessener Transienten-/Crest-Auswahl für Versatzmittelungen, 50 % Überlappung und energiegewichteter Rekonstruktionskorrektur. Tatsächlich auf CUDA mit synthetischem Signal geprüft: vier vollständige Quellen, Rekonstruktions-RMS unter 1e-5. Kein Nachweis perfekter Isolation.
- Kooperativer Auftragsabbruch mit globalem Banner, sicheren Haltepunkten und eigenem cancelled-Status; Datenbanktransaktionen prüfen vor Commit. Laufende GPU-Schritte/Netzwerkaufrufe können auslaufen. Nicht alle synchronen Metadatenaufrufe sind abbrechbar. Link-Downloader wird bei Abbruch beendet. Unvollständige Downloads erhalten keinen Installationsstatus.
- Eigene öffentliche Hugging-Face-Modellseiten: Konfigurations-/Formatprüfung, feste Revision, bestehende Adapter, kein Remote-Python-Code. Download, Auswahl und Modelllöschung in einheitlicher Oberfläche. Löschung prüft verwaltete Pfade; Songs/Analysen/Notizen bleiben erhalten. Fremde Modelle wurden nicht pauschal qualitativ getestet.
- Modelle & API als eigener Bereich links unter Song-Analyse. Reiterfolge Bibliothek, Songdetails, Stimmungsverlauf, Methode & Werte, Hörstudio, Interpretation; letzter Song-Reiter bleibt beim Einstellungswechsel erhalten. Responsive Hauptnavigation bleibt auch bei schmalen Fenstern zugänglich.
- 124 Backend-Tests im Gesamtlauf bestanden; anschließend 23 gezielte Modell-/Link-/Abbruchtests und 16 Modell-/Startertests bestanden. Frontend: neue Modellverwaltung einschließlich Download-Sperre und bestätigter Löschung geprüft; Navigationstests auf den neuen Bedienweg angepasst. Abschließender Windows-Build folgt.

## Abschließende Bedien- und Neustartkorrekturen

- 27 Frontend-Tests bestanden; nach dem 124er-Backend-Volltest wurden neue und betroffene Fälle gezielt geprüft, zuletzt 58 API-/Modell-/Link-/Starterfälle und sechs Harmonie-/Interpretationsfälle. Aktueller Umfang 137 Backend-Tests; kein weiterer Volltest unveränderter Fälle.
- Tatsächlicher isolierter Neustart bestätigte API 7 und eine neue Dienstinstanz; danach vollständiger Supervisor-Shutdown. Native Neustartkennung 75 lässt den Projektstarter die neueste vorhandene EXE wählen und die Dienstbereitschaft erneut prüfen.
- Hintergrund-Browserprüfung: Hauptnavigation, appweite Atmosphäre, eigene Modellhilfen in Deutsch/Englisch und Beenden-Dialog geprüft. Kein horizontaler Überlauf bei 1280 px. Beenden zeigte die endgültige Abschlussseite ohne Versionswarnung. Dabei gefundene englische Resttexte korrigiert.
- Eigene öffentliche CTranslate2-Whisper-Modellseite tatsächlich registriert und auf Revision fixiert; keine Gewichte erneut geladen. Wikidata-Tonartabruf lieferte einen zugeschriebenen Werktonartwert. Kein Nachweis beliebiger Fremdmodellqualität.
- Interpretation speichert die tatsächliche Textgrundlage und getrennte recherchierte Werkangaben. Geänderte Recherche macht gespeicherte Deutungen veraltet; Neugenerierung verwendet einen neuen Cache. Akkordbeiträge werden über tatsächliche zeitliche Überlappung gewichtet.

## Reale Songtests, Live-Mix und Exporte

- Reale Tests mit MP3 und FLAC aus dem Testordner und dem vollständigen angegebenen SoundCloud-Track: importiert, vier echte adaptive Hörspuren erzeugt, präzises Whisper über Gesangsspur, Zwei-Sekunden-Stimmungsverlauf, Harmoniemerkmale und lokale Interpretation. Originaldateien per Inhaltsvergleich unverändert. Wiedererkannte Importvarianten nutzen passende Caches. Keine quantitative Behauptung vollständiger Worterkennung.
- Dabei zwei echte Whisper-Probleme korrigiert: Wiederverwendung vorhandener Modellmanager-Snapshots aus dem gemeinsamen Cache sowie PyAV-19-Kompatibilität beim Dateidecoding. Normalisierte WAV-Dateien und Stems werden nun direkt gelesen und resampelt. Neue Regressionen bestanden.
- Öffentlicher YouTube-Import mit einem Creative-Commons-Testvideo erfolgreich; ein anderes Testvideo wurde von der Plattform abgelehnt. Keine Anmeldung oder Zugriffssperre umgangen.
- Eigenes Whisper-Tiny-Modell tatsächlich über die Oberfläche hinzugefügt, Download abgebrochen, fortgesetzt, ausgewählt, auf CUDA mit synthetischem Signal ausgeführt und wieder entfernt. Eintrag und verwaltete Gewichte entfernt, Standard wiederhergestellt. Null erkannte Segmente beim synthetischen Signal sind kein Gesangsgenauigkeitsnachweis.
- Live-Mix regelt gestreamte Quellen per Web Audio ohne neue Server-Mixdateien. Tatsächliche Browserwiedergabe mit stummgeschaltetem Original, Pegeländerung, Pause und ohne Konsolenfehler geprüft. Spur- und vollständigen Mixexport als echte Browserdownloads bestätigt. Mixexport senkt überhöhte Spitzen gleichmäßig ab statt die Wellenform zu clippen.
- A/B-Rechtsklickmarkierungen im Browser gesetzt; tatsächlicher Rücksprung vom Bereichsende zum Anfang beobachtet. Dritter Rechtsklick entfernt beide Markierungen. Tastaturalternative und Pegel-/Transportverhalten automatisiert geprüft.
- Abschließendes Layout im Hintergrund-Browser geprüft: neue Navigation, Hörstudio-Abstände, Export-/Live-Steuerung, A/B-Leiste und geöffnetes gestaltetes Dropdown. Kein horizontaler Überlauf bei 1280 px. Die native und die Linux-spezifische Download-/Audiobedienung sind dadurch nicht automatisch live bestätigt.
- Abschließender Testumfang vor API-Kennungsanpassung: 31 Frontend- und 141 Backend-Tests bestanden. Anbieter ohne Keys und Linux-/Windows-10-Laufzeit bleiben ungetestet. Weitere Kombinationen fremder Modelle sind nicht pauschal validiert.

## Zeitliche Harmonieanalyse und Wiedergabekorrekturen

- Harmoniepipeline v2: verstimmungskorrigiertes harmonisches CQT, empirische Krumhansl-Kessler-Tonartprofile, lokale Tonartkandidaten und Halbsekunden-Akkordraster mit Sept-, verminderten, übermäßigen und sus-Vorlagen. Stufen und V–I-Kandidaten bleiben unsichere Schätzungen. Ein selbst erzeugtes I–vi–IV–V7–I-Signal wird korrekt erkannt; dies belegt keine allgemeine Transkriptionsgenauigkeit für gemischte Musik.
- Musikalische Messwerte im Fünfsekundenraster und Tempo aus Beat-Zeitpunkten. Minor-Septakkorde erhalten korrekt einen Mollbeitrag. Endvalenz umfasst begrenzte Merkmalsbeiträge und eine explizite zeitliche Glättung; alle Zwischenergebnisse bleiben einsehbar. Neue Cacheversion; bestehende Analysen werden nicht stillschweigend überschrieben.
- Gesamt- und Positionsdeutung besitzen getrennte Wiederherstellungsschlüssel. Ein geänderter Cache-Ladestatus löst keine erneute Inferenz aus. Cachelöschung entfernt beide Varianten. Textprompts verlangen zeitbezogene Zeilenbelege und Alternativdeutungen.
- Stimmungskurve per Pointer ziehbar, Tastaturnavigation und mit der Playerleiste geteilte A/B-Marker. Lyrics scrollen nur im eigenen Bereich; manuelles Scrollen pausiert das Folgen. Kontinuierliche Farbinterpolation, ruhigere Übergänge und gleichmäßigere Bedienabstände; Aufnahmeauswahl als gestaltetes Dropdown.
- Hörstudio: kleine Taktabweichungen lösen keine wiederholten Decoder-Seeks mehr aus. Harte Korrekturen nur bei großen Abweichungen, bereiten Quellen und mit Zeitabstand; explizites Springen bleibt unmittelbar. Puffern des Originals pausiert die Hörspuren. Erneuter Songimport setzt A/B-Marker auch bei gleicher Song-ID zurück.
- Validierung: 145 Backend-Tests bestanden. Frontend: 32 Tests bestanden, anschließend drei neue Tests für Ziehen, Visualisierungsinterpolation und gemeinsame Marker bestanden. Produktionsbuild bestanden. Der gemeldete YouTube-Stream wurde geladen; die neue Wiedergabekorrektur ist bisher durch Transport-Regressionstests, noch nicht durch einen erneuten langen Hörtest dieses Songs nachgewiesen. Native Speichern-unter-Auswahl ist der nächste offene Exportpunkt. Linux- und Windows-10-Laufzeit bleiben ungetestet.

## WAV-Zielauswahl

- Nativer Speichern-unter-Dialog für Hörspuren und neue Mixe, mit Song-/Quellennamen. Die Renderer-Schnittstelle akzeptiert ausschließlich verwaltete Track-IDs, erlaubte Modelle und Quellen sowie begrenzte Pegel; Host und Downloadpfad sind fest auf den lokalen Dienst beschränkt. Keine Redirects oder System-Proxys. Vorhandene Zieldateien werden erst nach vollständigem, formatgeprüftem Transfer atomar ersetzt.
- Browser mit File System Access API wählen das Ziel vor dem Download. Andere Browser verwenden ihre Download-Einstellung und den vorgeschlagenen Namen. Abbruch wird ohne Fehlermeldung behandelt; Transferfehler bleiben sichtbar.
- Drei Browser-Exporttests für Zielauswahl/Reihenfolge, Abbruch und Transferfehler bestanden; zwei native Rust-Tests für die enge URL-Parameterprüfung und sichere Dateinamenvorschläge bestanden. Backend-Exporttest bestätigt benannte WAV-Anhänge, Pegel und Range-Zugriffe. Windows-Release kompilierbar; der native Betriebssystemdialog wurde noch nicht live bedient. Kein Linux-Laufzeitnachweis.
- Frontend-Gesamtlauf: 37 Fälle bestanden, ein Textselektor war nach ergänzter Unsicherheitserklärung mehrdeutig; anschließend korrigiert und gezielt zusammen mit den Exporttests bestanden. Kein fehlgeschlagener Verhaltenstest bleibt offen.

- Nachprüfung im Hintergrund-Browser mit der gemeldeten, zuvor importierten Aufnahme: Original und alle vier tatsächlichen Quellen liefen von 0 bis 81 Sekunden monoton weiter, zuletzt etwa 26 ms gegeneinander versetzt, ohne beobachteten Zwei-Sekunden-Rücksprung oder Konsolenfehler. Pause stoppte alle fünf Media-Elemente. Dies ersetzt keinen Test aller Puffer-/Hardwarekonstellationen. Einstellungen in Englisch geprüft; ausgerichtete Formularfelder und kein horizontaler Seitenüberlauf bei 1280 px.
- Export-Fallback ohne Dateiauswahl zusätzlich geprüft: benannter Blob-Download und Freigabe der temporären URL. Alle vier Exporttests bestanden. Aktualisierter OSV-Abgleich: 414 Rust-Pakete, dieselben zwei bekannten GTK/Linux-Befunde, keine neuen Meldungen.

## Fließende Bedienung, Prompt-Vorlagen und Gerätewahl

- Detailbereich bleibt bei Wiedergabe gemountet. Zwischenwerte der Scores werden nur für die Visualisierung interpoliert; der gespeicherte Rechenweg bleibt getrennt. Abschnittsauswahl wird während der Bedienung eingefroren und nach Auswahl/Blur wieder synchronisiert. Methode beschreibt CLAP-Rohwert, musikalische Korrektur und zeitliche Glättung; alte Caches ohne Beiträge erhalten einen Neuanalysehinweis.
- Einheitlicher 24-Pixel-Rhythmus für Inhaltsblöcke, gleich hohe Feld-/Aktionszeilen und eigene, auch per Fokus erreichbare Tooltips. Lyrics und Akkordfolge verwenden einen begrenzten animierten Scrollbereich statt Dokument-Scroll; manuelles Scrollen pausiert das Folgen.
- Lokale Prompt-Vorlagen für Audio-/Instrumentbeschreibungen und Gesamt-/Zeilendeutung in Deutsch und Englisch. Validierte feste Beschreibungsreihenfolge, explizite Aktivierung, Reset und Löschung. Neue Audio-/Instrument-/Deutungs-Cacheschlüssel berücksichtigen den relevanten aktiven Prompt; alte Ergebnisse werden erhalten. Keine Bearbeitung der festen Faktengrenzen, kein Prompt für den XLM-EMO-Klassifikator.
- Gerätewahl pro Aufgabe: CPU, Automatik oder verfügbare CUDA-Indizes. Einstellung ändert keine vorhandenen Caches. Modelle werden vor Gerätewechsel entladen; laufende Aufträge sperren Änderungen. Whisper reicht den GPU-Index an CTranslate2 weiter. Nicht vorhandene explizite Geräte erzeugen einen Fehler.
- Validierung: bisheriger Backend-Gesamtlauf mit 145 Fällen bestanden; anschließend fünf neue Prompt-/Gerätetests bestanden. Frontend-Gesamtlauf mit 42 erfolgreichen Fällen und einem nach neuem Akkord-Folgeknopf veralteten Positionsselektor; der Selektor wurde präzisiert und der Fall bestand anschließend. Die vier neuen UI-Fälle prüfen durchgängige Balken/Dropdown-DOM, Tastatur-Tooltip, Vorlagenaktivierung/Reset und getrennte Gerätewahl. Produktionsbuild bestanden. Native Neubündelung und Hintergrund-Bedienprüfung stehen für diesen Zwischenstand noch aus.

## Gemeinsame Kopfzeile und laufende Bedienprüfung

- Lokal/API-Schalter in allen Hauptbereichen; passende Modell-/Serveransichten und Prompt-Zwecke. Moduswechsel lädt den passenden gespeicherten Analysemodus oder zeigt fehlenden Cache, ohne Inferenz anzustoßen. Haftende, transparente Kopfzeile mit kompakter Scrollform und Expansion bei Hover/Fokus.
- Status links unten nutzt Geräte-/Modellangaben des Dienstes und zeigt eine ausgewählte Textserver-Deutung gesondert. Gerätewechsel aktualisiert die Anzeige. Eigene Prompt-Löschung bleibt sichtbar, Standardvorlagen sind geschützt.
- Tooltip bei Mausbedienung am Cursor, bei Tastaturfokus am Element; Shift+F10-Zusage entfernt, A/B-Schaltfläche bleibt per Tab/Enter bedienbar. Weichere transformbasierte Detailbalken. Ältere Merkmalsanalysen behaupten keine erst später hinzugefügte zeitliche Glättung.
- Hintergrundprüfung: Prompt gespeichert, aktiviert und auf Standard zurückgesetzt; eigene Vorlage blieb erhalten. CPU und RTX-GPU über UI getrennt gewählt und nach Neuladen wiederhergestellt. Abschnittsmenü blieb bei mehr als 23 Sekunden laufender Musik geöffnet. Separater echter CUDA-Kernel bestätigte RTX 5070 und CPU/GPU-Aufgabenzuordnung.
- Frontend: 44 von 45 Fällen im Gesamtlauf erfolgreich; dabei fehlende Anbindung der API-Modellbezeichnung gefunden und korrigiert. Anschließend alle 19 betroffenen App-/Interaktionsfälle bestanden, Produktionsbuild bestanden. Neuer vollständiger Backend-Lauf und abschließende Scroll-/Layoutprüfung werden für den Abschlussstand ergänzt. Maximierter Start und Songtitel-Kürzel folgen als zuletzt angeforderter Nachtrag.
- GitHub-Dateibaum des Zwischenstands vollständig mit lokalem Commit verglichen; lokale Branch anschließend an den identischen veröffentlichten Commit angebunden. Dadurch zeigt Git keine nur durch Connector-Metadaten abweichenden ausstehenden Commits mehr an.

- Abschließender Backend-Gesamtlauf dieses Stands: 150 Tests bestanden (CPU für Unit-Tests erzwungen; reale CUDA-Aufgabenzuordnung separat geprüft). Der zuvor eingeschränkt gestartete Lauf wurde ohne Ergebnis abgebrochen und wird nicht als bestanden gezählt.

## Schlanke matte Kopfzeile und nativer Abschluss

- Kopfzeile auf feste Zeilen reduziert: Modus/Sprache/App-Steuerung sowie Song-Aktionen/Linkimport. Alle vier Song-Steuerelemente bei 1280 px auf derselben Oberkante mit 38 px Höhe; gesamte Leiste etwa 105 px, ohne horizontalen Seitenüberlauf. Große Überschrift und Song-Reiter scrollen regulär mit. Keine geometrische Auf-/Zu-Animation mehr.
- Matte Glasfläche mit geringer Farbsättigung, subtilen Konturen und Blur. Die aktive Atmosphäre färbt die Kopfzeile über dieselben Mood-Variablen; eine schwache Lichtmodulation läuft nur bei Wiedergabe. Reduced Motion schaltet sie ab.
- Native Konfiguration startet maximiert im normalen Fensterrahmen, F11 bleibt separat. Songkarte und Player leiten ihre Kürzel vom Titel ab, mit Dateinamen-Fallback und Unicode-Unterstützung.
- Launcher und PowerShell-Desktopstart erkennen zusätzlich versionierte native Builds. Damit kann eine gerade laufende, unter Windows gesperrte EXE erhalten bleiben; ein frisch gelinkter Build wird separat bereitgestellt und beim Neustart gewählt. Ein Regressionstest bestätigt die Auswahl des neueren Artefakts.
- Abschlussprüfungen: alle 46 Frontend-Tests bestanden, TypeScript-/Produktionsbuild bestanden, acht Launcher-Tests bestanden. Vorheriger vollständiger Backend-Lauf: 150 Tests bestanden; der neue Launcherfall kam danach hinzu. Echte Textnachführung nach Sprung auf Zeile 41: aktive Zeile sichtbar und ungefähr vier Pixel von der Zielmitte; aktive Akkordstelle ebenfalls sichtbar im eigenen Scrollbereich. Kein erneuter Modell- oder Musikdownload für diese Nachprüfung.


## Abschließende Bedienungs- und Cache-Regressionen

- Die spätere Headerfassung ersetzt den statischen Zwischenstand: große Überschrift vor der Bedienleiste am Seitenanfang; kontinuierliches Verblassen beim Scrollen, natürliches Anheften der Leiste. Ohne Kontur, mit leicht gerundeter Unterkante und transparentem Auslauf. Dialoge sowie Fehler liegen als Body-Portale über dem Header. Alle sechs relativen Emotionsanteile mischen die Atmosphärenfarben in OKLab und gewichteten Nebelflächen; die bisherigen Bewegungstakte bleiben erhalten.
- Im Programm reproduziert und korrigiert: manuelle Hörhilfe suchte nach htdemucs-Spuren, obwohl htdemucs_auto getrennt worden war. Gemeinsame Modellwahl und nur tatsächlich verfügbare Quellen; bei Wechsel zunächst Originalmix. Gesangsfokus anschließend auf einer vollständigen Testaufnahme erfolgreich erzeugt. Live-Mix mit vier Quellen rund 50 Sekunden beobachtet, Zeitabweichung etwa zehn Millisekunden, ohne unbeabsichtigte Wiederholung.
- Cache-Zyklus in isolierter Testbibliothek über die Oberfläche geprüft: Analyse löschen, Song öffnen, leere Stimmungsgrafik ohne automatische Neuanalyse, getrennte Audiospuren weiterhin verfügbar. Backend bestätigt fehlende Analyse/Deutung und leere Recherche. UI invalidiert nur betroffene Songs, einschließlich geladener Details und Instrumenthinweise. Alte unzugeordnete Recherche-/Deutungsschlüssel werden über Songnamensräume beziehungsweise identische gespeicherte Deutungspointer einbezogen. Eigene Notizen und Originaldateien bleiben erhalten.
- Rechercheantworten prüfen vor dem Schreiben in einer SQLite-Schreibtransaktion die Cachegeneration. Laufende Antworten dürfen nach Cache- oder Songlöschung keine Geistereinträge erzeugen. Regressionstests prüfen beide Fälle. Vor vollständiger Songlöschung werden Live-Audiokanäle synchron freigegeben.
- Dienstneustart mit offenem Player im isolierten Programm erfolgreich bis zum wieder bereiten Dienst geprüft. Bestätigtes Erzwingen wird unabhängig von Analysejobs weitergereicht. Regulärer Shutdown erhält einen zeitlich begrenzten Abschluss.
- Vollständiger Backend-Lauf: 155 Tests bestanden. Vollständiger Frontend-Lauf: 52 Tests bestanden. TypeScript-/Produktionsbuild bestanden. Aktualisierter nativer Windows-Releasebuild erfolgreich, maximierte Fensterkonfiguration geprüft. Promptvorlage im Programm gespeichert, aktiviert und entfernt; Standard wieder aktiv. Lokaler/API-Modus und englische Oberfläche geprüft.
- Bereits in dieser Arbeitsrunde echte Inferenz auf MP3-/FLAC-Testausschnitten und vollständigem SoundCloud-Import ausgeführt; vorhandene Integrationsergebnisse für Whisper, CLAP, Harmonie, Interpretation und vier Demucs-Spuren erneut gesichtet statt kostspielige identische Modellläufe zu wiederholen. Der YouTube-Loopfall wurde zuvor mit echten Quellen über längere Wiedergabe geprüft. Automatisierte Fälle decken Loopmarkierungen, Export, Provider-Zustimmung, eigene Modelle, Abbruch, Geräte, Notizen und Bibliothekslöschung ab.
- Erneuter echter Katalogtest: MusicBrainz, Apple und Deezer erreichbar, zusammen 24 Kandidaten. Die geprüfte MusicBrainz-Aufnahme lieferte keine Instrumentcredits; die App darf daraus keine Besetzung erfinden. Externe kostenpflichtige/Schlüssel-APIs ohne Zugangsdaten, Linux-Laufzeit und der interaktive native Speichern-Dialog sind weiterhin nicht live validiert. Bestehende Sicherheitsbefunde in SECURITY.md bleiben ausgewiesen; keine Zusage vollständiger Fehlerfreiheit.


## Automatische Analyse beim Öffnen ohne Cache

- Bibliotheksöffnung verwendet wieder denselben Ablauf wie der Import: vorhandene Analyse laden oder bei fehlendem Cache automatisch Lyrics suchen und analysieren. Die Verlaufsansicht wird bereits beim Öffnen angezeigt, damit der laufende Auftrag sichtbar bleibt. Cache-Löschen selbst startet keinen Auftrag.
- Der Cache-Zyklus-Test erwartet jetzt genau einen neuen Analyseauftrag nach dem erneuten Öffnen sowie die automatische Recherche und Lyrics-Suche. Die oben protokollierte Zwischenfassung ohne automatische Neuanalyse ist damit ersetzt.
- Validierung: alle 52 Frontend-Tests sowie TypeScript- und Produktionsbuild bestanden. Der Test nutzt kontrollierte Antworten; ein weiterer kostspieliger Modelllauf war für diese Änderung am Auslöser nicht erforderlich.


## Einstellungen am oberen Fensterrand

- Gemeinsame Einstellungszeile steht vor der großen Überschrift am oberen Rand. Überschrift und Songaktionen behalten ihre natürliche Dokumentgeometrie; die Songaktionen gleiten beim Scrollen unter die oben bleibenden Einstellungen. Matte Einfärbung folgt kontinuierlich dem vorhandenen Scrollfortschritt. Keine zweite Kopie der Bedienelemente, kein Umbau der Dokumenthöhe.
- Hintergrund-Bedienprüfung: am Seitenanfang Einstellungszeile bei 0 px, Titel bei 54 px; während des Scrollens kontinuierliches Verblassen des Titels; kompakt bleiben Einstellungen bei 0 px und Songaktionen bei rund 54 px. Kein horizontaler Überlauf. Alle 52 Frontend-Tests sowie TypeScript-/Produktionsbuild bestanden.


## Kräftigere Atmosphärenfarben

- Farbtöne, relative Emotionsgewichte und Übergangszeiten bleiben unverändert. Hintergrund-Farbanteile von 12/9 auf 16/12 Prozent erhöht, Nebeldeckkraft moderat angehoben und Sättigung der rein dekorativen Nebel auf 1,2 gesetzt. Panels, Player und Header erhalten entsprechend etwas mehr Farbanteil, ohne Text und Bedienelemente zu filtern.
- Untere Header-Ecken von 12 auf 28 Pixel verstärkt, bei schmaler Ansicht 20 Pixel. Fade, matte Oberfläche und Scrollgeometrie bleiben erhalten. Hintergrundprüfung der Nebelebene bestätigt die erhöhte Deckkraft und Sättigung bei unveränderten Bewegungszeiten.


## Weiter auslaufender Header-Fade

- Matte Headerfläche läuft am Seitenanfang über 96 statt 24 Pixel mit mehreren weichen Deckkraftstufen aus. Beim Scrollen verkürzt sich die Strecke kontinuierlich auf 44 Pixel im kompakten Zustand. Maskiert wird ausschließlich die dekorative Glasfläche; Texte und Steuerelemente behalten ihre Deckkraft und Geometrie.


## Farbflächen statt grauer Deckflächen

- Die frühere Verwendung dunkler farbiger und transparenter Oberflächen wieder aufgenommen. Relative OKLCH-Farben leiten aus den weiterhin gemischten Emotionsfarben dunkle Hintergrund- und Paneltöne mit sichtbarer Chroma ab. Panels mit 78/80 Prozent Deckkraft lassen die Atmosphäre durchscheinen; Sidebar, Player und Header verwenden dieselben Farbflächen. Text und Bedienelemente werden nicht über einen globalen Filter verändert.
- Farbpalette, Emotionsgewichte und Bewegungszeiten unverändert; nur dekorative Farbstärke und Nebelsättigung erhöht. Relative Farbfunktionen sind durch eine Feature-Abfrage abgesichert, ältere Renderer behalten die bestehende Darstellung.
- Validierung: TypeScript-/Produktionsbuild bestanden. Hintergrund-Bedienprüfung mit vorhandener echter Songanalyse und ohne zusätzliche Modellinferenz: farbige Panelverläufe im Renderer wirksam, Text und Kurven lesbar, kein horizontaler Überlauf. Kein neuer Backend-Testlauf für diese reine Darstellungsänderung.


## Sechs-Spur-Blockade und Playerwechsel

- Fehler mit einer isolierten Kopie vorhandener Bibliotheksdaten reproduziert: Originalstream plus sechs Stem-Streams überschritten den Browser-Verbindungspool. Fünf Decoder liefen, der sechste blieb bei readyState 0; zusätzliche Bibliotheksanfragen blieben ebenfalls hängen. Die echten Audiodateien und Manifeste waren vorhanden und hatten passende Laufzeiten.
- Live-Wiedergabe verwendet nun einen lokal erzeugten stummen PCM-Takt, damit der Originalstream keinen siebten Medienkanal belegt. Der Takt enthält keine Musik oder Analysewerte, belegt höchstens 14,4 MB und wird beim Verlassen freigegeben. JSON-Steueranfragen verwenden den anderen Loopback-Namen; CORS erlaubt dessen Browser-Origin ausschließlich auf demselben Port. Fremde Origins, andere Ports und zusätzliche Preflight-Header bleiben gesperrt. Native CSP erlaubt dafür genau den zusätzlichen lokalen Steuerursprung.
- Playerwechsel beendet Decoder synchron, verwirft alte Play-Ergebnisse und erzeugt pro Songöffnung einen neuen Master. Lautstärke bleibt erhalten. Play/Pause prüft den tatsächlichen Medienzustand. Gleichbleibende Quellen erzeugen keinen liegengebliebenen Wiederherstellungsauftrag. Quellenfehler oder 20 Sekunden Startzeitlimit stellen den Originalmix wieder her; Abbruch während des Startens lässt sich unmittelbar wieder starten. Auch teilweise fehlgeschlagene Audiograph-Erzeugung räumt ihre Ressourcen auf.
- Vorhandene Trennungen werden ohne erneuten Job geladen und mit einer verständlichen Meldung bestätigt.
- Prüfergebnis dieses Zwischenstands: 60 Frontend- und 156 Backend-Tests bestanden, TypeScript-/Produktionsbuild bestanden. Im Programm alle sechs Decoder mit readyState 4 beobachtet, laufende Bibliotheksabfrage bedienbar, Wechsel zu zweitem Song und WAV-Wiederimport mit vorhandener echter Analyse ohne Freeze. Originaldatenbank und Originalmusik blieben unberührt; importierter Test-WAV ist eine Kopie derselben Aufnahme. Im erweiterten Importtest wurde zusätzlich ein automatischer Analyseauftrag erfolgreich abgeschlossen; die Wiedergabeprüfungen verwendeten vorhandene echte Spuren und Analysen. Nativer Releasebuild folgt nach Abschluss der weiteren Importvariantenprüfung.


## Abschluss: Importvarianten, Hörfokus und Export

- Hörstudio löst bestätigte Importvarianten auf vorhandene Spuren der zugehörigen Aufnahme auf. Bereits vorhandene eigene Trennungen älterer Varianten haben Vorrang und bleiben nutzbar. Status, Quellenmix, Sichtbarkeit, Trennauftrag und manueller Fokus verwenden denselben Speicherort. Fokusdateien älterer Varianten bleiben weiterhin abrufbar.
- Neue API-Regressionen prüfen gemeinsame und separat gespeicherte Trennungen, Sichtbarkeit, erneuten Abruf ohne neue Inferenz, echten Hörfilter und dessen Audioabruf. Dabei entdeckter Mono-Fehler im Hörfilter behoben: vor dem Stereo-/Frequenzfilter werden einkanalige Quellen dupliziert. Eigenständiger Signaltest bestätigt beide Kanäle und einen nicht stummen Filterausgang.
- Browserexport nutzt ebenfalls den separaten lokalen Steuerursprung, damit die sechs Medienverbindungen den Exportabruf nicht blockieren. Regressionstest prüft diese Trennung und weiterhin Dateiauswahl vor Download.
- Abschließende Validierung: 159 Backend- und 60 Frontend-Tests bestanden, TypeScript-/Produktionsbuild bestanden. Nativer Windows-Releasebuild erfolgreich bereitgestellt. In der Oberfläche Importvariante mit vorhandenen sechs Quellen geladen; nach rund 55 Sekunden alle Decoder bereit und höchstens ungefähr 20 Millisekunden von der Masterzeit entfernt. Bibliothek währenddessen bedienbar. Vollständiger WAV-Export mit sechs Quellen und individuellen Pegeln geprüft: 44,1 kHz, zwei Kanäle und passende vollständige Laufzeit. Danach Originalmix wiederhergestellt und über den normalen Player pausiert. Testeingabedatei per Prüfsumme unverändert.
- Die interaktive native Dateiauswahl, externe KI-APIs ohne Zugangsdaten und Linux wurden in dieser Runde nicht live bedient. Die dokumentierten früheren Einschränkungen bleiben bestehen; ein vollständiger Ausschluss aller Fehler wird nicht behauptet.

## Kontrollierte Diagnose der musikalischen Emotionsanalyse

- Separates Offline-Werkzeug `scripts.audio_evaluation` und ein [Bewertungskonzept](AUDIO-EVALUATION.md) ergänzt. Produktive Analyse, Wiedergabe, API, Cacheformate und gespeicherte Einstellungen sind unverändert. Ein vorläufiger Produktentwurf wurde vor dieser Diagnose vollständig aus dem Produktcode zurückgenommen.
- Das Werkzeug vergleicht die unveränderten CLAP-Prompts mit einer gezielten Wortlautvariation, parallelen Formulierungen, einer ausdrücklich explorativen Ausdrucksliste und unabhängigen dimensionalen Abfragen. Einzelprompt-Logits und Kosinusähnlichkeiten, Pegelkontrollen, Laufzeiten und Torch-Speicher bleiben ausschließlich in privaten Testausgaben. Kein pauschaler Ärger-Abzug und keine automatische Auswahl eines vermeintlich besseren Modells.
- Reale Offline-Diagnose mit vorhandenem CLAP-Snapshot auf einem anonymisierten Satz von 16 Zehnsekunden-Ausschnitten aus acht Aufnahmegruppen ausgeführt. Originalpegel, Absenkung und konstanter Analysepegel wurden verglichen. Ein zusätzlicher Blindhör-Pilot enthält 24 Ausschnitte aus zwölf anderen Aufnahmegruppen, mit getrenntem Entwicklungs- und noch nicht ausgewertetem Holdout-Teil. Die Abdeckung gewünschter emotionaler Gruppen ist noch durch Menschen zu prüfen. Private Quellen und Ergebnisse werden nicht versioniert.
- Es liegen keine unabhängigen menschlichen Bewertungen vor. Geringere Ärgeranteile, veränderte Kategorien und robustere technische Pegelkontrollen werden daher ausdrücklich nicht als nachgewiesen bessere Emotionserkennung ausgegeben. Mehrdimensionaler Produktvertrag, Kalibrierung, zusätzliche Modelle und UI-Änderungen stehen vor einer gesonderten Freigabe.
- Validierung: 26 neue Diagnosetests bestanden; 24 vorhandene gezielte Regressionen für Audioverfahren, Harmonie, Interpretation, Prompts und Geräte bestanden. Nach den letzten Ergänzungen wurden die 26 Diagnosetests erneut vollständig geprüft. Der erste kombinierte Sandbox-Lauf hing im Windows-Testclient bei der lokalen socketpair-Erzeugung; Stacktrace bestätigte den Umgebungsblocker. Die gezielten Regressionen bestanden anschließend außerhalb dieser Sandbox mit isoliertem Testdatenordner. Kein neuer vollständiger Backend-/Frontend-Lauf und kein nativer Build für diese reine Werkzeug-/Dokumentationsänderung.
- Originalquellen wurden vor und nach den tatsächlichen Diagnoseläufen per SHA256 verglichen. Die App-Datenbank wird vom Werkzeug nicht geöffnet; Ergebnisse und Hörkopien entstehen nur in neuen ignorierten Testordnern. Keine Downloads, Systeminstallationen oder Veröffentlichung.

## Externe menschliche Referenzen und Musikbelege

- Erste Integrationsstufe nach Freigabe: optionale Musik-/Textdeutung mit versioniertem Musikbelegpaket, getrennt von bestehender Textdeutung gespeichert. API-Revision 11 gemeinsam in Backend, Oberfläche und Startern gepflegt. Die Audio-Emotionspipeline und vorhandene Analysewerte bleiben unverändert. Details und Grenzen: [menschliche Referenzen](HUMAN-REFERENCE.md).
- Emotify-Einzelantworten und 32 zugehörige öffentliche Einminutenbeispiele aus vier Genres für einen lokalen Vergleich geladen. Demografische Spalten und Vorabstimmungen werden nicht verwendet. Nur ausgewählte Audiomember per begrenztem HTTP-Teilabruf geladen, CRC und Dateihashes geprüft. Globale Bewertungs-IDs werden ausdrücklich auf genrelokale Archiv-IDs abgebildet; Regression prüft diese fehleranfällige Zuordnung. Antworten oberhalb der dokumentierten maximalen drei Kategorien werden ausgeschlossen und gezählt.
- Das Offline-Werkzeug vergleicht Originalprompts, datensatznahe GEMS-Beschreibungen, unabhängige Ähnlichkeiten und Softmax bei Original- und kontrolliertem Analysepegel. Ausgelöste Gefühle werden nicht als wahrgenommener Ausdruck umgedeutet. Es wurde kein neuer Klassifikator trainiert. Ergebnisse bleiben privat; eine allgemein bessere Emotionserkennung wird nicht behauptet. Die offizielle DEAM-Quelle war nicht abrufbar.
- Musikbelege unterscheiden Messung, Modellschätzung und Kandidat. Globale Energieentwicklung verwendet tatsächliche stärkere/schwächere Messabschnitte statt des trivialen Nullabstands zum eigenen Songmittel. Lokale Merkmale tragen ihre tatsächlichen zugrunde liegenden Zeitfenster. Hohe Energie legt keine Emotion fest. Lokale Tonartbelege stammen aus der passenden Region; fehlende lokale Schätzungen werden nicht als globale Ersatztonart ausgegeben. Akkordbeispiele verteilen sich über die ganze Auswahl und zeigen die Teilabdeckung.
- Im optionalen Musikvergleich erhält das Sprachmodell kompakte referenzierte Musikbeobachtungen und zeitmarkierte Textbelege, keine persönlichen Notizen oder unsicheren Instrumentbesetzungen. Die sechs Kategorien werden nicht ungeprüft zur Textdeutung vorgegeben. Exakte Musikangaben werden separat deterministisch angezeigt. Fehlende/ungültige M-Referenzen, bestimmte unbelegte Audioaussagen und beobachtete fremdsprachige Schriftwechsel werden verworfen. Das ist keine vollständige semantische Belegprüfung.
- Tatsächlicher Offline-Vergleich mit vorhandenem Qwen 1.5B: vereinfachte Darstellung ermöglichte eine referenzierte Ausgabe, weitere Versuche zeigten dennoch unplausible Verknüpfungen und Regelverletzungen. Verworfene Antworten wurden nicht in der Bibliothek gespeichert. Die neue Option ist deshalb ausdrücklich experimentell und zunächst ausgeschaltet; es gibt keinen automatischen Cloudersatz oder größeren Modelldownload. Tests verwendeten isolierte Daten; der direkte Modellvergleich las ausschließlich einen vorhandenen Analyse-Snapshot und schrieb nur private Testausgaben.
- Abschließende automatisierte Validierung: 198 Backend-Tests, 62 Frontend-Tests und TypeScript-/Produktionsbuild bestanden. Cache-Trennung, gemeinsames Löschen, lokale Zeitfenster, Promptübergabe, Quellen-ID-Prüfung und vorhandene Wiedergabe-/Hörstudiofälle sind abgedeckt. Keine neue interaktive native Bedienprüfung, kein externer KI-Anbieter und kein Linux-Lauf ausgeführt. Nativer Windows-Releasebuild mit eingebettetem aktuellem Frontend erfolgreich bereitgestellt; maximierter Start bleibt konfiguriert.
- Neue UI verwendet bestehende Klassen und Designflächen; keine Änderung an Farben, Atmosphäre, Header, Player oder der Reihenfolge der Hauptbereiche. Veröffentlichung bleibt auf ausdrücklichen Wunsch ausgesetzt; Fortschritte werden nur lokal auf dem separaten Branch gesichert.


## Emotionskurve v7 und Vergleich vorhandener Musikmodelle

- Auf erneuten Auftrag wird die Emotionskurve priorisiert und die GitHub-Sicherung wieder aufgenommen. Der zuvor nur lokale Stand wurde nach Index- und vollstaendiger erreichbarer Historienpruefung auf den bestehenden Arbeitsbranch veroeffentlicht.
- Neue lokale Pipelinekennung v7: konstanter Analysepegel je Audiokontext (-20 dBFS RMS, Spitzenobergrenze 0,99); Original-RMS bleibt gespeichert. Kein Eingriff in Originaldateien oder Wiedergabe. Die getestete Pegelkontrolle reduziert einen technischen Stoereinfluss, beweist aber keine semantische Genauigkeit.
- Untrainierte Valenzzuschlaege fuer Tempo, Helligkeit, Dur/Moll und Aufloesung sowie die nachtraegliche Dreipunktglaettung entfallen fuer neue Analysen. Die ueberlappenden CLAP-Kontexte bleiben. Alte Methoden und Ergebnisse bleiben lesbar; neue Cacheversion verhindert ihre Umdeutung.
- Der Analysebericht zeigt die Valenzspannweite zweier Beschreibungsvarianten und deren Kategorie-Uebereinstimmung. Dies ist Formulierungssensitivitaet, kein Konfidenzintervall. Die sechs Kategorien und ihre unkalibrierten Valenzgewichte bleiben eine offene Einschraenkung.
- Validierung: 203 Backend-Tests, 62 Frontend-Tests und TypeScript-/Produktionsbuild bestanden. Backend-Testclient benoetigte wegen lokaler Windows-Sockets Ausfuehrung ausserhalb der Sandbox, mit isolierten Testdaten. Ein Offline-Lauf der echten neuen Pipeline wird separat ausgefuehrt; kein neuer nativer Build oder interaktiver Bediennachweis an diesem Checkpoint.
- Oeffentliche Alternativen werden anhand ihrer tatsaechlichen Inferenz geprueft: Music2Emo mittelt standardmaessig lange Aufnahmen, Moody nutzt Essentia-Modelle fuer Verlaeufe, AudioMuse bietet lokale ONNX-Inferenz. Noch kein spezialisiertes Ersatzmodell produktiv aktiviert und keine hoehere semantische Genauigkeit behauptet.

- Echter Offline-Produktionslauf auf dem festgelegten Diagnosesatz abgeschlossen: Original und -12-dB-Variante mit identischen vorhandenen CLAP-Gewichten, Quellpruefsummen unveraendert. Pegelstabilitaet wurde geprueft; fehlende menschliche Zeitreferenzen erlauben weiterhin keine Aussage zur Emotionsgenauigkeit. Detailausgaben bleiben im ignorierten Evaluationsordner.


## Wiederverwendbare Music2Emo-Vergleichsinferenz

- Spezialisierte oeffentliche Projekte und konkrete Wiederverwendungsgrenzen in [EMOTION-MODELS.md](EMOTION-MODELS.md) dokumentiert. Music2Emo mit freigegebenen Gewichten und isolierten Zusatzpaketen tatsaechlich lokal ausgefuehrt; keine Aenderung der aktiven Modellwahl.
- Offline-Adapter mit Quellstandpruefung der angepassten Stellen, Gewichtspruefsummen, lokalem Modellzugriff, getrennten Rohregressionen und unabhaengigen Tags ergaenzt. Ungueltige Ausgaben werden nicht als neutrale Emotion umgedeutet. Keine erfundenen sechs Kategorien aus den Mood-Tags.
- Ein-Zeitframe-Tensorfehler und uebergewichtete Decoderrestsegmente behandelt. Eine getrennte Option untersucht den im Upstream-Code verwechselten Tonikanamen und Dur/Moll-Modus. Ergebnisse dieser Varianten sind diagnostisch und keine nachgewiesene allgemeine Genauigkeit.
- Neuer Adapter real auf 16 Kontexten ausgefuehrt. 8 Adaptertests und 5 Pegelkontrolltests bestanden; die zuvor geprueften 203 Backend- und 62 Frontend-Tests bleiben der letzte komplette Produktcheck. Nativer Windows-Releasebuild der v7-Oberflaeche erfolgreich bereitgestellt. Keine neue interaktive Bedienpruefung.
- DEAM-Audio aus einem oeffentlichen Spiegel anhand einer vor Inferenz eingefrorenen Auswahl von 32 IDs des veroeffentlichten Testsplits geladen, nur mit begrenzten ZIP-Teilabrufen und CRC-Pruefung. Die Bewertungs-/Splitdateien stammen vom gepinnten Forschungsprojekt. Die offizielle Audioquelle bleibt nicht erreichbar. Der neue Kurvenvergleich laeuft getrennt; Ergebnisse und Quelleigenschaften werden nicht vorweggenommen.


## Optionaler Music2Emo-Zweitverlauf in der App

- Neuer Bereich unter Methode & Werte: explizit gestarteter Music2Emo-Vergleich mit getrennten Valenz-/Aktivierungswerten, unabhaengigen Tags, Zeitfensteranzeige und Positionsauswahl. Hauptanalyse, Atmosphaerenfarben und aktive Modelleinstellung bleiben bestehen.
- Eigener lokaler Worker verwendet die verifizierte Basisumgebung, auch bei einem Dienst in der neueren Transkriptionsumgebung. Vorher werden Audio-/Textklassifikatoren aus dem Speicher entladen. Fortschritt, Zeitlimit und Abbruch beenden den Worker kontrolliert; temporaere Kopien werden entfernt. Quell-/Gewichtspruefsummen werden vor Inferenz geprueft. Keine automatischen Downloads.
- Vergleichscache separat versioniert und mit Songbesitz verknuepft. Wiederanzeigen, erzwungene Neuberechnung, Methodenwechsel und gemeinsames Analyse-Cache-Loeschen getestet. API-Revision 12 in Backend, UI und Startern synchronisiert.
- Der vorab festgelegte DEAM-Vergleich umfasst 32 Aufnahmen aus dem veroeffentlichten Testsplit. Music2Emo zeigte bessere statische Songmittel als CLAP v7. Zeitgenaue menschliche Uebergangsreferenzen wurden nicht ausgewertet; allgemeine Genauigkeit und vollstaendige Trainingsdaten-Unabhaengigkeit bleiben unbelegt. Details und Lizenzgrenzen stehen in EMOTION-MODELS.md.
- Validierung: 215 Backend-Tests, 64 Frontend-Tests sowie TypeScript-/Produktionsbuild bestanden. Echter Workerprozess auf einem oeffentlichen Referenzausschnitt mit vollstaendiger Kurve erfolgreich; Aufraeumen der Scratch-Ordner bestaetigt. Windows-Releasebuild erfolgreich bereitgestellt. Keine neue interaktive native Bedienpruefung und kein Linux-Lauf. Der erneute echte Workercheck nach der abschliessenden Geraeteauswahlkorrektur und 20 betroffene Regressionstests bestanden ebenfalls.


## Dynamische Referenzpruefung und Open-Source-Vorbereitung

- MIT-Lizenz fuer eigenen Code nach ausdruecklicher Auswahl ergaenzt. Fremde Gewichte und Daten bleiben ihren eigenen Bedingungen unterstellt. Die Publikationspruefung erlaubt gezielt die neue LICENSE-Datei.
- Weitere vorgeschlagene Projekte anhand ihrer README und Anbieterbeschreibung eingeordnet; insbesondere genrebasierte Ersatzlabels und rein akustische Heuristiken nicht als bessere menschliche Emotionserkennung uebernommen.
- Neuer Offline-Evaluator fuer dynamische DEAM-Annotationen: echte CSV-Zeitstempel, keine erfundenen ersten 15 Sekunden, explizite Aktivierungsskala, Abdeckung, absolute und innerhalb der Songs zentrierte Fehler sowie konstanter Kontrollverlauf. Bereits vorhandene 32 Referenzkurven ausgewertet. Zeitliche Praezision bleibt unbelegt; keine Gewichte anhand einzelner Nutzerbeispiele angepasst.
- Im Analysebericht stimmen nun Prozentbalken und Formel auch zwischen Messpunkten ueberein. Der Bericht zeigt gespeicherte Abschnittswerte und erklaert den moeglichen Fehlschluss von rauem Klang ueber Aerger-Aehnlichkeit zu negativer Valenz. Die Playerkurve bleibt interpoliert.
- Music2Emo berechnet exakt identische Audiokontexte am Rand nur einmal pro Lauf; alle Anzeigeintervalle und Fortschrittsmeldungen bleiben erhalten. Nichtendliche Eingaben werden abgewiesen.
- Validierung: 222 Backend-Tests, 65 Frontend-Tests und Produktionsbuild bestanden. Ein vorhandener Frontend-Test wurde auf die bewusst geaenderte Berichtssemantik angepasst. Echter lokaler Worker mit zehn Ergebnisabschnitten und bestaetigter Scratch-Bereinigung erfolgreich. Frisch verlinkter nativer Windows-Build wegen gesperrter laufender EXE ueber den bestehenden alternativen Startpfad bereitgestellt. Keine neue interaktive native Bedienpruefung, kein frischer Linux-Lauf, kein Nachweis einer fertigen Installation auf einem sauberen Rechner.


## Kontextvergleich, psychologische Einordnung und Atmosphaerenfarben

- Echter Offline-Parametervergleich auf allen 32 vorhandenen DEAM-Diagnosestuecken mit 10 und 20 Sekunden Music2Emo-Kontext abgeschlossen. Kein stabiler zeitlicher Vorteil gegenueber 30 Sekunden; Standard nicht umgestellt. CLI mit Quellen-/Gewichtspruefung und getrennten Zwischenstaenden ergaenzt.
- Psychologische und neurowissenschaftliche Quellen in MUSIC-PSYCHOLOGY.md dokumentiert. Neue zweidimensionale Darstellung der gespeicherten Valenz und Aktivierung unter Methode & Werte; keine ausgedachten Neuroparameter oder Merkmalsboni. Fehlende Aktivierung erzeugt keinen erfundenen Messpunkt. Neue Texte auch auf Englisch.
- Atmosphaere: zentrale Grundfarbe aus Audiomischung mit stetigem Dominanzakzent; kleinere Anteile proportional als Unterfarben. Textfarbe beeinflusst sekundaere Flaechen nur schwach, ohne Textdaten folgt die Flaeche dem Audio. Fehlende/ungueltige Scores erhalten eine neutrale Farbe statt einer scheinbaren Gefuehlszuordnung.
- Validierung: 222 Backend-Tests, 69 Frontend-Tests und Produktionsbuild bestanden. Die neue Vorschau mit sechs synthetischen Mischungen war ueber den eingebauten Browser nicht erreichbar; keine visuelle Abnahme behauptet. Nativer Windows-Build erfolgreich fuer den naechsten Start bereitgestellt. Zwei zusaetzliche Tests fuer Parameterduplikate und manipulierte Modellquellen sowie die betroffenen Kontext-/Evaluator-Tests bestanden anschliessend.
- Zusaetzlicher kleiner MusiCNN/DEAM-ONNX-Kandidat anhand offizieller Schnittstellen und Vorverarbeitung untersucht. Der Gewichtsabruf antwortete in diesem Lauf nicht; kein neuer Modellvergleich oder erfolgreicher Download behauptet.


## Bestehende Hauptkurve, fließende Balken und vertiefte Gefuehlsrecherche

- Die zuvor eingefuehrte statische Abschnittsanzeige der Gefuehlsbalken war ein Animationsrueckschritt. Visuelle Interpolation wiederhergestellt, gespeicherte Rohwerte/Formel weiterhin getrennt dokumentiert. Tests pruefen Zwischenwerte sowie stabile DOM-Elemente bei laufender Wiedergabe.
- Music2Emo laesst sich jetzt unter der vorhandenen Audio-/Lyrics-Kurve als Audioquelle verwenden; die zusaetzliche Vergleichsgrafik und die zweidimensionale Grafik entfallen. Audio-Kennzahl, Kontrastmarkierung und Biggest Split verwenden denselben ausgewaehlten Verlauf. Die sechs CLAP-Anteile behalten ihre eigene Herkunft; keine erfundenen Music2Emo-Kategoriescores.
- Wahl wird lokal gespeichert. Nur passende aktuelle Vergleichscaches werden wieder aktiviert. Songwechsel, Cacheloeschen und spaet eintreffende Ergebnisse koennen keinen fremden Verlauf aktivieren. Statische Audio-Pfadgeometrie wird zwischen Wiedergabeframes wiederverwendet.
- Primaerforschung zu GEMS, kulturuebergreifenden Gefuehlsdimensionen, musikalischen Merkmalen sowie Text-/Musik-Wechselwirkung einschliesslich widersprechender Replikationsbefunde geprueft. Keine feste Audio-/Text-Mischformel aus einzelnen Studien abgeleitet. Quellen und Konsequenzen in MUSIC-PSYCHOLOGY.md ergaenzt.
- Echter neuer Deskriptorlauf auf 32 vorhandenen Emotify-Beispielen abgeschlossen. Ueberarbeitete musikspezifische Beschreibungen verbesserten einzelne Gefuehle, waren im Mittel aber nicht besser; keine ungepruefte Umstellung der produktiven Balken. Reproduktion im bestehenden Evaluator ueber --descriptor-profile revised. Referenzen messen ausgeloestes Gefuehl, keine wahrgenommene zeitliche Ausdruckskurve.
- Validierung: 74 Frontend-Tests und Produktionsbuild bestanden; neun betroffene Backend-Tests bestanden. Letzter kompletter Backendlauf umfasst 222 Tests, danach kamen zwei separat bestandene Parameter-/Pruefsummentests hinzu. Kein erneuter kompletter Backendlauf fuer diese UI-Aenderung. Neue App-Integrationstests pruefen tatsaechlichen Wechsel der bestehenden Kurve, Rueckwechsel, stale Cache und verspätete Ergebnisse. Kein neuer interaktiver nativer Bediennachweis; Nativer Windows-Releasebuild erfolgreich bereitgestellt.


## Zeitbezogene gemeinsame Einordnung und konsistente Musikquelle

- Gemeinsame Einordnung an der vorhandenen Hauptkurve ergaenzt; keine weitere Grafik. Musik-/Text-Kontrast, geringe Textabdeckung, markierte Erkennungsunsicherheit und instabile Audiotendenzen bleiben sichtbar. Ueberlappende Textintervalle koennen Abdeckung nicht kuenstlich erhoehen. Kein erfundener numerischer Gesamtscore oder psychologischer Merkmalsbonus.
- Kombinierte Interpretation verwendet nun die ausgewaehlte Music2Emo- oder bisherige Analysequelle. Getrennte Cachezuordnung und Stale-Pruefung verhindern unbemerkten Quellenwechsel. Neue Belegpakete enthalten konkrete zeitliche Beziehungen mit Textreferenzen und erhalten kurze Gegenbeispiele in Gesamtdeutungen. API-Revision 13 mit Oberflaeche und Startern synchronisiert.
- Validierung: 229 Backend-Tests und 76 Frontend-Tests sowie Produktionsbuild bestanden. Ein weiterer Test zum Erhalt kurzer Gegenbeispiele wurde anschliessend ergaenzt und wird vor Veroeffentlichung separat geprueft. Kein neuer nativer Bediennachweis.
- Qwen-3B-Download wurde ausdruecklich freigegeben; alternative bereits installierte Downloadlaufzeit wird wegen stagnierender erster Abrufe verwendet. Noch kein erfolgreicher Download oder Vergleich behauptet. MERGE und weitere multimodale Forschungsdaten auf Eignung und notwendige Nachweisgrenzen geprueft; noch keine gelernte Fusion auf diesen Daten ausgefuehrt.


## Gepruefte oeffentliche Ablage und private Zwischenstaende

- Oeffentliche Ablage aus der geprueften aktuellen Branchhistorie bereitgestellt. Aeltere CI-Inhalte der bisherigen privaten Ablage wurden nicht uebernommen. Lokale Arbeitsdateien und heruntergeladene Modelle sind weiterhin ausgeschlossen.
- Nach ausdruecklicher Workflowvorgabe werden Zwischenstaende zuerst privat gesichert. Oeffentliche Uebernahmen verwenden einen getrennten Commitverlauf aus dem geprueften Quellbaum, ohne private Zwischenstaende als Vorfahren. Git-Standardeinstellungen bleiben lokal; der Push-Hook prueft tatsaechlich gepushte Referenzen und blockiert private Zwischenstaende in der oeffentlichen Vorgeschichte. Sieben gezielte Publikations-/Workflowtests bestanden.

## Gelernte Musik-Tags fuer die vorhandenen Emotionsbalken

- Kurve und Balken verwenden bei Music2Emo dieselbe Quelle. Neun echte gelernte Musik-Tags ersetzen dann die unpassende Umrechnung in sechs CLAP-Richtungen. Rohscores bleiben unabhaengig; keine Darstellung als gemessene Gefuehlsprozente. Kraft und Energie erhalten eigene Hinweise und Gestaltungsfarben. Visuelle Interpolation bleibt bestehen.
- Eingerichtetes Music2Emo wird ohne ausdrueckliche CLAP-Wahl bevorzugt; fehlende aktuelle Vergleiche werden einmalig lokal berechnet. Kein automatischer Gewichtsdownload.
- 80 Frontend-Tests und Produktionsbuild bestanden. Vollstaendiger Backendlauf vor diesen UI-Anpassungen: 233 Tests bestanden. Sprachmodell erzeugt jetzt nur die Textlesart; Musikbeziehungen werden kontrolliert aus Belegen hinzugefuegt. Freier Musikvergleich mit dem kleinen Modell zeigte trotz bestandener formaler Guards unplausible kausale Aussagen. Der abgesicherte kleine Diagnoselauf bestand sieben statt zuvor fuenf von acht formalen Faellen; keine Genauigkeitsmessung menschlicher Gefuehle.
- Freigegebene Qwen-3B-Gewichte vollstaendig geladen und gegen die offiziellen SHA256-Pruefsummen geprueft. Aktive Modellwahl unveraendert. Weitere Bewertung konzentriert sich auf die Text-Emotionskurve, nicht auf zusaetzliche Grafiken. Ein kleiner menschlich bewerteter Lyrics-Datensatz wird lokal auf Eignung geprueft; keine Referenztexte oder Bewertungen werden publiziert.


## Gemeinsame Audioquelle und Abschnittsbalken

- Die Modellauswahl lebt jetzt unabhaengig vom sichtbaren Songbereich. Ein Ansichtswechsel unterbricht weder das Laden eines aktuellen Music2Emo-Caches noch dessen Berechnung. Kurve und Detailbericht erhalten dieselbe Quelle. Ein Integrationstest bildet den zuvor fehlerhaften Wechsel waehrend eines ausstehenden Abrufs nach.
- CLAP-Fallback und Wechsel zur direkten Musikbewertung stehen sichtbar an Kurve und Bericht. Eine ausdruecklich gespeicherte CLAP-Auswahl bleibt erhalten. Fehlender Zugriff auf den Browserspeicher verhindert die bevorzugte direkte Bewertung nicht mehr.
- Vorhandene Detailbalken trennen gefuehlsbezogene Tags von Kraft/Energie als Klangcharakter. Interpolierte direkte Valenz und Aktivierung folgen derselben Wiedergabeposition wie die Balken; gespeicherte Abschnittswerte bleiben getrennt lesbar. Vor-/Zurueck-Tasten springen zu echten Abschnittsgrenzen. Ausserhalb der Trainingsskala liegende Schaetzungen werden markiert; nicht vorhandene Konfidenz-/RMS-Werte werden nicht als Messung vorgetaeuscht.
- Die bestehende Hauptkurve erhaelt einen Positionspunkt auf der Audio-Valenz. Keine weitere Diagrammart.
- Erneute Recherche zu Music2Emotion, Essentia und audioFX: direkte Valenz-/Aktivierungsregression und getrennte Musik-Tags statt Energie-zu-Aerger-Regeln; Klangveraenderungen als Robustheitsdiagnose pruefen. Kein fremder Programmcode uebernommen.
- Vier vor Inferenz festgelegte oeffentliche Rock-Ausschnitte mit Original, -12 dB Pegel und RMS-angepasster Saettigung lokal geprueft. Der Music2Emo-Pegeldrift blieb in dieser kleinen Diagnose unter 0,004 Valenzpunkten; Saettigung veraenderte die Valenz staerker. Dies ist kein Nachweis korrekter Gefuehle oder allgemeiner Gitarrenrobustheit. Referenzmaterial und Ergebnisse bleiben lokal.
- Zwischenvalidierung: 82 Frontend-Tests und Produktionsbuild bestanden. Erneuter kompletter Backend-Check und nativer Build fuer diesen Stand stehen noch aus.

- Abschlussvalidierung: 233 Backend-Tests und 82 Frontend-Tests sowie Produktions- und nativer Windows-Releasebuild bestanden. Zwei Hoerstudio-Tests scheiterten zuerst mit ueberlangem temporaerem Windows-Pfad; beide einzeln und danach die gesamte Suite mit kurzem Testpfad erfolgreich.
- Native Bedienpruefung: App gestartet, vorhandene Analyse geoeffnet, laufende direkte Musikbewertung waehrend des Wechsels zu Methode & Werte erfolgreich uebernommen. Detailbalken, getrennte Klangcharakter-Gruppe, realer 30-Sekunden-Kontext und Abschnittssteuerung sichtbar geprueft. Kein Nachweis vollstaendiger Genre- oder zeitlicher Emotionsgenauigkeit; kein frischer Linux-Lauf.


## Balkenfarben im Hintergrund und zugaengliche API-Profile

- Gemeinsame Farbquelle fuer Balken und Atmosphaerenhintergrund; haeufige psychologische Assoziationen und Gestaltungsentscheidungen in MUSIC-PSYCHOLOGY.md getrennt dokumentiert. Staerkerer, kontinuierlicher Dominanzakzent anhand des rohen Balkenabstands statt eines durch neun unabhaengige Tags verduennten Abstands. Farbigerer grossflaechiger Hintergrund, dunklere Inhaltsflaechen und unveraenderte Modellwerte.
- Anbieter-/Key-Verwaltung in beiden Modi sichtbar, vor lokalen Einstellungen. Allgemeinere API-Modusbezeichnung mit konkreter Faehigkeitserklaerung: Gemini-Audio und separate Textanbieter. Kein automatischer API-Aufruf durch Moduswechsel.
- Moduswechsel stellt die vorhandene Analyse sofort wieder her und ignoriert ueberholte Antworten nach Modus-/Songwechsel. Atmosphaerenstatus bleibt bestehen. Integrationstest prueft lokale Musik-Tags, API-Modus ohne Cache und identische Hintergrundfarbe nach der Rueckkehr.
- Zwischenvalidierung: 85 Frontend-Tests und Produktionsbuild bestanden; 23 gezielte Backend-Tests fuer Anbieter, Sprache und Publikationsschutz bestanden. Native und visuelle Pruefung stehen fuer diesen Stand noch aus.

- Abschlusspruefung: 85 Frontend-Tests und Produktionsbuild nach der abschliessenden Anordnung erneut erfolgreich. Nativer Windows-Releasebuild erfolgreich bereitgestellt. In der gestarteten App Anbieter-/Key-Verwaltung im lokalen Modus, allgemeine API-Auswahl und sichtbarer songabhaengiger Hintergrund geprueft. API-Modus ohne Analyse und Rueckkehr zu lokal stellten den Music2Emo-Hintergrund wieder her. Es wurden dabei keine Zugangsdaten eingegeben oder Anbieteranfragen gestartet. Der letzte komplette Backend-Lauf bleibt 233 bestanden; fuer diesen Oberflaechenstand bestanden die 23 gezielten Backend-Checks.


## Mehrere API-Anbieter fuer Audio und weitere KI-Funktionen

- Explizite Audiofaehigkeit und Nutzungs-/Kostenbestaetigung fuer OpenAI-kompatible Profile, Mistral/Voxtral-Preset sowie Aktivierung eines konkreten Audioprofils. Gemini behaelt seine bestehende Gratisprojekt-Bestaetigung. Claude-Messages und das DeepSeek-Textprofil werden nicht als Audioadapter ausgegeben. Profilbearbeitung deaktiviert eine zuvor vorbereitete Audiokonfiguration.
- Nativer Gemini-Pfad und neuer Chat-Completions-input_audio-Pfad mit WAV; OpenAI nur Textausgabe und store=false. Keine automatische Wiederholung oder Anbieterausweichung. API-Keys bleiben nur im Speicher.
- API-Audio- und Textbewertung getrennt, unabhaengige Emotionsscores fuer bestehende Balken und Atmosphaere; Kraft/Energie getrennt von Aerger. Direkte Valenz bleibt unabhaengig von Balkengewichten. Vollstaendige Scores/IDs und endliche Werte erforderlich.
- Optionales API-Transkript ohne LRC, mit validierten Zeitbereichen und Unsicherheitsmarkierung. Separat angeforderte API-Instrumenthinweise bleiben Hypothesen. Akustische Messungen und Spurentrennung bleiben lokal.
- Cache-Version unterscheidet Profil, Zieladresse, Protokoll und Modell. Auch API-Textdeutungen werden bei Profilwechsel als veraltet erkannt. API-Revision 14 in Backend, UI, Startern und Launchertests synchronisiert.
- Zwischenvalidierung: 244 Backend-Tests vor dem zusaetzlichen App-Durchlauftest bestanden; danach 66 betroffene Backend-Tests einschliesslich des simulierten OpenAI-Durchlaufs bestanden. 85 Frontend-Tests/Produktionsbuild sowie danach 26 betroffene Frontend-Tests bestanden. Erneute Gesamtsuiten und nativer Build fuer den Abschluss folgen. Kein echter kostenpflichtiger Anbieteraufruf oder Nachweis besserer Emotionsgenauigkeit.

- Abschlussvalidierung: Gesamtlauf mit 245 Backend- und 86 Frontend-Tests erfolgreich. Nach der letzten Validierungs-/Zustimmungsabsicherung bestanden 55 betroffene Backend- und 23 betroffene Frontend-Tests sowie der Produktionsbuild erneut. Nativer Windows-Releasebuild erfolgreich fuer den naechsten regulären Start bereitgestellt. Anbieterziel, Modell und Key werden atomar je Anfrage erfasst; Profil-/Key-Aenderungen sind waehrend laufender Jobs gesperrt. Keine neuen Live-Anbieteraufrufe oder native Abnahme eines echten API-Durchlaufs. Fuer API-Revision 14 Dienst und App neu starten; Sitzungs-Keys anschliessend erneut eingeben.

- Abschliessend wird auch bei Textanfragen und Audioprofil-Aktivierung das Profil zusammen mit seinem Sitzungs-Key unter derselben Sperre erfasst. 66 betroffene Anbieter-/Audio-/App-Tests danach erneut bestanden.


## Heimserver-Verbindung und Modellliste

- Ollama, LM Studio und kompatible Heimserver koennen per privater IP-Adresse oder aufloesbarem Heimnetz-Namen konfiguriert werden. HTTP-Namen sind nur bei ausschliesslich lokalen/privaten Zieladressen erlaubt; IPv4-in-IPv6-Adressen werden vor der Pruefung normalisiert. Oeffentliche HTTP-Ziele und linklokale Adressen bleiben ausgeschlossen.
- Expliziter Verbindungstest liest nur die kompatible Modellliste und erlaubt anschliessend die Modellauswahl. Keine automatische Modellinstallation, kein Modellstart und keine Uebertragung von Songtext oder Audio bei diesem Test. Der aktuell eingegebene Key wird nur fuer diese Anfrage verwendet und nicht durch den Test gespeichert.
- Lokaler echter HTTP-Testserver prueft Modellliste und ausdrueckliche Textanfrage ohne Key. Dies prueft das Protokoll, nicht einen konkreten Nutzer-Ollama-Server. Audio bleibt an tatsaechliche input_audio-Unterstuetzung und ein passendes Audiomodell gebunden.
- API-Revision 15 in Backend, UI und Startern abgestimmt. 87 Frontend-Tests und Produktionsbuild bestanden; nativer Windows-Releasebuild fuer den naechsten regulaeren Start bereitgestellt. Kein neuer nativer Bedienlauf an einem echten Heimserver und keine Aenderung von Serverfreigaben oder Firewall.

- Abschliessender kompletter Backend-Lauf: 251 Tests bestanden. Frontend, Produktionsbuild und nativer Build entsprechen dem oben dokumentierten erfolgreichen Stand.
