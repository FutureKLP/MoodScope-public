# Backend und Analysegrenzen

Jobaufnahme und Profilmutation sind serialisiert. Jeder Auftrag erhält den
geprüften Ziel-/Key-Stand. Kooperative Abbrüche verhindern spätes Cache-Schreiben;
Modell-/Unterprozessfreigabe und Fehlercleanup sind regressionsgeprüft.
GPU-Schritte können bis zum nächsten sicheren Haltepunkt auslaufen.

Nicht endliche Modellwerte und ungültige Zeitbereiche werden verworfen.
Textdeutungen benötigen passende Zeilenbelege; dies ist kein Wahrheitsfilter.
Instrumenthinweise bleiben Hypothesen. Whisper liefert keine garantierte
vollständige Worterkennung; Demucs trennt keine einzelnen Sänger.

Die vorhandene diagnostische Referenzauswertung belegt keinen präzisen zeitlichen
Emotionsverlauf. Ein wiederholt betrachtetes Set ist kein neuer Holdout.
Analyseformeln und Gewichte wurden für diese Quellübernahme nicht neu kalibriert.
Ein sporadischer Music2Emo-Prüfdienstfehler bleibt offen. Einzelne erfolgreiche
CPU-/CUDA-Läufe ersetzen weder Ursachenklärung noch allgemeine Modellfreigabe.

[Offene Abnahmen](CORE-ACCEPTANCE.md) und [Testverfahren](TEST-BASELINE.md).
