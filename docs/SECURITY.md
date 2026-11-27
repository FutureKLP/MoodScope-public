# Sicherheitsstand und Grenzen

Entwicklungsversion, keine Freigabe als gehärteter öffentlicher Dienst.
Der Dienst bindet an Loopback. Host-/Origin-Prüfung ersetzt keine Authentifizierung
gegen andere lokale Prozesse. LAN-Server nur innerhalb der eigenen Vertrauensgrenze.

Entfernte Anbieter benötigen HTTPS; explizite lokale/LAN-Ziele dürfen HTTP nutzen.
Keine eingebetteten URL-Zugangsdaten und keine Keyweiterleitung über Redirects.
Schlüssel bleiben im Backend-Arbeitsspeicher. Zustimmung bindet Ziel, Modell,
Protokoll, Fähigkeiten und Sitzung. Es gibt keine automatische Anbieterumleitung.
Profil-/Key-Snapshots gelten pro Auftrag. Logs enthalten Fehlertypen und
Codepositionen; Lyrics, Antworten und Zugangsdaten gehören nicht in Logs.

Eigene Transformers-Modelle benötigen Safetensors, festgelegte Revisionen und
`trust_remote_code=False`. Offizielle Demucs-Gewichte werden über begrenzte
Downloadpfade mit Herausgeber-Prüfsummen geladen. Das ersetzt keine Bibliothekspatches.

Veröffentlichungsprüfung kontrolliert den vorgemerkten Baum, erreichbare frühere
Dateiversionen und Commit-Metadaten. Musterprüfungen garantieren keine Erkennung
jedes Geheimnisformats; Dateien müssen zusätzlich inhaltlich geprüft werden.

