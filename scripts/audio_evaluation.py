"""Opt-in, offline CLAP diagnostics, isolated from the application and its database.

Run as python -m scripts.audio_evaluation --help. Private manifests, human ratings
and model outputs belong in ignored directories. No imports of backend.app.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import random
import statistics
import time

from backend.audio_method import PROMPTS as LEGACY_PROMPTS, LABELS as LEGACY_LABELS, VALENCE

PROTOCOL = 'moodscope-audio-diagnostic-v1'
REVISION = '8fa0f1c6d0433df6e97c127f64b2a1d6c0dcda8a'
WORDS = {
    'joy': ['joyful and happy', 'cheerful and celebratory', 'uplifting and exuberant'],
    'calm': ['peaceful and relaxed', 'serene and soothing', 'tranquil and meditative'],
    'tenderness': ['tender and affectionate', 'loving and gentle', 'warm and intimate'],
    'melancholy': ['melancholic and wistful', 'bittersweet and reflective', 'pensive and somber'],
    'longing': ['yearning and longing', 'nostalgic and homesick', 'aching with unfulfilled desire'],
    'sadness': ['sad and sorrowful', 'grieving and mournful', 'heartbroken and full of loss'],
    'despair': ['desperate and anguished', 'hopeless and emotionally tormented', 'painful and full of desperation'],
    'anger': ['angry and resentful', 'hostile and furious', 'outraged and confrontational'],
    'fear': ['anxious and apprehensive', 'fearful and uneasy', 'ominous and unsettling'],
    'power': ['powerful and determined', 'energetic and driving', 'intense and resolute'],
}
# Two controlled comparisons before changing the number of candidate descriptions.
LEXICAL_PROMPTS = list(LEGACY_PROMPTS)
LEXICAL_PROMPTS[6:8] = ['This music sounds angry, resentful and confrontational.',
                       'The musical expression is hostile and furious.']
BALANCED_WORDS = {k: WORDS[k][:2] for k in LEGACY_LABELS}
METHODS = {
    'legacy6': dict(zip(LEGACY_LABELS, [LEGACY_PROMPTS[i:i+2] for i in range(0, 12, 2)])),
    'anger_wording6': dict(zip(LEGACY_LABELS, [LEXICAL_PROMPTS[i:i+2] for i in range(0, 12, 2)])),
    'parallel_wording6': {k: [f'The emotional expression of this music is {w}.' for w in words]
                          for k, words in BALANCED_WORDS.items()},
    'exploratory10': {k: [f'The emotional expression of this music is {w}.' for w in words]
                      for k, words in WORDS.items()},
}
AXES = {
    'valence': [['happy and hopeful', 'pleased and content'], ['sad and distressed', 'unhappy and troubled']],
    'arousal': [['activated and excited', 'stimulated and alert'], ['restful and subdued', 'unhurried and relaxed']],
    'energy': [['energetic and driving', 'vigorous and forceful'], ['low-energy and restrained', 'soft and still']],
    'harshness': [['harsh and distorted', 'abrasive and rough'], ['smooth and clean', 'soft and mellow']],
    'tension': [['tense and uneasy', 'suspenseful and unsettled'], ['resolved and at ease', 'relaxed and untroubled']],
}
FACETS = ['melancholy', 'despair', 'anger', 'longing', 'hope', 'determination', 'triumph']
FACET_WORDS = dict(WORDS)
FACET_WORDS.update(hope=['hopeful and optimistic', 'encouraging and full of hope'],
                   determination=['determined and resolute', 'persistent and steadfast'],
                   triumph=['triumphant and victorious', 'heroic and glorious'])


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def softmax(values):
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError('Scores must be nonempty and finite')
    exp = [math.exp(v-max(values)) for v in values]
    return [v/sum(exp) for v in exp]


def load_manifest(path):
    path = Path(path).resolve()
    value = json.loads(path.read_text(encoding='utf8'))
    if value.get('protocol') != PROTOCOL or not value.get('cases'):
        raise ValueError('Unknown protocol or empty case set')
    cases = []; ids = set(); splits = {}; file_splits = {}; hashes = {}
    for original in value['cases']:
        case = dict(original)
        identity = case['case_id']; recording = case['recording_id']; split = case['split']
        if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', identity) or identity in ids:
            raise ValueError('Case IDs must be unique nonempty strings')
        if not isinstance(recording, str) or not recording or split not in {'development', 'holdout', 'diagnostic'}:
            raise ValueError('Invalid recording or split')
        source = (path.parent / case['source']).resolve()
        start, duration = float(case['start']), float(case['duration'])
        if not all(math.isfinite(v) for v in [start, duration]) or start < 0 or not 0 < duration <= 10:
            raise ValueError('Use valid nonnegative start and at most ten seconds of audio')
        if not source.is_file():
            raise ValueError('A declared source is missing')
        file_hash = hashes.setdefault(source, None)
        if file_hash is None:
            file_hash = hashes[source] = digest(source)
        for key, mapping in [(recording, splits), (file_hash, file_splits)]:
            if key in mapping and mapping[key] != split:
                raise ValueError('Recording or identical file crosses evaluation splits')
            mapping[key] = split
        ids.add(identity)
        cases.append({**case, 'source': source, 'source_sha256': file_hash, 'start': start, 'duration': duration})
    return cases


def prompt_bank():
    texts = []; indices = {}
    def add(key, prompts):
        rows = []
        for text in prompts:
            if text not in texts:
                texts.append(text)
            rows.append(texts.index(text))
        indices[key] = rows
    for method, labels in METHODS.items():
        for label, prompts in labels.items():
            add(f'{method}:{label}', prompts)
    for name, poles in AXES.items():
        for i, words in enumerate(poles):
            add(f'axis:{name}:{i}', [f'The music sounds {w}.' for w in words])
    for facet in FACETS:
        add(f'facet:{facet}', [f'The emotional expression of this music is {w}.' for w in FACET_WORDS[facet]])
    return texts, indices


def estimates(logits, similarities, indices):
    def mean(values, key):
        return statistics.mean(values[i] for i in indices[key])
    methods = {}
    for method, labels in METHODS.items():
        means = [mean(logits, f'{method}:{label}') for label in labels]
        scores = dict(zip(labels, softmax(means)))
        ordered = sorted(scores, key=scores.get, reverse=True)
        row = {'scores': scores, 'winner': ordered[0], 'score_gap': scores[ordered[0]]-scores[ordered[1]],
               'entropy_separation': 1+sum(p*math.log(max(p, 1e-12)) for p in scores.values())/math.log(len(scores))}
        if len(labels) == 6:
            row['legacy_valence'] = sum(scores[label]*weight for label, weight in zip(LEGACY_LABELS, VALENCE))
        methods[method] = row
    axes = {}
    for name in AXES:
        difference = mean(logits, f'axis:{name}:0')-mean(logits, f'axis:{name}:1')
        preference = softmax([difference, 0])[0]
        axes[name] = {'cosine_difference': mean(similarities, f'axis:{name}:0')-mean(similarities, f'axis:{name}:1'),
                      'logit_difference': difference, 'uncalibrated_coordinate': preference*2-1 if name=='valence' else preference}
    # Independent retrieval similarities: these do not sum to one or imply absence of other facets.
    facets = {name: mean(similarities, f'facet:{name}') for name in FACETS}
    return {'methods': methods, 'axes': axes, 'facet_similarities': facets}


def summary(rows):
    result = {'cases': len({r['case_id'] for r in rows}), 'audio_variants': len(rows), 'methods': {},
              'human_quality': 'Not measured without independent human ratings'}
    original = [r for r in rows if r['gain_db'] == 0]
    for method in METHODS:
        counts = Counter(r['estimates']['methods'][method]['winner'] for r in original)
        paired = {(r['case_id'], r['gain_db']): r for r in rows}
        changes = []
        for row in original:
            for (case_id, gain), other in paired.items():
                if case_id == row['case_id'] and gain != 0:
                    first, second = row['estimates']['methods'][method], other['estimates']['methods'][method]
                    changes.append({'winner_changed': first['winner'] != second['winner'],
                                    'score_l1': sum(abs(first['scores'][k]-second['scores'][k]) for k in first['scores'])})
        result['methods'][method] = {'winner_counts': dict(counts), 'gain_pairs': len(changes),
            'gain_winner_changes': sum(r['winner_changed'] for r in changes),
            'mean_gain_score_l1': statistics.mean(r['score_l1'] for r in changes) if changes else None}
    times = sorted(r['inference_seconds'] for r in rows)
    result['runtime'] = {'median_seconds': statistics.median(times), 'max_seconds': max(times)}
    return result


def ranks(values):
    ordered = sorted(range(len(values)), key=values.__getitem__); result = [0.]*len(values)
    for value in set(values):
        positions = [i for i, index in enumerate(ordered) if values[index] == value]
        rank = statistics.mean(positions)
        for i in positions:
            result[ordered[i]] = rank
    return result


def correlation(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    divisor = math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return sum((a-mx)*(b-my) for a, b in zip(x, y))/divisor if divisor else None


def score_humans(report, ratings, split='holdout', processing='original'):
    """Missing ratings are unknown, not negative; duplicates never count as extra raters."""
    if ratings.get('protocol') != PROTOCOL or ratings.get('target') != 'perceived_expression':
        raise ValueError('Use the declared protocol and perceived-expression target')
    if report.get('protocol')!=PROTOCOL or not report.get('manifest_sha256') or ratings.get('manifest_sha256')!=report['manifest_sha256']:
        raise ValueError('Human ratings must refer to the same frozen manifest')
    if split not in {'development','holdout','diagnostic'}:
        raise ValueError('Unknown evaluation split')
    all_cases = {r['case_id']: r for r in report['rows'] if r['gain_db'] == 0 and r.get('processing','original')==processing}
    cases = {key: row for key, row in all_cases.items() if row['split']==split}
    grouped = defaultdict(lambda: defaultdict(dict)); seen = set()
    for row in ratings['ratings']:
        case, rater = row['case_id'], row['rater_id']
        if case not in all_cases or not isinstance(rater, str) or not rater or (case, rater) in seen:
            raise ValueError('Unknown case or duplicate/missing rater')
        seen.add((case, rater))
        for dimension, value in row['values'].items():
            if dimension not in set(AXES)|set(FACETS):
                raise ValueError('Unknown human dimension')
            low = -1 if dimension == 'valence' else 0
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= 1:
                raise ValueError('Human score outside its scale')
            if case in cases:grouped[dimension][case][rater] = value
    result = {'split':split,'processing':processing,'independent_raters_required': 3, 'dimensions': {}, 'cases_without_reference': len(cases)}
    covered = set()
    for dimension, case_ratings in grouped.items():
        samples = []
        for case, values in case_ratings.items():
            if len(values) < 3:
                continue
            covered.add(case); scores = list(values.values())
            samples.append((cases[case], statistics.median(scores), max(scores)-min(scores)))
        if not samples:
            continue
        reference = [r[1] for r in samples]
        estimates_by_method = {}
        if dimension in AXES:
            estimates_by_method['independent_axis'] = [r[0]['estimates']['axes'][dimension]['uncalibrated_coordinate'] for r in samples]
            if dimension == 'valence':
                for method in ['legacy6', 'anger_wording6', 'parallel_wording6']:
                    estimates_by_method[method] = [r[0]['estimates']['methods'][method]['legacy_valence'] for r in samples]
        else:
            estimates_by_method['independent_similarity'] = [r[0]['estimates']['facet_similarities'][dimension] for r in samples]
            if dimension == 'anger':
                for method in METHODS:
                    estimates_by_method[method] = [r[0]['estimates']['methods'][method]['scores']['anger'] for r in samples]
        metrics = {}
        for method, predicted in estimates_by_method.items():
            metrics[method] = {'spearman': correlation(ranks(reference), ranks(predicted)) if len(samples)>=3 else None}
            # Cosine similarities and closed-set scores are not calibrated facet intensities.
            if dimension in AXES:
                metrics[method]['mae'] = statistics.mean(abs(a-b) for a,b in zip(reference,predicted))
        result['dimensions'][dimension] = {'cases': len(samples), 'recordings': len({r[0]['recording_id'] for r in samples}),
            'median_human_range': statistics.median(r[2] for r in samples), 'metrics': metrics}
    result['cases_without_reference'] -= len(covered)
    return result


def output_directory(path):
    root = Path(__file__).resolve().parents[1]
    path = Path(path).resolve()
    if not any(path.is_relative_to(base) for base in [root/'.tools', root/'data'/'evaluation']):
        raise ValueError('Evaluation outputs must stay under .tools or data/evaluation')
    path.mkdir(parents=True, exist_ok=False)
    return path


def level_match(audio):
    """Constant gain only: -20 dBFS RMS target, with 0.99 peak ceiling.

    A diagnostic nuisance control, not a loudness measurement or emotion correction.
    Preserve dynamics within the excerpt and retain original signal measurements.
    """
    import numpy as np
    rms = float(np.sqrt(np.mean(audio.astype('float64')**2)))
    peak = float(np.max(np.abs(audio)))
    gain = min(.1/rms, .99/peak) if rms>1e-12 and peak>1e-12 else 1.
    return audio*gain


def prepare(manifest, output, seed=20261107):
    """Prepare blind listening files without loading any model or assigning emotions."""
    import numpy as np
    import soundfile as sf
    import librosa
    cases=load_manifest(manifest)
    for case in cases:
        if case['start']+case['duration']>sf.info(case['source']).duration+1e-6:
            raise ValueError('An excerpt exceeds its source duration')
    destination=output_directory(output); listening=destination/'listening';listening.mkdir()
    for case in cases:
        info=sf.info(case['source'])
        audio,sr=sf.read(case['source'],start=round(case['start']*info.samplerate),
                         frames=round(case['duration']*info.samplerate),always_2d=True,dtype='float32')
        audio=audio.mean(axis=1)
        if sr!=48000:audio=librosa.resample(audio,orig_sr=sr,target_sr=48000)
        sf.write(listening/f'{case["case_id"]}.wav',audio,48000,subtype='FLOAT')
    orders=[]
    for i in range(3):
        order=[case['case_id'] for case in cases];random.Random(seed+i).shuffle(order)
        orders.append({'seed':seed+i,'case_ids':order})
    packet={'protocol':PROTOCOL,'target':'perceived_expression','manifest_sha256':digest(manifest),
            'case_ids':[case['case_id'] for case in cases],'suggested_blind_orders':orders,'ratings':[]}
    (destination/'human-ratings.json').write_text(json.dumps(packet,indent=2),encoding='utf8')
    for source,expected in {(case['source'],case['source_sha256']) for case in cases}:
        if digest(source)!=expected:raise RuntimeError('Source changed during preparation')
    return {'cases':len(cases),'recordings':len({case['recording_id'] for case in cases}),
            'split_counts':dict(Counter(case['split'] for case in cases)),'human_ratings':0}


def run(manifest, output, model_directory, device='cpu'):
    cases = load_manifest(manifest)
    manifest_hash = digest(manifest)
    model_directory = Path(model_directory).resolve()
    if not model_directory.is_dir() or not (model_directory/'config.json').is_file():
        raise ValueError('Supply an existing local CLAP snapshot; downloads are disabled')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', USE_TF='0', USE_FLAX='0')
    import numpy as np
    import soundfile as sf
    import librosa
    import torch
    from transformers import ClapModel, ClapProcessor
    from importlib.metadata import version
    # Check ranges before creating artifacts or loading weights.
    for case in cases:
        info = sf.info(case['source'])
        if case['start']+case['duration'] > info.duration+1e-6:
            raise ValueError('An excerpt exceeds its source duration')
    destination = output_directory(output)
    weight_files=sorted(set(model_directory.glob('*.safetensors'))|set(model_directory.glob('pytorch_model*.bin')))
    weight_hashes={path.name:digest(path) for path in weight_files}
    started = time.perf_counter()
    processor = ClapProcessor.from_pretrained(model_directory, local_files_only=True)
    model = ClapModel.from_pretrained(model_directory, local_files_only=True).to(device).eval()
    load_seconds = time.perf_counter()-started
    texts, indices = prompt_bank()
    rows = []; peak_memory = 0
    listening=destination/'listening';listening.mkdir()
    if device.startswith('cuda'):
        torch.cuda.reset_peak_memory_stats(device)
    for index, case in enumerate(cases):
        info = sf.info(case['source'])
        audio, sr = sf.read(case['source'], start=round(case['start']*info.samplerate),
                            frames=round(case['duration']*info.samplerate), dtype='float32', always_2d=True)
        audio = audio.mean(axis=1)
        if sr != processor.feature_extractor.sampling_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=processor.feature_extractor.sampling_rate)
        sf.write(listening/f'{case["case_id"]}.wav',audio,processor.feature_extractor.sampling_rate,subtype='FLOAT')
        for processing, gain_db in [(p,g) for p in ['original','level_matched'] for g in [0,-12]]:
            clip = audio * 10**(gain_db/20)
            source_rms_dbfs=float(20*np.log10(max(1e-12,np.sqrt(np.mean(clip**2)))))
            if processing=='level_matched':clip=level_match(clip)
            started = time.perf_counter()
            inputs = processor(text=texts, audio=clip, sampling_rate=processor.feature_extractor.sampling_rate,
                               return_tensors='pt', padding=True).to(device)
            with torch.inference_mode():
                result = model(**inputs)
                logits = result.logits_per_audio[0].float().cpu().tolist()
                similarities = (result.audio_embeds@result.text_embeds.T)[0].float().cpu().tolist()
            elapsed = time.perf_counter()-started
            rows.append({'case_id': case['case_id'], 'recording_id': case['recording_id'], 'split': case['split'],
                'start':case['start'],'duration':case['duration'],
                'gain_db': gain_db, 'processing':processing,'source_rms_dbfs':source_rms_dbfs,'source_sha256': case['source_sha256'],
                'decoded_sha256': hashlib.sha256(clip.tobytes()).hexdigest(),
                'rms_dbfs': float(20*np.log10(max(1e-12, np.sqrt(np.mean(clip**2))))),
                'peak': float(np.max(np.abs(clip))), 'inference_seconds': elapsed,
                'logits': logits, 'cosine_similarities': similarities,
                'estimates': estimates(logits, similarities, indices)})
        print(f'Cases completed: {index+1}/{len(cases)}', flush=True)
    for source, expected in {(c['source'], c['source_sha256']) for c in cases}:
        if digest(source) != expected:
            raise RuntimeError('Source changed during evaluation; results invalid')
    if digest(manifest)!=manifest_hash:
        raise RuntimeError('Manifest changed during evaluation; results invalid')
    if device.startswith('cuda'):
        peak_memory = torch.cuda.max_memory_allocated(device)
    report = {'protocol': PROTOCOL, 'manifest_sha256': manifest_hash, 'model_snapshot': model_directory.name,
        'weight_sha256':weight_hashes,
        'config_sha256': digest(model_directory/'config.json'), 'device': device,
        'packages': {name:version(name) for name in ['torch','transformers','librosa','soundfile']},
        'logit_scale': float(model.logit_scale_a.exp().detach().cpu()), 'load_seconds': load_seconds,
        'peak_torch_allocated_bytes': peak_memory, 'prompts': texts, 'prompt_indices': indices,
        'rows': rows, 'summary': {p:summary([r for r in rows if r['processing']==p]) for p in ['original','level_matched']}}
    (destination/'model-results.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf8')
    # No model estimates in the rating packet. Do not preload provisional class labels.
    packet = {'protocol': PROTOCOL, 'target': 'perceived_expression', 'manifest_sha256':manifest_hash,
              'case_ids': [case['case_id'] for case in cases], 'ratings': []}
    (destination/'human-ratings.json').write_text(json.dumps(packet, indent=2), encoding='utf8')
    print(json.dumps(report['summary'], indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    preparation=sub.add_parser('prepare',help='Create blind listening excerpts without loading a model')
    preparation.add_argument('--manifest',required=True);preparation.add_argument('--output',required=True)
    preparation.add_argument('--seed',type=int,default=20261107)
    probe = sub.add_parser('run', help='Read a private manifest and run cached CLAP only')
    probe.add_argument('--manifest', required=True)
    probe.add_argument('--output', required=True, help='New directory below .tools or data/evaluation')
    probe.add_argument('--model-directory', required=True, help='Existing local snapshot, never a model URL')
    probe.add_argument('--device', choices=['cpu','cuda','cuda:0'], default='cpu')
    score = sub.add_parser('score', help='Compare model results with independent human ratings')
    score.add_argument('--results', required=True); score.add_argument('--ratings', required=True)
    score.add_argument('--split',choices=['development','holdout','diagnostic'],default='holdout')
    score.add_argument('--processing',choices=['original','level_matched'],default='original')
    args = parser.parse_args()
    if args.command == 'prepare':
        print(json.dumps(prepare(args.manifest,args.output,args.seed),indent=2))
    elif args.command == 'run':
        run(args.manifest, args.output, args.model_directory, args.device)
    else:
        results=json.loads(Path(args.results).read_text(encoding='utf8'))
        ratings=json.loads(Path(args.ratings).read_text(encoding='utf8'))
        print(json.dumps(score_humans(results, ratings,args.split,args.processing), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
