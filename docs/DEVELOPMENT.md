# Aktueller Entwicklungsstand

Dieser Checkpoint erweitert Version 0.2. Er ist noch nicht als vollständig abgenommene neue Desktop-Version zu verstehen.

## Implementiert

- Getrennte Anweisungen für Gesamtdeutung und Einzelstelle; ungetakteter Text kann für die Gesamtdeutung verwendet werden. Ohne Text erscheint eine konkrete Anleitung statt erfundener Lyrics.
- Mehr Ausgabetext, sichtbare Hinweise bei Kontext-/Ausgabelimit und separate musikalische Begründung aus tatsächlichen Mess-/Modellwerten.
- Gespeicherte KI-Deutung automatisch laden, bewusst neu erzeugen oder gemeinsam mit Analyse-Cache löschen; eigene Notizen bleiben erhalten.
- Lokales Demucs-Hörstudio mit Solo-/Mix-Knöpfen und zeitlich fortgesetzter Wiedergabe beim Quellenwechsel. Vier oder experimentell sechs Gruppen; keine Trennung einzelner Sänger.
- Lokale Texterkennung per Knopf; Whisper-Fallback bei neuen Analysen standardmäßig aktiviert. Vorhandene Vier-Spur-Gesangstrennung wird bevorzugt. Unverstandener Text wird nicht als gesichert ausgegeben.
- Auswahl von Einzeltracks aus öffentlichen SoundCloud-Suchlinks.
- Kostenlose MusicBrainz-Recherche ohne Key mit bewusst bestätigter Aufnahme und Quellenlink.
- Mehrere Textmodellprofile für OpenAI, Anthropic und kompatible lokale/LAN-Server; Schlüssel nur im Arbeitsspeicher. Kein pauschales Versprechen universeller Anbieter-/Modellkompatibilität.
- Rotierende lokale Logs mit Fehler-ID, Codepositionen und Auftragslaufzeiten; keine Songtexte oder Zugangsdaten in den Protokollen.

## Bisher ausgeführt

- Bestehende 59 Python- und 9 Frontend-Tests nach den ersten Erweiterungen bestanden; danach 73 Python-Tests einschließlich neuer Anbieter-/Trennungs-/Diagnosefälle bestanden. Weitere Regressionstests laufen.
- Frontend-Produktionsbuild bestanden.
- Offizielle Demucs-Gewichte heruntergeladen; echte Vier-Spur-GPU-Inferenz auf selbst erzeugtem Audio bestanden. Das beweist technische Funktion, keine quantitative Trennqualität für Gesang.
- Echter Offline-Durchlauf auf CUDA mit CLAP, XLM-EMO, Instrumenthinweisen und neuer ausführlicher Zeilendeutung bestanden. Cachetreffer und erzwungene Neuanalyse nachgewiesen.
- Öffentlichen SoundCloud-Suchlink live auf einzelne Songlinks aufgelöst.
- MusicBrainz-Livesuche lieferte HTTP 503. Die App behandelt den Ausfall mit Fehler-ID; erfolgreiche Live-Recherche ist damit noch nicht belegt.

## Noch zu prüfen

Gesamtdeutung mit vollständigem Liedtext, Sechs-Spur-GPU-Modell, Browser-Hörstudio und neuer nativer Windows-Build. Echte OpenAI-/Anthropic-Inferenz ohne Nutzer-Key nicht geprüft; Adapter werden mit Vertragstests validiert. Linux und Windows 10 weiterhin nicht lokal geprüft. Genauigkeits- und Qualitätsgrenzen aus der README gelten unverändert.
