"""Diagnostic-tool contracts; all scores here are authored numerical fixtures."""
import json
import math

import pytest

from scripts import audio_evaluation as evaluation


def manifest(tmp_path, cases):
    source = tmp_path/'source.bin'
    source.write_bytes(b'authored input, not music')
    path = tmp_path/'manifest.json'
    path.write_text(json.dumps({'protocol': evaluation.PROTOCOL, 'cases': cases}), encoding='utf8')
    return path


def case(identity='case_1', recording='recording_1', split='holdout', **changes):
    return {'case_id': identity, 'recording_id': recording, 'split': split,
            'source': 'source.bin', 'start': 0, 'duration': 10, **changes}


def test_manifest_preserves_sources_and_hashes_them(tmp_path):
    path = manifest(tmp_path, [case()])
    result = evaluation.load_manifest(path)
    assert result[0]['source_sha256'] == evaluation.digest(tmp_path/'source.bin')
    assert (tmp_path/'source.bin').read_bytes() == b'authored input, not music'


@pytest.mark.parametrize('changes', [{'start': -1}, {'duration': 11}, {'duration': 0},
                                   {'start': float('nan')}, {'case_id': '../unsafe'}, {'split': 'training'}])
def test_invalid_ranges_ids_and_splits_are_rejected(tmp_path, changes):
    with pytest.raises(ValueError):
        evaluation.load_manifest(manifest(tmp_path, [case(**changes)]))


def test_identical_files_cannot_leak_across_splits_even_with_different_recording_ids(tmp_path):
    with pytest.raises(ValueError, match='crosses'):
        evaluation.load_manifest(manifest(tmp_path, [case(), case('case_2','other_recording','development')]))


def test_variants_of_a_recording_cannot_cross_splits(tmp_path):
    path=manifest(tmp_path, [case(), case('case_2','recording_1','development',source='variant.bin')])
    (tmp_path/'variant.bin').write_bytes(b'different encoding')
    with pytest.raises(ValueError, match='crosses'):
        evaluation.load_manifest(path)


def test_literal_legacy_prompts_are_preserved_and_wording_ablation_is_controlled():
    assert list(evaluation.METHODS['legacy6']) == evaluation.LEGACY_LABELS
    original = [p for rows in evaluation.METHODS['legacy6'].values() for p in rows]
    assert original == evaluation.LEGACY_PROMPTS
    modified = [p for rows in evaluation.METHODS['anger_wording6'].values() for p in rows]
    assert [i for i,(a,b) in enumerate(zip(original,modified)) if a!=b] == [6]


def numerical_fixture():
    prompts, indices = evaluation.prompt_bank()
    logits = [0.]*len(prompts); similarities = [0.]*len(prompts)
    return prompts, indices, logits, similarities


def test_independent_facets_can_both_be_high_without_competing():
    prompts, indices, logits, similarities = numerical_fixture()
    for label in ['melancholy','despair']:
        for i in indices[f'facet:{label}']:
            similarities[i] = .7
    result = evaluation.estimates(logits, similarities, indices)
    assert result['facet_similarities']['melancholy'] == pytest.approx(.7)
    assert result['facet_similarities']['despair'] == pytest.approx(.7)
    assert result['methods']['legacy6']['legacy_valence'] == pytest.approx(-.65/6)


def test_energy_and_harshness_do_not_force_anger_or_valence():
    _, indices, logits, similarities = numerical_fixture()
    for axis in ['energy','harshness']:
        for i in indices[f'axis:{axis}:0']:
            logits[i] = 8
    result = evaluation.estimates(logits, similarities, indices)
    assert result['axes']['energy']['uncalibrated_coordinate'] > .99
    assert result['axes']['valence']['uncalibrated_coordinate'] == 0
    assert result['methods']['legacy6']['scores']['anger'] == pytest.approx(1/6)


def report_and_ratings():
    _, indices, logits, similarities = numerical_fixture()
    estimates = evaluation.estimates(logits, similarities, indices)
    rows = [{'case_id':f'case_{i}', 'recording_id':f'recording_{i}', 'split':'holdout',
             'gain_db':0, 'estimates':estimates} for i in range(3)]
    ratings = [{'case_id':row['case_id'], 'rater_id':f'rater_{i}', 'values':{'valence':0,'melancholy':.8}}
               for row in rows for i in range(3)]
    return {'protocol':evaluation.PROTOCOL,'manifest_sha256':'authored-fixture','rows':rows}, {'protocol':evaluation.PROTOCOL,'manifest_sha256':'authored-fixture','target':'perceived_expression','ratings':ratings}


def test_no_human_reference_is_invented_and_partial_ratings_are_unknown():
    report, ratings = report_and_ratings()
    ratings['ratings'] = ratings['ratings'][:2]
    result = evaluation.score_humans(report,ratings)
    assert result['dimensions'] == {} and result['cases_without_reference'] == 3


