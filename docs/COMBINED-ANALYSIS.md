# Gemeinsame Auswertung von Musik und Text

## Verfuegbarer Produktstand

Die vorhandene Audio-/Lyrics-Kurve erhaelt eine zeitbezogene gemeinsame
Einordnung. Musik und Text koennen eine aehnliche Valenztendenz, einen Kontrast
oder ein uneindeutiges Verhaeltnis zeigen. Ausreichende zeitliche Textabdeckung,
als unsicher markierte Transkriptionen und instabile Audiovorhersagen werden
ausdruecklich beruecksichtigt. Ueberlappende Textzeilen vergroessern die
Abdeckung nicht kuenstlich. Die Anzeige verwendet gespeicherte Abschnittswerte;
die bestehenden Balken bleiben visuell interpoliert.

Es wird kein neuer Gesamtscore durch Mittelung gebildet. Positive Musik und
negativer Text duerfen als Kombination erhalten bleiben. Die neutrale Zone von
plus/minus 0,15 ist eine dokumentierte Darstellungskonvention fuer die Relation,
kein psychologischer Grenzwert und keine kalibrierte Sicherheit. Auch die
50-Prozent-Mindestabdeckung ist eine Vergleichskonvention; sie beweist keine
Wortgenauigkeit. Die Anzeige kann persoenliche Gefuehle nicht messen.

Unter Interpretation verwendet **Musikbelege einbeziehen** dieselbe Musikquelle
wie die Hauptkurve. Ein ausgewaehlter Music2Emo-Verlauf wird auf seinen aktuellen
Modellstand geprueft; fehlende oder veraltete Ergebnisse werden nicht still durch
CLAP ersetzt. Modellquelle, Analysebasis und gespeicherte Deutungen bleiben
zugeordnet. Textdeutung ohne Musikbelege bleibt moeglich.

Die Deutung erhaelt konkrete Textreferenzen und Musikbelege mit Zeitbereichen:
gelernte Valenz, relative Energieentwicklung, Tempo- und Harmoniekandidaten sowie
die zeitliche Beziehung von Text und Musik. Bei Gesamtdeutungen bleiben auch
kurze Gegenbeispiele und unsichere Passagen in der begrenzten Belegauswahl.
Neue Belegpaketkennung: `music-observations-v2-joint`, API-Revision 13.

## Psychologische Daten und Grenzen

Die [Forschungsgrundlage](MUSIC-PSYCHOLOGY.md) unterscheidet musikalischen
Ausdruck, persoenlich ausgeloeste Gefuehle und Gefallen. Musikalische Mittel
wirken zusammen; Erinnerung, Vertrautheit und Hoersituation sind zusaetzliche
Einfluesse. Diese Erkenntnisse begruenden die Belegtrennung und Gegenlesarten.
Sie werden nicht in ungetestete Emotionszuschlaege fuer BPM, Dur/Moll oder
Energie umgewandelt.

Fuer eine gelernte numerische Fusion braucht es passende Audio-/Lyrics-Paare
mit unabhaengigen Zielbewertungen. Die bisher eingesetzten DEAM-Referenzen
pruefen musikalischen Ausdruck; Emotify prueft ausgeloeste Gefuehle. Keiner
dieser bisherigen Laeufe bestaetigt die Genauigkeit einer kombinierten
Audio-/Lyrics-Vorhersage.

[MERGE](https://zenodo.org/records/13939205) bietet gepaarte 30-Sekunden-Audios,
vollstaendige Lyrics, AV-Werte und festgelegte Trainings-/Validierungs-/Testsplits.
Die Zuordnung eines Audioausschnitts zum vollstaendigen Text ist keine
zeilengenaue Zeitannotation. Herkunft der Labels und moegliche Ueberschneidungen
muessen vor einem unabhängigen Fusionstest geprueft werden. Ein
[weiteres Forschungsprojekt](https://github.com/alitalaghat/multi-modal-music-emotion-dataset)
stellt Kennungen und Splits bereit; seine Beschreibung allein belegt keine hier
verifizierte, sofort nutzbare lokale Inferenz.

## Lokaler Sprachmodellvergleich

Ein groesseres Sprachmodell kann die Verknuepfung gelieferter Belege verbessern,
ist aber nicht automatisch ein genauerer Gefuehlsklassifikator. Qwen 3B wird nach
gesonderter Downloadfreigabe in einem isolierten Vergleich vorbereitet. Der
Download- oder Vergleichsstatus ist kein Genauigkeitsnachweis. Die aktive
Modellwahl wird durch den Vergleich nicht geaendert. Kriterien sind unter anderem
korrekte Textbelege, Erhalt von Kontrasten, Behandlung unsicherer Woerter,
Ausgabesprache und Vermeidung erfundener musikalischer Ursachen.

Die Qwen-Gewichte behalten ihre eigenen Bedingungen; die MIT-Lizenz des
Anwendungscodes gilt nicht automatisch fuer sie. Referenzdateien, Gewichte und
Modellausgaben sind kein Bestandteil der Veroeffentlichung.
