import csv
import pytest
from scripts.emotify_evaluation import reference,member_name,GEMS,metrics


def test_induced_response_import_excludes_demographics_and_invalid_selections(tmp_path):
    path=tmp_path/'reference.csv'
    with path.open('w',newline='') as output:
        writer=csv.writer(output);writer.writerow(['track id','genre',*GEMS,'age','mood'])
        writer.writerow(['101','rock',0,0,0,1,0,1,0,0,1,'ignored demographic','ignored mood'])
        writer.writerow(['101','rock',1,1,1,1,0,0,0,0,0,'ignored','ignored'])
    data=reference(path)['101']
    assert data['target']=='induced_emotion' and data['responses']==1 and data['excluded_responses']==1
    assert data['mean_selected_feelings']==3 and data['frequencies']['power']==1
    assert 'age' not in data and 'mood' not in data


def test_annotation_ids_match_genre_local_archive_members():
    assert member_name('101','rock')=='rock/1.mp3'
    assert member_name('201','electronic')=='electronic/1.mp3'
    assert member_name('400','pop')=='pop/100.mp3'
    with pytest.raises(ValueError):member_name('101','classical')


def test_correlations_do_not_treat_external_induced_labels_as_perceived_truth():
    rows=[{'reference':{'frequencies':{key:.5 for key in GEMS},'mean_selected_feelings':2},
        'gems_cosine':{key:.2 for key in GEMS},'gems_softmax':{key:1/9 for key in GEMS},
        'legacy6':{'sadness':.1,'calm':.1,'tenderness':.1}} for _ in range(3)]
    result=metrics(rows)
    assert result['not_a_perceived_expression_benchmark']
    assert result['dimensions']['power']['gems_cosine']['spearman'] is None
    assert 'legacy6' not in result['dimensions']['power']
