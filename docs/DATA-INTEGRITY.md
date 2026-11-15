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
