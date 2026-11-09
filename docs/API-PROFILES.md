# Anbieterprofile fuer Audio und Text

Lokal ist der Standard. In Modelle & API ein Profil mit exakter Modell-ID und
Basis-URL anlegen. Keys bleiben nur im Backend-Arbeitsspeicher. Ein Chat-Abonnement
ist kein API-Zugang. Die App prueft weder Tarif noch Modellfreischaltung.

## Unterstuetzte Wege

- Gemini: bestehender nativer Audio-/Textadapter, weiterhin mit Bestaetigung eines
  Projekts ohne aktivierte Abrechnung.
- OpenAI: Audioeingabe ueber Chat Completions mit einem passenden Audiomodell,
  beispielsweise einer im [Audio-Leitfaden](https://developers.openai.com/api/docs/guides/audio-chat-completions)
  dokumentierten Modell-ID. WAV-Eingabe, ausschliesslich Textantwort, store=false.
- Mistral/Voxtral: OpenAI-kompatibles Profil mit https://api.mistral.ai/v1 und
  geeigneter Modell-ID. Die [Mistral-Dokumentation](https://docs.mistral.ai/studio/audio/audio-in-chat)
  beschreibt input_audio und akzeptiert das verwendete Objektformat.
- Eigene Audio-Server: explizit konfiguriertes OpenAI-kompatibles input_audio-Protokoll.
  Reine Textmodelle, Claude-Messages und das DeepSeek-Textprofil sind keine
  Audioadapter. Die tatsaechlichen Modellfaehigkeiten prueft der gewaehlte Server.

Bei OpenAI-kompatiblen Profilen Audiofaehigkeit und moegliche Kosten ausdruecklich
bestaetigen, speichern und Fuer Audio-API verwenden waehlen. Jede neue
Audiozielauswahl setzt die Uebertragungszustimmung zurueck. Erst nach Auswahl des
API-Modus und der Sitzungszustimmung werden Daten uebertragen. Keine automatischen
Anbieterwechsel, Wiederholungen oder ersatzweise lokalen Modellaufrufe.

## Funktionen und Grenzen

Das Audioprofil uebernimmt Audio-Valenz/Aktivierung und unabhaengige
Gefuehlsschaetzungen fuer die vorhandenen Balken. Kraft und Energie sind getrennt
von Aerger. Die API-Scores sind unkalibrierte Schaetzungen; keine feste Formel
rechnet sie in Valenz um. Audio wird mit dem tatsaechlich gesendeten Gesamtkontext
ausgewiesen. API-Schritte garantieren keine sekundengenaue Gefuehlserkennung.

Ohne LRC und mit aktivierter Texterkennung wird zuerst Gesangstext mit unsicheren
Zeitstempeln abgefragt. Das kann eine zusaetzliche kostenpflichtige Anfrage sein.
Instrumenthinweise werden erst separat in Songdetails angefordert; sie bleiben
unsichere Hypothesen. Akustische Messungen und Spurentrennung rechnen weiterhin
lokal. Ein Sprachmodell ersetzt keine Trennung von Audiowellenformen.

Textdeutungen verwenden das dort ausgewaehlte Textprofil; ohne separates Profil
kann im API-Modus das vorbereitete Audioprofil die Textdeutung uebernehmen.
Audio und Textemotion werden getrennt abgefragt. Die gemeinsame Einordnung
bleibt an die vorhandenen zeitlichen Belege gebunden.

## Validierung

JSON-Schema, endliche Skalenwerte, vollstaendige IDs, Zeitstempel und Abbruchgruende
werden geprueft. Fehlerhafte Antworten werden verworfen. Cache-Versionen
unterscheiden Protokoll, Zieladresse, Modell und Profil. Keys stehen weder in
Cache-Schluesseln noch in gespeicherten Profilen.

Die Anbindung wird mit simulierten Antworten der dokumentierten Protokolle
getestet. Ein echter kostenpflichtiger Durchlauf und eine wissenschaftliche
Genauigkeitspruefung dieser Anbieter sind damit nicht nachgewiesen.


## Eigene Heimserver mit Ollama oder LM Studio

In Modelle & API die Vorlage Ollama oder LM Studio waehlen. Die Basis-URL kann
auf denselben Rechner oder einen Heimserver zeigen. Beispiele fuer denselben
Rechner sind http://127.0.0.1:11434/v1 und http://127.0.0.1:1234/v1. Auf einem
anderen Rechner die dortige LAN-Adresse oder dessen Heimnetz-Namen einsetzen;
localhost bezeichnet immer den Rechner, auf dem der MoodScope-Dienst laeuft.
HTTP-Hostnamen werden nur akzeptiert, wenn alle aufgeloesten Adressen lokal/privat
sind. Linklokale, nicht angegebene und Multicast-Adressen bleiben ausgeschlossen.
Fuer entfernte oeffentliche Server ist HTTPS erforderlich.

Verbindung pruefen und Modelle laden liest ausschliesslich GET /models am
angegebenen kompatiblen Endpoint. Es werden weder Songdaten uebertragen noch
Modelle heruntergeladen oder gestartet. Ein Modell aus der Antwort auswaehlen
oder die genaue Modell-ID direkt eingeben, dann Profil speichern. Ein Key ist
nur noetig, wenn der eigene Server oder sein vorgeschalteter Proxy Authentifizierung
verlangt. Der Verbindungstest verwendet den aktuell eingegebenen Key.

Das Textprofil anschliessend unter Interpretation waehlen und der Uebertragung
an diesen Server zustimmen. Der Server muss aus dem MoodScope-Netz erreichbar sein;
die App aendert keine Serverfreigaben oder Firewall-Einstellungen. Die
[Ollama-Kompatibilitaetsdokumentation](https://docs.ollama.com/api/openai-compatibility),
[Ollama-FAQ](https://docs.ollama.com/faq) und
[LM-Studio-Modellliste](https://lmstudio.ai/docs/developer/openai-compat/models)
beschreiben die serverseitigen Voraussetzungen.

Ein uebliches Ollama-Textmodell kann nicht allein durch Aktivieren der
Audio-Checkbox Musik hoeren. Fuer Audio muss der eigene Server tatsaechlich
input_audio und ein passendes Audiomodell bereitstellen. Ein Heimserver kann
seinerseits Cloud-Modelle aufrufen; seine Konfiguration bestimmt, wo die KI rechnet.
