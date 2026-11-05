from backend.core import parse_lrc, biggest_split
import pytest


def test_lrc_offsets_repeated_tags_and_fractional_seconds():
    lines = parse_lrc('[offset:-500]\n[00:01.25][00:05.500]hello\n[00:09]bye', 10)
    assert [l['start'] for l in lines] == [.75, 5., 8.5]
    assert lines[0]['end'] == 5
    assert lines[-1]['end'] == 10


def test_plain_text_has_no_invented_timestamps():
    assert parse_lrc('hello\nworld',100) == []


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
