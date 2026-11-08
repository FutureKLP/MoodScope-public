"""Bounded, time-aligned observations for interpretation; never emotion ground truth."""
import math

VERSION='music-observations-v2-joint'


def prompt_rows(value,language='de'):
    """Compact evidence for small language models; the UI retains exact values."""
    en=language=='en';result=[]
    for row in value['observations']:
        data=row['value']
        if 'relation' in data:
            text=(f'Time-aligned audio/text relationship: {data["relation"]}; text references {", ".join(data["text_references"]) or "none"}. This compares model tendencies, not listener feelings. Preserve contradictions and uncertain transcription.' if en else
                  f'Zeitlich zugeordnete Beziehung zwischen Musik und Text: {data["relation"]}; Textbelege {", ".join(data["text_references"]) or "keine"}. Verglichen werden Modelltendenzen, keine Hoerergefuehle. Widersprueche und unsichere Texterkennung erhalten.')
        elif data.get('direct_regression'):
            text=('Direct learned audio-valence estimate from Music2Emo; no six-category projection. Song-level training does not establish precise transitions.' if en else
                  'Direkt gelernte Audio-Valenzschaetzung von Music2Emo; keine Projektion aus sechs Kategorien. Songbewertungen im Training belegen keine praezisen Uebergaenge.')
        elif 'relative_descriptions' in data:
            text=(f'Uncalibrated audio-valence candidate {data["valence"]:+.2f}. The category ranking has not been validated as an interpretation cue and must not determine the lyric reading.' if en else
                  f'Unkalibrierter Audio-Valenzkandidat {data["valence"]:+.2f}. Die Kategorienrangfolge ist als Deutungsbeleg nicht validiert und darf die Textlesart nicht bestimmen.')
        elif 'energy_range_db' in data:
            text=(f'Measured energy development: strongest sampled section at {data["peak_start"]:.1f}–{data["peak_end"]:.1f} seconds. Energy can reinforce different feelings; it does not identify one.' if en else
                  f'Gemessene Energieentwicklung: kräftigster gemessener Abschnitt bei {data["peak_start"]:.1f}–{data["peak_end"]:.1f} Sekunden. Energie kann verschiedene Gefühle verstärken; sie legt keines fest.')
        elif 'rms_mean' in data:
            change=data['relative_to_song_db']
            text=(f'Measured relative energy: {change:+.1f} dB against song average; this is not a specific feeling.' if en else
                  f'Gemessene relative Energie: {change:+.1f} dB gegenüber dem Songmittel; das bezeichnet kein bestimmtes Gefühl.') if change is not None else ('Energy is not comparable.' if en else 'Energie ist nicht vergleichbar.')
        elif 'bpm' in data:
            text=(f'Tempo candidate {data["bpm"]:.1f} BPM; half/double tempo is possible.' if en else f'Tempokandidat {data["bpm"]:.1f} BPM; halbes/doppeltes Tempo möglich.')
        elif 'dynamic_range_db' in data:
            text=(f'Energy variation over the whole recording: {data["dynamic_range_db"]:.1f} dB; not a feeling score.' if en else f'Energieschwankung der gesamten Aufnahme: {data["dynamic_range_db"]:.1f} dB; kein Gefühlswert.')
        elif 'tonic' in data:
            text=(f'Uncertain tonal candidate: {data["tonic"]} {data["mode"]}; alternatives exist. This does not determine emotion.' if en else
                  f'Unsicherer Tonartkandidat: {data["tonic"]} {data["mode"]}; es gibt Alternativen. Das bestimmt kein Gefühl.')
        else:
            text=(f'Partial harmonic candidates cover {data.get("coverage",0):.0%} of the selection; no complete chord transcription.' if en else
                  f'Partielle Harmoniekandidaten decken {data.get("coverage",0):.0%} der Auswahl ab; keine vollständige Akkordtranskription.')
        result.append({'reference':row['id'],'observation':text})
    return result


def overlap(row,start,end):
    return max(0.,min(end,row['end'])-max(start,row['start']))


