import importlib
import threading
from concurrent.futures import ThreadPoolExecutor
import pytest
from test_api import client
from backend import cancellation


def test_submission_failure_does_not_leave_backend_busy(client,monkeypatch):
    app=importlib.import_module('backend.app')
    def fail(*args):raise RuntimeError('executor unavailable')
    monkeypatch.setattr(app.executor,'submit',fail)
    before=set(app.cancel_events)
    with pytest.raises(RuntimeError,match='executor unavailable'):
        app.start_job('fixture',lambda *args:None)
    assert not app.jobs and set(app.cancel_events)==before


def test_concurrent_admission_accepts_exactly_one_job(client,monkeypatch):
    app=importlib.import_module('backend.app');barrier=threading.Barrier(2);submitted=[]
    monkeypatch.setattr(app.executor,'submit',lambda *args:submitted.append(args))
    def start():
        barrier.wait()
        try:return app.start_job('fixture',lambda *args:None)
        except app.HTTPException as exc:return exc.status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(start) for _ in range(2)]
        values=[future.result(timeout=5) for future in futures]
    assert len(submitted)==1 and values.count(409)==1
    for identity in list(app.jobs):app.cancel_events.pop(identity,None)


def test_token_cancellation_uses_captured_scope_in_generation_thread():
    import torch
    event=threading.Event()
    with cancellation.scope(event):criteria=cancellation.generation_stopping_criteria()
    tokens=torch.zeros((1,2),dtype=torch.long)
    assert not criteria(tokens,None).any()
    event.set()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(criteria,tokens,None)
        with pytest.raises(cancellation.Cancelled):future.result(timeout=5)
    cancellation.check()


@pytest.mark.parametrize('error',[cancellation.Cancelled,RuntimeError])
def test_failed_job_releases_models_after_exception_handler(client,monkeypatch,error):
    import sys
    app=importlib.import_module('backend.app');released=[]
    app.jobs['failed']={'status':'running'};app.cancel_events['failed']=threading.Event()
    def release(engine):released.append(sys.exc_info()[1])
    monkeypatch.setattr(app.catalog,'unload_models',release)
    def fail(*args):raise error()
    app.execute_job('fixture',fail,'failed',())
    assert released==[None]
    assert app.jobs['failed']['status'] in {'cancelled','error'} and 'failed' not in app.cancel_events
