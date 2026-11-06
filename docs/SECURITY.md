# Sicherheitsstand

Stand: 6. November 2026. Entwicklungsversion, keine Freigabe als gehärteter öffentlicher Dienst.

## Geprüft und korrigiert

- npm-Audit: keine bekannten Meldungen in den installierten JavaScript-Abhängigkeiten.
- OSV-Abgleich: 92 Pakete der isolierten Python-3.13-Umgebung geprüft, keine bekannten Meldungen im ausgeführten Abgleich. PyTorch 2.15, Transformers 5.22.1 und filelock 4.2.1 ersetzen die zuvor beanstandeten Versionen. Das ist keine Garantie gegen unbekannte Schwachstellen.
- Dienst nur auf Loopback starten. Host-/Origin-Prüfung verwirft fremde Browser-Ursprünge einschließlich `null`; entsprechende Regressionstests bestehen. Dies ist keine Authentifizierung gegenüber anderen lokalen Prozessen.
- Provider-URLs ohne eingebettete Zugangsdaten; HTTPS für entfernte Server, HTTP nur für explizit konfigurierte lokale/LAN-Server. Keine Weiterleitung von API-Schlüsseln über HTTP-Redirects. LAN-Server nur innerhalb der eigenen Vertrauensgrenze verwenden.
- Schlüssel verbleiben im Backend-Arbeitsspeicher. Validierungsantworten enthalten keine ursprünglichen Eingabewerte. Logs speichern Fehlertypen und Codepositionen; keine Modellantworten oder Lyrics. Kein ungeprüftes HTML aus KI-Ausgaben.
- Demucs-Downloads sind auf die verpackten offiziellen Modelle begrenzt; TLS, Dateigrößen-/Zeitlimit und Herausgeber-Prüfsummen. `weights_only=True` bleibt aktiv; nur die benötigten Typen des offiziellen HTDemucs-Pakets werden während des Ladens freigegeben.
- Vorgegebene sowie eigene kompatible öffentliche Hugging-Face-Modelle; eigene Revisionen werden festgelegt, `auto_map` wird verworfen und `trust_remote_code=False` bleibt aktiv. Eigene Transformers-Modelle und lokale Interpretation laden ausschließlich Safetensors. Keine beliebigen Downloadhosts und kein fremder Python-Modellcode. Das reduziert Angriffsflächen, ersetzt aber keine Bibliothekspatches.
- Veröffentlichungsprüfung kontrolliert ausgewählte Dateien, erreichbare frühere Dateiversionen, Commit-Texte und E-Mail-Metadaten. Lokale Entwicklungsanweisungen werden ebenso ausgeschlossen wie Musik, Schlüssel, Notizen, Ausgaben und Modelle.

## Offene Bibliotheksmeldungen

Die validierte projektlokale Umgebung ist jetzt der Standard. Die ältere Python-Umgebung bleibt nur als lokale Rückfallinstallation erhalten und wurde nicht systemweit verändert.

OSV-Abgleich des Rust-Lockfiles: 414 Registry-Pakete geprüft, einschließlich der ergänzten nativen Export-Abhängigkeiten. Offen sind glib 0.18.5 (VariantStrIter-Unsoundness, korrigiert ab 0.20.0) und ein Wartungshinweis zu proc-macro-error 1.0.4. Das betrifft den GTK/Linux-Abhängigkeitszweig; keine vollständige Linux-Sicherheitsfreigabe. Externe Downloadwerkzeuge wurden nicht vollständig mit einer eigenen Advisory-Datenbank auditiert. FFmpeg und yt-dlp ebenfalls aktuell halten.

Primärquellen: [OSV](https://osv.dev/), [filelock](https://github.com/advisories/GHSA-8mx5-7m5m-r77g), [PyTorch](https://github.com/advisories/GHSA-rrmf-rvhw-rf47), [Transformers](https://github.com/advisories/GHSA-x9r9-c232-4q39).

## Repository-Historie

Die Hauptbranch enthält neu geschriebene technische Commit-Texte; lokale Agent-Regeln wurden auch aus ihren früheren Entwicklungsständen entfernt. Es werden keine Entwicklungsordner oder lokalen Hilfsdateien veröffentlicht. Vor einer öffentlichen Freigabe werden der veröffentlichte Stand und die erreichbare Branch-Historie erneut geprüft. Ein Rewrite entfernt alte Commits aus der erreichbaren Branch-Historie, erzwingt jedoch keine Löschung aus fremden Klonen oder GitHubs internen Caches. Falls jemals ein echter Schlüssel veröffentlicht würde, müsste er zusätzlich widerrufen werden.
