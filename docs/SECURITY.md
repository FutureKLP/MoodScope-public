# Sicherheitsstand

Stand: 6. November 2026. Entwicklungsversion, keine Freigabe als gehärteter öffentlicher Dienst.

## Geprüft und korrigiert

- npm-Audit: keine bekannten Meldungen in den installierten JavaScript-Abhängigkeiten.
- OSV-Abgleich für 78 verwendete Python-Pakete samt transitiven Abhängigkeiten. Projektlokale Patches für certifi, requests, urllib3, idna, protobuf und fsspec installiert. filelock 3.20.3 behebt die früheren SoftFileLock-Rennen; neuere Legacy-Zweige führen zusätzliche Meldungen ein und werden nicht übernommen.
- Dienst nur auf Loopback starten. Host-/Origin-Prüfung verwirft fremde Browser-Ursprünge einschließlich `null`; entsprechende Regressionstests bestehen. Dies ist keine Authentifizierung gegenüber anderen lokalen Prozessen.
- Provider-URLs ohne eingebettete Zugangsdaten; HTTPS für entfernte Server, HTTP nur für explizit konfigurierte lokale/LAN-Server. Keine Weiterleitung von API-Schlüsseln über HTTP-Redirects. LAN-Server nur innerhalb der eigenen Vertrauensgrenze verwenden.
- Schlüssel verbleiben im Backend-Arbeitsspeicher. Validierungsantworten enthalten keine ursprünglichen Eingabewerte. Logs speichern Fehlertypen und Codepositionen; keine Modellantworten oder Lyrics. Kein ungeprüftes HTML aus KI-Ausgaben.
- Demucs-Downloads sind auf die verpackten offiziellen Modelle begrenzt; TLS, Dateigrößen-/Zeitlimit und Herausgeber-Prüfsummen. `weights_only=True` bleibt aktiv; nur die benötigten Typen des offiziellen HTDemucs-Pakets werden während des Ladens freigegeben.
- Kuratierte Modellliste, `trust_remote_code=False`; lokales Interpretationsmodell lädt ausschließlich Safetensors. Kein frei konfigurierbares Python-Modellrepository. Das reduziert Angriffsflächen, ersetzt aber keine Bibliothekspatches.
- Veröffentlichungsprüfung kontrolliert ausgewählte Dateien, erreichbare frühere Dateiversionen, Commit-Texte und E-Mail-Metadaten. Lokale Entwicklungsanweisungen werden ebenso ausgeschlossen wie Musik, Schlüssel, Notizen, Ausgaben und Modelle.

## Offene Bibliotheksmeldungen

Die vorhandene Python-3.10-Modellumgebung ist **nicht frei von bekannten Sicherheitsmeldungen**:

- filelock 3.20.3: GHSA-69hj-f68j-2879 und GHSA-8mx5-7m5m-r77g (Lockdateien/Dateirechte). Die korrigierte 4.2.1-Linie benötigt Python 3.11. Daten- und Modellordner nicht mit nicht vertrauenswürdigen Nutzern gemeinsam beschreibbar machen.
- PyTorch 2.8.0: Meldungen zu nicht vertrauenswürdigen Checkpoints sowie LSTM-/TorchScript-/Packed-Sequence-Pfaden. Die zuletzt gemeldete TorchScript-Korrektur liegt in 2.13.0. Beliebige Checkpoints werden nicht als App-Eingabe angeboten; die verbleibende Bibliotheksversion wird dadurch jedoch nicht gepatcht.
- Transformers 4.57.6: Meldungen zu Modellinitialisierung, Trainer, benutzerdefiniertem Generierungscode und Chat-Template-Speicherung. Mehrere Korrekturen liegen in 5.x. Die App nutzt kuratierte CLAP/XLM-EMO/Qwen-Modelle, keinen Trainer und keine Chat-Template-Exportfunktion. Keine generelle Unbedenklichkeitszusage.

Ein vollständiger Wechsel auf eine aktuelle Python-/PyTorch-/Torchaudio-/Transformers-Kombination samt erneuter CUDA-, CLAP-, Qwen- und Demucs-Kompatibilitätsprüfung ist noch erforderlich. Der aktuelle Lauf nimmt diesen großen Laufzeitwechsel nicht stillschweigend vor. OSV-Abgleich des Rust-Lockfiles: 406 Registry-Pakete geprüft. Offen sind glib 0.18.5 (VariantStrIter-Unsoundness, korrigiert ab 0.20.0) und ein Wartungshinweis zu proc-macro-error 1.0.4. Das betrifft den GTK/Linux-Abhängigkeitszweig; keine vollständige Linux-Sicherheitsfreigabe. Externe Downloadwerkzeuge wurden nicht vollständig mit einer eigenen Advisory-Datenbank auditiert. FFmpeg und yt-dlp ebenfalls aktuell halten.

Primärquellen: [OSV](https://osv.dev/), [filelock](https://github.com/advisories/GHSA-8mx5-7m5m-r77g), [PyTorch](https://github.com/advisories/GHSA-rrmf-rvhw-rf47), [Transformers](https://github.com/advisories/GHSA-x9r9-c232-4q39).

## Repository-Historie

Die Hauptbranch enthält neu geschriebene technische Commit-Texte; lokale Agent-Regeln wurden auch aus ihren früheren Entwicklungsständen entfernt. Es werden keine Entwicklungsordner oder lokalen Hilfsdateien veröffentlicht. Das Repository bleibt privat. Ein Rewrite entfernt alte Commits aus der erreichbaren Branch-Historie, erzwingt jedoch keine Löschung aus fremden Klonen oder GitHubs internen Caches. Falls jemals ein echter Schlüssel veröffentlicht würde, müsste er zusätzlich widerrufen werden.
