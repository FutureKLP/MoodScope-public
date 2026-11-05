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
