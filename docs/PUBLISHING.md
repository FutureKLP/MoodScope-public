# Veröffentlichungsablauf

Die Entwicklung verwendet die öffentliche Repositoryhistorie. Geprüfte Quellcommits, Pushes, Pull Requests und Merges erfolgen im öffentlichen Repository. Frühere Vorgaben zur Sicherung in einem privaten Remote sind aufgehoben. Die Sichtbarkeit einer Ablage wird nur auf ausdrücklichen Wunsch geändert.

## Inhalt

Veröffentlicht werden Quellcode, projektgenerierte Icons, Abhängigkeits-Lockdateien, Tests und bereinigte Dokumentation. Keine Zugangsdaten, persönlichen Kontaktdaten, Benutzerpfade, Screenshots, privaten Songmetadaten oder Emoji-Zeichen.

Der gesamte Testmusikordner bleibt ausgeschlossen, einschließlich aller Unterordner und abgeleiteten Inhalte. Audio, Songtexte, Analyseergebnisse, SQLite-Dateien, Modelle, Installationsdateien, lokale Werkzeuge und virtuelle Umgebungen bleiben lokal.

## Lokale Zwischenstände

Gezielt ausgewählte App-Quellen regelmäßig lokal committen. Nur funktionierende, getestete und bereinigte Quellstände pushen. Keine Musik, Lyrics, Zugangsdaten, Gewichte, persönlichen Notizen, internen Übergabeberichte, erzeugten Ergebnisse oder lokalen Versuchswerkzeuge vormerken. Lokale Arbeitsstände mit solchen Inhalten bleiben von der öffentlichen Historie getrennt.

## Öffentliche Übernahme

Die Entwicklung verwendet den Branch `codex/public-release` auf Basis der vorhandenen öffentlichen Historie. Private Entwicklungsbranches werden niemals als Vorfahren übernommen. Änderungen an `main` erfolgen über geprüfte Pull Requests mit erfolgreichen Pflichtchecks und aufgelösten Diskussionen; Branchschutz nicht umgehen. Relevante Tests, Builddateien und Dokumentation gehören zur App-Entwicklung; persönliche und rein lokale Inhalte nicht.

Die Remote-Zuordnung und URLs bleiben lokale Git-Einstellungen. Der normale Push des Veröffentlichungsbranches zielt auf `origin`. Pushes zum früheren privaten Remote sind lokal gesperrt; archivierte Entwicklungsbranches bleiben erhalten.

## Vor jeder öffentlichen Übernahme

1. Änderungen gezielt vormerken; keine ignorierten Dateien erzwingen.
2. `python scripts/check_publication.py` ausführen. Die Prüfung liest die tatsächlich vorgemerkten Git-Inhalte.
3. Relevante Tests und Buildprüfungen ausführen.
4. Commit mit einer Projektidentität und einer GitHub-noreply-Adresse erstellen. Keine persönliche E-Mail-Adresse verwenden.
5. `python scripts/check_publication.py --ref codex/public-release` ausführen. Diese Prüfung kontrolliert auch frühere Dateiversionen und E-Mail-Adressen in der erreichbaren Commit-Historie. Ein später gelöschtes Geheimnis blockiert die Veröffentlichung weiterhin.
6. Den geprüften Commit übertragen und den GitHub-Stand kontrollieren. Für die Übernahme nach `main` die Pflichtchecks des konkreten Pull Requests abwarten; Sicherheitswarnungen gesondert bewerten.

Optional lokal `git config core.hooksPath .githooks` setzen. Der enthaltene pre-push-Hook prüft über `scripts/check_push.py` die tatsächlich übertragenen Referenzen statt pauschal `HEAD`. Bei lokal konfigurierter öffentlicher Ablage blockiert er direkte Pushes vom Arbeitsbranch und private Zwischenstände in der vorgeschlagenen öffentlichen Vorgeschichte. Ein CI-Schritt prüft veröffentlichte Commits zusätzlich; dieser ersetzt die Kontrolle vor dem Upload nicht.

Die Musterprüfung erkennt verbreitete Tokenformate und verdächtige Zugangsdatenzuweisungen. Sie ist keine Garantie für beliebige Geheimnisformate oder semantisch persönliche Angaben. Änderungen müssen zusätzlich gelesen werden. Bei einem Fund wird nicht veröffentlicht; Fundwerte werden nicht in Logs ausgegeben.
