# Veröffentlichungsablauf

Die Entwicklung verwendet die öffentliche Repositoryhistorie. Geprüfte Quellcommits, Pushes, Pull Requests und Merges erfolgen im öffentlichen Repository. Frühere Vorgaben zur Sicherung in einem privaten Remote sind aufgehoben. Die Sichtbarkeit einer Ablage wird nur auf ausdrücklichen Wunsch geändert.

## Inhalt

Veröffentlicht werden Quellcode, projektgenerierte Icons, Abhängigkeits-Lockdateien, Tests und bereinigte Dokumentation. Keine Zugangsdaten, persönlichen Kontaktdaten, Benutzerpfade, Screenshots, privaten Songmetadaten oder Emoji-Zeichen.

Der gesamte Testmusikordner bleibt ausgeschlossen, einschließlich aller Unterordner und abgeleiteten Inhalte. Audio, Songtexte, Analyseergebnisse, SQLite-Dateien, Modelle, Installationsdateien, lokale Werkzeuge und virtuelle Umgebungen bleiben lokal.

## Lokale Zwischenstände

Gezielt ausgewählte App-Quellen regelmäßig lokal committen. Nur funktionierende, getestete und bereinigte Quellstände pushen. Keine Musik, Lyrics, Zugangsdaten, Gewichte, persönlichen Notizen, internen Übergabeberichte, erzeugten Ergebnisse oder lokalen Versuchswerkzeuge vormerken. Lokale Arbeitsstände mit solchen Inhalten bleiben von der öffentlichen Historie getrennt.

## Öffentliche Übernahme

`main` ist die langfristige technische Hauptlinie. Entwicklung erfolgt auf wenigen klar abgegrenzten `codex/`-Branches aus der geprüften öffentlichen Main-Historie. `codex/public-release` bleibt eine getrennte Veröffentlichungsroute, soweit sie für geprüfte Übernahmen benötigt wird. Private Entwicklungsbranches werden niemals als Vorfahren übernommen. Änderungen an `main` erfolgen über geprüfte Pull Requests mit erfolgreichen Pflichtchecks und aufgelösten Diskussionen; Branchschutz nicht umgehen. Relevante Tests, Builddateien und Dokumentation gehören zur App-Entwicklung; persönliche und rein lokale Inhalte nicht.

Die Remote-Zuordnung und URLs bleiben lokale Git-Einstellungen. Der normale Push des Veröffentlichungsbranches zielt auf `origin`. Pushes zum früheren privaten Remote sind lokal gesperrt; archivierte Entwicklungsbranches bleiben erhalten.

## Vor jeder öffentlichen Übernahme

1. Änderungen gezielt vormerken; keine ignorierten Dateien erzwingen.
2. `python scripts/check_publication.py` ausführen. Die Prüfung liest die tatsächlich vorgemerkten Git-Inhalte.
3. Relevante Tests und Buildprüfungen ausführen.
4. Commit mit einer Projektidentität und einer GitHub-noreply-Adresse erstellen. Keine persönliche E-Mail-Adresse verwenden.
5. `python scripts/check_publication.py --ref HEAD` für den tatsächlich vorgesehenen Commit ausführen. Diese Prüfung kontrolliert auch frühere Dateiversionen und E-Mail-Adressen in der erreichbaren Commit-Historie. Ein später gelöschtes Geheimnis blockiert die Veröffentlichung weiterhin.
6. Den geprüften Commit übertragen und den GitHub-Stand kontrollieren. Für die Übernahme nach `main` die Pflichtchecks des konkreten Pull Requests abwarten; Sicherheitswarnungen gesondert bewerten.

Optional lokal `git config core.hooksPath .githooks` setzen. Der enthaltene pre-push-Hook prüft über `scripts/check_push.py` die tatsächlich übertragenen Referenzen statt pauschal `HEAD`. Bei lokal konfigurierter öffentlicher Ablage blockiert er direkte Pushes vom Arbeitsbranch und private Zwischenstände in der vorgeschlagenen öffentlichen Vorgeschichte. Ein CI-Schritt prüft veröffentlichte Commits zusätzlich; dieser ersetzt die Kontrolle vor dem Upload nicht.

Für einen anderen ausdrücklich freigegebenen öffentlichen Quellbranch die
vorhandene Hookprüfung auf genau diesen Push begrenzen, zum Beispiel
`git -c moodscope.publicationBranch=codex/topic push origin codex/topic`.
Dies setzt keine Prüfung aus und ist keine Erlaubnis, private Abstammung zu
übertragen. Keine Hookumgehung oder Force-Pushes.

## Integration und Branchbereinigung

Abgeschlossene, ausreichend geprüfte Änderungen zeitnah einzeln integrieren.
Vor jedem Merge Restdiff, Vorgänger, Konflikte, Reviews, Sicherheitsbefunde und
Pflichtchecks des tatsächlichen Heads prüfen. Danach neuen Main-Commit,
Quellbaum und Main-CI bestätigen; erst dann den nächsten Merge abschließen.
Quellintegration ist keine automatische Installer- oder Endnutzerfreigabe.

Überflüssige öffentliche Branches nur im autorisierten Umfang entfernen:
sämtliche erhaltenswerten Commits müssen in Main oder einer vorgesehenen
verbleibenden Linie liegen, exklusive Änderungen und offene abhängige PRs
müssen ausgeschlossen sein. Merge-/CI-/Abstammungsnachweise vorher sichern.
Alternative PR-Routen erst nach vollständiger Integration schließen. Main,
aktive oder unklare Entwicklungsstände, lokale/private Sicherungsbranches und
interne Nachweise erhalten; keine pauschale Branchlöschung oder Umschreibung.

Die Musterprüfung erkennt verbreitete Tokenformate und verdächtige Zugangsdatenzuweisungen. Sie ist keine Garantie für beliebige Geheimnisformate oder semantisch persönliche Angaben. Änderungen müssen zusätzlich gelesen werden. Bei einem Fund wird nicht veröffentlicht; Fundwerte werden nicht in Logs ausgegeben.
