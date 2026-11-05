"""Timing and comparison functions, independent of model inference."""
import re


def analysis_grid(duration: float, hop: float = 5.) -> list[dict]:
    if duration <= 0 or hop <= 0:
        raise ValueError('Duration and hop must be positive')
    rows=[]
    start=0.
    while start<duration:
        rows.append({'start':start,'end':min(duration,start+hop)})
        start+=hop
    return rows


def parse_lrc(text: str, duration: float) -> list[dict]:
    offset_match = re.search(r"\[offset:([+-]?\d+)\]", text, re.I)
    offset = int(offset_match[1]) / 1000 if offset_match else 0
    rows = []
    for line in text.splitlines():
        stamps = list(re.finditer(r"\[(\d+):(\d{2})(?:[.:](\d{1,3}))?\]", line))
        words = re.sub(r"\[[^\]]*\]", "", line).strip()
        for stamp in stamps:
            fraction = float('0.' + stamp[3]) if stamp[3] else 0
            start = max(0., int(stamp[1]) * 60 + int(stamp[2]) + fraction + offset)
            # Empty timed lines are real boundaries (instrumental breaks), not words.
            if start < duration:
                rows.append({"start": start, "text": words})
    rows.sort(key=lambda x: x['start'])
    for i, row in enumerate(rows):
        row['end'] = rows[i + 1]['start'] if i + 1 < len(rows) else duration
    return [row for row in rows if row['text'] and row['end'] > row['start']]


def biggest_split(audio: list[dict], lyrics: list[dict]) -> dict | None:
    """Compare each audio window against duration-weighted overlapping lyric spans."""
    candidates = []
    for a in audio:
        spans = [(max(0., min(a['end'], l['end']) - max(a['start'], l['start'])), l) for l in lyrics]
        covered = sum(w for w, _ in spans)
        if covered < .5 * (a['end']-a['start']) or covered <= 0:
            continue
        value = sum(w * l['valence'] for w, l in spans) / covered
        candidates.append({"start": a['start'], "end": a['end'], "audio": a['valence'],
                           "lyric": value, "gap": abs(a['valence'] - value),
                           "lyric_coverage":min(1.,covered/(a['end']-a['start']))})
    return max(candidates, key=lambda x: x['gap']) if candidates else None