Kein neuer vollständiger Advisory-Abgleich in dieser Quellvorbereitung.
Historisch dokumentierte Rust-Restpunkte: glib 0.18.5 und proc-macro-error 1.0.4
im GTK/Linux-Zweig. Keine Linux-Sicherheitsfreigabe. Externe Downloadwerkzeuge
und FFmpeg benötigen gesonderte Pflege und Prüfung. [OSV](https://osv.dev/).

LRC-Tags und Katalogzusätze werden ohne wiederholtes Durchsuchen ungepaarter
Klammern entfernt. Regressionen prüfen große fehlerhafte Eingaben in begrenzten
Unterprozessen sowie den Erhalt von Zeitstempeln, unvollständigen Tags und
Aufnahmebezeichnungen. Die vorhandenen API-Eingabelimits bleiben zusätzlich aktiv.

## Begrenzte Modellantworten und verbleibende Zielgrenze

Modelllisten und reine Anbietertextantworten werden während des Empfangs auf
2.000.000 Bytes begrenzt. Ein zu großer Content-Length-Wert wird vor dem Körper
abgewiesen; fehlende oder falsche Größenangaben ersetzen das laufende Bytebudget
nicht. Fehlerantwortkörper werden nicht gelesen, Streams auch bei Abbruch und
Zeitüberschreitung geschlossen. Diese Aufrufe fordern `Accept-Encoding: identity`
an und weisen unerwartet komprimierte Antworten vor dem Lesen ab. Das begrenzt
auch den Dekompressionspfad; Server müssen die angeforderte Identitätskodierung
unterstützen. Audio-/Modelldownloads besitzen getrennte Verträge.

## Anbieterziele, DNS und Proxies

Alle Modelllisten-, Text- und Audioanbieteraufrufe verwenden denselben direkten
Transport in `backend/provider_http.py`. Die URL erlaubt ausschließlich HTTP(S),
keine Zugangsdaten, Queries, Fragmente, Backslashes, Steuerzeichen oder IPv6-
Zonenkennungen. Vor der Verbindung werden sämtliche DNS-Ergebnisse geprüft;
leere, übergroße oder unzulässige Ergebnismengen werden verworfen. IPv4-mapped
IPv6-Adressen werden vor der Prüfung normalisiert. HTTP ist nur für Loopback,
RFC1918 und IPv6-ULA erlaubt. HTTPS erlaubt zusätzlich globale Unicastadressen.
Linklokale, nicht angegebene, Multicast-, Dokumentations- und sonstige nicht
freigegebene Sonderadressen sind ausgeschlossen. `localhost` muss Loopback sein.

Die Verbindung verwendet eine tatsächlich geprüfte numerische IP statt einer
zweiten Auflösung des Modellservernamens. Bei mehreren Adressen wird IPv4
bevorzugt; kein automatischer Verbindungswiederholungs- oder Empfängerwechsel.
HTTP-Host und HTTPS-SNI bleiben an den ursprünglichen Namen gebunden. Die
normale Zertifikatsketten- und Hostnamenprüfung bleibt eingeschaltet. Die
`sni_hostname`-Erweiterung ist in der
[HTTPCore-Dokumentation](https://www.encode.io/httpcore/extensions/) beschrieben;
der Transport verwendet die öffentliche
[HTTPX-Transport-Schnittstelle](https://www.python-httpx.org/advanced/transports/).
Jeder Aufruf besitzt einen eigenen Client; keine hostübergreifende Poolwiederverwendung.

Proxyvertrag: Anbieteraufrufe sind direkt. HTTP_PROXY, HTTPS_PROXY, ALL_PROXY und
NO_PROXY samt Kleinschreibvarianten steuern diese Aufrufe nicht. Ebenso werden
SSL_CERT_FILE/SSL_CERT_DIR nicht als aufrufbezogene Vertrauenskonfiguration
übernommen. Es gibt keine implizite Proxyanmeldung oder Weitergabe von Schlüsseln
an einen Umgebungsproxy. Ein bewusst vorgeschalteter Modellgateway muss selbst
als Profilziel eingetragen sein und den gleichen URL-/TLS-Vertrag erfüllen.
Redirects werden nicht verfolgt. Andere Downloadpfade sind davon getrennt.

Die Prüfung bindet einen Aufruf an seine geprüfte Auflösung, keine gesamte
Sitzung an eine dauerhaft gespeicherte IP. Bewusst konfigurierte lokale/LAN-
Server bleiben erreichbar, auch unter HTTPS mit gültigem Zertifikat. Ein
kompromittierter konfigurierter Server, Resolver oder lokaler Prozess bleibt
Teil der Betreiber-Vertrauensgrenze; HTTP im LAN schützt weder Inhalt noch Keys
vor dem Netzbetreiber. Die System-DNS-Auflösung besitzt weiterhin die Laufzeit-
grenzen des Betriebssystems; HTTPX-Connect-/Read-Timeouts sind keine garantierte
Gesamtfrist für DNS oder einen langsam kontinuierlich sendenden Server.

## Einordnung von CodeQL #1 und #18

Beide Meldungen verwenden `py/full-ssrf` und sind von GitHub als kritisch
klassifiziert, haben aber verschiedene Quellenstände und Senken: #1 auf Main
`ba10356208deb12bdab59141ada3a4bc43f16405` führt in zehn Schritten von
`backend/app.py:1307` (ProviderProbe) über `request.base_url`, `discover_models`
und `endpoint` zu `httpx.get` in `backend/providers.py:56`. #18 auf PR #20
`829ba068ab25c4c8fd0dcb93cc80e9a6c5114009` führt denselben Eingang in zwölf
Schritten über `_bounded_response` zu `httpx.stream` an Zeile 58. Der neue
Streamingpfad verlagert die Senke und begrenzt Antworten; er führt nicht erst
die Benutzerkonfiguration von Serverzielen ein. Beide vollständigen Pfade wurden
in der autorisierten GitHub-Oberfläche separat gelesen.

Die vorherige DNS-Vorabprüfung ohne Verbindungsbindung und übernommene
Umgebungsproxies waren konkrete Lücken des dokumentierten Zielvertrags. Die
Korrektur schützt alle betroffenen Anbieterpfade gemeinsam. Die statische
Benutzereingabe-zu-URL-Meldung allein beweist dagegen keinen anonymen entfernten
Angriff: Der Dienst ist ein lokaler Desktopdienst mit Host-/Origin-Prüfung,
nicht gegenüber lokalen Prozessen authentifiziert. Ein Angreifer benötigt
Zugriff auf die lokale API oder Einfluss auf einen vom Benutzer gewählten
Servernamen beziehungsweise die Prozessumgebung. Mögliche Folgen sind
ungewollte lokale Anfragen und Offenlegung der für diesen Aufruf übergebenen
Inhalte/Keys; eine vollständige Remoteausnutzung ist hier nicht nachgewiesen.
Die Modelllistenroute sendet nur den ausdrücklich eingegebenen Probe-Key;
Text-/Audioaufträge nutzen die vorhandenen Empfänger-/Consent-Snapshots.

Lokale Regressionen prüfen DNS-Wechsel, unzulässige/mischte Auflösungen,
IPv4/IPv6, direkte eigene Modellserver, Proxyfreiheit, Redirectablehnung und
TLS-Identitätsparameter. Getrennte eigene TLS-Kontrollen prüfen erfolgreiche
Hostnamenvalidierung sowie Ablehnung unbekannter Zertifikate und falscher
Hostnamen. Das ersetzt weder den CodeQL-Gesamtcheck des veröffentlichten Heads
noch dessen Review-/Branchschutzanforderungen. Keine Meldung wird unterdrückt
oder ohne vollständige fachliche Grundlage geschlossen.
