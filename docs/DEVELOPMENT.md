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
