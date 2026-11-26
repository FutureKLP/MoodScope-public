# Lizenzen und Veröffentlichungsumfang

Prüfstand: 16. November 2026. Veröffentlicht werden MoodScope-Quellen,
Build-/Setupdateien, Lockdateien, Tests und technische Dokumentation.
Der Anwendungscode trägt die [MIT-Lizenz](../LICENSE). Abhängigkeiten und Modelle
behalten ihre eigenen Bedingungen. Diese Quellvorbereitung ändert keine
Abhängigkeitsmanifeste oder Lockdateien gegenüber der vorherigen öffentlichen Basis.

## Optionale Modelle und Werkzeuge

- [Music2Emotion-Code](https://github.com/AMAAI-Lab/Music2Emotion/blob/main/LICENSE)
  und [Demucs-Code](https://github.com/facebookresearch/demucs/blob/main/LICENSE)
  tragen MIT. Ihre Quellpakete und Gewichte werden nicht in diesen Baum kopiert.
  Modell- und Datenrechte sind zusätzlich zu beachten.
- [MERT-v1-95M](https://huggingface.co/m-a-p/MERT-v1-95M/blob/main/README.md)
  ist als CC BY-NC 4.0 ausgewiesen. MoodScopes MIT-Lizenz ersetzt insbesondere
  diese Nichtkommerziell-Bedingung nicht. Der optionale Music2Emo-Pfad benötigt
  eine separat geprüfte lokale Installation; Gewichte werden nicht veröffentlicht.
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE)
  trägt BSD-2-Clause. Die Lizenz des tatsächlich verwendeten FFmpeg-Builds ist
  gesondert maßgeblich: [FFmpeg](https://ffmpeg.org/legal.html) nennt LGPL 2.1+
  beziehungsweise GPL bei entsprechenden optionalen Komponenten.
- Für yt-dlp, Modellhubs und Katalog-/Lyrics-/Musikplattformen gelten die
  jeweiligen Rechte und Nutzungsbedingungen. Ein öffentlich erreichbarer Link
  begründet kein Recht, Musik, Lyrics oder Datensätze weiterzuverteilen.

Keine Drittanbieterbinaries, Modellgewichte, Musik, Lyrics, Transkripte oder
Referenzdatensätze werden mitgeliefert. Projekticons stammen aus dem vorhandenen
Generierungsskript. Es wurde kein neuer fremder Anwendungscode übernommen.
Eine spätere Installer-/Binaryverteilung benötigt eine eigene Bestands-,
Lizenzhinweis- und gegebenenfalls Quellangebotsprüfung der tatsächlich gebündelten
Versionen. Dafür wird hier keine pauschale Freigabe behauptet.


## Paketierte CPU-Runtime (23. November 2026)

Die zusätzliche Backendverteilung wird getrennt von Modellgewichten geprüft.
Der Builder erzeugt Paketversionen, mitgelieferte Lizenztexte und Dateihashes.
Python-Metadaten ersetzen nicht die Bedingungen eingebetteter nativer Bibliotheken.
Insbesondere ist der untersuchte Windows-FFmpeg ein GPLv3-Build; vollständige
Quellbereitstellung und native Notices sind vor öffentlicher Binärverteilung
noch zu klären. Keine öffentliche Paketfreigabe.
[Architektur und Lizenzumfang](BACKEND-RUNTIME.md#lizenzen-und-binärfreigabe).

## Distributionsnachprüfung Phase 4.4 (23. November 2026)

Die erhaltenen Phase-4.3-Artefakte wurden erneut anhand ihrer vollständigen
Dateimanifeste geprüft. Windows: 6.876 Dateien, 377 PE-Dateien; Linux: 6.779
Dateien, 393 ELF-Dateien, davon 388 Shared Objects. PE-Imports und ELF-NEEDED-
Einträge sind lokal erfasst. 276 PE-Dateien haben keine FileVersion-Ressource.
Dateiidentität und Verknüpfung sind damit prüfbar; exakte Wheelarchive,
Quellrevisionen und Buildbelege aller nativen Komponenten fehlen weiterhin.
Kein Versionsfeld wird aus einem Dateinamen oder Wrapper abgeleitet.

### Ergänzte Originaltexte

Der Builder übersah die Schreibweise `LICENCE`. Er sammelt jetzt auch diese
Dateien. Die vorhandene tqdm-LICENCE stimmt bytegenau mit Upstream 4.70.1 überein.
Zusätzliche, unveränderte Texte sind in [distribution-licenses](distribution-licenses/README.md)
mit offizieller URL, Version, Upstreamcommit und SHA256 zugeordnet. Beim Build
werden ausschließlich zur Paketversion passende, hashgeprüfte Texte kopiert;
es findet kein Netzabruf statt. Drei Regressionen prüfen Sammlung, Versions-/Hashzuordnung und die Bindung an native Programmdateien.

| Komponente | Exakte Version | Ergänzte Texte / Copyright | Verbleibende Pflicht oder Herkunftslücke |
|---|---|---|---|
| CTranslate2 | 4.9.1 | Original-MIT einschließlich SYSTRAN/OpenNMT-Copyright | Eingebettete BLAS/OpenMP-/andere native Bestandteile getrennt zuordnen |
| flatbuffers | 25.12.19 | Original-Apache-2.0 | Betroffene Copyright-/Quellhinweise erhalten; tatsächlich eingebettete Teile abgleichen |
| sentencepiece | 0.2.3 | Original-Apache-2.0; Darts-Clone-/libsais-Originaltexte | Konkrete Wheel-/Compiler-/OpenMP-Herkunft und weitere eingebettete Teile offen |
| tokenizers | 0.23.3 | Original-Apache-2.0 | Rust-Crategraph und Drittanbieterhinweise des konkreten Wheels offen |
| tqdm | 4.70.1 | Original-LICENCE mit MIT-Text, MPL-Hinweis und Autorenangaben | MPL-betroffene Dateiquellen und deren Zugang bei Binärverteilung bereitstellen |
| Microsoft C/C++ Runtime | 14.51.36247.0 | Versions-/Copyrightressourcen in den tatsächlich gebündelten MSVC-DLLs gelesen | Zugehörige offizielle Redistributable-Lizenz und zulässige Redist-Dateiliste belegen; Copyright allein genügt nicht |
| Linux libgcc/libstdc++/libgomp (systemgleiche Kopien) | 14.2.0-4ubuntu2~24.04.1 | Bytegleich mit Dateien der Ubuntu-Pakete libgcc-s1, libstdc++6 und libgomp1 | GCC-Lizenztexte, Runtime-Ausnahme und passende Ubuntu-Quellen/Buildinformationen zuordnen |
| Weitere Wheel-OpenMP-Kopien | Nicht vollständig festgestellt | Mehrere verschiedene Hashes, auch bei ähnlichen Dateinamen | Nicht pauschal dem System-GCC zuordnen; exakte Vendorversionen und Ausnahmebedingungen offen |

Die vollständigen versionsbezogenen Quellbäume der vier erstgenannten Projekte
enthalten keine zusätzliche rootweite NOTICE-Datei. Das ersetzt keine Prüfung
von Submodulen, Wheels und deren eingebetteten Abhängigkeiten. An Upstreamcode
wurde für diese Ergänzung nichts verändert. Historische Pakete werden dadurch
nicht rückwirkend vollständig: neue Testpakete enthalten die Zusatztexte,
Quell-/Build- und native Weiterverteilungsnachweise bleiben offen.

### FFmpeg: konkrete Veröffentlichungsvoraussetzungen

Die separaten ImageIO-Programme bleiben die unten dokumentierten GPLv3-Builds:
Windows 9.0.2 (gyan.dev essentials), Linux n9.0.2-17-g2a571b6068 (20260930),
jeweils GCC 16.2.0, `--enable-gpl --enable-version3`. Windows meldet unter anderem
statische Verknüpfung und x264/x265. Die BSD-Lizenz von ImageIO-FFmpeg 0.8.1
ersetzt diese Bedingungen nicht. PyAV 19.0.2 lädt eigene Shared Libraries von
FFmpeg 9.0.2: deren LGPL-3+-Selbstauskunft bei gleichzeitig gemeldeten x264/x265-
Optionen bleibt ohne belegte Build-/Codecbedingungen widersprüchlich ungeklärt.
Daraus wird weder eine GPL- noch eine LGPL-Freigabe der PyAV-Wheels abgeleitet.

Nachtrag vom 24. November: Die beiden Programmdateien sind nun exakt dem
[versionsgebundenen ImageIO-Herkunftsmanifest](https://github.com/imageio/imageio-ffmpeg/blob/v0.8.1/tools/ffmpeg-sources.json)
zugeordnet. Windows-FFmpeg ist zusätzlich bytegleich mit dem offiziellen Gyan-
9.0.2-Archiv (dessen SHA256 mit der offiziellen Prüfsumme abgeglichen).
Das enthaltene README nennt FFmpeg-Quellrevision `946fcce07b`; der Linux-Build
gehört zu BtbN/FFmpeg-Builds `autobuild-2026-09-30-13-08`, FFmpeg `2a571b6068`.
Die jeweiligen Releaseartefakte sind verfügbar. Damit ist die Herkunft der
Programme wesentlich enger belegt; vollständige entsprechende Quellen aller
statisch eingebauten Bibliotheken und exakt zugeordnete Buildrezepte fehlen
weiterhin. Ein bewegliches `master` als Release-Metadatum reicht dafür nicht.

Der unveränderte GPLv3-Originaltext aus dem hashgeprüften Gyan-Archiv ist als
achter Zusatztext im Katalog zugeordnet. Der Builder verlangt hierfür neben
ImageIO-FFmpeg 0.8.1 auch den exakten plattformspezifischen FFmpeg-Dateihash;
bei Abweichung schlägt der Build fehl, andere Plattformen werden nicht
ungeprüft zugeordnet. Die BSD-Lizenz des Wrappers bleibt separat erhalten.
Der GPL-Text ersetzt keine vollständigen Quellen oder Copyright-/Codec-Notices.

PyAV 19.0.2 nennt in seinem versionsbezogenen
[Abhängigkeitsmanifest](https://github.com/PyAV-Org/PyAV/blob/v19.0.2/scripts/ffmpeg-latest.json)
die separaten pyav-ffmpeg-Artefakte `9.0.2-1`. Die Releasequellen und Buildskripte
sind ein konkreter Prüfpfad; die tatsächlichen Wheelbibliotheken sind dadurch
noch nicht vollständig an Quellen und Vendor-Patches gebunden. Das ebenfalls
vorhandene Entwicklungs-Buildskript ist kein Beleg für das Wheelrezept.
Die Lizenz-/x264-/x265-Frage bleibt offen.

Vor öffentlicher Binärverteilung benötigt jeder konkrete FFmpeg-Build:

1. Herkunftsbeleg und Hash des tatsächlichen Wheels/Archivs sowie die exakt
   entsprechende FFmpeg-Quellrevision einschließlich aller lokalen Patches.
2. Quellen und Lizenz-/Copyright-/NOTICE-Texte aller eingebauten Bibliotheken,
   insbesondere x264/x265 und weiterer GPL-/LGPL-Komponenten; nicht nur FFmpeg.
3. Tatsächlich verwendete Configure-Zeile, Compiler-/Linkerversionen,
   Buildskripte, Abhängigkeitsrevisionen und Steuerdateien für den Bau.
4. Einen zur gewählten GPLv3-Verteilungsform passenden Zugang zum vollständigen
   Corresponding Source; bei Internetdownload vorzugsweise gleichwertiger
   Quellzugang neben dem Binärdownload. Ein beliebiger Upstreamlink oder
   nachträglich rekonstruierter Build reicht als Identitätsnachweis nicht.
5. Für LGPL-Bibliotheken die konkret erforderlichen Austausch-/Relinking-
   Möglichkeiten und Nutzungsbedingungen einschließlich nötiger Objektdateien,
   soweit die gewählte Verknüpfungs-/Verteilungsform sie verlangt.

Für SoundFile 0.14.0 / libsndfile 1.2.2 bleiben zusätzlich passende native
Quellen, Codec-Notices und LGPL-Relinkingbedingungen offen. Für Torch
2.15.0+cpu (65 gesammelte Texte) und Torchaudio 2.11.1+cpu (ein Text) sind die
konkreten CPU-Wheel-/nativen Buildbestandteile vollständig abzugleichen.
CPython-/PyInstaller- und App-Lizenzen ersetzen diese Pflichten nicht.

Quellen: [FFmpeg-Bedingungen](https://ffmpeg.org/legal.html),
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html),
[LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html),
[GCC Runtime Library Exception](https://www.gnu.org/licenses/gcc-exception-3.1.html).

**Offene rechtliche Prüfung und Binär-Releaseblocker.** Die ergänzten Texte
schließen die fünf konkret festgestellten Sammlungslücken im neuen Buildumfang,
aber nicht die vollständige Lizenz-, Quell- oder Weiterverteilungsprüfung.
Keine definitive Rechts- oder Endnutzerfreigabe.

## Konkrete Distributionsprüfung Phase 4.3

Prüfstand: 23. November 2026, Paketquellen `25b4dc0`. Beide CPU-Builder wurden
mit `pip check`, Paket-/Lizenzinventar und Datei-SHA256-Manifest geprüft. Die
folgenden Angaben betreffen die tatsächlich eingesammelten Versionen; eine
Metadatendeklaration oder vorhandene Lizenzdatei ist keine vollständige
Weiterverteilungsfreigabe. Rohinventare und Binärdateien bleiben lokal.

| Bestandteil | Version im Kandidaten | Lizenzangabe / tatsächlicher Befund | Noch erforderlicher Distributionsnachweis |
|---|---|---|---|
| ImageIO-FFmpeg | 0.8.1 | Wrapper BSD-2-Clause; eigenes FFmpeg auf beiden Plattformen mit `--enable-gpl --enable-version3` | GPL-konforme Bereitstellung exakt entsprechender Quellen, Änderungen und Buildangaben einschließlich eingebauter Bibliotheken |
| FFmpeg-Programm Windows | 9.0.2, gyan.dev essentials | GPLv3-Build, GCC 16.2.0 | Exakte Herkunfts-/Buildbelege und zugehörige Quellen fehlen |
| FFmpeg-Programm Linux | n9.0.2-17-g2a571b6068, Build 20260930 | GPLv3-Build, GCC 16.2.0 | Exakte Herkunfts-/Buildbelege und zugehörige Quellen fehlen |
| PyAV | 19.0.2 | BSD-3-Clause, Lizenztext vorhanden; separate FFmpeg-9.0.2-Bibliotheken | Native Quellen und vollständige Notices fehlen; Bibliotheken melden LGPL-3.0-or-later, Konfiguration mit x264/x265 muss mit deren konkreten Bedingungen abgeglichen werden |
| SoundFile / libsndfile | 0.14.0 / 1.2.2 | BSD-3-Clause / LGPL-2.1; drei gesammelte Lizenz-/Hinweisdateien | Passende native Quellen, Build- und Relinkingbedingungen samt Codec-Notices vervollständigen |
| CTranslate2 | 4.9.1 | MIT laut Paketmetadaten; kein gesammelter Lizenztext | Copyright-/Lizenztext und eingebettete native Notices nachliefern |
| PyTorch | 2.15.0+cpu | BSD-3-Clause und weitere native Bedingungen; 65 gesammelte Texte | Vollständigkeit und Zuordnung zum konkreten CPU-Build prüfen |
| Torchaudio | 2.11.1+cpu | BSD-2-Clause, Lizenztext vorhanden | Zugehörige native Bestandteile und deren Bedingungen abschließend abgleichen |
| flatbuffers | 25.12.19 | Apache-2.0 laut Metadaten; kein gesammelter Text | Lizenz und gegebenenfalls NOTICE nachliefern |
| sentencepiece | 0.2.3 | Apache-2.0 laut Metadaten; kein gesammelter Text | Lizenz und gegebenenfalls NOTICE nachliefern |
| tokenizers | 0.23.3 | Apache-Lizenzklassifikation; kein gesammelter Text | Exakten Lizenztext und native Abhängigkeitshinweise nachliefern |
| tqdm | 4.70.1 | `MPL-2.0 AND MIT` laut Metadaten; kein gesammelter Text | Beide Bedingungen einschließlich gegebenenfalls erforderlicher Dateiquellen erfüllen |
| C-/C++-Laufzeiten | plattformspezifische DLL-/ELF-Dateien im Hashmanifest | Microsoft-Laufzeiten unter Windows, GCC-/glibc-/weitere native Komponenten unter Linux | Versionen, Herkunft, Weiterverteilungsrechte und Notices je konkreter Binärdatei abschließen |

Die Programm-FFmpegs und die von PyAV geladenen FFmpeg-Bibliotheken sind getrennte
Artefakte. Die Lizenz des Python-Wrappers ersetzt keine dieser Bedingungen.
Dateihashes belegen die Identität der untersuchten Dateien, nicht deren
Lizenzkonformität; vollständige Wheel- und native Buildherkunft ist noch offen.
[FFmpeg-Veröffentlichungsbedingungen](https://ffmpeg.org/legal.html).

**Releaseblocker bleibt bestehen.** Keine öffentlichen Installationsbinaries und
keine pauschale Freigabe der nativen Notices oder Quellbereitstellung. Die
Entfernung unbenutzter Torch-Testprogramme aus dem neuen Runtimeordner reduziert
den Umfang, löst diese rechtlichen Nachweise aber nicht.
