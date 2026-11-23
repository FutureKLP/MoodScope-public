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
