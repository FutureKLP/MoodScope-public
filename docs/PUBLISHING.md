# Veröffentlichungsablauf

Zwischenstände werden zuerst im privaten Backup-Remote gesichert. Die öffentliche Ablage erhält erst funktionierende, getestete und bereinigte Veröffentlichungsstände. Die Sichtbarkeit einer Ablage wird nur auf ausdrücklichen Wunsch geändert.

## Inhalt

Veröffentlicht werden Quellcode, projektgenerierte Icons, Abhängigkeits-Lockdateien, Tests und bereinigte Dokumentation. Keine Zugangsdaten, persönlichen Kontaktdaten, Benutzerpfade, Screenshots, privaten Songmetadaten oder Emoji-Zeichen.

Der gesamte Testmusikordner bleibt ausgeschlossen, einschließlich aller Unterordner und abgeleiteten Inhalte. Audio, Songtexte, Analyseergebnisse, SQLite-Dateien, Modelle, Installationsdateien, lokale Werkzeuge und virtuelle Umgebungen bleiben lokal.

## Private Zwischenstände

Gezielt ausgewählte App-Quellen regelmäßig privat committen und sichern. Auch dort keine Musik, Lyrics, Zugangsdaten, Gewichte, persönlichen Notizen, erzeugten Ergebnisse oder lokalen Versuchswerkzeuge vormerken. Ein privater Commit ist noch keine Freigabe zur öffentlichen Veröffentlichung.

## Öffentliche Übernahme

Die öffentliche Veröffentlichung verwendet einen eigenen Branch `codex/public-release`. Sein neuer Commit enthält den geprüften Quellbaum und hat ausschließlich den vorherigen öffentlichen Stand als Elterncommit. Private Zwischenstände werden nicht gemergt oder als Vorfahren übernommen. Relevante Tests, Builddateien und Dokumentation gehören zur App-Entwicklung; persönliche und rein lokale Inhalte nicht.

Die Remote-Zuordnung und URLs bleiben lokale Git-Einstellungen. Der normale Push wird lokal auf das private Backup gerichtet. Ein öffentlicher Push erfolgt ausdrücklich vom Veröffentlichungsbranch.

## Vor jeder öffentlichen Übernahme

1. Änderungen gezielt vormerken; keine ignorierten Dateien erzwingen.
2. `python scripts/check_publication.py` ausführen. Die Prüfung liest die tatsächlich vorgemerkten Git-Inhalte.
3. Relevante Tests und Buildprüfungen ausführen.
4. Commit mit einer Projektidentität und einer GitHub-noreply-Adresse erstellen. Keine persönliche E-Mail-Adresse verwenden.
5. `python scripts/check_publication.py --ref codex/public-release` ausführen. Diese Prüfung kontrolliert auch frühere Dateiversionen und E-Mail-Adressen in der erreichbaren Commit-Historie. Ein später gelöschtes Geheimnis blockiert die Veröffentlichung weiterhin.
6. Den geprüften Commit übertragen und den GitHub-Stand kontrollieren.

Optional lokal `git config core.hooksPath .githooks` setzen. Der enthaltene pre-push-Hook prüft über `scripts/check_push.py` die tatsächlich übertragenen Referenzen statt pauschal `HEAD`. Bei lokal konfigurierter öffentlicher Ablage blockiert er direkte Pushes vom Arbeitsbranch und private Zwischenstände in der vorgeschlagenen öffentlichen Vorgeschichte. Ein CI-Schritt prüft veröffentlichte Commits zusätzlich; dieser ersetzt die Kontrolle vor dem Upload nicht.

Die Musterprüfung erkennt verbreitete Tokenformate und verdächtige Zugangsdatenzuweisungen. Sie ist keine Garantie für beliebige Geheimnisformate oder semantisch persönliche Angaben. Änderungen müssen zusätzlich gelesen werden. Bei einem Fund wird nicht veröffentlicht; Fundwerte werden nicht in Logs ausgegeben.
