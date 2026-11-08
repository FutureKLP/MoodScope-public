"""Time-aligned cross-modal evidence, without an unvalidated fused emotion score."""
import math

VERSION='joint-evidence-v1'
NEUTRAL_BAND=.15  # Display convention; not a psychological or confidence threshold.


def direction(value):
    return 'positive' if value>NEUTRAL_BAND else 'negative' if value<-NEUTRAL_BAND else 'mixed'


def timeline(analysis):
    rows=[]
    lyrics=analysis.get('lyrics',[])
    for audio in analysis.get('audio',[]):
        start,end=audio['start'],audio['end']
        if end<=start or not math.isfinite(audio['valence']):
            raise ValueError('Invalid audio evidence interval')
        overlaps=[(i,row,max(0.,min(end,row['end'])-max(start,row['start']))) for i,row in enumerate(lyrics)]
        overlaps=[item for item in overlaps if item[2]>0]
        # Divide at every boundary so simultaneous/overlapping lines cannot inflate coverage.
        boundaries=sorted({start,end,*[max(start,row['start']) for _,row,_ in overlaps],
                           *[min(end,row['end']) for _,row,_ in overlaps]})
        covered=usable=weighted=0.
        for left,right in zip(boundaries,boundaries[1:]):
            active=[row for _,row,_ in overlaps if row['start']<right and row['end']>left]
            if not active:continue
            covered+=right-left
            reliable=[row for row in active if not row.get('uncertain') and math.isfinite(row.get('valence',float('nan')))]
            if not reliable:continue
            usable+=right-left
            weighted+=(right-left)*sum(row['valence'] for row in reliable)/len(reliable)
        value=weighted/usable if usable else None
        unstable=bool(audio.get('outside_training_scale')) or (
            audio.get('prompt_valence_min',1)<-NEUTRAL_BAND and audio.get('prompt_valence_max',-1)>NEUTRAL_BAND)
        if covered<(end-start)*.5:relation='music_only'
        elif usable<(end-start)*.5:relation='uncertain_text'
        elif unstable:relation='uncertain_audio'
        elif direction(audio['valence'])=='mixed' or direction(value)=='mixed':relation='mixed'
        elif direction(audio['valence'])==direction(value):relation='aligned'
        else:relation='contrasting'
        sections=analysis.get('features',{}).get('sections',[])
        section=next((row for row in sections if row['start']<end and row['end']>start),None)
        rows.append({'start':start,'end':end,'audio_valence':audio['valence'],'lyric_valence':value,
                     'text_coverage':covered/(end-start),'usable_text_coverage':usable/(end-start),
                     'text_references':[f'L{i+1}' for i,_,_ in overlaps],
                     'relation':relation,'audio_direction':direction(audio['valence']),
                     'lyric_direction':direction(value) if value is not None else None,
                     'feature_window':{'start':section['start'],'end':section['end']} if section else None})
    return {'version':VERSION,'audio_source':analysis.get('expression_source','analysis'),
            'neutral_band':NEUTRAL_BAND,'calibrated':False,'fused_score':None,'rows':rows}


def observations(analysis,position=None,limit=8):
    rows=timeline(analysis)['rows']
    if position is not None:rows=[row for row in rows if row['start']<=position<row['end']]
    if len(rows)>limit:
        indices={0,len(rows)-1}
        # Preserve brief contradictions and missing/uncertain evidence in whole-song readings.
        for relation in ('contrasting','uncertain_text','uncertain_audio','aligned','mixed','music_only'):
            found=next((i for i,row in enumerate(rows) if row['relation']==relation),None)
            if found is not None and len(indices)<limit:indices.add(found)
        for i in range(limit):
            if len(indices)<limit:indices.add(round(i*(len(rows)-1)/(limit-1)))
        rows=[row for i,row in enumerate(rows) if i in indices]
    return rows
