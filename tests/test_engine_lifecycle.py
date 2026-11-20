from types import SimpleNamespace
import numpy as np
import pytest
from backend.models import Engines


@pytest.mark.parametrize('stage', ['processor', 'weights'])
def test_missing_clap_files_explain_recovery_without_partial_engine(tmp_path, monkeypatch, stage):
    import transformers
    engine = Engines()
    engine.data = tmp_path
    monkeypatch.setattr(engine, 'device', lambda *args: 'cpu')
    def missing(*args, **kwargs):
        raise OSError('loader internals must not become the user message')
    monkeypatch.setattr(transformers.ClapProcessor, 'from_pretrained',
                        missing if stage == 'processor' else lambda *args, **kwargs: object())
    monkeypatch.setattr(transformers.ClapModel, 'from_pretrained', missing)
    with pytest.raises(ValueError, match='Installation prüfen') as error:
        engine.audio(np.zeros(48000), 48000, lambda *args: None)
    assert 'loader internals' not in str(error.value)
    assert engine.processor is None and engine.audio_model is None


@pytest.mark.parametrize('invalid',[False,True])
def test_clap_rejects_nonfinite_predictions_and_preserves_valid_formula(tmp_path,monkeypatch,invalid):
    import torch
    from backend import prompt_presets
    engine=Engines();engine.data=tmp_path
    monkeypatch.setattr(engine,'device',lambda *args:'cpu')
    monkeypatch.setattr(prompt_presets,'content',lambda *args:'\n'.join(['authored prompt']*12))
    class Inputs(dict):
        def to(self,device):return self
    engine.processor=lambda **kwargs:Inputs()
    logits=torch.zeros((1,12))
    if invalid:logits[0,0]=float('nan')
    engine.audio_model=lambda **kwargs:SimpleNamespace(logits_per_audio=logits)
    if invalid:
        with pytest.raises(ValueError,match='CLAP lieferte'):engine.audio(np.zeros(48000),48000,lambda *args:None)
    else:
        result=engine.audio(np.zeros(48000),48000,lambda *args:None)
        assert len(result)==1 and result[0]['end']==1
        assert sum(result[0]['scores'].values())==pytest.approx(1)
        from backend.audio_method import VALENCE,AROUSAL
        assert result[0]['valence']==pytest.approx(sum(VALENCE)/6)
        assert result[0]['arousal']==pytest.approx(sum(AROUSAL)/6)


def test_lyric_batch_cancellation_prevents_later_inference(tmp_path,monkeypatch):
    import threading
    from backend import cancellation
    engine=Engines();engine.data=tmp_path;event=threading.Event();calls=[]
    def predict(lines,**kwargs):
        calls.append(len(lines));event.set()
        return [[{'label':name,'score':.25} for name in ['joy','sadness','anger','fear']] for line in lines]
    engine.lyric_pipe=predict
    with pytest.raises(cancellation.Cancelled),cancellation.scope(event):
        engine.lyrics([{'start':i,'end':i+1,'text':'Authored words'} for i in range(17)],lambda *args:None)
    assert calls==[8]


def test_nonfinite_lyric_scores_are_not_published():
    engine=Engines()
    engine.lyric_pipe=lambda lines,**kwargs:[[
        {'label':name,'score':float('nan') if name=='joy' else .25}
        for name in ['joy','sadness','anger','fear']] for line in lines]
    with pytest.raises(ValueError,match='Emotionswerte'):
        engine.lyrics([{'start':0,'end':1,'text':'Authored words'}],lambda *args:None)


def test_text_model_switch_reloads_selected_source_with_controlled_doubles(tmp_path, monkeypatch):
    """Selection/lifecycle regression only; no second real model inference."""
    import transformers
    from backend import app, catalog
    engine = Engines()
    engine.data = tmp_path
    monkeypatch.setattr(engine, 'device', lambda *args: 'cpu')
    monkeypatch.setattr(app, 'engines', engine)
    monkeypatch.setattr(app, 'DATA', tmp_path)
    monkeypatch.setattr(app, 'jobs', {})
    second = 'controlled-text-fixture'
    models = {**catalog.CATALOG, second: {
        'repo': 'fixture/text-emotions', 'purpose': 'lyrics', 'custom': True}}
    monkeypatch.setattr(catalog, 'entries', lambda data: models)
    monkeypatch.setattr(catalog, 'status', lambda data: catalog.configuration(data))
    fixture = tmp_path / 'controlled-text-model'
    fixture.mkdir()
    catalog.save(tmp_path, {'active': {}, 'installed': {second: str(fixture)}})
    loaded = []

    def pipeline(task, *, model, **kwargs):
        loaded.append(model)
        dominant = 'sadness' if model == str(fixture) else 'joy'
        def predict(lines, **kwargs):
            return [[{'label': label, 'score': .7 if label == dominant else .1}
                     for label in ('joy', 'sadness', 'anger', 'fear')] for line in lines]
        return predict

    monkeypatch.setattr(transformers, 'pipeline', pipeline)
    values = []
    for key in ('xlm-emo', second, 'xlm-emo'):
        app.select_model(app.ModelChoice(model_id=key))
        assert engine.lyric_pipe is None
        values.append(engine.lyrics([{'start': 0, 'end': 1, 'text': 'Authored fixture'}],
                                    lambda *args: None, context_weight=0)[0]['valence'])
    assert loaded == [catalog.CATALOG['xlm-emo']['repo'], str(fixture),
                      catalog.CATALOG['xlm-emo']['repo']]
    assert values[0] > 0 and values[1] < 0 and values[2] == values[0]
