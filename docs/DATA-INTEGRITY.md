# Musikdaten und Wiederherstellung

Importquellen werden nur gelesen. Die Anwendung erstellt eigene Stereo-WAVs
im Datenordner. Originalpfade gehören nicht zur Löschplanung. Wiederimport
derselben Quelle erhält Notizen, Metadaten und Analysen. Beschädigte verwaltete
Kopien werden vor Reparatur separat erhalten; fehlende Kopien sind reparierbar.

Bibliothekslöschung verschiebt verwaltete Kopien und Stems in eine Quarantäne.
Ein synchronisiertes Journal geht den Dateiverschiebungen voraus. Trackfamilie,
Notizen, Caches und Löschmarkierung werden gemeinsam in SQLite geschrieben.
Nach Prozessneustart entscheidet die persistierte Markierung über Rücknahme
oder Fertigstellung. Bei Zielkonflikten bleiben beide Dateistände erhalten.
Ein späterer Wiederimport darf nicht von einer alten Bereinigung entfernt werden.

Cache löschen erhält Notizen und Audio. Song/Bibliothek entfernen erfasst auch
eigene Notizen und verwaltete Kopien; Originalmusik und Modelle bleiben erhalten.
Reparaturkopien und alte Quarantänen ohne Journal werden nicht automatisch entfernt.

SQLite-Verbindungen, Schemaöffnung, Transaktion, Abbruch und Freigabe sind in
`backend/persistence.py` gebündelt. Fachliche Abfragen verwenden SQLite-SQL;
dies ist kein austauschbarer externer Datenbankadapter. Mehrere unabhängige
Dienste auf demselben Datenordner sind nicht freigegeben. Prozessabbruchtests
belegen keine Sicherheit bei Stromausfall oder Datenträgerdefekten.

Stemheader, Aufnahmeverweise und endliche Music2Emo-Zeitbereiche werden geprüft.
WAV-Export ersetzt ein gewähltes Ziel erst nach vollständiger Transfer- und
Formatprüfung. Abnahmegrenzen stehen in [CORE-ACCEPTANCE.md](CORE-ACCEPTANCE.md).

## Music2Emo-Worker nach Prozessabbruch

Seit Phase 2B.3 erstellt ausschließlich der Music2Emo-Pfad Arbeitsbereiche unter
`.music2emo-workers-v1` im gewählten Datenordner. Ein Wurzelmarker und ein eigener
Auftragsmarker verbinden jeden zufälligen `job-`-Bereich mit dieser Wurzel.
Die Bereichskennung ist eine technische Ausführungskennung, kein Musikdateiname.
Originalaudio und Gewichte werden weiterhin nur außerhalb dieses Bereichs gelesen.

Der Dienst hält eine Elternsperre vom Anlegen des Markers bis zum Abschluss.
Der Worker hält eine zweite Betriebssystem-Dateisperre über die gesamte Inferenz;
vor Modellstart prüft er die Elternsperre. Ein Wächter prüft deren Fortbestand.
Reguläres Ende, Abbruch und Timeout warten weiterhin auf das Ende des eigenen
Workerprozesses. Ein hartes Dienstende kann kein Python-`finally` ausführen;
der separate Wächter beendet dann den Worker ohne Speicherung eines Teilresultats.
Es wird kein fremder Prozess anhand einer möglicherweise wiederverwendeten PID beendet.

Der Dienst prüft beim Start, alle fünf Sekunden sowie vor/nach einem Workerauftrag
die eigenen Bereiche. Nur passende Marker und zwei frei erwerbbare Sperren erlauben
eine Bereinigung. Der vollständige Baum wird vorab begrenzt geprüft: höchstens
4096 Einträge und zwölf Unterverzeichnisebenen, keine symbolischen Links,
Windows-Reparsepunkte, mehrfach verlinkten Dateien oder Spezialdateien.
Dateien und Verzeichnisse werden einzeln entfernt; kein allgemeines rekursives
Löschen des Daten- oder Tempordners. Ein Durchlauf betrachtet höchstens 1024
Wurzeleinträge. Unklare oder gesperrte Bereiche bleiben erhalten.

Alte `expression-*`-Ordner ohne Besitzmarker werden ausdrücklich nicht automatisch
übernommen. Auch bei beschädigten Markern, übergroßen Bäumen oder fehlenden
Sperrdateien gilt: erhalten statt eine Eigentümerschaft zu vermuten. SQLite,
Notizen, verwaltete Audiokopien, Originalmusik und Modelle gehören nicht zur
Bereinigungsmenge. Mehrere Dienste auf demselben Datenordner bleiben nicht freigegeben.

Grenze: Ein nativer Modellschritt, der den Python-Interpreter vollständig blockiert,
kann den Wächter verzögern. Solange der Prozess lebt und seine Sperre hält, wird
sein Bereich auch nach Dienstneustart nicht gelöscht. Nach tatsächlichem Prozessende
kann der nächste periodische Durchlauf aufräumen. Kein garantierter sofortiger
GPU-/Treiberrückbau bei einem Betriebssystem- oder Treiberhänger.
Regressions- und reale Dienstnachweise: [Phase 2B.3](PHASE2B-ACCEPTANCE.md#nachabnahme-2b3-vom-20-november-2026).