def test_human_metrics_separate_disagreement_from_model_scores():
    report, ratings = report_and_ratings()
    ratings['ratings'][0]['values']['valence'] = -.5
    result = evaluation.score_humans(report,ratings)
    assert result['dimensions']['valence']['metrics']['independent_axis']['mae'] == 0
    assert 'mae' not in result['dimensions']['melancholy']['metrics']['independent_similarity']
    assert result['dimensions']['valence']['metrics']['independent_axis']['spearman'] is None


def test_development_ratings_do_not_enter_holdout_metrics():
    report, ratings = report_and_ratings()
    report['rows'][0]['split']='development'
    result=evaluation.score_humans(report,ratings)
    assert result['dimensions']['valence']['cases']==2


def test_ratings_from_a_different_manifest_are_rejected():
    report,ratings=report_and_ratings();ratings['manifest_sha256']='different-fixture'
    with pytest.raises(ValueError,match='same frozen manifest'):
        evaluation.score_humans(report,ratings)


@pytest.mark.parametrize('kind',['duplicate','unknown_case','wrong_target','out_of_range','boolean'])
def test_invalid_human_ratings_are_rejected(kind):
    report, ratings = report_and_ratings()
    if kind=='duplicate': ratings['ratings'].append(ratings['ratings'][0])
    if kind=='unknown_case': ratings['ratings'][0]['case_id']='missing'
    if kind=='wrong_target': ratings['target']='felt_emotion'
    if kind=='out_of_range': ratings['ratings'][0]['values']['valence']=2
    if kind=='boolean': ratings['ratings'][0]['values']['valence']=True
    with pytest.raises(ValueError):evaluation.score_humans(report,ratings)


def test_spearman_ties_and_temperature_do_not_invent_discrimination():
    assert evaluation.ranks([3,1,1]) == [2,.5,.5]
    assert evaluation.correlation([1,1],[2,3]) is None
    assert evaluation.softmax([1000,1000]) == [.5,.5]
    with pytest.raises(ValueError):evaluation.softmax([math.inf,0])


def test_output_refuses_source_tree_and_existing_run(tmp_path,monkeypatch):
    monkeypatch.setattr(evaluation,'__file__',str(tmp_path/'scripts/audio_evaluation.py'))
    with pytest.raises(ValueError):evaluation.output_directory(tmp_path/'backend')
    destination=tmp_path/'.tools/run'
    assert evaluation.output_directory(destination)==destination
    with pytest.raises(FileExistsError):evaluation.output_directory(destination)


def test_run_never_resolves_a_remote_model(tmp_path):
    path=manifest(tmp_path,[case()])
    with pytest.raises(ValueError,match='downloads are disabled'):
        evaluation.run(path,tmp_path/'.tools/run',tmp_path/'missing-model')
    assert not (tmp_path/'.tools/run').exists()


def test_level_matching_controls_gain_without_changing_relative_dynamics():
    import numpy as np
    audio=np.array([.02,-.2,.1,.04],dtype='float32')
    matched=evaluation.level_match(audio)
    assert np.allclose(matched,evaluation.level_match(audio*.25),rtol=1e-6)
    assert np.allclose(matched/audio,np.full_like(audio,matched[0]/audio[0]))
    assert np.sqrt(np.mean(matched**2))==pytest.approx(.1)
    assert np.max(np.abs(evaluation.level_match(np.array([1.]+[0.]*1000))))<=.99+1e-6
    assert np.array_equal(evaluation.level_match(np.zeros(8)),np.zeros(8))


def test_blind_preparation_keeps_ratings_empty_and_does_not_load_a_model(tmp_path,monkeypatch):
    import numpy as np
    import soundfile as sf
    monkeypatch.setattr(evaluation,'__file__',str(tmp_path/'scripts/audio_evaluation.py'))
    source=tmp_path/'authored.wav';sf.write(source,np.zeros((48000,2)),48000)
    path=tmp_path/'manifest.json'
    path.write_text(json.dumps({'protocol':evaluation.PROTOCOL,'cases':[case(source='authored.wav',duration=1)]}),encoding='utf8')
    before=evaluation.digest(source)
    result=evaluation.prepare(path,tmp_path/'.tools/prepared')
    assert result['cases']==1 and result['human_ratings']==0
    packet=json.loads((tmp_path/'.tools/prepared/human-ratings.json').read_text())
    assert packet['ratings']==[] and packet['manifest_sha256']==evaluation.digest(path)
    assert len(packet['suggested_blind_orders'])==3
    assert sf.info(tmp_path/'.tools/prepared/listening/case_1.wav').frames==48000
    assert evaluation.digest(source)==before
