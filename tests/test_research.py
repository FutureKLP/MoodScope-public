from backend import research


def test_duration_ranking_never_auto_matches_a_different_version():
    candidates=[{'id':'long','artist':'Artist','title':'Title','duration':245},
                {'id':'near','artist':'Artist','title':'Title','duration':240.5},
                {'id':'remix','artist':'Artist','title':'Title (Remix)','duration':240}]
    result=research.ranked_candidates(candidates,'Artist','Title',240)
    assert result[0]['id']=='near' and result[0]['auto_eligible']
    assert not next(r for r in result if r['id']=='remix')['auto_eligible']


def test_online_tonality_is_scoped_and_ignores_deprecated_claims(monkeypatch):
    def get(url,params):
        if params['props']=='claims':return {'entities':{'Q1':{'claims':{'P826':[
            {'mainsnak':{'datavalue':{'value':{'id':'Q2'}}}},
            {'rank':'deprecated','mainsnak':{'datavalue':{'value':{'id':'Q3'}}}}]}}}}
        assert params['ids']=='Q2'
        return {'entities':{'Q2':{'labels':{'en':{'value':'C major'},'de':{'value':'C-Dur'}}}}}
    monkeypatch.setattr(research,'get_json',get)
    result=research.wikidata_tonality('Q1')[0]
    assert result['value']=='C major' and result['value_de']=='C-Dur'
    assert result['scope']=='linked_work_or_song'


def test_catalog_fallback_survives_musicbrainz_outage(monkeypatch):
    def unavailable(*a):raise RuntimeError('upstream unavailable')
    monkeypatch.setattr(research,'musicbrainz_search',unavailable)
    monkeypatch.setattr(research,'itunes_search',lambda *a:[{'id':'itunes:1','title':'Public candidate'}])
    monkeypatch.setattr(research,'deezer_search',lambda *a:[])
    result=research.search('Artist','Title')
    assert result['candidates'][0]['source']=='Apple iTunes'
    assert result['unavailable']==['MusicBrainz']


def test_empty_catalogue_queries_broaden_and_deezer_is_an_automatic_fallback(monkeypatch):
    calls=[]
    def empty(*args):calls.append(args);return []
    monkeypatch.setattr(research,'musicbrainz_search',lambda *a:{'candidates':[]})
    monkeypatch.setattr(research,'itunes_search',empty)
    monkeypatch.setattr(research,'deezer_search',lambda *a:[{'id':'deezer:42','title':'Authored Song'}])
    result=research.search('Authored Artist','Authored Song (Official Video)')
    assert result['candidates'][0]['source']=='Deezer'
    assert ('','Authored Song') in calls
    assert any(row['source']=='Apple iTunes' and row['status']=='empty' for row in result['attempts'])


def test_all_services_unavailable_returns_actionable_error(monkeypatch):
    import pytest
    def fail(*a):raise RuntimeError('outage')
    for name in ['musicbrainz_search','itunes_search','deezer_search']:monkeypatch.setattr(research,name,fail)
    with pytest.raises(RuntimeError,match='Verbindung prüfen'):research.search('Artist','Title')


def test_basic_catalogue_enriches_only_an_exact_recording_match(monkeypatch):
    identity='12345678-1234-1234-1234-123456789abc'
    monkeypatch.setattr(research,'get_json',lambda *a,**k:{'results':[{'trackName':'Authored Song','artistName':'Artist','trackTimeMillis':10000}]})
    monkeypatch.setattr(research,'musicbrainz_search',lambda *a:{'candidates':[{'id':identity,'title':'Authored Song','artist':'Artist','duration':10}]})
    monkeypatch.setattr(research,'musicbrainz_details',lambda *a:{'url':'https://musicbrainz.org/recording/'+identity,'credits':[{'name':'Authored performer','instruments':['piano']}],'instrumentation':[]})
    result=research.details('itunes:42')
    assert result['credits'][-1]['source']=='MusicBrainz'
    assert result['credits'][-1]['instruments']==['piano']
    monkeypatch.setattr(research,'musicbrainz_search',lambda *a:{'candidates':[{'id':identity,'title':'Other Song','artist':'Artist','duration':10}]})
    assert not research.details('itunes:42')['supplemental']


def test_wikidata_instrumentation_is_marked_as_linked_work_evidence(monkeypatch):
    def data(url,params):
        if params['props']=='claims':return {'entities':{'Q123':{'claims':{'P870':[{'mainsnak':{'datavalue':{'value':{'id':'Q456'}}}}]}}}}
        return {'entities':{'Q456':{'labels':{'en':{'value':'piano'}}}}}
    monkeypatch.setattr(research,'get_json',data)
    result=research.wikidata_instruments('Q123')
    assert result[0]['name']=='piano' and result[0]['scope']=='linked_work_or_song'


def test_credit_attributes_do_not_promote_production_roles_to_instruments(monkeypatch):
    monkeypatch.setattr(research,'request',lambda *a:{'title':'Authored Song','relations':[{'type':'producer','attributes':['additional'],'artist':{'name':'Producer'}},{'type':'instrument','attributes':['guest','piano'],'artist':{'name':'Performer'}}]})
    result=research.musicbrainz_details('12345678-1234-1234-1234-123456789abc')
    assert result['credits'][0]['instruments']==[]
    assert result['credits'][1]['instruments']==['piano']

def test_discogs_keeps_album_instruments_separate_from_matching_track_credits(monkeypatch):
    monkeypatch.setattr(research,'get_json',lambda *a,**k:{'title':'Authored album','extraartists':[{'name':'Album performer','role':'Drums'},{'name':'Track performer','role':'Bass Guitar','tracks':'A1'},{'name':'Producer','role':'Mixed By'}],
        'tracklist':[{'title':'Authored Song','position':'A1','extraartists':[{'name':'Guitarist','role':'Electric Guitar'}]}]})
    result=research.discogs_credits('123','Authored Song')
    assert [c['name'] for c in result['album_credits']]==['Album performer']
    assert {c['name'] for c in result['credits']}=={'Track performer','Guitarist'}
    assert all(c['scope']=='recording' and c['source']=='Discogs' for c in result['credits'])


def test_discogs_outage_does_not_erase_existing_musicbrainz_credits(monkeypatch):
    data={'title':'Authored Song','credits':[{'name':'Confirmed performer','instruments':['piano']}]}
    monkeypatch.setattr(research,'discogs_credits',lambda *a:(_ for _ in ()).throw(RuntimeError('outage')))
    result=research.enrich_discogs(data,{'relations':[{'url':{'resource':'https://www.discogs.com/release/123-example'}}]})
    assert result['credits'][0]['name']=='Confirmed performer' and result['unavailable']==['Discogs']
