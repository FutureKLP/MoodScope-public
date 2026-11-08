"""External induced-emotion check; never a perceived-expression ground truth.

Input: the public Emotify annotation CSV (demographic columns are ignored), a
private selected.json with global track IDs and provenance, and matching audio.
No automatic downloads, fitting, app imports, or publication of reference data.
"""
import argparse
from collections import defaultdict
import csv
import json
import math
import os
from pathlib import Path
import statistics
import time

from .audio_evaluation import digest, softmax, correlation, ranks, level_match, output_directory
from backend.audio_method import LABELS, PROMPTS, VALENCE

SOURCE='https://www2.projects.science.uu.nl/memotion/emotifydata/'
GEMS={
    'amazement':['filled with wonder and amazement','amazed, moved and dazzled'],
    'solemnity':['solemn and transcendent','inspiring and spiritually moving'],
    'tenderness':['tender and affectionate','loving and gentle'],
    'nostalgia':['nostalgic and melancholic','dreamy and sentimental'],
    'calmness':['calm and relaxed','serene and meditative'],
    'power':['powerful and triumphant','strong, heroic and energetic'],
    'joyful_activation':['joyful and animated','bouncy and danceable'],
    'tension':['tense and nervous','uneasy and agitated'],
    'sadness':['sad and sorrowful','depressed and mournful'],
}

# A separately evaluated descriptor candidate; never activated in the product.
GEMS_REVISED={
    'amazement':['awe, wonder and fascination','amazed and emotionally moved'],
    'solemnity':['solemn, reverent and contemplative','transcendent and spiritually moved'],
    'tenderness':['tender, affectionate and warm','gentle, loving and compassionate'],
    'nostalgia':['nostalgic, wistful and longing','sentimental and yearning for the past'],
    'calmness':['peaceful, calm and relaxed','serene and soothed'],
    'power':['empowered, determined and confident','triumphant, courageous and strong'],
    'joyful_activation':['joyful, happy and uplifting','cheerful, delighted and celebratory'],
    'tension':['tense, anxious and uneasy','restless, nervous and apprehensive'],
    'sadness':['sad, melancholic and sorrowful','grieving and mournful'],
}


def reference(path):
    grouped=defaultdict(list);genres={};excluded=defaultdict(int)
    with Path(path).open(encoding='utf8',newline='') as source:
        for raw in csv.DictReader(source):
            row={k.strip():v.strip() for k,v in raw.items() if k is not None}
            identity=row['track id'];genre=row['genre']
            if genre not in {'classical','rock','electronic','pop'}:raise ValueError('Unknown genre')
            values={key:float(row[key]) for key in GEMS}
            if any(value not in {0.,1.} for value in values.values()):
                raise ValueError('Expected binary strong-feeling selections')
            if sum(values.values())>3:
                excluded[identity]+=1
                continue
            if identity in genres and genres[identity]!=genre:raise ValueError('Conflicting track genres')
            genres[identity]=genre;grouped[identity].append(values)
    return {identity:{'target':'induced_emotion','genre':genres[identity],'responses':len(rows),'excluded_responses':excluded[identity],
        'frequencies':{key:statistics.mean(row[key] for row in rows) for key in GEMS},
        'mean_selected_feelings':statistics.mean(sum(row.values()) for row in rows)}
        for identity,rows in grouped.items()}


def member_name(identity,genre):
    offset={'classical':0,'rock':100,'electronic':200,'pop':300}[genre]
    local=int(identity)-offset
    if not 1<=local<=100:raise ValueError('Global Emotify ID does not match genre')
    return f'{genre}/{local}.mp3'


def metrics(rows):
    result={'target':'induced_emotion','not_a_perceived_expression_benchmark':True,'tracks':len(rows),'dimensions':{}}
    for key in GEMS:
        actual=[row['reference']['frequencies'][key] for row in rows]
        current={}
        for method in ['gems_cosine','gems_softmax']:
            predicted=[row[method][key] for row in rows]
            current[method]={'spearman':correlation(ranks(actual),ranks(predicted)) if len(rows)>=3 else None}
        # Only explicitly matching broad categories; no fabricated zeroes for absent categories.
        mapped={'sadness':'sadness','calmness':'calm','tenderness':'tenderness'}.get(key)
        if mapped:
            predicted=[row['legacy6'][mapped] for row in rows]
            current['legacy6']={'spearman':correlation(ranks(actual),ranks(predicted)) if len(rows)>=3 else None}
        result['dimensions'][key]=current
    valid=[row['reference']['mean_selected_feelings'] for row in rows]
    result['mean_human_selected_feelings']=statistics.mean(valid)
    return result


