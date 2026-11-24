# Paketierte Backend-Runtime (Entwicklung)

Prüfnachtrag Phase 4.3 vom 23. November 2026: Beide neuen Kandidaten wurden aus
`25b4dc06211d7f4d925d426b8011b39e764be6aa` gebaut. Ihre Paket-, Quell- und
Runtime-Dateihashes werden getrennt geführt. Windows enthält 6.876 Runtime-
Dateien mit 1.120.328.268 Bytes, Linux nach Entfernung unbenutzter Torch-
Testprogramme 6.779 Dateien mit 1.763.082.947 Bytes. Aufgelöste Builderinventare
und erfolgreiche `pip check`-Läufe machen diese Kandidaten nachvollziehbar;
plattformweise gesperrte CPU-Distributionslocks und bitidentische Neubauten
sind damit noch nicht nachgewiesen.

Die finale Modellpfadkorrektur ist über beide installierten APIs geprüft:
verwaltete Benutzermodelle außerhalb der Ressourcen lassen sich entfernen,
fremde Pfade werden abgewiesen und die Auswahl fällt auf den Standard zurück.
Hierfür wurden ausschließlich selbst verfasste Wegwerfmarker verwendet,
keine echten Modellgewichte. Fehlende Offline-Whisper-Gewichte liefern jetzt
eine übersetzte Installationshilfe ohne Wiederholung oder Ersatzwerte. Eine
echte Inferenz aus diesen Installationen ist weiterhin nicht nachgewiesen.

Das Debianpaket lässt sich einschließlich seiner GStreamer-Abhängigkeiten in
einer isolierten Kopie der vorhandenen Ubuntu-Systemdateien vollständig
konfigurieren. Das ist mehr als eine extrahierte Pluginbibliothek oder kopierte
dpkg-Statusliste, aber kein frischer unabhängiger Ubuntu-Desktop. Der tatsächliche
WSL-Host und sein halb konfiguriertes `libc-bin` bleiben unverändert.
[Genauer Paketnachweis und offene Grenzen](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).

## Nachprüfung Phase 4.4

Die Sammlung erfasst jetzt auch `LICENCE`. Sie ergänzt acht überprüfte
Originaltexte für sechs exakt zugeordnete Paketversionen einschließlich
SentencePiece-Drittanbieterhinweisen. Quellen, Upstreamcommits und SHA256 stehen
im [versionsgebundenen Katalog](distribution-licenses/provenance.json). Der
Builder kopiert nur bei passender Paketversion und korrektem Hash; keine
Netzabfrage im Build. Eine andere Version erhält keine irrtümlich zugeordnete
Altversion-Lizenz. Ihre Lizenzprüfung ist erneut erforderlich.

Neue lokale Kandidaten verwenden dieselben hashgeprüften eingefrorenen
Anwendungs-/Abhängigkeitsbinaries von `25b4dc0` mit zusätzlichen Lizenzdateien;
keine neue Python-Abhängigkeitsauflösung und kein Dependency-Upgrade. Die
Tauri-Clients werden mit einer separaten Testkennung neu gebaut. Das ist ein
nachvollziehbarer Lizenz-Paketnachlauf, kein frischer PyInstaller-Neubau und
kein Beleg bitidentischer Builds. Historische Kandidaten bleiben erhalten.

Echte Offline-CPU-Inferenz in installierten Windows-/Linux-Clients ist nun mit vorhandenen,
in das eigene Benutzerprofil kopierten Gewichten nachgewiesen: CLAP/XLM-EMO,
Demucs und Faster-Whisper. Audio stammt aus freigegebener lokaler Testmusik;
der getrennte XLM-EMO-Test verwendet selbst verfassten Text. Keine vorbereiteten
Analyse-/Stemcaches als Inferenznachweis. Ergebnisse, Modellkopien und Rohbelege
bleiben lokal. Teilumfang und native Neustartgrenzen stehen im
[Abnahmebericht](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).

