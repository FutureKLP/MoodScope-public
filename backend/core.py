"""Timing and comparison functions, independent of model inference."""
import re
import math


def text_coverage(lines,duration):
    intervals=sorted((max(0.,r['start']),min(duration,r['end'])) for r in lines
                     if math.isfinite(r['start']) and math.isfinite(r['end']) and min(duration,r['end'])>max(0.,r['start']))
    merged=[]
    for start,end in intervals:
        if merged and start<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],end)
        else:merged.append([start,end])
    gaps=[];previous=0.
    for start,end in merged:
        if start-previous>=5:gaps.append({'start':previous,'end':start})
        previous=end
    if duration-previous>=5:gaps.append({'start':previous,'end':duration})
    return {'segments':len(lines),'words':sum(len(r.get('text','').split()) for r in lines),
        'covered_seconds':sum(end-start for start,end in merged),'duration':duration,'gaps':gaps,
        'note':'Zeitbereiche mit Text sind keine Wortgenauigkeit. Lücken können Instrumentalpausen oder nicht erkannte Stimmen sein.'}


def analysis_grid(duration: float, hop: float = 5.) -> list[dict]:
    if not all(math.isfinite(v) and v>0 for v in (duration,hop)):
        raise ValueError('Duration and hop must be positive')
    rows=[]
    start=0.
    while start<duration:
        rows.append({'start':start,'end':min(duration,start+hop)})
        start+=hop
    return rows


def _lrc_words(line):
    """Remove bracketed tags in one pass, preserving an unclosed final tag."""
    parts=[];cursor=0
    while True:
        opening=line.find('[',cursor)
        if opening<0:break
        closing=line.find(']',opening+1)
        if closing<0:break
        parts.append(line[cursor:opening]);cursor=closing+1
    parts.append(line[cursor:])
    return ''.join(parts).strip()


def parse_lrc(text: str, duration: float) -> list[dict]:
    offset_match = re.search(r"\[offset:([+-]?\d+)\]", text, re.I)
    offset = int(offset_match[1]) / 1000 if offset_match else 0
    rows = []
    for line in text.splitlines():
        stamps = list(re.finditer(r"\[(\d+):(\d{2})(?:[.:](\d{1,3}))?\]", line))
        words = _lrc_words(line)
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
