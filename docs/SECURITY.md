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

LRC-Tags und Katalogzusätze werden ohne wiederholtes Durchsuchen ungepaarter
Klammern entfernt. Regressionen prüfen große fehlerhafte Eingaben in begrenzten
Unterprozessen sowie den Erhalt von Zeitstempeln, unvollständigen Tags und
Aufnahmebezeichnungen. Die vorhandenen API-Eingabelimits bleiben zusätzlich aktiv.

## Begrenzte Modellantworten und verbleibende Zielgrenze

Modelllisten und reine Anbietertextantworten werden während des Empfangs auf
2.000.000 Bytes begrenzt. Ein zu großer Content-Length-Wert wird vor dem Körper
abgewiesen; fehlende oder falsche Größenangaben ersetzen das laufende Bytebudget
nicht. Fehlerantwortkörper werden nicht gelesen, Streams auch bei Abbruch und
Zeitüberschreitung geschlossen. Diese Aufrufe fordern `Accept-Encoding: identity`
an und weisen unerwartet komprimierte Antworten vor dem Lesen ab. Das begrenzt
auch den Dekompressionspfad; Server müssen die angeforderte Identitätskodierung
unterstützen. Audio-/Modelldownloads besitzen getrennte Verträge.

Die Anbieter-Zielprüfung bindet eine DNS-Vorabprüfung derzeit nicht an die
spätere Verbindung. Kontrollierte eigene Loopbackserver bestätigen unterschiedliche
Auflösungen bei Prüfung und Verbindung sowie die Berücksichtigung eines
Umgebungsproxys. Redirects werden nicht verfolgt. Dies ist keine Freigabe für
feindliche Modellservernamen und keine Auflösung von CodeQL `py/full-ssrf`.
Lokale/LAN-Server bleiben bewusst unterstützt. Eine getrennte Korrektur muss
Zielbindung, TLS-Hostprüfung, IPv4/IPv6, Proxyverhalten und bestehende
Empfänger-/Zustimmungssnapshots gemeinsam prüfen.
