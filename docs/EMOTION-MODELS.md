# Spezialisierte Musikmodelle fuer die Emotionskurve

Die Zielaufgabe ist ein zeitlicher Verlauf wahrgenommenen musikalischen Ausdrucks.
Eine hohe Energie kann verschiedene Gefuehle begleiten. Ein Gesamturteil ueber
einen Song und ein gefuehlsbezogenes Suchergebnis sind keine validierte Zeitkurve.

## Gepruefte oeffentliche Implementierungen

[Music2Emo](https://github.com/AMAAI-Lab/Music2Emotion) verbindet MERT-Audiofeatures
mit gelernten Akkord-/Tonartmerkmalen und separaten Ausgaengen fuer Valenz,
Aktivierung und Mood-Tags. Code und veroeffentlichte Gewichte sind vorhanden.
Die Autoren berichten Vergleiche auf mehreren Musikdatensaetzen. Der Quellcode
mittelt MERT-Segmente bei langen Dateien; fuer eine Zeitkurve muss die Inferenz
auf ausdrueckliche Kontexte angewendet werden. Dies braucht eine eigene zeitliche
Validierung. Standard-Schwellwerte fuer Tags sind keine kalibrierten Intensitaeten.
Der Projektcode traegt MIT; Modell- und Datenbedingungen sind gesondert zu beachten.

[Moody](https://github.com/circuitflow/moody) hat eine passende Produktidee mit
Stimmungsverlaeufen innerhalb einer Aufnahme. Die Modellregistrierung verwendet
Essentia/MusiCNN mit DEAM- und emoMusic-Regressionskoepfen sowie separate
Mood-Klassifikatoren. Wiederverwendbar sind insbesondere die Trennung der
Modellrollen und die versionierten Pruefsummen. Die dokumentierte Essentia-
Laufzeit ist kein sofortiger nativer Windows-Ersatz. Projektcode: AGPL-3.0.

[AudioMuse-AI](https://github.com/NeptuneHub/AudioMuse-AI) ist eine lokale
Musikbibliotheks-/Playlistanwendung mit ONNX-Inferenz. Das ist ein nuetzliches
Vorbild fuer Laufzeit und Modellverwaltung, aber keine unabhaengige Bestaetigung
zeitgenauer Emotionswerte. Projektcode: AGPL-3.0. Es wird kein fremder Anwendungscode
ungeprueft in MoodScope kopiert.

Die [Essentia-Modelluebersicht](https://essentia.upf.edu/models.html) bietet
trainierte Valenz-/Aktivierungsmodelle. Die MTG-Gewichte stehen unter
CC BY-NC-SA 4.0, mit separat angebotener kommerzieller Lizenz. Eine spaetere
Produktintegration muss daher Modellbedingungen und Laufzeit gemeinsam behandeln.

[Continuous Music Emotion Recognition](https://github.com/SantiagoCotrini/continuous-music-emotion-recognition)
ist fachlich passend, beschreibt jedoch einen Trainings-/Kreuzvalidierungsablauf.
Ein sofort einsetzbarer, hier verifizierter Inferenzcheckpoint liegt nicht vor.
Die README-Aussage zur Generalisierung ersetzt keine unabhaengige Pruefung.

## Konkreter lokaler Vergleich

Music2Emo wurde als erster spezialisierter Kandidat ausgewaehlt. Nach Freigabe
wurden MERT-95M (rund 378 MB), ein Emotionskopf (rund 13 MB) und das Akkordmodell
(rund 12 MB) geladen. Downloadrevisionen und SHA256-Pruefsummen werden privat
aufgezeichnet. Unbenutzte Training-/Webabhaengigkeiten werden im isolierten
Versuch entfernt, vorhandene App-Pakete bleiben unveraendert.

Vor einer produktiven Auswahl muessen lokale Inferenz, tatsaechliche Zeitfenster,
Gegenbeispiele mit hoher Energie und eine passende menschliche Referenz geprueft
werden. Das Emotify-Set prueft ausgeloeste Gefuehle und kann allein weder Valenz
noch einen zeitgenauen Ausdrucksverlauf bestaetigen. Kein Modell wird allein wegen
weniger Aergerwerten oder schoenerer Kurven als genauer bezeichnet.

## Reproduzierbare Offline-Inferenz

`scripts.music2emo_evaluation` arbeitet mit einem explizit angegebenen, zuvor
geprueften lokalen Upstream-Checkout und vorhandenen Gewichten. Es startet keine
Downloads und oeffnet keine App-Datenbank. Die Inferenz laeuft als eigener Prozess,
weil die Upstream-Bibliothek globale Imports und relative Arbeitsverzeichnisse
verwendet. Ein neuer isolierter Ausgabeordner begrenzt alle Scratch-Dateien.

```powershell
python -m scripts.music2emo_evaluation --manifest .tools/emotion-evaluation/diagnostic-manifest.json --output .tools/emotion-evaluation/music2emo-run --source-directory .tools/music2emo-source --weights-directory models/music2emo --dependency-directory .tools/music2emo-packages --device cuda
```

Gepruefter Quellstand: `c5f7984f78d9928b841f25bd05a47377c12c58ca`.
MERT-Revision: `12af15fef9d0ac838c3f475bfbbf26d2060dd4f5`.
Die private `provenance.json` im Gewichtsordner enthaelt Dateinamen und SHA256.
Sie wird vor der Inferenz geprueft. Keine Gewichte, Referenzaudios, abgeleitete
MIDI-Dateien, Bibliothekskopien oder Modellausgaben werden veroeffentlicht.

Die Anpassung entfernt unbenutzte Training-/Webimports, verwendet den vorhandenen
Audioddecoder und eingeschraenktes Checkpoint-Laden. Ein Tensorfehler bei einem
einzigen Zeitframe wurde behoben. Restsegmente unter einer Sekunde werden mit
ihrem Vorgaenger verbunden, damit ein Decoderrest nicht das gleiche Gewicht wie
30 Sekunden Musik erhaelt. Die Option `--correct-key-mode` prueft getrennt eine
Korrektur der Upstream-Tonartuebergabe: Dort wurde der Tonikaname versehentlich
als Modus verwendet. Diese Variante ist kein automatisch aktivierter Produktwechsel.

Ein echter Lauf mit 16 diagnostischen Kontexten wurde abgeschlossen. Ein separater
Vergleich mit 32 bereits vorhandenen Emotify-Beispielen pruefte auch die beiden
Upstream-Randfaelle. Verbesserte Rangfolgen auf diesem diagnostisch mehrfach
verwendeten Set sind kein Holdout-Nachweis. Ein neuer, vor der Inferenz festgelegter
DEAM-Testsatz untersucht als naechstes passende Valenz-/Aktivierungsurteile.
