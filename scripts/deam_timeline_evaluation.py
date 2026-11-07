"""Score saved curves against local DEAM dynamic annotations; never runs inference."""
import argparse
import csv
import json
import math
import re
from pathlib import Path


def annotations(path):
    result = {}
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            identity = row.pop('song_id').strip()
            if identity in result:
                raise ValueError('Duplicate reference identity')
            points = []
            for key, value in row.items():
                match = re.fullmatch(r'sample_(\d+)ms', key)
                if not match:
                    raise ValueError('Unexpected annotation column')
                if value is not None and value.strip():
                    number = float(value)
                    if not math.isfinite(number) or not -1 <= number <= 1:
                        raise ValueError('Invalid dynamic reference scale')
                    points.append((int(match[1]) / 1000, number))
            result[identity] = sorted(points)
    return result


def metrics(pairs):
    if not pairs:
        raise ValueError('No aligned reference points')
    count = len(pairs)
    target_mean = sum(a for a, _ in pairs) / count
    predicted_mean = sum(b for _, b in pairs) / count
    target_var = sum((a-target_mean)**2 for a, _ in pairs) / count
    predicted_var = sum((b-predicted_mean)**2 for _, b in pairs) / count
    covariance = sum((a-target_mean)*(b-predicted_mean) for a, b in pairs) / count
    denominator = target_var + predicted_var + (target_mean-predicted_mean)**2
    return {'samples': count,
            'mae': sum(abs(a-b) for a, b in pairs)/count,
            'rmse': math.sqrt(sum((a-b)**2 for a, b in pairs)/count),
            'ccc': 2*covariance/denominator if denominator > 1e-15 else None}


def align(curve, references, dimension):
    previous = -1.0
    for row in curve:
        start, end, value = row['start'], row['end'], row[dimension]
        if not all(math.isfinite(v) for v in (start, end, value)):
            raise ValueError('Nonfinite prediction')
        if start < previous or start < 0 or end <= start:
            raise ValueError('Overlapping or unordered prediction intervals')
        low = 0 if dimension == 'arousal' else -1
        if not low <= value <= 1:
            raise ValueError('Invalid prediction scale')
        previous = end
    pairs = []
    for time, target in references:
        row = next((r for r in curve if r['start'] <= time < r['end']), None)
        if row is not None:
            # DEAM dynamic arousal is [-1,1]; the application uses [0,1].
            pairs.append(((target+1)/2 if dimension == 'arousal' else target, row[dimension]))
    return pairs


def evaluate(rows, references):
    output = {}
    identities = [str(row['track_id']) for row in rows]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate prediction identity')
    for model in ('music2emo', 'clap_v7'):
        output[model] = {}
        for dimension in ('valence', 'arousal'):
            pooled, centered, flat, per_track = [], [], [], []
            expected = 0
            for row in rows:
                reference = references[dimension][str(row['track_id'])]
                expected += len(reference)
                pairs = align(row['music2emo_curve' if model == 'music2emo' else 'clap_curve'], reference, dimension)
                score = metrics(pairs)
                per_track.append(score)
                pooled.extend(pairs)
                target_mean = sum(a for a, _ in pairs)/len(pairs)
                prediction_mean = sum(b for _, b in pairs)/len(pairs)
                centered.extend((a-target_mean, b-prediction_mean) for a, b in pairs)
                flat.extend((a, prediction_mean) for a, _ in pairs)
            output[model][dimension] = {
                'tracks': len(per_track), 'coverage': len(pooled)/expected,
                'pooled': metrics(pooled), 'within_track_centered': metrics(centered),
                'flat_prediction_baseline': metrics(flat),
                'macro_track_mae': sum(m['mae'] for m in per_track)/len(per_track)}
    return {'target': 'perceived_expression_dynamic', 'alignment': 'stored_half_open_intervals',
            'lag_seconds': 0, 'interpolation': False, 'metrics': output}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('predictions', 'valence', 'arousal', 'output'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    report = evaluate(json.loads(Path(args.predictions).read_text(encoding='utf8'))['rows'],
                      {key: annotations(getattr(args, key)) for key in ('valence', 'arousal')})
    # Exclusive creation protects existing evaluations and supplied input files.
    with Path(args.output).open('x', encoding='utf8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
    print(json.dumps(report, allow_nan=False))

