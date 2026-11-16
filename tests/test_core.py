from backend.core import parse_lrc, biggest_split
import pytest


def test_lrc_offsets_repeated_tags_and_fractional_seconds():
    lines = parse_lrc('[offset:-500]\n[00:01.25][00:05.500]hello\n[00:09]bye', 10)
    assert [l['start'] for l in lines] == [.75, 5., 8.5]
    assert lines[0]['end'] == 5
    assert lines[-1]['end'] == 10


def test_plain_text_has_no_invented_timestamps():
    assert parse_lrc('hello\nworld',100) == []


@pytest.mark.parametrize('text,expected',[
    ('[00:01][tag[nested]words', 'words'),
    ('[00:01]words[unclosed', 'words[unclosed'),
    ('[00:01]words]after[tag]end', 'words]afterend'),
])
def test_lrc_tag_removal_preserves_nested_and_unclosed_tag_behavior(text,expected):
    assert parse_lrc(text,10)[0]['text']==expected


def test_unclosed_lrc_tags_complete_within_bounded_subprocess():
    import subprocess
    import sys
    from pathlib import Path
    # Valid request-sized input previously spent seconds retrying every '['.
    program="from backend.core import parse_lrc; text='['*190000; rows=parse_lrc('[00:01]'+text,10); assert rows[0]['text']==text"
    subprocess.run([sys.executable,'-c',program],cwd=Path(__file__).resolve().parents[1],check=True,timeout=8,capture_output=True)


def test_empty_timed_lines_stop_lyrics_during_instrumental_breaks():
    rows=parse_lrc('[00:01]hello\n[00:03]\n[00:07]world\n[00:09]',12)
    assert [(r['start'],r['end']) for r in rows]==[(1,3),(7,9)]
    assert biggest_split([{'start':9,'end':12,'valence':1}],
                         [{**r,'valence':-1} for r in rows]) is None


def test_split_uses_duration_weighted_overlap():
    audio = [{'start':0,'end':10,'valence':1}, {'start':10,'end':20,'valence':0}]
    lyrics = [{'start':0,'end':2,'valence':1}, {'start':2,'end':10,'valence':-1}]
    result = biggest_split(audio, lyrics)
    assert result['start'] == 0
    assert result['lyric'] == pytest.approx(-.6)
    assert result['gap'] == pytest.approx(1.6)
    assert biggest_split(audio, []) is None


def test_sparse_lyrics_do_not_create_a_spurious_split():
    assert biggest_split([{'start':0,'end':10,'valence':1}],
                         [{'start':9,'end':10,'valence':-1}]) is None


def test_display_grid_covers_whole_track_without_overlaps():
    from backend.core import analysis_grid
    rows=analysis_grid(12)
    assert rows==[{'start':0,'end':5},{'start':5,'end':10},{'start':10,'end':12}]
    with pytest.raises(ValueError):analysis_grid(0)


@pytest.mark.parametrize('duration,hop',[(float('inf'),5),(12,float('nan')),(12,float('inf'))])
def test_nonfinite_grid_cannot_hang_or_create_invalid_intervals(duration,hop):
    from backend.core import analysis_grid
    with pytest.raises(ValueError):analysis_grid(duration,hop)


def test_coverage_ignores_outside_and_nonfinite_spans_without_negative_coverage():
    from backend.core import text_coverage
    rows=[{'start':-10,'end':-2}, {'start':25,'end':30}, {'start':float('nan'),'end':4}, {'start':2,'end':6}]
    value=text_coverage(rows,20)
    assert value['covered_seconds']==4
    assert value['gaps']==[{'start':6,'end':20}]
