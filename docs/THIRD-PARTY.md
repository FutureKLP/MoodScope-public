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
