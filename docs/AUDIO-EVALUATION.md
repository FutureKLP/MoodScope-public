# Vergleichskonzept fuer musikalischen Ausdruck

Status: Diagnose und Architekturvorschlag, keine neue produktive Analysemethode.
Die anschließend freigegebene erste Integrationsstufe und die externe menschliche
Referenz sind in [HUMAN-REFERENCE.md](HUMAN-REFERENCE.md) dokumentiert. Die
Audio-Emotionspipeline bleibt unverändert; der optionale Musikvergleich ist neu.
Die bestehende Sechs-Kategorien-Pipeline, Nutzerdaten, Einstellungen und Caches
werden durch das Diagnosewerkzeug nicht veraendert. Modellantworten, Musik,
Bewertungen und private Manifeste werden nicht versioniert.

## Fragestellung und Zielgroessen

Untersucht wird der wahrgenommene Ausdruck der Musik, nicht die persoenliche
Stimmung des Hoerers, die Kuenstlerabsicht oder die Bedeutung des Songtexts.
Persoenlich ausgeloeste Gefuehle koennen separat erhoben werden, duerfen aber
nicht als dieselbe Referenz behandelt werden. Textwissen, Bekanntheit,
Hoergewohnheiten und Kontext koennen Urteile beeinflussen.

Ein mehrdimensionales System ist ein Kandidat, keine bereits bestaetigte
Verbesserung. Zu unterscheiden sind:

- Signalpegel: RMS in dBFS, Spitzenpegel und relative Energieentwicklung.
  Das ist keine LUFS- oder subjektive Lautheitsmessung.
- Musikalische Energie und wahrgenommene Klanghaerte/Verzerrung. Ein hoher
  Spektralschwerpunkt beweist weder Verzerrung noch ein bestimmtes Instrument.
- Emotionale Valenz und Aktivierung/Arousal als getrennte Schaetzungen.
- Emotionale Spannung als eigene Frage, nicht als Synonym fuer Energie.
- Gleichzeitig moegliche Ausdrucksweisen, beispielsweise Melancholie und
  Verzweiflung neben Entschlossenheit. Unbekannt ist nicht gleich abwesend.

Das Ziel ist nicht eine gleichmaessige Verteilung von Kategorien oder weniger
AErger um jeden Preis. Ein wirklich wuetender Abschnitt muss weiterhin als
solcher erkennbar sein. Mehr Begriffe allein sind kein Qualitaetsgewinn.

## Phase A: Vergleichsset und menschliche Referenz

Zunaechst wird ein unveraenderliches Pilotset mit 24 Ausschnitten aus mindestens
12 unterschiedlichen Aufnahmen geplant. Ein Ausschnitt dauert hoechstens zehn
Sekunden, damit genau derselbe CLAP-Kontext verglichen werden kann. Laengere
musikalische Entwicklungen werden spaeter mit zusammenhaengenden Abschnitten
und zeitlich ausgerichteten Urteilen separat bewertet.

Sechs Abdeckungsgruppen dienen der Auswahl, nicht als vorab festgelegte Wahrheit:

1. Kraftvoll und wahrscheinlich melancholisch/sehnsuechtig.
2. Kraftvoll und wahrscheinlich verzweifelt.
3. Tatsaechlich wuetend/feindselig, mit unterschiedlicher musikalischer Energie.
4. Hoffnungsvoll/entschlossen/triumphierend, auch mit Gitarren und Schlagzeug.
5. Angespannt oder emotional gemischt/mehrdeutig.
6. Kontraste mit niedriger Energie, darunter traurige, ruhige und positive Musik.

Die Gruppen sollen Stile, Gesang/Instrumentalmusik, Produktionsdichte und
verschiedene Dynamiken abdecken. Mehrere Gruppen duerfen zutreffen. Ausgewaehlt
wird nicht anhand der Modellvorhersage. Vorlaeufige Auswahlbeschreibungen werden
den Bewertern nicht gezeigt. Eine vorhandene private Bibliothek ist ein
Bequemlichkeitskorpus und keine repraesentative Stichprobe.

