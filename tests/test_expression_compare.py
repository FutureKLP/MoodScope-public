import importlib
import json
import threading
import pytest
from test_api import client,wav_bytes
from backend import expression_compare,cancellation
from scripts.music2emo_curve import context_spans


def test_context_windows_cover_the_track_without_inventing_finer_context():
    rows=list(context_spans(47))
    assert rows[0]['start']==0 and rows[-1]['end']==47
    assert all(a['end']==b['start'] for a,b in zip(rows,rows[1:]))
    assert all(r['context_end']-r['context_start']==30 for r in rows)
    assert list(context_spans(7))[-1]['context_end']==7


def test_comparison_cache_is_independent_and_deleted_with_analyses(client,monkeypatch):
    app=importlib.import_module('backend.app')
    identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    baseline={'audio':[{'start':0,'end':1,'valence':.25,'scores':{'joy':1}}]}
    with app.db() as conn:
        conn.execute('INSERT INTO cache VALUES (?,?)',(f'latest:{identity}:local',json.dumps(baseline)))
    calls=[]
    def analyse(*args):
        calls.append(1)
        return {'method':expression_compare.METHOD,'rows':[{'start':0,'end':1,'valence':-.2,'arousal':.7,'tags':{'sad':.4}}]}
    monkeypatch.setattr(expression_compare,'ready',lambda:True)
    monkeypatch.setattr(expression_compare,'fingerprint',lambda:'fixture-v1')
    monkeypatch.setattr(expression_compare,'analyse',analyse)
    monkeypatch.setattr(app.engines,'device',lambda:'cpu')
    app.jobs['fixture']={'status':'running'}
    app.run_expression_comparison('fixture',identity,app.ExpressionRequest())
    app.run_expression_comparison('fixture',identity,app.ExpressionRequest())
    assert len(calls)==1 and app.jobs['fixture']['result']['cached']
    value=client.get(f'/api/tracks/{identity}/expression-comparison').json()
    assert value['ready'] and not value['stale'] and value['result']['rows'][0]['valence']==-.2
    with app.db() as conn:
        assert json.loads(conn.execute('SELECT result FROM cache WHERE key=?',(f'latest:{identity}:local',)).fetchone()[0])==baseline
    app.run_expression_comparison('fixture',identity,app.ExpressionRequest(force=True))
    assert len(calls)==2
    monkeypatch.setattr(expression_compare,'fingerprint',lambda:'fixture-v2')
    assert client.get(f'/api/tracks/{identity}/expression-comparison').json()['stale']
    client.post(f'/api/tracks/{identity}/notes',json={'interpretation':'Authored note'})
    client.post(f'/api/tracks/{identity}/cache/delete',json={})
    assert client.get(f'/api/tracks/{identity}/expression-comparison').json()['result'] is None
    assert client.get(f'/api/tracks/{identity}/notes').json()['interpretation']=='Authored note'


def test_missing_installation_never_triggers_a_download(client,monkeypatch):
    identity=client.post('/api/tracks',files={'file':('authored.wav',wav_bytes())}).json()['id']
    monkeypatch.setattr(expression_compare,'ready',lambda:False)
    assert client.post(f'/api/tracks/{identity}/expression-comparison',json={}).status_code==409


def test_cancellation_terminates_worker_and_removes_only_scratch(tmp_path,monkeypatch):
    stopped=[]
    class Process:
        returncode=None
        def poll(self):return self.returncode
        def terminate(self):stopped.append(True);self.returncode=-1
        def wait(self,timeout=None):return self.returncode
    event=threading.Event()
    def start(*args,**kwargs):event.set();return Process()
    monkeypatch.setattr(expression_compare,'ready',lambda:True)
    monkeypatch.setattr(expression_compare.subprocess,'Popen',start)
    original=tmp_path/'original.wav';original.write_bytes(b'authored source')
    with pytest.raises(cancellation.Cancelled),cancellation.scope(event):
        expression_compare.analyse(original,tmp_path,'cpu',lambda *args:None)
    assert stopped and original.read_bytes()==b'authored source'
    assert not list(tmp_path.glob('expression-*'))
