# Audiowiedergabe und Export

Player, Kurve, Detailansichten und Atmosphäre verwenden dieselbe Medienzeit.
PlaybackClock hält häufige Zeitupdates von unveränderten Formularen getrennt.
Stemwiedergabe verwendet eine gemeinsame Startzeit; Gainänderungen während des
Ladens bleiben wirksam. Pause/Resume und Quellwechsel erhalten die Timeline.
Audiokontexte und Decoder werden bei Fehlern und Unmount freigegeben.

Mix-Caches berücksichtigen den Quellenstand. WAV-Exporte prüfen RIFF-Länge,
Format, Datenblöcke und Framegröße vor Ersetzung eines vorhandenen Ziels.
Fehlgeschlagene Transfers erhalten dessen bisherigen Inhalt. Eine bewusst
gewählte Zieldatei kann nach erfolgreichem Transfer ersetzt werden.

Vier oder experimentell sechs Demucs-Gruppen bedeuten keine Isolation einzelner
Sänger. Samplegenaue Phasenkohärenz, allgemeine Hörqualität und Langzeitstabilität
sind nicht nachgewiesen. Nativer Exportabbruch und Desktopmatrix bleiben offen:
[Kernabnahme](CORE-ACCEPTANCE.md). Keine Musikdaten werden als Testfixtures verteilt.
