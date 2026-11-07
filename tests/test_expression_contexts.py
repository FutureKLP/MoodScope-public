import numpy as np
import pytest
from scripts.music2emo_curve import context_spans,predict_spans


def test_short_song_runs_model_once_without_dropping_display_intervals():
    calls=[];updates=[]
    def predict(clip):
        calls.append(clip.copy())
        return {'valence': 6, 'arousal': 7, 'tag_scores': {'calm': .3}}
    audio=np.arange(240,dtype=float)
    rows=predict_spans(audio,10,list(context_spans(24)),predict,lambda *x:updates.append(x))
    assert len(calls)==1 and np.array_equal(calls[0],audio)
    assert len(rows)==5 and rows[-1]['end']==24
    assert updates[-1]==(5,5) and all(r['valence']==.25 for r in rows)


def test_only_identical_contexts_are_reused():
    calls=[]
    def predict(clip):
        calls.append(clip[0])
        return {'valence': 5, 'arousal': 5, 'tag_scores': {'calm': .5}}
    spans=list(context_spans(47))
    predict_spans(np.arange(470,dtype=float),10,spans,predict,lambda *x:None)
    assert len(calls)==len({(s['context_start'],s['context_end']) for s in spans})
    assert len(calls)<len(spans)


def test_invalid_audio_and_infinite_duration_fail_before_inference():
    with pytest.raises(ValueError):list(context_spans(float('inf')))
    with pytest.raises(ValueError):
        predict_spans(np.array([float('nan')]),1,list(context_spans(1)),lambda _:pytest.fail('Must not infer'),lambda *x:None)
