# Entwicklungsversion 0.2

## Neue Bereiche

- Verlauf: synchronisierte Audio- und Textvalenz, Player und Biggest Split.
- Bibliothek: vorhandene Analysen laden, manuell neu berechnen und Analyse-Cache löschen.
- Songdetails: gemessenes Tempo und spektrale Helligkeit; relative Instrumenthinweise; eigene Angaben zu Genre, Instrumenten und Besetzung.
- Interpretation: lokale Text- und Zeilendeutung, getrennt von belegten Audiohinweisen und eigenen Notizen.
- Modelle & API: kuratierte lokale Modelldownloads und -auswahl; ausdrücklich optionaler Gemini-Modus mit eigenem Sitzungs-Key.

Lokale KI bleibt auch bei Internetverbindung der Standard. Audio und Lyrics werden nur bei ausdrücklich gewähltem API-Modus und Zustimmung an Google gesendet. Eigene Interpretationsnotizen werden nicht an den Anbieter gesendet.

## Nachgewiesene Prüfungen dieses Zwischenstands

- 59 Python-Tests bestanden, einschließlich Cache-Wiedererkennung, erzwungener Neuanalyse, gezielter Cache-Löschung, Geheimnisschutz, Backend-Versionsprüfung und begründeter Interpretation.
- 9 Frontend-Tests bestanden, einschließlich Schutz vor vorzeitigem Freigeben paralleler Vorgänge und Überschreiben noch nicht geladener Notizen.
- Produktionsbuild der Oberfläche und nativer Windows-Build 0.2 im getrennten Buildordner bestanden.
- Öffentliche Einzeltracks von YouTube und SoundCloud tatsächlich importiert. Ein zuvor verwendetes YouTube-Testvideo war nicht mehr verfügbar; ein anderer öffentlicher Testlink funktionierte.
- CLAP-Ensemble, XLM-EMO mit Kontext, Instrumenthinweise und Qwen 1.5B auf CUDA offline ausgeführt.
- Vollständiger isolierter Offline-Durchlauf mit echten Modellen: Analyse, Cachetreffer ohne erneute Audioinferenz, Instrumenthinweise, Zeilendeutung, Löschen von fünf Analyse-Cacheeinträgen bei erhaltenen eigenen Notizen und anschließende erzwungene Neuanalyse bestanden.
- Browser: öffentlicher YouTube-Link bis zur echten lokalen CUDA-Analyse; danach Bibliotheksöffnung aus Cache und eigene Notiz nach vollständigem Neuladen erhalten.
- Eigenes kleines Diagnose-Set mit zwölf deutschen/englischen Textfällen: Einzelzeilen- und Kontextmodell jeweils 75 % korrekte Valenzrichtung. Das belegt keinen allgemeinen Genauigkeitsgewinn.

## Noch nicht als vollständig geprüft ausgeben

- Echte Gemini-Inferenz wurde mangels eigenem API-Key nicht ausgeführt. Adapter, Einwilligung, Fehlerbehandlung und Trennung von lokaler Inferenz sind durch Vertragstests geprüft.
- Nicht alle angebotenen Modellvarianten wurden heruntergeladen oder qualitativ verglichen.
- Linux und Windows 10 wurden nicht lokal ausgeführt. Plattformskripte und CI-Konfiguration sind vorhanden.
- Sprachmodell-Deutungen sind mögliche Lesarten und können Fehler enthalten. Textmodelle erhalten keine akustischen Zahlenwerte zum freien Interpretieren; Audiohinweise stammen aus den tatsächlichen Mess-/Modellergebnissen.
- Es gibt noch keinen eigenständigen Installer mit eingebettetem Python-Backend und keinen Videoexport.
