# Kernabnahme und Freigabegrenzen

Fachlicher Überblick und datierte Nachweise. Aktueller Projekt- und Integrationsstatus:
[STATUS.md](STATUS.md); Navigation: [Dokumentationsübersicht](README.md).

## Entscheidung

Die Anwendung bleibt eine Entwicklungsversion. Die Veröffentlichung geprüfter
Quellverbesserungen bedeutet keine vollständige Kern-, Plattform- oder
Qualitätsfreigabe. Die externe Datenbankphase ist weiterhin gesperrt; SQLite
bleibt Standard. Kein MariaDB-, Supabase- oder Firebase-Adapter wurde ergänzt.

## Abgesicherte Bereiche

- Zielgebundene Übertragungszustimmung und Aufgaben-/Profil-/Key-Snapshots.
- Journalisierte Bibliothekslöschung, Wiederimport und SQLite-Transaktionen.
- Gemeinsame Medienzeit, Stemstart, Ressourcenfreigabe und WAV-Transferprüfung.
- Schutz vor verspäteten Songdetails und veralteten Notizspeicherantworten.
- Endliche Modellwerte, kooperative Abbrüche und Belegpflicht für Textdeutungen.
- Deutsch/Englisch, gemeinsame Palette und reduzierte Bewegung.

## Noch erforderliche Abnahmen

### Windows-Exportprüfung am 17. November 2026

Die gezielte Phase-1-Prüfung hat keinen Anwendungsfehler beim Abbruch des
Speicherdialogs nachgewiesen. Die 16 × 16 stammen von einem separaten sichtbaren
`Tao Thread Event Target` mit leerem Clientbereich. Das Hauptfenster war normal
groß und hatte 96 DPI. Ein als Cancel adressierter Accessibility-Indexklick
aktivierte tatsächlich Speichern; bei bestehendem Ziel erschien die
Überschreibbestätigung. Diese Eingabefehler erklären die im neuen Lauf erzeugten
synthetischen WAVs. Die historische Sequenz lässt sich ohne damaligen
Eingabetrace nicht rückwirkend vollständig beweisen.

Mit frischen, bildgebundenen Dialogeingaben bestanden Escape, Cancel-Schaltfläche,
Dateinameneingabe mit Abbruch, Erhalt einer vorhandenen Zieldatei, wiederholte
Abbrüche und bestätigter Export vor und nach App-/Dienstneustart. Beide bestätigten
Exporte sind gültige Stereo-WAVs mit 48 kHz, zwei Sekunden und identischem
Quellhash. Produktive SQLite bytegleich, isolierte SQLite intakt, eigene
Prüfprozesse beendet. Ausschließlich synthetische Exportfixtures; keine neue
tatsächliche Musik- oder Modellqualitätsabnahme.

Entscheidung: **Kein Anwendungsfehler nachgewiesen, Automationsproblem behoben**
durch den dokumentierten Eingabeweg. Der Werkzeugfehler selbst ist nicht gepatcht.
Andere DPI-Stufen und längere Ressourcenläufe bleiben unbestätigt. Die breitere
Kernfreigabe und das Datenbank-Gate bleiben unverändert offen.
[Verfahren, vollständige Testmatrix und Grenzen](WINDOWS-DESKTOP-TESTING.md).

### Nachprüfung am 16. November 2026

Die native Windows-App wurde mit neu gebauter Oberfläche und einer isolierten
Kopie der freigegebenen lokalen Testbibliothek bedient. Bibliothek, gespeicherte
Analyse, Vier-Stem-Modell und deutscher WAV-Speicherdialog waren erreichbar.
Zwei Abbrüche mit Escape ließen den beobachteten Exportordner unverändert.
Ein vorheriger Versuch mit automatischer Dateinamensänderung und anschließendem
Cancel-Klick erzeugte hingegen eine WAV; dieser Versuch ist kein Abbruchnachweis.
Direkte Cancel-Klicks blieben wegen erneut gemeldeter 16-mal-16-Fenstergrenzen
unbestätigt. Die widersprüchliche Eingabesequenz ist noch zu klären.

Local/API/Local wurde ohne Anbieteranalyse sichtbar gewechselt: API ohne Cache
wurde neutral, die lokale Rückkehr stellte die Modellfarbe wieder her.
Deutsch/Englisch, Originalmix-Wiedergabe bis zum Abschnittsende und der mit der
Atmosphäre gestaltete Neustartdialog wurden nativ geprüft. App und Dienst
starteten anschließend neu; englische Sprache und Atmosphäreneinstellung blieben
erhalten. Dies deckt nicht die gesamte Profil-/Song-/Modell-/Dialogfehlermatrix ab.
Nach dem Neustart stimmen Tracks und Metadaten der isolierten SQLite mit der
kopierten Ausgangsbibliothek überein; sechs gespeicherte Ergebnisse bleiben
vorhanden und die Datenbankintegrität ist in Ordnung.

Wiederholte tatsächliche Music2Emo-Läufe mit bestehenden lokalen Gewichten
bestanden auf CPU, GPU und erneut CPU. Workerlogs wurden lokal erhalten.
Die korrigierte Wiederholung bestätigte unveränderte Originaldatei und produktive
SQLite. Erfolgreiche Wiederholungen erklären den früheren sporadischen Fehler
weiterhin nicht. Keine neue Qualitäts-, Langzeit- oder Plattformfreigabe.

MariaDB, Supabase und Firebase/Firestore sowie Migration und Rückmigration
sind nicht implementiert. Dafür wurden keine Emulatoren, Mocks oder Liveziele
als erfolgreiche Anwendungstests ausgegeben; keine externe Verbindung geöffnet.
Die folgenden offenen Kriterien gelten mit diesen begrenzten Ergänzungen weiter.

1. Den nun belegten Windows-Dialogablauf bei weiteren DPI-Konfigurationen und
   in längeren Läufen prüfen. Der frühere unklare Versuch bleibt historisch;
   die neue synthetische Abnahme ist oben getrennt dokumentiert.
2. Native Local/API/Local-, Song-/Modellwechsel-, Dialogfehler- und gemeinsame
   App-/Dienstneustartmatrix bei zuverlässigem Fensterzugriff vervollständigen.
3. Sporadischen Music2Emo-Prüfdienstfehler bei Wiederholung mit erhaltenem
   Workerlog aufklären. Erfolgreiche Wiederholungen sind keine Ursachenklärung.
4. Längere Wiedergabe-/Mix-/Speicherprüfung und verfügbare Zielplattformen
   getrennt abnehmen. Windows 10, Linux und Installation bleiben unbestätigt;
   ein erfolgreicher Windows-NSIS-Paketbuild ist keine Installationsabnahme.
5. Grenzen von Worterkennung, Deutungswahrheit, Sängertrennung und zeitlichen
   Emotionsverläufen erhalten. Modellschätzungen sind keine bestätigten Fakten.

[Automatisierte Prüfungen](TEST-BASELINE.md) und [Sicherheitsgrenzen](SECURITY.md).