def packet(analysis,position=None):
    audio=analysis.get('audio',[]);features=analysis.get('features',{})
    duration=features.get('duration') or max([r['end'] for r in audio]+[0.])
    selected=next((r for r in audio if position is not None and r['start']<=position<r['end']),None)
    start,end=(selected['start'],selected['end']) if selected else (position,min(duration,position+1)) if position is not None else (0.,duration)
    observations=[]
    def add(kind,origin,value,limits,interval=None):
        observations.append({'id':f'M{len(observations)+1}','kind':kind,'source':origin,
            'start':(interval or (start,end))[0],'end':(interval or (start,end))[1],
            'value':value,'limits':limits})
    rows=[(row,overlap(row,start,end)) for row in audio if overlap(row,start,end)>0]
    covered=sum(weight for _,weight in rows)
    if covered:
        add('model_estimate',analysis.get('expression_source','CLAP'),{
            'valence':sum(row['valence']*weight for row,weight in rows)/covered,
            'direct_regression':analysis.get('expression_source')=='Music2Emo',
            'relative_descriptions':{label:sum(row.get('scores',{}).get(label,0)*weight for row,weight in rows)/covered
                for label in sorted({label for row,_ in rows for label in row.get('scores',{})})}},
            'Relative description similarities are uncalibrated. Anger may be confused with force or timbre. These scores must not dictate the lyric reading.')
    sections=[(row,overlap(row,start,end)) for row in features.get('sections',[]) if overlap(row,start,end)>0]
    seconds=sum(weight for _,weight in sections)
    if seconds:
        support=(min(row['start'] for row,_ in sections),max(row['end'] for row,_ in sections))
        rms=sum(row['rms']*weight for row,weight in sections)/seconds
        mean=features.get('rms_mean',0)
        if position is None:
            peak=max(sections,key=lambda pair:pair[0]['rms'])[0];trough=min(sections,key=lambda pair:pair[0]['rms'])[0]
            energy={'energy_range_db':20*math.log10(peak['rms']/trough['rms']) if peak['rms']>0 and trough['rms']>0 else None,
                    'peak_start':peak['start'],'peak_end':peak['end'],'trough_start':trough['start'],'trough_end':trough['end']}
        else:energy={'rms_mean':rms,'relative_to_song_db':20*math.log10(rms/mean) if rms>0 and mean>0 else None}
        add('measurement','audio_features',energy,
            'Relative RMS energy over the supplied feature windows, not perceived loudness. Energy can reinforce different emotions; it does not identify a particular feeling.',support)
        tempos=[(row['bpm'],weight) for row,weight in sections if row.get('bpm')]
        if tempos:add('estimate','beat_tracker',{'bpm':sum(bpm*weight for bpm,weight in tempos)/sum(weight for _,weight in tempos)},
            'Beat-derived tempo candidate; half/double tempo is possible. Speed is not emotional valence.',support)
    if not sections and features.get('bpm'):
        add('estimate','beat_tracker',{'bpm':features['bpm']},'Whole-recording tempo, not a local measurement. Half/double tempo is possible.',(0.,duration))
    if features.get('dynamic_range_db') is not None:
        add('measurement','audio_features',{'dynamic_range_db':features['dynamic_range_db']},
            'Whole-recording RMS percentile range. It is neither mastering loudness nor an emotional intensity score.',(0.,duration))
    harmony=features.get('harmony',{})
    if position is None:
        key=harmony.get('key');key_scope=(0.,duration)
    else:
        region=next((r for r in harmony.get('key_regions',[]) if r['start']<=position<r['end']),None)
        key=region.get('key') if region else None
        key_scope=(region['start'],region['end']) if region else (start,end)
    if key:
        add('candidate','harmony',key,'Key profile candidate, not a confirmed key or emotional cause. Preserve alternatives and ambiguity.',key_scope)
    chords=[(row,overlap(row,start,end)) for row in harmony.get('chords',[]) if row.get('label') and overlap(row,start,end)>0]
    if chords:
        totals={}
        for row,weight in chords:totals[row['label']]=totals.get(row['label'],0)+weight
        # Distribute examples over the entire selection; never pretend the opening represents the song.
        indices=sorted({round(i*(len(chords)-1)/min(7,len(chords)-1)) for i in range(min(8,len(chords)))}) if len(chords)>1 else [0]
        add('candidate','harmony',{'coverage':sum(weight for _,weight in chords)/max(1e-9,end-start),
            'chord_duration_seconds':totals,
            'sequence_examples':[{'start':max(start,chords[i][0]['start']),'end':min(end,chords[i][0]['end']),
                'label':chords[i][0]['label'],'margin':chords[i][0].get('margin'),
                'degree':chords[i][0].get('degree'),'resolution_candidate':bool(chords[i][0].get('resolution'))} for i in indices]},
            'Estimated partial chord coverage; examples are sampled, not the complete progression. Major/minor and resolution candidates do not determine emotion.')
    from .joint_evidence import observations as joint_observations
    for row in joint_observations(analysis,position):
        add('cross_modal_relation','audio_lyrics_alignment',row,
            'Temporal comparison of model estimates, not a validated fused prediction or personal feeling.',
            (row['start'],row['end']))
    return {'version':VERSION,'scope':'whole_song' if position is None else 'selected_position',
            'start':start,'end':end,'observations':observations,
            'unmeasured':['independent emotional tension','validated timbral harshness','confirmed instrumentation'],
            'rule':'Keep observations, model estimates and possible interpretations separate. Never infer anger from high energy alone.'}
