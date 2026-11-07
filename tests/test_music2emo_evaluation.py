import pytest
from scripts.music2emo_evaluation import checked_result,replace_once,segment_ranges


def test_regression_scale_and_independent_tags_are_preserved():
    result=checked_result({'valence':3,'arousal':7,'tag_scores':{'sad':.8,'happy':.7}})
    assert result['valence']==-.5 and result['arousal']==.75
    assert result['valence_raw']==3 and not result['outside_training_scale']
    assert sum(result['tags'].values())==1.5 and 'scores' not in result


def test_out_of_range_regression_is_flagged_and_raw_value_kept():
    result=checked_result({'valence':10,'arousal':0,'tag_scores':{'sad':.1}})
    assert result['outside_training_scale'] and result['valence_raw']==10
    assert result['valence']==1 and result['arousal']==0


@pytest.mark.parametrize('invalid',[float('nan'),float('inf'),True,None])
def test_invalid_predictions_never_become_neutral(invalid):
    with pytest.raises(ValueError):checked_result({'valence':invalid,'arousal':5,'tag_scores':{'sad':.2}})
    with pytest.raises(ValueError):checked_result({'valence':5,'arousal':5,'tag_scores':{'sad':invalid}})


def test_adaptation_stops_on_unexpected_upstream_code():
    with pytest.raises(ValueError):replace_once('changed source','expected','replacement')
    with pytest.raises(ValueError):replace_once('expected expected','expected','replacement')


def test_decoder_tail_does_not_become_a_third_equally_weighted_segment():
    assert segment_ranges(60001,1000)==[(0,30000),(30000,60001)]
    assert segment_ranges(45000,1000)==[(0,30000),(30000,45000)]
    assert segment_ranges(10000,1000)==[(0,10000)]
    assert segment_ranges(30001,1000)==[(0,30001)]
    with pytest.raises(ValueError):segment_ranges(0,1000)