Pro Ausschnitt bewerten mindestens drei Personen unabhaengig und ohne
Modellergebnisse. Die gewuenschten Referenzen sind Valenz (-1 bis +1), Arousal,
Energie, Klanghaerte und emotionale Spannung (je 0 bis 1). Fuer Ausdrucksbegriffe
werden unabhaengige Intensitaeten erfasst, keine Auswahl genau eines Gewinners.
Freie Beschreibungen, "nicht beurteilbar" und Sicherheit des eigenen Urteils
werden separat dokumentiert; ein fehlender Wert wird nicht auf null gesetzt.

Die bereitgestellten Hoerausschnitte tragen nur neutrale Fallkennungen. Die
Reihenfolge wird pro Bewerter mit protokolliertem Seed randomisiert. Abhoerpegel,
Kopfhoerer/Lautsprecher, Bekanntheit und Kenntnis des Textes werden festgehalten.
Wiederholte verdeckte Ausschnitte pruefen Urteilskonsistenz und werden nicht als
zusaetzliche unabhaengige Referenzen gezaehlt. Die eigene Meinung des Entwicklers
ist keine ersatzweise menschliche Mehrheitsbewertung.

Aufnahmen und ihre Import-/Masteringvarianten bleiben vollstaendig in einem
Split. Der Entwicklungsteil darf fuer Promptauswahl verwendet werden; der
zurueckgehaltene Teil erst nach Festlegung der Kandidaten. Das Werkzeug prueft
Gruppenkennungen und Dateihashes auf Split-Leckage. Unterschiedlich codierte
Versionen benoetigen dieselbe manuell gepflegte recording_id; Hashes allein
erkennen diese nicht. Bei der kleinen Pilotgroesse sind nur beschreibende
Ergebnisse sinnvoll. Fuer belastbare Freigabeentscheidungen ist ein groesseres,
vorab festgelegtes Testset mit Unsicherheitsintervallen auf Aufnahmeebene noetig.

## Vergleichskandidaten

Das Werkzeug `scripts/audio_evaluation.py` verwendet ausschliesslich einen
explizit angegebenen lokalen CLAP-Snapshot und liest keinen App-Zustand:

1. `legacy6`: unveraenderte zwoelf produktive Beschreibungen und Projektion.
2. `anger_wording6`: genau eine Beschreibung geaendert; "tense/aggressive"
   wird durch Aergerbegriffe ersetzt. Kategorien und Auswertung bleiben gleich.
3. `parallel_wording6`: dieselben sechs Kategorien mit paralleler Formulierung
   und gleicher Anzahl von Beschreibungen. Dies untersucht Formulierungsbias.
4. `exploratory10`: zusaetzliche Nachbarschaften wie Kraft, Verzweiflung und
   Sehnsucht. Nur ein explorativer Kandidat, keine beschlossene Taxonomie.
   Gewinnerquoten verschiedener Kategorienzahlen sind nicht direkt vergleichbar.
5. Unabhaengige Kontrastabfragen fuer Valenz, Arousal, Energie, Klanghaerte und
   Spannung sowie nicht auf Summe eins normierte Ausdrucksaehnlichkeiten.
   Diese Abfragen koennen weiterhin miteinander korrelieren und sind weder
   unabhaengig validierte Dimensionen noch kalibrierte Wahrscheinlichkeiten.

Alle Kandidaten erhalten dieselben dekodierten Ausschnitte. Pro Fall werden
Originalpegel und -12 dB verglichen, zusaetzlich beide Varianten mit konstantem
Analysepegel. Die Pegelkontrolle peilt -20 dBFS RMS mit Spitzenbegrenzung durch
konstanten Gain auf 0,99 an. Sie veraendert weder die Quelle noch die Dynamik
innerhalb des Ausschnitts und ist kein Compressor/Limiter. Die Zielwerte sind
explizite Versuchsparameter, keine trainierten Emotionsgewichte. Sensitivitaet
gegen andere Zielpegel ist vor einer produktiven Auswahl gesondert zu testen.

Pro Prompt werden Kosinusaehnlichkeit und skalierter Logit erhalten. Dadurch
lassen sich Einzelbeschreibungen, Mittelung und Softmax unterscheiden. Eine
gemeinsame positive Temperatur veraendert die Kategorie-Rangfolge nicht.
Klassenbezogene Korrekturen benoetigen Referenzdaten; es gibt keinen pauschalen
AErger-Abzug. Eine Softmax ueber Kandidaten ist kein Beweis fuer deren Eignung.

