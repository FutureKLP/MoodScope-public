import pytest
from scripts.deam_timeline_evaluation import align, annotations, evaluate, metrics


def test_alignment_uses_real_timestamps_and_converts_only_arousal():
    curve = [{'start': 0, 'end': 15, 'arousal': 0}, {'start': 15, 'end': 20, 'arousal': .75}]
    assert align(curve, [(15, .5), (20, 1)], 'arousal') == [(.75, .75)]
    assert align([{'start': 15, 'end': 20, 'valence': -.5}], [(15, -.5)], 'valence') == [(-.5, -.5)]


def test_correct_song_mean_does_not_pass_as_correct_timeline():
    references = {key: {'1': [(15, -1), (16, 1)]} for key in ('valence', 'arousal')}
    curve = [{'start': 15, 'end': 17, 'valence': 0, 'arousal': .5}]
    report = evaluate([{'track_id': '1', 'music2emo_curve': curve, 'clap_curve': curve}], references)
    value = report['metrics']['music2emo']['valence']
    assert value['within_track_centered']['ccc'] == 0
    assert value['pooled']['rmse'] == value['flat_prediction_baseline']['rmse'] == 1
    assert value['coverage'] == 1


def test_no_silent_nan_overlap_or_empty_scoring():
    with pytest.raises(ValueError):
        align([{'start': 0, 'end': 1, 'valence': float('nan')}], [(0, 0)], 'valence')
    with pytest.raises(ValueError):
        align([{'start': 0, 'end': 2, 'valence': 0}, {'start': 1, 'end': 3, 'valence': 0}], [], 'valence')
    with pytest.raises(ValueError):
        metrics([])
    assert metrics([(1, 1), (1, 1)])['ccc'] is None


def test_reference_loader_does_not_invent_missing_first_seconds(tmp_path):
    source = tmp_path/'reference.csv'
    source.write_text('song_id,sample_15000ms,sample_15500ms\n1,-0.5,\n')
    assert annotations(source) == {'1': [(15, -.5)]}

