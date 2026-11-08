# Musik, Gefuehle und Darstellung

## Was die App unterscheiden muss

Wahrgenommener musikalischer Ausdruck und selbst empfundenes Gefuehl sind
unterschiedliche Ziele. Eine traurige Passage kann als angenehm, beruehrend oder
troestlich erlebt werden. Valenz (positive/negative Faerbung) und Aktivierung
(ruhig/angeregt) sind getrennte Dimensionen. Ein lauter, schneller Abschnitt darf
nicht allein deshalb als negativ oder aergerlich gelten.

Eine [experimentelle Untersuchung zu Tempo, Modus und Perkussivitaet](https://doi.org/10.1177/1029864911403364)
vergleicht subjektive Bewertungen mit physiologischen Reaktionen. Solche
Gruppeneffekte sind Hinweise auf Zusammenhaenge, keine allgemeingueltigen
Gewichte fuer beliebige Aufnahmen. Instrumentierung, Harmonie und Rhythmus
wirken gemeinsam; die App zeigt deshalb vorhandene Tempo- und Tonartkandidaten
als Belege und addiert keine erfundenen Gefuehlsboni.

Die [Untersuchung musikalischer Erwartungen](https://arxiv.org/abs/1708.03687)
behandelt Tonhoehen- und Zeitvorhersagbarkeit. Eine Akkordfolge allein misst
die Erwartung eines konkreten Hoerers nicht. Musikalische Erfahrung und Kontext
muessen bei einer kuenftigen lernenden Spannungsanalyse beruecksichtigt werden.

## Neurowissenschaftliche Einordnung

[Salimpoor et al.](https://www.nature.com/articles/nn.2726) untersuchten
Erwartung und besonders intensive angenehme Musikreaktionen mit PET/fMRI.
Die Beobachtung unterschiedlicher Belohnungsprozesse bedeutet nicht, dass
eine Audiodatei Dopaminausschuettung, Gehirnaktivitaet oder persoenliche
Gefuehle messbar macht. MoodScope behauptet keine solche Messung.

[Juslin und Kollegen](https://online.ucpress.edu/mp/article/40/1/55/192145/Emotions-Mechanisms-and-Individual-Differences-in)
untersuchen unterschiedliche Mechanismen und individuelle Unterschiede.
Erinnerungen, Vertrautheit, Vorlieben und Hoersituation sind zusaetzliche
Einfluesse, fuer die hier keine persoenlichen Eingangsdaten vorliegen.

## Konkrete Umsetzung

Die bestehende Audio-/Lyrics-Kurve kann direkt gelernte Music2Emo-Valenz anzeigen.
Die Gefuehlsbalken verwenden wieder visuelle Interpolation zwischen den
gespeicherten CLAP-Abschnitten; Rohwerte und Formel bleiben separat sichtbar.
Es gibt keine zusaetzliche zweidimensionale Grafik. Die Erklaerung musikalischer
Einfluesse und Quellen bleibt aufklappbar.

Die Atmosphaere verwendet weiterhin sechs konsistente Gestaltungsfarben.
[Palmer et al.](https://doi.org/10.1073/pnas.1212562110) zeigen in ihren
Experimenten emotionsvermittelte Musik-Farb-Assoziationen. Daraus folgt keine
universelle biologische Zuordnung unserer sechs Hex-Farben.

Fuer die Darstellung werden gueltige Kategoriescores normiert. Alle Anteile
bleiben in der Grundmischung erhalten. Ein zusaetzlicher Farbakzent fuer die
fuehrende Kategorie nimmt stetig mit dem Abstand zum zweiten Rang zu; bei
Gleichstand ist dieser Akzent null. Das ist ausschliesslich eine gestalterische
Gewichtung, keine Aenderung der Scores oder der Emotionserkennung.
Die Unterfarben verwenden ihre unveraenderten relativen Anteile. Die Textfarbe
beeinflusst den sekundaeren Hintergrund nur zu 12 Prozent; ohne Textwerte
uebernimmt er die Audiofarbe. Energie und Tempo steuern weiterhin nur Bewegung.
Reduzierte Bewegung bleibt beruecksichtigt.

## Was eine neue Bewertungsmethode nachweisen muss

Parameter und Modelle werden auf menschlichen Zeitreferenzen verglichen.
Neben absolutem Fehler zaehlt, ob Schwankungen innerhalb eines Songs besser
getroffen werden als mit einer konstanten Modellvorhersage. Wiederholt
betrachtete Beispiele gelten als Diagnosematerial. Eine produktive Umstellung
braucht zusaetzlich unberuehrte Referenzen und eine Pruefung verschiedener
Genres, Pegel und gegensaetzlicher Kombinationen von Valenz und Aktivierung.
Ein ansprechenderer Farbverlauf allein ist kein Qualitaetsnachweis.


## Vertiefung: Text, musikalische Mittel und Gefuehlsbalken

Die [GEMS-Forschungsgruppe](https://musemap.org/resources/gems) unterscheidet
neun musikspezifische Gefuehlsbereiche, darunter Kraft, Nostalgie, Zartheit,
Ruhe und Spannung. Die Skala misst Selbstberichte von Hoerern; das Benennen
dieser Bereiche macht einen Audioklassifikator noch nicht gueltig.
[Cowen et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6995018/) fanden in
US-amerikanischen und chinesischen Stichproben ein breiteres Spektrum
unterschiedlicher, ineinander uebergehender Erfahrungen. Daraus folgt fuer
MoodScope: koexistierende Gefuehle zulassen und Kraft nicht pauschal als
Aerger oder negative Valenz interpretieren.

[Eine experimentelle Untersuchung musikalischer Mittel](https://pmc.ncbi.nlm.nih.gov/articles/PMC3726864/)
manipuliert mehrere Merkmale und untersucht ihre Beitraege zu Emotionsurteilen.
Die Bedeutung eines Merkmals variiert mit Gefuehl und musikalischer Struktur.
Eine Formel wie "schnell + laut = aergerlich" wuerde diese Befunde verkuerzen.

Die [fMRI-Studie zu Musik mit und ohne Text](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2011.00308/full)
unterscheidet musikalischen Ausdruck, eigenes Gefuehl und Gefallen.
Eine spaetere [praeregistrierte Replikation mit 104 Personen](https://journals.sagepub.com/doi/10.1177/10298649221149109)
widersprach fuer mehrere Variablen den frueheren Ergebnissen zum Einfluss von
Text und Melodie. Deshalb erhalten Audio und Lyrics keine pauschale gemeinsame
Gewichtung. Der vorhandene Vergleich zeigt ihre Beziehung zeitlich; ein Abstand
ist keine gemessene emotionale Wirkung des Gesamtstuecks.

Ein zusaetzlicher echter CLAP-Lauf verglich ueberarbeitete GEMS-Beschreibungen
auf denselben 32 Emotify-Beispielen mit menschlichen Gefuehlsangaben. Die neue
Variante verbesserte einzelne Kategorien, verschlechterte andere und war im
Durchschnitt der neun Rangkorrelationen nicht besser. Sie wird deshalb nicht
als neue produktive Balkenbewertung aktiviert. Der Lauf ist mit
`scripts.emotify_evaluation --descriptor-profile revised` reproduzierbar.
Wiederholt betrachtete Daten bleiben diagnostisch; ausgeloeste Gefuehle sind
keine zeitgenaue Referenz fuer wahrgenommenen Ausdruck.