CPU-Distributionslocks bleiben ein gesondertes offenes Gate. Exakte Versionen
und SHA256 sind für die geprüften veröffentlichten Artefakte lesend verfügbar;
PyPI-Torch-Metadaten belegen ausdrücklich nicht die CPU-Wheels. Ein belastbarer
Lock benötigt pro OS/Python/Architektur alle transitiven Versionen und die
konkreten offiziellen CPU-/PyPI-Artefakthashes, inklusive Buildwerkzeugen.
Demucs 4.0.1 liegt dort als Source Distribution vor: dessen Wheelbau benötigt
zusätzlich gesperrte Buildabhängigkeiten und ein überprüftes Wheelartefakt.
Die bisherigen Paket-/Dateimanifeste und `pip freeze` sind kein solcher Lock.
Eine frische isolierte Installation aus einem vollständigen Hashlock samt
`pip check`, Regressionen und Paketbau ist noch nicht erfolgt. Keine ungetestete
Lockdatei als reproduzierbare Freigabe veröffentlicht. Selbst ein vollständiger
Resolverlock garantiert keine bitidentischen PyInstaller-/Compiler-/NSIS-Builds.

## Architektur

Der zusätzliche Build `src-tauri/tauri.runtime.conf.json` aktiviert das Rust-
Feature `packaged-backend` und nimmt ausschließlich den erzeugten Ordner
`.tools/backend-runtime` als Tauri-Ressource auf. Entwicklungsbuilds ohne dieses
Feature behalten den Projektstarter. Ein Runtimebuild mit fehlender Ressource
scheitert beim Start, statt einen zufällig laufenden Dienst zu übernehmen.

Gewählt ist PyInstaller im One-folder-Modus, je Zielplattform separat gebaut.
Das vermeidet eine zusätzliche Python-Installation und das wiederholte Entpacken
eines One-file-Bundles. Eine kopierte venv ist nicht relocierbar und kann private
Caches sowie plattformspezifische CUDA-Pakete enthalten. Eine separate eingebettete
Python-Distribution benötigt zusätzlich plattformspezifische Bootstrap- und
Importpfadpflege. Das Ordnerbundle ist größer als ein reiner Client, lässt sich
aber als vollständige Ressource prüfen und mit dem Client aktualisieren.

