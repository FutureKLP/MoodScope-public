# Audiowiedergabe und Export

Player, Kurve, Detailansichten und Atmosphäre verwenden dieselbe Medienzeit.
PlaybackClock hält häufige Zeitupdates von unveränderten Formularen getrennt.
Stemwiedergabe verwendet eine gemeinsame Startzeit; Gainänderungen während des
Ladens bleiben wirksam. Pause/Resume und Quellwechsel erhalten die Timeline.
Audiokontexte und Decoder werden bei Fehlern und Unmount freigegeben.

Der direkte Solo-Mix prüft auch bei vorhandenen Energiewerten im Manifest
blockweise endliche Audiosamples vor der Auslieferung. NaN und Unendlichkeiten
werden wie im Mehrspurpfad verworfen; die Quelldatei bleibt unverändert.

Mix-Caches berücksichtigen den Quellenstand. WAV-Exporte prüfen RIFF-Länge,
Format, Datenblöcke und Framegröße vor Ersetzung eines vorhandenen Ziels.
Fehlgeschlagene Transfers erhalten dessen bisherigen Inhalt. Eine bewusst
gewählte Zieldatei kann nach erfolgreichem Transfer ersetzt werden.

Vier oder experimentell sechs Demucs-Gruppen bedeuten keine Isolation einzelner
Sänger. Samplegenaue Phasenkohärenz, allgemeine Hörqualität und Langzeitstabilität
sind nicht nachgewiesen. Native Speicherdialogabbrüche sind im definierten
synthetischen Windows-Umfang geprüft. Phase 2C ergänzt echte lokale Demucs-
Trennung, native Solo-/Mehrspur-/Gain-Exporte mit numerischem Vergleich und
App-/Dienstneustart. 32 Player-/Kurvenpaare zeigten maximal 23,3 ms Anzeigedifferenz;
dies misst weder Decoderdrift pro Spur noch Audioausgabelatenz.
[Phase-2C-Matrix und offene Kriterien](PHASE2C-ACCEPTANCE.md),
[Kernabnahme](CORE-ACCEPTANCE.md). Keine Musikdaten werden als Testfixtures verteilt.
