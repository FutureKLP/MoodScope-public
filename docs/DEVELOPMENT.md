# Entwicklungsstand 0.3

Anbieteraufgaben binden Zustimmung, Ziel, Modell und Sitzungsschlüssel an einen
geprüften Jobstand. Profile und lokale Modelle bleiben gespeichert; Schlüssel
und Zustimmung werden nach Backendneustart erneut benötigt. Deutsch und Englisch
sowie die gemeinsame Farbquelle für Balken und Atmosphäre bleiben erhalten.

Bibliothekslöschung nutzt Journal und SQLite-Markierung für Wiederherstellung.
Fehlende oder beschädigte verwaltete Kopien lassen sich durch Wiederimport
reparieren. Originalmusik gehört nicht zur Löschplanung. Live-Stems verwenden
eine gemeinsame Zeitbasis; WAV-Transfers prüfen vollständige Blöcke und Frames
vor Zielersetzung. PlaybackClock entkoppelt Medienzeit von unveränderten Ansichten.
Verspätete Detail- und Speicherantworten dürfen neuere Zustände nicht überdecken.

Backendabbrüche, Modellfreigabe, endliche Analysewerte und Textbelege sind
zusätzlich abgesichert. Keine Garantie für Wortgenauigkeit, Sängerisolation,
Instrumentpräsenz oder präzise zeitliche Emotionen. SQLite bleibt Standard;
die externe Datenbankphase ist nicht freigegeben.

[Prüfbefehle](TEST-BASELINE.md), [Abnahmegrenzen](CORE-ACCEPTANCE.md),
[Lizenzen](THIRD-PARTY.md) und [Änderungen](PUBLIC-RELEASE-NOTES.md).
