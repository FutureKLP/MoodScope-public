# Veröffentlichungsablauf

Geprüfte Entwicklungsstände werden als nachvollziehbare Commits auf GitHub gesichert. Das Repository startet privat. Die Sichtbarkeit darf nur auf ausdrücklichen Wunsch geändert werden.

## Inhalt

Veröffentlicht werden Quellcode, projektgenerierte Icons, Abhängigkeits-Lockdateien, Tests und bereinigte Dokumentation. Keine Zugangsdaten, persönlichen Kontaktdaten, Benutzerpfade, Screenshots, privaten Songmetadaten oder Emoji-Zeichen.

Der gesamte Testmusikordner bleibt ausgeschlossen, einschließlich aller Unterordner und abgeleiteten Inhalte. Audio, Songtexte, Analyseergebnisse, SQLite-Dateien, Modelle, Installationsdateien, lokale Werkzeuge und virtuelle Umgebungen bleiben lokal.

## Vor jedem Upload

1. Änderungen gezielt vormerken; keine ignorierten Dateien erzwingen.
2. `python scripts/check_publication.py` ausführen. Die Prüfung liest die tatsächlich vorgemerkten Git-Inhalte.
3. Relevante Tests und Buildprüfungen ausführen.
4. Commit mit einer Projektidentität und einer GitHub-noreply-Adresse erstellen. Keine persönliche E-Mail-Adresse verwenden.
5. `python scripts/check_publication.py --ref HEAD` ausführen. Diese Prüfung kontrolliert zusätzlich die E-Mail-Adressen der Commit-Historie.
6. Den geprüften Commit übertragen und den GitHub-Stand kontrollieren.

Optional lokal `git config core.hooksPath .githooks` setzen. Der enthaltene pre-push-Hook wiederholt die Prüfung. Ein CI-Schritt prüft veröffentlichte Commits zusätzlich; dieser ersetzt die Kontrolle vor dem Upload nicht.

Die Musterprüfung erkennt verbreitete Tokenformate und verdächtige Zugangsdatenzuweisungen. Sie ist keine Garantie für beliebige Geheimnisformate oder semantisch persönliche Angaben. Änderungen müssen zusätzlich gelesen werden. Bei einem Fund wird nicht veröffentlicht; Fundwerte werden nicht in Logs ausgegeben.
