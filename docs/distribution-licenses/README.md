# Versionsgebundene Distributionshinweise

Diese unveränderten Originaltexte ergänzen die Lizenzsammlung des CPU-Builders.
`provenance.json` ordnet jeden Text Paketversion, offiziellem Upstreamtag,
Upstreamcommit und SHA256 zu. Der Builder lädt nichts aus dem Netz und kopiert
nur Texte mit passender installierter Version und korrekter Prüfsumme.

- CTranslate2 4.9.1: MIT einschließlich der Upstream-Copyrightangaben.
- flatbuffers 25.12.19: Apache-2.0.
- sentencepiece 0.2.3: Apache-2.0 und die im exakten Quellbaum enthaltenen
  Darts-Clone-/libsais-Texte. Wheelabhängigkeiten bleiben zusätzlich zu prüfen.
- tokenizers 0.23.3: Apache-2.0; Rustabhängigkeiten erfordern eigene Zuordnung.
- tqdm 4.70.1: originale `LICENCE` mit MIT-Text, MPL-Hinweis und Autorenangaben.
  Der Text stimmt bytegenau mit dem vorhandenen Wheel überein. Die MPL-Pflichten
  zur Bereitstellung der betreffenden Dateiquellen bleiben gesondert zu erfüllen.

Die vollständig gelesenen versionsbezogenen Upstreambäume der vier erstgenannten
Pakete enthalten keine zusätzliche rootweite NOTICE-Datei. Das beweist keine
Vollständigkeit der nativen Wheelbestandteile, Submodule oder Rustabhängigkeiten.
Diese Texte ersetzen weder deren Notices noch GPL-/LGPL-Quellen, Buildbelege,
Relinkingmöglichkeiten oder die rechtliche Prüfung der konkreten Binärverteilung.
[Offene Distributionsprüfung](../THIRD-PARTY.md).

Der zusätzliche originale FFmpeg-GPLv3-Text stammt aus dem hashgeprüften Gyan-
9.0.2-Archiv, unverändert als `imageio-ffmpeg/ffmpeg/LICENSE`. Er wird nur für
ImageIO-FFmpeg 0.8.1 und die überprüften Windows-/Linux-Programmhashes kopiert.
Der Wrapper behält seine eigene BSD-Lizenz. Ein Hashfehler stoppt den Build;
ungeprüfte Plattformen erhalten diese Komponenten-Zuordnung nicht automatisch.
