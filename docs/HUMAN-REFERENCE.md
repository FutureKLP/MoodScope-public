# Menschliche Musikbewertungen als externe Referenz

Aktualisierung: Die neue Pipeline v7 integriert die technische Pegelkontrolle und
entfernt untrainierte Merkmalszuschlaege. Die folgenden Vergleiche beschreiben
den vorherigen Stand; ein semantisch validierter Modellwechsel steht weiterhin
aus. Aktueller Implementierungsstand: [DEVELOPMENT.md](DEVELOPMENT.md).

Menschliche Emotionsurteile und Interpretationsprosa beantworten unterschiedliche
Fragen. Rezensionen und Songdeutungen koennen Gegenlesarten liefern; sie
bestaetigen weder gemessene Akkorde noch die emotionale Absicht einer Aufnahme.
Modellantworten werden nicht als menschliche Referenz ausgegeben.

## Tatsächlich untersuchte Quelle

[Emotify, Universitaet Utrecht](https://www2.projects.science.uu.nl/memotion/emotifydata/)
stellt menschliche Einzelantworten und einminuetige Hoerbeispiele bereit.
Die neun Dimensionen umfassen Verwunderung, Feierlichkeit/Transzendenz,
Zaertlichkeit, Nostalgie, Ruhe, Kraft, freudige Aktivierung, Spannung und Trauer.
Je Antwort konnten hoechstens drei stark empfundene Gefuehle ausgewaehlt werden.

Erhoben wurden **ausgeloeste Gefuehle**, nicht ausschliesslich der wahrgenommene
Ausdruck der Musik. Dies ist ein separater Vergleich, kein vollstaendiger
Zielbenchmark fuer MoodScope. Nichtauswahl beweist keine Emotionsfreiheit.

Der lokale Vergleich verwendet 32 Hoerbeispiele, acht je Genre Rock, Pop, Klassik
und Elektronik, mit festem Auswahlseed. Nur die gewaehlten Archivdateien wurden
ueber HTTP-Teilabrufe geladen. Musik, Bewertungen, Auswahl und Modellergebnisse
bleiben in ignorierten Testordnern. Demografische Spalten und persoenliche
Vorabstimmungen werden weder ausgewertet noch an ein Modell uebergeben.

Die Annotationen haben globale IDs 1 bis 400, das Audioarchiv dagegen Nummern
1 bis 100 innerhalb jedes Genres. Das Werkzeug prueft diese Zuordnung und die
Dateihashes. Antworten oberhalb der protokollierten maximalen drei Kategorien
werden ausgeschlossen und gezaehlt. Es werden keine Bewerteridentitaeten erfunden.

## Auswertung

`scripts.emotify_evaluation` arbeitet offline mit einem expliziten vorhandenen
CLAP-Snapshot, ohne Downloads und ohne App-Datenbank. Es vergleicht:

- unveraenderte Sechs-Kategorien-Beschreibungen;
- neun an der Datensatzbeschreibung orientierte GEMS-Beschreibungsgruppen;
- unabhaengige Kosinusaehnlichkeiten und dieselben Beschreibungen mit Softmax;
- Originalpegel und eine diagnostische konstante Pegelkontrolle.

Die komplette Minute wird im Fuenf-Sekunden-Raster mit bis zu zehn Sekunden
Kontext verarbeitet. Dauergewichtete Mittel werden mit den Urteilen ueber das
gesamte Hoerbeispiel verglichen. Songurteile sind keine zeitgenauen Annotationen.
Die menschlichen Antwortanteile werden nicht auf Summe eins reduziert.

Berichtet werden Rangkorrelationen je Dimension. Nur direkt passende breite
Kategorien der alten Pipeline werden zugeordnet; fehlende Kategorien erhalten
keine erfundenen Nullvorhersagen. Antwortanteile sind keine Intensitaetsmessung.
Die kleine Stichprobe beweist weder Stilunabhaengigkeit noch Signifikanz. Es
wurden keine Parameter auf diesen Beispielen trainiert oder kalibriert.

Der Vergleich begruendet keinen pauschalen Wechsel zu unabhaengigen
CLAP-Abfragen. Ihre Eignung unterscheidet sich nach Dimension. Die Trennung der
Analyseebenen ist sinnvoll, eine neue produktive Emotionstaxonomie damit noch
nicht allgemein validiert.

[DEAM und das Benchmark-Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC5345802/)
sind eine weitere Referenz fuer wahrgenommene Valenz und Aktivierung. Die
offizielle Downloadquelle war in dieser Runde nicht erreichbar; ein erfolgreicher
DEAM-Audiovergleich wird nicht behauptet. Auch DEAM allein validiert nicht alle
Ausdrucksfacetten, Klanghaerte und Interpretationsqualitaet.

Datensatzbedingungen und Zitation bleiben zu beachten. Referenzmusik,
Bewertungen und Modellantworten werden nicht im Repository verteilt.

## Umsetzung in der App

Die bisherige Emotionskurve bleibt Vergleichsbasis, bis ein Ersatz an passenden
menschlichen Referenzen besser belegt ist. Die Pegelkontrolle bleibt ein Versuch,
kein automatisch aktivierter Eingriff in Nutzeraufnahmen. Energie kann einen
Ausdruck unterstreichen; daraus wird kein festes Gefuehl abgeleitet.

**Musikbelege einbeziehen** ergaenzt einen experimentellen Musik-/Textvergleich.
Energieentwicklung, Tempo- und Harmoniekandidaten tragen Zeitbereiche und
werden getrennt von der moeglichen Lesart angezeigt. Globale Energieentwicklung
ist nicht der triviale Abstand des Songs zu seinem eigenen Mittelwert. Lokale
Messungen zeigen ihre tatsaechlichen Quellfenster, keine feinere Scheingenauigkeit.

Das Sprachmodell hoert kein Audio. Es erhaelt kompakte Beobachtungen mit
M-Referenzen und Textbelege mit Zeiten. Die unvalidierte Kategorienrangfolge
wird nicht als Textdeutungsauftrag uebergeben. Eigene Notizen und unsichere
Instrumenthinweise bleiben ausgeschlossen. Ausfuehrliche Musikangaben werden
unabhaengig vom Modell gerendert. Vorhandene Referenzen und bestimmte unbelegte
Audioaussagen werden geprueft; das beweist keine semantische Richtigkeit.

Der reale Qwen-1.5B-Vergleich zeigte weiterhin inhaltliche Schwaechen,
Sprachwechsel und Verletzungen der Belegregeln. Eine vereinfachte Darstellung
ermoeglichte auch eine syntaktisch gueltige referenzierte Ausgabe, bewies aber
keine allgemein bessere Interpretation. Die Option bleibt experimentell und
zunaechst ausgeschaltet. Ungueltige Antworten werden verworfen, ohne
automatischen kostenpflichtigen Ersatzanbieter.

Textdeutung und Musikvergleich werden pro Sprache, Modellprofil und Gesamt-/
Positionsdeutung getrennt gespeichert und gemeinsam vom Analyse-Cache-Loeschen
erfasst. Alte Textdeutungen bleiben wiederherstellbar. Der optionale API-Vertrag
wird mit Frontend und Startern als Revision 11 versioniert. Die Audio-Pipeline
und ihre alten Ergebnisse werden nicht umetikettiert.