[PyInstaller-Betriebsarten](https://pyinstaller.org/en/stable/operating-mode.html),
[Tauri-Ressourcen](https://v2.tauri.app/develop/resources/) und
[Sidecar-Konzept](https://v2.tauri.app/develop/sidecar/).
Die Prozesssteuerung liegt ausschließlich in Rust; kein allgemeiner Shellzugriff
wird für den Renderer freigegeben. `externalBin` allein bildet den benötigten
Mehrdateienordner nicht ab. Zusätzliche Tauri-Shell-Plugins sind nicht erforderlich.

## Dienstbesitz und Ende

Rust startet den festen Ressourcenpfad mit einer offenen Stdin-Pipe. Der
Supervisor reserviert ausschließlich `127.0.0.1:8765` und hält den Socket auch
zwischen Workerstarts. Windows übergibt eine zielprozessgebundene Socketkopie;
Linux erbt ausschließlich den explizit freigegebenen Dateideskriptor. Ein fremder
Listener wird weder übernommen noch beendet. Rust wartet maximal 120 Sekunden
auf Status, Clientversion, API-Revision 16 und die eigene Ausführungskennung.
Diese Kennung dient der Zuordnung, nicht als Zugriffstoken oder zusätzliche
Authentisierung gegenüber gleichberechtigten lokalen Prozessen.

Pipe-EOF beendet eigene Worker und deren noch zugeordnete Kinder. Auch der
Serving-Worker beobachtet eine Pipe zum Supervisor. Prozessobjekte stammen aus
der laufenden eigenen Familie; keine PID-Datei und kein Kill nach Portnummer.
Backend-Neustartcode 75 startet einen neuen Worker. Unerwartete Workerfehler
erhalten höchstens zwei Wiederanläufe pro Supervisorsitzung; Anbieteraufträge
werden dabei nicht wiederholt. Ein regulär beendeter Dienst wird nicht erneut
gestartet. Appneustart verwendet im Runtimebuild Tauris Restart-Ereignisse,
der Entwicklungsstarter behält Exitcode 75.

Das Hauptfenster wird erst nach dem eigenen erfolgreichen Healthcheck erzeugt.
Ein Monitor beendet den Client mit Exitcode 1, wenn der Supervisor verschwindet.
Windows verwendet für den geteilten Socket den Selector-Eventloop; unter POSIX
verhindert SO_REUSEADDR einen Neustartfehler durch eigene TIME_WAIT-Verbindungen.

Die bestehende Local/API-Zustimmung, Routingversion, neue Sitzung nach
Dienstneustart und Music2Emo-Crashbereinigung bleiben erhalten. Harte Abbrüche
und vollständiges Kindprozesscleanup wurden mit den lokalen Kandidaten geprüft;
der genaue Umfang steht im Abnahmebericht. Unit-Tests allein sind keine
entsprechende Plattformfreigabe.

## Schreibbare Verzeichnisse

Rust wählt `app_local_data_dir` anhand der Appkennung: unter Windows im lokalen
Benutzer-AppData, unter Linux unter dem XDG-Datenverzeichnis. Darunter liegen
`data` und `models`. SQLite, verwaltete WAVs, Stems, Profile, Einstellungen,
Workerbereiche und rotierende Diagnoselogs bleiben unter `data`; das Dienstlog
liegt in `data/backend.log`, temporäre Dateien unter `data/tmp`. HF-, Whisper-,
Demucs- und verwaltete Modellgewichte liegen unter `models`. Numbaroutinen
verwenden `data/cache/numba`. Der Installationsordner muss nicht beschreibbar sein.

Direkt gestartete eingefrorene Backends verwenden die Benutzerwurzel MoodScope
bzw. moodscope; Tauri übergibt seine Kennungsverzeichnisse ausdrücklich.
`MOODSCOPE_DATA` und `MOODSCOPE_MODELS` bleiben für isolierte direkte Diensttests
verfügbar. Bestehende Projektverzeichnisse werden nicht migriert, verschoben oder
gelöscht. Eine spätere Migration benötigt einen eigenen getesteten Rückfallpfad.
Installerupdates ersetzen Ressourcen; sie sind keine Datenmigration.

## Nachvollziehbarer Kandidatenbau

Eine neue Build-venv ohne geerbte Systempakete anlegen. Torch 2.15.0 und Torchaudio
2.11.1 gemeinsam vom CPU-Index installieren; danach Backend- und Separation-
Anforderungen ohne die Testabhängigkeit pytest sowie PyInstaller 6.22.3.
`pip check` ausführen und die tatsächlich aufgelösten Versionen sichern.
Die vorhandene Windows-Entwicklungslockdatei ist ein CUDA-Entwicklungsstand und
darf nicht als CPU-Distributionslock verwendet werden. Aufgelöste Versionen
zwischen Plattformen können sich unterscheiden; vor Release separat sperren.

```text
<builder-python> scripts/build_backend_runtime.py
npm run tauri build -- --config src-tauri/tauri.runtime.conf.json --bundles nsis
# Linux entsprechend --bundles deb
```

Der Builder verweigert die beiden bekannten Entwicklungsvenvs und vorhandene
Ausgabeordner. Er prüft auf NVIDIA-/CUDA-Distributionen, schreibt vor dem Bundlebau
ein Paketinventar, sammelt Lizenzdateien und erzeugt anschließend eine vollständige
Datei-/Größen-/SHA256-Liste. Inventar und Lizenztexte liegen auch im Bundle.
Das ist eine nachvollziehbare Bestandsaufnahme, keine automatisierte rechtliche
Freigabe. Runtime, Manifest, Modelle und Rohprotokolle bleiben ignoriert lokal.

## Modelle und optionale Werkzeuge

CLAP und XLM-EMO verwenden Transformers/PyTorch, Whisper CTranslate2/PyAV,
Demucs PyTorch/Torchaudio. Pythonimplementierungen sind enthalten, Gewichte nicht.
Fehlende Modelle erfordern die bestehende Modellverwaltung; kein Test behauptet
eine erfolgreiche lokale Inferenz ohne Gewichte. Linkimporte benötigen weiterhin
eine separat geprüfte yt-dlp-/JavaScript-Laufzeit und sind nicht durch dieses
Backendbundle automatisch verfügbar.

Music2Emo benötigt die separate ältere Python-/Torch-Kompatibilitätsumgebung und
seine Forschungsadapter. Im eingefrorenen Bundle meldet `ready()` deshalb false,
selbst bei vorhandenen Gewichtsdateien. Die bestehende Entwicklungsinstallation
und deren Crash-Recovery bleiben erhalten. Es gibt noch keinen freigegebenen
optionalen Installer für den Kompatibilitätsworker. Vorhandene Gewichte werden
nicht verschoben; die Paketfunktion darf nicht als verfügbar beworben werden.

Für eine spätere optionale Music2Emo-Runtime empfiehlt sich ein eigenes,
plattformweise gesperrtes CPU-Paket mit eng versioniertem Arbeitsprotokoll und
derselben Besitz-/Pipe-Lebensdauer wie beim Hauptdienst. Vor Aufnahme sind
Python-/Torch-/Transformers-Kompatibilität, Abbruch und Wiederanlauf, RAM-/
Plattenbedarf sowie Code- und Gewichtsrechte getrennt zu prüfen. Insbesondere
ersetzen MIT-Codebedingungen nicht die Nichtkommerziell-Bedingungen optionaler
MERT-Gewichte. Kein ungeprüfter Worker und keine Gewichte wurden in die
aktuellen Kandidaten übernommen; Download und Einrichtung bleiben ausdrücklich
optional und benötigen eine eigene Abnahme.

## Lizenzen und Binärfreigabe

Eigener Code: MIT; Tauri: MIT/Apache-2.0; CPython: PSF-Lizenz mit enthaltenen
Drittanbieterbedingungen. PyInstaller hat eine Bundle-Ausnahme, die keine
Abhängigkeitslizenzen ersetzt. FastAPI/Starlette/Uvicorn und Demucs: MIT;
Transformers/Hugging Face: Apache-2.0; NumPy/SciPy/Scikit-learn und Librosa:
überwiegend BSD, jeweils mit zusätzlichen eingebetteten Notices. Torch enthält
mehrere native Lizenzbestandteile, LLVMLite die LLVM-Ausnahme. SoundFile bringt
libsndfile, PyAV FFmpeg-Bibliotheken, CTranslate2 native Inferenzbibliotheken und
ImageIO-FFmpeg ein separates FFmpeg-Programm mit. Windows benötigt außerdem
passende C/C++-Laufzeitbibliotheken; Linux weiterhin glibc und die nativen Tauri-
Desktopbibliotheken. Eine native Abhängigkeitsprüfung je tatsächlichem Paket ist
erforderlich, nicht nur die Python-Metadatenprüfung.

Der untersuchte Windows-FFmpeg meldet GPLv3 mit `--enable-gpl --enable-version3`.
Die BSD-Lizenz des Python-Wrappers beschreibt nicht die Lizenz dieses Programms.
Vor öffentlicher Binärverteilung müssen exakt passende Quellen, Buildkonfiguration
und Weiterverteilungsbedingungen aller gebündelten nativen Bibliotheken geklärt
sein. Alternative: selbst nachvollziehbar gebauter FFmpeg mit geprüftem kleinem
Codecumfang und vollständiger Quellbereitstellung. Bis dahin ausschließlich
lokale Testkandidaten, keine Endnutzer- oder öffentliche Paketfreigabe.
[PyInstaller-Lizenz](https://pyinstaller.org/en/stable/license.html),
[FFmpeg-Bedingungen](https://ffmpeg.org/legal.html).

Die tatsächlichen Paketgrößen, Tests und verbleibenden Grenzen stehen in der
[Phase-4-Abnahme](PHASE4-PLATFORM-INSTALLER-ACCEPTANCE.md).
