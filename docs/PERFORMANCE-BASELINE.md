# Performance prüfen

Die wiederverwendbaren Werkzeuge messen getrennt Modelllaufzeit, Cache,
Ressourcen und React-/SVG-/Atmosphärenkosten. Erzeugte Signale sind synthetische
Diagnosefixtures; sie sind keine Musik-, Hörqualitäts- oder Emotionsabnahme.
Historische synthetische Benchmarks gelten nicht als aktuelle Musikmessung.

`python -m scripts.performance_baseline --help` beschreibt den Offlineprüfhalter.
Er verwendet separate Prozesse und ignorierte Ausgaben, lädt keine Gewichte
herunter und darf nicht auf die produktive Bibliothek zeigen.
`scripts/performance/vite.config.ts` erstellt einen separaten React-Profilingbuild;
`scripts/performance_browser.mjs` misst ihn mit einem ausdrücklich angegebenen
Browser. Profile, Audio, Logs und Messergebnisse bleiben lokal und ignoriert.

Vorher/Nachher nur bei gleicher Quelle, Umgebung, Auflösung und Funktion
vergleichen. Inklusive Reactzeiten sind keine End-to-End-Framezeiten.
Langzeit-/GPU-/Plattformfreigaben müssen separat belegt werden.

## Phase 3 am 20./21. November 2026

[Messbedingungen, Ergebnisse und offene Grenzen](PHASE3-PERFORMANCE-ACCEPTANCE.md).
Neue Musikmessungen sind von den historischen synthetischen Benchmarks getrennt:
zwei kurze überlappende Ausschnitte derselben lokalen Aufnahme, keine breite
Musikabdeckung. CPU-/CUDA-Läufe, direkte Cacheaufrufe und HTTP-Pollingzeiten
nicht miteinander vermischen. Kaltstart bedeutet frischen Prozess, keinen
geleerten Betriebssystem-Dateicache.

Zehn native Original-/Mixzyklen schließen zehn Contexts und trennen 90 Nodes.
Ein zusätzlicher Graph bleibt bei Ansichtswechsel erhalten und wird beim Songwechsel
geschlossen; alle 99 Nodes getrennt und acht Mixerlistener entfernt. Keine
physische Audioausgabemessung oder allgemeine Leckfreiheit. Die erste native
Prozesslebensdauer endet nach 17 Minuten 18,9 Sekunden; die Fortsetzung nach
Neustart dauert 6 Minuten 4,98 Sekunden und wird separat ausgewertet.
Unterbrechungszeit zählt nicht als Testdauer; kein einzelner 20-Minuten-Lauf.

Im ersten Prozess zwischen Minute 5 und 10: native RSS 589,60–618,45 MiB,
Private Bytes 395,50–490,99 MiB, 5.246–5.324 Handles, acht Prozesse.
Spätere Song-/Modell-/Atmosphärenwechsel verändern die Last; deren höhere
Private-Bytes-Spitzen sind kein vergleichbarer Lecknachweis und bleiben im
Abnahmebericht sichtbar. Kein verbindliches Speicherbudget vorhanden.

Zweite Prozesslebensdauer, letzte Minute mit konstantem Originalloop/Atmosphäre:
native RSS 606,46–609,59 MiB, Private Bytes 573,91–603,78 MiB und 5.254–5.266
Handles. Kein Vergleich absoluter Werte verschiedener Neustarts als Leaktrend.
493 SQLite-Verbindungen im instrumentierten zweiten Dienstlauf geschlossen,
abschließend null aktiv; keine Inferenzworkerreste. Vollständiger Neustartvergleich
der SQLite-Zeilen und Audio-/Stemhashes identisch. Physische Audioausgabe offen.

## Phase 3.2 am 21. November 2026

Neuer einzelner Lauf: **20 Minuten 54,51 Sekunden**, 251 Proben, maximal
5,025 Sekunden Abstand, dieselbe App-/Dienstlebensdauer. Historische getrennte
Sitzungen oben bleiben unverändert. Zehn native Mixzyklen schließen zehn
Contexts/90 Nodes, kein erzwungener GC. Zwei kurze Ausschnitte derselben erlaubten
Aufnahme, keine breite Musik- oder Ausgangsqualitätsabnahme.

Im selben Prozess: konstanter Live-Mix ohne Atmosphäre 411,95–417,75 MiB
Private Bytes; mit Atmosphäre 500,69–524,42 MiB. Nach Context-Freigabe und
Atmosphäre aus 412,00–415,27 MiB. Bei weiteren neun gezielten Graphzyklen
steigt der Speicher auch in Originalzuständen nach Freigabe bis etwa 656 MiB;
JS-Heap während der Folge 3,82–6,69 MiB. Kein fortlaufender Handletrend,
keine bestätigte Allokations-/Leckursache und kein Leckfreiheitsnachweis.
Die Zustandswechselspitze der nativen Familie beträgt 711,88 MiB Private Bytes,
RSS maximal 810,77 MiB. Dienst-Modelllast und nativen Speicher getrennt halten.

Echte Offline-CLAP-Neuberechnung per HTTP bei nativer Wiedergabe: 12,03 s.
210 Dienst-SQLite-Verbindungen geschlossen, keine aktiven Verbindungen oder
eigenen Workerreste. Regressionen/Builds erst nach Sitzungsende. Phase 3 bleibt
teilweise bestanden; [vollständige Zustandsfenster, Grenzen und Diagnose](PHASE3-PERFORMANCE-ACCEPTANCE.md#phase-32-ununterbrochener-nachlauf-und-speicherdiagnose).