Die GEMS-Familie ist ein wissenschaftlich begruendeter Vergleich fuer musikalische
Emotionsdimensionen, aber kein unveraendert zu uebernehmender Produktvertrag:
Sie wurde fuer musikinduzierte emotionale Erfahrung entwickelt. DEAM liefert
eine moegliche externe Valenz-/Arousal-Referenz, jedoch keine vollstaendige
Referenz fuer alle Ausdrucksfacetten. Datenlizenzen, Zielkonstrukt, trainierte
Datenueberschneidungen und Annotationszeitversatz muessen vor Nutzung geklaert
werden. Es wurden dafuer keine Datensaetze oder neuen Modelle heruntergeladen.

Primaerquellen:

- [CLAP-Schnittstelle und skalierte Aehnlichkeiten](https://huggingface.co/docs/transformers/model_doc/clap)
- [GEMS-Forschung der Universitaet Genf](https://www.unige.ch/cisa/research/topics/culture-and-arts)
- [DEAM-Datenbank](https://cvml.unige.ch/databases/DEAM/)
- [Musikbezogene Modelle und Metadaten in Essentia](https://essentia.upf.edu/models.html)
- [MTG-Jamendo: Daten, Tags und Splits](https://github.com/MTG/mtg-jamendo-dataset)

Musikbezogen trainierte Mood-/Theme-Modelle aus dem Essentia/MTG-Umfeld sind
moegliche spaetere Vergleichsmodelle. Uploader-Tags in MTG-Jamendo ersetzen
keine unabhaengigen Hoererurteile. Lizenz, Zielkategorien, zeitliche Aufloesung,
Windows-Laufzeit und zusaetzliche Abhaengigkeiten muessen vor einem Versuch
geprueft werden. Diese Modelle wurden weder installiert noch ausgefuehrt.

## Auswertungsmethode und Entscheidungsregeln

Ohne menschliche Referenz werden nur Sensitivitaet, Rangfolgen, Pegelstabilitaet,
Laufzeit und Ressourcen berichtet. Gewinnerhaeufigkeiten sind keine Genauigkeit.
Die -12-dB-Kontrolle prueft Empfindlichkeit gegen eine technische Pegelaenderung;
sie beweist nicht, dass Lautstaerke niemals eine emotionale Wirkung hat.

Das Bewertungswerkzeug verwendet pro Dimension den Median von mindestens drei
unabhaengigen Urteilen und erhaelt die Spannweite menschlicher Bewertungen.
Fuer dimensionale Kandidaten werden MAE und Rangkorrelation ausgegeben;
fuer unkalibrierte Ausdrucksaehnlichkeiten nur Rangkorrelation, keine erfundene
Intensitaetsgenauigkeit. Fehlende und konstante Referenzen liefern keine
scheinbar aussagekraeftige Korrelation. Entwicklung und Holdout werden getrennt
ausgewertet. Unterschiedliche Zielkonstrukte werden nicht vermischt.

Vor produktiver Auswahl sind zu ergaenzen:

- Uebereinstimmung zwischen Bewertern, Wiederholkonsistenz und Fehler getrennt
  nach Aufnahme, Ausdrucksgruppe und hoher/niedriger Energie.
- Gezielte Verwechslung von Aerger mit Verzweiflung, Melancholie und Spannung;
  zugleich Erhalt der Erkennung wirklich wuetender Musik.
- Vergleich mit einfachen Referenzen, etwa konstantem Median und bestehender
  Pipeline, damit komplexere Kandidaten ihren Zusatznutzen zeigen muessen.
- Fehler von Valenz/Arousal, Rangtreue der Ausdrucksfacetten und zeitlich
  ausgerichtete Uebergangsfehler. Korrelierte Fenster sind keine unabhaengigen
  Testbeispiele. Kalibrierung nur auf Entwicklung, niemals auf Holdout anpassen.
- Aufnahmeweise Bootstrap-Intervalle und gepaarte Vergleiche erst bei
  ausreichender Stichprobe. Das aktuelle Werkzeug behauptet keine Signifikanz.
- Interpretation: verblindete Bewertung von Belegtreue, musikalischer
  Plausibilitaet, Behandlung von Gegenbelegen und ungestuetzten Aussagen.
- Getrennte Messung von Modellstart, Vorverarbeitung, Inferenz und Nachverarbeitung;
  Warm-up, Median und Spitzenlaufzeit. Torch-Speicher ist nicht Gesamt-VRAM/RAM.

Eine Methode wird nicht wegen geringerer Aergerquote freigegeben. Sie muss auf
zurueckgehaltenen menschlichen Bewertungen besser abschneiden, bei klaren
Faellen keine relevante Verschlechterung zeigen und Unsicherheit bewahren.
Numerische Zielschwellen werden nach dem Pilot, aber vor dem finalen Holdout
festgelegt. Aktuell gibt es keine belastbare Prozentzusage fuer eine Verbesserung.

## Ausfuehren ohne App-Aenderungen

Private Dateien unter `.tools/emotion-evaluation/` oder `data/evaluation/` halten.
Ein Manifest hat `protocol: moodscope-audio-diagnostic-v1` und eine nichtleere
Liste `cases`. Jeder Fall hat `case_id`, `recording_id`, `split`, `source`,
`start` und `duration`. Quellenpfade sind relativ zum Manifest oder absolut.
Zulaessige Splits sind `development`, `holdout` und `diagnostic`.

```powershell
python -m scripts.audio_evaluation prepare --manifest .tools/emotion-evaluation/manifest.json --output .tools/emotion-evaluation/blind-01
python -m scripts.audio_evaluation run --manifest .tools/emotion-evaluation/manifest.json --output .tools/emotion-evaluation/run-01 --model-directory models/hub/models--laion--clap-htsat-unfused/snapshots/SNAPSHOT --device cpu
python -m scripts.audio_evaluation score --results .tools/emotion-evaluation/run-01/model-results.json --ratings .tools/emotion-evaluation/run-01/human-ratings.json --split holdout --processing original
```

`SNAPSHOT` durch einen bereits vorhandenen lokalen Snapshot ersetzen. Downloads
sind gesperrt. CUDA ist ausdruecklich mit `--device cuda` moeglich. Bestehende
Ausgabeordner werden nicht ueberschrieben. Quellen werden vor und nach dem Lauf
per SHA256 verglichen. Das Programm erzeugt ausschliesslich im neuen privaten
Ausgabeordner Modellwerte, neutrale WAV-Hoerausschnitte und eine leere
Bewertungsdatei. Es startet keinen Dienst und oeffnet keine Nutzerdatenbank.
`prepare` erstellt nur den Blindhoersatz und drei reproduzierbar randomisierte
Reihenfolgen, ohne ein Modell zu laden. Die Aufnahmen sind mono und entsprechen
damit der Audioeingabe der bisherigen CLAP-Pipeline. Die gemeinsame Referenz
muss diese Abhoerbedingung beruecksichtigen.

Ein tatsaechlich vorbereiteter lokaler Pilot enthaelt 24 Ausschnitte aus zwoelf
weiteren Aufnahmegruppen, getrennt von der explorativen Diagnosestichprobe.
Davon sind 16 Ausschnitte Entwicklung und acht Holdout. Diese Zuordnung ist
eingefroren; die klangliche und emotionale Gruppenabdeckung ist noch durch
Menschen zu pruefen. Das Set ist deshalb noch kein validierter Benchmark.
Der Holdout wurde nicht fuer die Promptuntersuchung ausgefuehrt.

Die Bewertungsdatei erhaelt `target: perceived_expression`. Ihre `ratings` sind
Eintraege mit `case_id`, pseudonymer `rater_id` und `values`. Darin sind Zahlen
fuer vorhandene Dimensionen zulaessig, keine automatisch ergaenzten Modellwerte.
Fuer Valenz gilt -1 bis +1, sonst 0 bis 1. Die Datei ist eine technische
Schnittstelle; eine komfortable verblindete Bewertungsoberflaeche ist noch offen.
Der Manifest-Hash bindet Bewertungen und Modellergebnisse an denselben
eingefrorenen Vergleichssatz; fremde Bewertungsdateien werden verworfen.

## Architekturvorschlag zur Freigabe

Empfohlen wird eine Schichtung, keine neue exklusive Gewinnerliste:

1. Signal und musikalische Struktur: Zeitintervalle, Pegel, Dynamik, Beat-/Tempo-
   Kandidaten, Tonart-/Akkordalternativen, Harmonieabdeckung und Quellen.
2. Musikalischer Ausdruck: getrennte Schaetzungen fuer Valenz, Aktivierung und
   Spannung. Energie und Klanghaerte bleiben davon unterscheidbar. Mehrere
   Ausdrucksfacetten koennen gleichzeitig relevant sein.
3. Evidenzqualitaet: Messgrenzen, Kandidatenabstaende, Promptempfindlichkeit,
   fehlende Daten und Uneinigkeit menschlicher Bewertungen getrennt erhalten.
4. Interpretation: Text- und Musikbelege mit Zeitbereichen und Herkunft verbinden.
   Die reine Audioeinschaetzung verwendet keine Lyrics; sonst wuerde der
   anschliessende Vergleich beider Perspektiven seine Unabhaengigkeit verlieren.

CLAP kann ein Vergleichs- und Merkmalslieferant bleiben. Eine kleine, auf
passenden Referenzen trainierte und getrennt kalibrierte Vorhersageschicht oder
ein musikbezogen trainiertes Modell sind spaetere Alternativen. Ein neuer
Modellname ist ohne Vergleich kein Qualitaetsnachweis. Neue Gewichte,
Architekturentscheidungen und Downloads benoetigen eine eigene Freigabe.

Vor der gemeinsamen Interpretation werden bekannte zeitliche Schwachstellen
der Harmonieausgabe behandelt: globale und lokale Tonart unterscheiden,
mehrdeutige Tonarten nicht erzwingen, Aufloesungen nur als Kandidaten behandeln
und den ganzen gewaehlten Zeitraum statt der ersten Akkorde zusammenfassen.
Messwerte sind keine Erklaerung emotionaler Ursachen. Ein Sprachmodell soll
nur die gelieferten Belege verknuepfen und auch widersprechende Befunde nennen.

Erst nach Freigabe wird ein neuer versionierter Analysevertrag konkret
implementiert. Geplant sind additive optionale Felder und Methodenkennungen in
neuen Cache-Namensraeumen. Bestehende sechs Scores, Prompts und Ergebnisse
werden weder neu beschriftet noch automatisch migriert. Leere Evidenz wird
nicht als nachgewiesene Neutralitaet ausgegeben. API-Vertragsaenderungen muessen
mit Frontend, Launchern und Startkompatibilitaet gemeinsam versioniert werden.

Die bestehende Reihenfolge Bibliothek, Songdetails, Stimmungsverlauf, Methode &
Werte, Hoerstudio, Interpretation unterstuetzt den Weg bereits weitgehend.
Zunaechst werden passende Verweise zwischen Fakten, Verlauf, Hoerstudio und
Interpretation vorgeschlagen. Eine Umordnung von Methode & Werte ist erst
sinnvoll, wenn Bedienpruefungen einen Vorteil zeigen. Player, A/B-Loops, Lyrics-
Vergleich, Quellentrennung und Design benoetigen keinen grundsaetzlichen Umbau.

## Risiken und offene Arbeit

- Die unabhaengigen CLAP-Abfragen koennen dieselben akustischen Eigenschaften
  wiederholt messen und nur scheinbar verschiedene Dimensionen darstellen.
- Pegelnormierung kann eine Stoergroesse reduzieren, aber einen Teil der
  musikalischen Wirkung veraendern; Originalmerkmale muessen erhalten bleiben.
- Kleine lokale Sprachmodelle koennen trotz zusaetzlicher Fakten plausibel
  klingende Fehlschluesse formulieren. Belegpruefung und verblindeter Vergleich
  bleiben erforderlich; reine Zitatpruefung reicht nicht aus.
- Momentan fehlen unabhaengige menschliche Bewertungen und eine grosse
  Referenzbasis. Das Diagnosewerkzeug ersetzt deren Erhebung nicht.
- Kalibrierung und trainierte Vorhersageschichten sind noch nicht implementiert.
  Die freigegebene erste Integration additiver Belegfelder und der optionalen
  Musikvergleichs-Oberflaeche steht in HUMAN-REFERENCE.md.
- Bereits behobene Wiedergabe-, Bibliotheks-, Quellen- und Cacheprobleme bleiben
  durch unveraenderten Produktcode erhalten; spaetere Integration benoetigt
  passende Regressionen und isolierte schreibende Tests.
