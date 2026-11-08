# Spezialisierte Musikmodelle fuer die Emotionskurve

## Weitere Vorschlaege und zeitlicher Pruefstand

Das Ziel ist eine lokal nutzbare oeffentliche Entwicklungsversion. Eine
kommerzielle Freigabe ist nicht das Projektziel. Bedingungen fremder Modelle
gelten dennoch unabhaengig von der Lizenz des Anwendungscodes.

- [Music Analysis Skill](https://mcpmarket.com/tools/skills/music-analysis-audio-intelligence):
  lokale DSP-Messungen und zeitliche Zusammenfassung sind als Architekturidee
  brauchbar. Ein validierter gelernter Emotionsverlauf ist damit nicht belegt.
  Der verlinkte Marketplace ist inzwischen archiviert. Keine ungepruefte
  Installation und keine Uebernahme fremden Codes ohne Lizenzklaerung.
- [local-music-analyzer](https://github.com/chris-miaskowski/local-music-analyzer):
  Die README unterscheidet macOS-Liveaufnahme von Dateianalyse. Die Aussage
  "alles nur macOS" waere zu pauschal; Windows-Dateianalyse ist hier jedoch
  nicht verifiziert. Optionale Essentia-Modelle und Demucs sind kein Nachweis
  genauer Emotionen. Beim Abruf wurde keine Repository-Lizenz ausgewiesen;
  daher keine Codeuebernahme. Die getrennten Status pro Analysestufe sind
  ein nuetzliches Gestaltungsvorbild.
- [music-emotion-analysis](https://github.com/ryhirz/music-emotion-analysis):
  MIT-Code, lokale SVM-Inferenz. Laut eigener README werden GTZAN-Genres per
  Regel in Emotionen umbenannt. Das Modell lernt vor allem Genreunterschiede,
  keine menschlich annotierten Gefuehle. Kein geeigneter Ersatz fuer diese Kurve.
- [Songfinder](https://songfinder.dev/tools/mood-detector): Der Anbieter nennt
  handgebaute akustische Heuristiken und die ersten 60 Sekunden. Kostenloser
  Webzugang ist keine Lizenz fuer wiederverwendbaren lokalen Anwendungscode.
- [DEAM](https://cvml.unige.ch/databases/DEAM/) liefert relevante menschliche
  Zeitreferenzen. Der Kaggle-Link ist ein Datenangebot, kein fertiges Modell.
  Datenrechte, Modelltraining und Zielaufgabe bleiben getrennt zu pruefen.
- Der verlinkte [Review](https://link.springer.com/article/10.1007/s42452-025-07178-9)
  bietet einen Forschungsueberblick, keinen direkt integrierbaren Checkpoint.
  Nicht eindeutig bezeichnete Projekte wie "music-mood-analysis" werden
  ohne konkreten Quellverweis nicht als verifizierter Kandidat eingestuft.

Die gespeicherten Kurven der bereits ausgewaehlten 32 DEAM-Stuecke wurden jetzt
auch gegen dynamische Annotationen geprueft. Laut
[DEAM-Handbuch](https://cvml.unige.ch/databases/DEAM/manual.pdf) fehlen die ersten
15 Sekunden absichtlich; sie werden nicht durch kuenstliche Referenzwerte ersetzt.
Die kleinen Annotationen stammen aus einem [oeffentlichen Spiegel](https://zenodo.org/records/11400122).
`scripts.deam_timeline_evaluation` ordnet anhand der CSV-Zeitstempel gespeicherte
Abschnittswerte zu, ohne Interpolation oder nachtraeglich optimierte Zeitverschiebung.
Aktivierung wird fuer den Vergleich von [-1,1] auf die App-Skala [0,1] umgerechnet.

Neben absoluten Fehlern und Concordance Correlation Coefficient (CCC) werden
die Verlaeufe nach Abzug ihres jeweiligen Songmittels verglichen. Eine konstante
Vorhersage aus dem jeweiligen Modellmittel dient als Kontrollwert. Das verhindert,
dass unterschiedliche Songmittel allein als erfolgreiche Verlaufserkennung gelten.
Alle vorhandenen Referenzpunkte des ausgewaehlten Sets waren abgedeckt.
Music2Emo liegt absolut naeher an den Referenzen als CLAP. Die zeitlichen
Schwankungen schlagen jedoch bei beiden Modellen den konstanten Kontrollwert
im RMSE nicht. Damit ist ein praeziser zeitlicher Ersatz weiterhin nicht belegt.
Dieses mehrfach betrachtete Set ist jetzt diagnostisch, kein neuer Holdout.

Reproduktion mit eigenen lokalen Dateien:

```powershell
python -m scripts.deam_timeline_evaluation --predictions .tools/evaluation/results.json --valence .tools/evaluation/valence.csv --arousal .tools/evaluation/arousal.csv --output .tools/evaluation/timeline-metrics.json
```

Das Vorhersageformat enthaelt `rows` mit `track_id`, `music2emo_curve` und
`clap_curve`; jede Kurve enthaelt `start`, `end`, `valence` und `arousal`.
Ausgabedateien werden nicht ueberschrieben. Es gibt keine Downloads und keinen
Zugriff auf die Bibliotheksdatenbank. Referenzen und Modellausgaben bleiben lokal.

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

Ein weiterer tatsaechlicher Parameterlauf verglich Music2Emo mit 10 und 20
Sekunden Kontext gegen die vorhandenen 30-Sekunden-Kurven und CLAP auf allen
32 diagnostischen DEAM-Stuecken. Anzeigeintervall, Annotationen und Ausrichtung
blieben konstant. Kuerzere Kontexte lieferten keinen verlaesslichen Vorteil
fuer die zeitlichen Schwankungen; der Produktstandard bleibt bei 30 Sekunden.
Die wiederverwendbare CLI `scripts.emotion_parameter_sweep` prueft Quell- und
Gewichtspruefsummen, verwendet nur lokale Dateien und haelt Protokoll und
Zwischenergebnisse in einem neuen privaten Ausgabeordner fest. Beispiel:

```powershell
python -m scripts.emotion_parameter_sweep --weights models/music2emo --baseline .tools/evaluation/results.json --selection .tools/evaluation/selected.json --audio-directory .tools/evaluation/audio --valence .tools/evaluation/valence.csv --arousal .tools/evaluation/arousal.csv --output .tools/evaluation/context-sweep --contexts 10 20 --device cpu
```

Die Auswahldatei enthaelt `tracks` mit `track_id` und `sha256`; die vorhandenen
Vorhersagen entsprechen dem oben dokumentierten Timeline-Format. Jeder
Parameterlauf ist diagnostisch und aktiviert sich nicht automatisch in der App.

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
DEAM-Testsatz pruefte anschliessend passende Valenz-/Aktivierungsurteile; siehe unten.


## Produktintegration und Nachweisgrenze

Die optionale Modellauswahl unter der bestehenden Audio-/Lyrics-Kurve fuehrt die korrigierte
Music2Emo-Inferenz in einem eigenen Prozess aus. Beide Regressionsausgaenge und
die unabhaengigen Tags bleiben getrennt; sie werden nicht in sechs CLAP-Kategorien
umgerechnet. Anzeigeintervall: fuenf Sekunden; Kontext: bis zu 30 Sekunden,
am Rand innerhalb der Aufnahme verschoben. Die gespeicherte Hauptanalyse bleibt erhalten; die Anzeige kann ihre Audio-Valenz
durch den separat gespeicherten Verlauf ersetzen. Biggest Split wird dazu passend
aus den ueberlappenden Lyrics neu berechnet.

Ein Vergleich auf 32 vorab ausgewaehlten IDs des veroeffentlichten DEAM-Testsplits
zeigte bessere Songmittelwerte fuer Valenz und Aktivierung als die CLAP-v7-
Projektion. Parameter wurden nach Sichtung dieses Sets nicht angepasst. Dies
ist ein kleiner datensatznaher Vergleich, keine unabhaengige Pruefung der gesamten
Trainingshistorie und kein Nachweis zeitgenauer Uebergaenge oder allgemeiner
Genre-Robustheit. Die erzeugten Kurven wurden gegen statische Songurteile gemittelt;
sie wurden nicht gegen dynamische DEAM-Annotationen bewertet. Ergebnisse bleiben
privat. Die App kennzeichnet den Zweitverlauf weiterhin als experimentell.

Fuer die vorhandene Entwicklungsinstallation wurden isoliert folgende Pakete
ergaenzt: mir_eval 0.8.2, pretty_midi 0.2.10, music21 9.3.0, mido 1.3.3,
more-itertools 10.5.0, jsonpickle 3.4.2 und webcolors 24.11.1. Die normale
App-Umgebung wurde dabei nicht per pip veraendert. Der Adapter wurde mit Python
3.10, Torch 2.8.0 und Transformers 4.57.6 tatsaechlich ausgefuehrt. Die neuere
Transkriptionsumgebung ist nicht die Modelllaufzeit dieses Adapters.

Bereits heruntergeladene, gepruefte Quellen und Pakete lassen sich so registrieren:

```powershell
python -m scripts.install_music2emo_local --source .tools/music2emo-source --weights models/music2emo --dependencies .tools/music2emo-packages
```

Dieses Kommando laedt nichts nach. Es erhaelt die Upstream-Lizenz und schreibt
Pruefsummen fuer den lokalen Quellstand. `installation.json` und
`provenance.json` sind lokale Installationsdateien. Die App prueft Quellen und
Gewichte im Worker vor Inferenz; fehlende oder veraenderte Dateien fuehren zum
Abbruch, nicht zu Ersatzwerten. Gespeicherte Vergleiche erhalten einen eigenen
Cache-Schluessel und werden beim Loeschen des Analyse-Caches mit entfernt.

Die [MERT-Modellkarte](https://huggingface.co/m-a-p/MERT-v1-95M) nennt
**CC BY-NC 4.0**. Die MIT-Lizenz des Music2Emo-Codes hebt diese Modellbedingung
nicht auf. Modellgewichte und Drittanbieterquellen sind kein Bestandteil der
GitHub-Veroeffentlichung. Fuer eine kommerzielle Weitergabe ist die nichtkommerzielle
MERT-Bedingung vorab zu klaeren; dieser Zwischenstand behauptet keine kommerzielle
Lizenzfreigabe.