def run(annotations,selection,audio_directory,model_directory,output,device='cpu',descriptor_profile='original'):
    descriptors={'original':GEMS,'revised':GEMS_REVISED}[descriptor_profile]
    import numpy as np
    import soundfile as sf
    import librosa
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',USE_TF='0',USE_FLAX='0')
    import torch
    from transformers import ClapModel,ClapProcessor
    references=reference(annotations);selected=json.loads(Path(selection).read_text(encoding='utf8'))['tracks']
    if not selected or len({track['track_id'] for track in selected})!=len(selected):
        raise ValueError('Select distinct external tracks')
    model_directory=Path(model_directory)
    if not model_directory.is_dir():raise ValueError('Use an existing local model snapshot')
    for track in selected:
        ref=references[track['track_id']]
        if track['source_member']!=member_name(track['track_id'],ref['genre']):raise ValueError('Mismatched annotation/audio ID')
        if digest(Path(audio_directory)/f'{track["track_id"]}.mp3')!=track['sha256']:raise ValueError('Audio hash mismatch')
    destination=output_directory(output)
    processor=ClapProcessor.from_pretrained(model_directory,local_files_only=True)
    model=ClapModel.from_pretrained(model_directory,local_files_only=True).to(device).eval()
    names=list(descriptors);texts=PROMPTS+[f'The music evokes feelings that are {word}.' for words in descriptors.values() for word in words]
    rows=[];started=time.perf_counter()
    for number,track in enumerate(selected):
        path=Path(audio_directory)/f'{track["track_id"]}.mp3'
        audio,sr=sf.read(path,always_2d=True,dtype='float32');audio=audio.mean(axis=1)
        target=processor.feature_extractor.sampling_rate
        if sr!=target:audio=librosa.resample(audio,orig_sr=sr,target_sr=target)
        duration=len(audio)/target
        for processing in ['original','level_matched']:
            predictions=[]
            for start in np.arange(0,duration,5):
                end=min(duration,start+5);center=(start+end)/2
                clip=audio[int(max(0,center-5)*target):int(min(duration,center+5)*target)]
                if processing=='level_matched':clip=level_match(clip)
                inp=processor(text=texts,audio=clip,sampling_rate=target,return_tensors='pt',padding=True).to(device)
                with torch.inference_mode():out=model(**inp)
                logits=out.logits_per_audio[0].float().cpu().tolist()
                cosine=(out.audio_embeds@out.text_embeds.T)[0].float().cpu().tolist()
                legacy=softmax([statistics.mean(logits[i:i+2]) for i in range(0,12,2)])
                gm=[statistics.mean(logits[i:i+2]) for i in range(12,len(logits),2)]
                gc=[statistics.mean(cosine[i:i+2]) for i in range(12,len(cosine),2)]
                predictions.append({'duration':float(end-start),'legacy':legacy,'gems_softmax':softmax(gm),'gems_cosine':gc})
            def average(key,size):return [sum(p[key][i]*p['duration'] for p in predictions)/duration for i in range(size)]
            legacy=dict(zip(LABELS,average('legacy',6)))
            rows.append({'track_id':track['track_id'],'source_sha256':track['sha256'],'processing':processing,
                'reference':references[track['track_id']],'legacy6':legacy,
                'legacy_valence':sum(legacy[label]*weight for label,weight in zip(LABELS,VALENCE)),
                'gems_softmax':dict(zip(names,average('gems_softmax',len(names)))),
                'gems_cosine':dict(zip(names,average('gems_cosine',len(names))))})
        if digest(path)!=track['sha256']:raise RuntimeError('Source changed')
        print(f'External tracks completed: {number+1}/{len(selected)}',flush=True)
    report={'version':'emotify-induced-check-v1','descriptor_profile':descriptor_profile,'source':SOURCE,'annotations_sha256':digest(annotations),
        'selection_sha256':digest(selection),'model_snapshot':model_directory.name,'device':device,
        'prompts':texts,'seconds':time.perf_counter()-started,'rows':rows,
        'metrics':{p:metrics([row for row in rows if row['processing']==p]) for p in ['original','level_matched']}}
    (destination/'external-results.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf8')
    print(json.dumps(report['metrics'],indent=2,allow_nan=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ['annotations','selection','audio-directory','model-directory','output']:parser.add_argument('--'+arg,required=True)
    parser.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    parser.add_argument('--descriptor-profile',choices=['original','revised'],default='original')
    args=parser.parse_args()
    run(args.annotations,args.selection,args.audio_directory,args.model_directory,args.output,args.device,args.descriptor_profile)
