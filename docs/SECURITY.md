# Sicherheitsstand und Grenzen

Entwicklungsversion, keine Freigabe als gehärteter öffentlicher Dienst.
Der Dienst bindet an Loopback. Host-/Origin-Prüfung ersetzt keine Authentifizierung
gegen andere lokale Prozesse. LAN-Server nur innerhalb der eigenen Vertrauensgrenze.

Entfernte Anbieter benötigen HTTPS; explizite lokale/LAN-Ziele dürfen HTTP nutzen.
Keine eingebetteten URL-Zugangsdaten und keine Keyweiterleitung über Redirects.
Schlüssel bleiben im Backend-Arbeitsspeicher. Zustimmung bindet Ziel, Modell,
Protokoll, Fähigkeiten und Sitzung. Es gibt keine automatische Anbieterumleitung.
Profil-/Key-Snapshots gelten pro Auftrag. Logs enthalten Fehlertypen und
Codepositionen; Lyrics, Antworten und Zugangsdaten gehören nicht in Logs.

Eigene Transformers-Modelle benötigen Safetensors, festgelegte Revisionen und
`trust_remote_code=False`. Offizielle Demucs-Gewichte werden über begrenzte
Downloadpfade mit Herausgeber-Prüfsummen geladen. Das ersetzt keine Bibliothekspatches.

Veröffentlichungsprüfung kontrolliert den vorgemerkten Baum, erreichbare frühere
Dateiversionen und Commit-Metadaten. Musterprüfungen garantieren keine Erkennung
jedes Geheimnisformats; Dateien müssen zusätzlich inhaltlich geprüft werden.

Kein neuer vollständiger Advisory-Abgleich in dieser Quellvorbereitung.
Historisch dokumentierte Rust-Restpunkte: glib 0.18.5 und proc-macro-error 1.0.4
im GTK/Linux-Zweig. Keine Linux-Sicherheitsfreigabe. Externe Downloadwerkzeuge
und FFmpeg benötigen gesonderte Pflege und Prüfung. [OSV](https://osv.dev/).
