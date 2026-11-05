from backend import research


def test_catalog_fallback_survives_musicbrainz_outage(monkeypatch):
    def unavailable(*a):raise RuntimeError('upstream unavailable')
    monkeypatch.setattr(research,'musicbrainz_search',unavailable)
    monkeypatch.setattr(research,'itunes_search',lambda *a:[{'id':'itunes:1','title':'Public candidate'}])
    result=research.search('Artist','Title')
    assert result['candidates'][0]['source']=='Apple iTunes'
    assert result['unavailable']==['MusicBrainz']
