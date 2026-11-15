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
