"""Versioned, inspectable parameters of the local audio emotion projection."""
from copy import deepcopy
import math

LABELS=['joy','calm','sadness','anger','fear','tenderness']
VALENCE=[1.,.3,-1.,-.7,-.75,.5]
AROUSAL=[.8,.15,.3,.95,.85,.3]
CURRENT_METHOD='clap-level-controlled-v7'
PROMPTS=[
    'This music sounds joyful, happy and uplifting.','The musical expression is bright, cheerful and celebratory.',
    'This music sounds peaceful, calm and relaxed.','The musical expression is serene and soothing.',
    'This music sounds sad, melancholic and sorrowful.','The musical expression conveys grief and sadness.',
    'This music sounds angry, tense and aggressive.','The musical expression is hostile and furious.',
    'This music sounds fearful, anxious and unsettling.','The musical expression creates dread and nervous tension.',
    'This music sounds tender, affectionate and warm.','The musical expression conveys gentle love and tenderness.']


def describe(model,grid_seconds,recording='recorded'):
    return {'id':'clap-prompt-ensemble-v4','recording':recording,'model':model,'grid_seconds':grid_seconds,
        'context_seconds':10,'mix':'mono-original','score_method':'mean_pair_logits_then_softmax',
        'valence_formula':'sum(score[label] * valence_weight[label])',
        'confidence_formula':'1 - entropy(scores) / log(6)',
        'labels':[{'id':label,'valence_weight':VALENCE[i],'arousal_weight':AROUSAL[i],
            'prompts':PROMPTS[2*i:2*i+2]} for i,label in enumerate(LABELS)],
        'features_used_in_valence':False,'calibrated':False}


def musical_projection(rows,features):
    """Small explicit, uncalibrated feature adjustments; keep original inference intact."""
    result=[];h=features.get('harmony',{});global_key=h.get('key')
    for original in rows:
        row=deepcopy(original);mid=(row['start']+row['end'])/2;terms=[]
        def term(name,value,weight,reliability=1.):
            terms.append({'feature':name,'value':float(value),'weight':weight,'reliability':float(reliability),'contribution':float(value*weight*reliability)})
        key=next((r['key'] for r in h.get('key_regions',[]) if r['start']<=mid<r['end'] and r.get('key')),None) or global_key
        section=next((s for s in features.get('sections',[]) if s['start']<=mid<s['end']),None)
        silent=row.get('rms') is not None and row['rms']<1e-5
        if key and not silent:term('key_mode',1 if key['mode']=='major' else -1,.04,min(1,max(0,key['margin'])/.15))
        chords=[(c,max(0,min(row['end'],c['end'])-max(row['start'],c['start']))) for c in h.get('chords',[]) if c.get('label')]
        chords=[(c,overlap) for c,overlap in chords if overlap>0]
        duration=max(1e-8,row['end']-row['start'])
        coverage=sum(overlap for _,overlap in chords)
        reliability=sum(overlap*min(1,c['margin']/.15) for c,overlap in chords)/duration
        if chords and not silent:
            mode=sum(overlap*min(1,c['margin']/.15)*({'major':1,'minor':-1}.get(c.get('mode'),0) if c.get('mode') else (-1 if c['label'].endswith('m') else 1)) for c,overlap in chords)
            term('triad_mode',mode/max(1e-8,reliability*duration),.06,reliability)
        resolutions=[(c,overlap) for c,overlap in chords if c.get('resolution')]
        if resolutions and not silent:term('harmonic_resolution',1,.025,sum(overlap*min(1,c['margin']/.15) for c,overlap in resolutions)/duration)
        tempo=(section or {}).get('bpm') or features.get('bpm');regularity=features.get('beat_regularity') or 0
        if tempo and not silent:term('tempo',math.tanh((tempo-100)/60),.04,regularity)
        brightness=(section or {}).get('brightness_hz',features.get('brightness_hz'))
        if brightness is not None and not silent:term('brightness',math.tanh((brightness-2000)/2000),.02)
        adjustment=max(-.12,min(.12,sum(t['contribution'] for t in terms)))
        raw=row['valence'];row.update(clap_valence=raw,valence=max(-1,min(1,raw+adjustment)),musical_adjustment=adjustment,musical_contributions=terms)
        raw_arousal=row.get('arousal',.5);mean=features.get('rms_mean') or 0
        section=next((s for s in features.get('sections',[]) if s['start']<=mid<s['end']),None)
        energy=section.get('rms') if section else row.get('rms')
        dynamic=.12*math.tanh(math.log(max(1e-8,energy)/mean)) if energy is not None and mean>1e-8 else 0
        row.update(clap_arousal=raw_arousal,dynamic_arousal_adjustment=dynamic,arousal=max(0,min(1,raw_arousal+dynamic)))
        result.append(row)
    # Duration-aware three-bin triangular smoothing; raw inference remains untouched.
    values=[r['valence'] for r in result]
    for i,row in enumerate(result):
        neighbors=[(j,(2 if j==i else 1)*max(1e-6,result[j]['end']-result[j]['start'])) for j in range(max(0,i-1),min(len(result),i+2))]
        smoothed=sum(values[j]*weight for j,weight in neighbors)/sum(weight for _,weight in neighbors)
        row.update(feature_valence=values[i],temporal_adjustment=smoothed-values[i],valence=smoothed)
    return result


def describe_musical(model,grid_seconds,data=None):
    base=describe(model,grid_seconds)
    if data is not None:
        from .prompt_presets import content
        prompts=content(data,'audio').splitlines()
        for i,label in enumerate(base['labels']):label['prompts']=prompts[2*i:2*i+2]
    return {**base,'id':'clap-musical-sequence-v6','features_used_in_valence':True,
            'valence_formula':'duration_weighted_triangular_1_2_1(clip(clap_valence + clip(sum(feature * weight * reliability), -.12, .12), -1, 1))',
            'feature_weights':{'key_mode':.04,'triad_mode':.06,'tempo':.04,'brightness':.02,'harmonic_resolution':.025},
            'temporal_filter':{'weights':[1,2,1],'duration_weighted':True,'online':False},
            'arousal_formula':'clip(clap_arousal + .12 * tanh(log(local_rms / global_rms)), 0, 1)',
            'note':'Explicit Western major/minor and tempo/brightness heuristics; not a trained or calibrated emotion model. Dynamics affect arousal, not valence.'}


def with_method(result):
    if result.get('audio_method'):return result
    if result.get('mode')=='cloud':return {**result,'audio_method':{'id':'provider-audio','recording':'provider','model':result.get('models',{}).get('audio')}}
    # Only this documented, unchanged pipeline can be reconstructed for old caches.
    if str(result.get('pipeline_version','')).startswith('clap-ensemble-context-v4-features-grid5-coverage50:'):
        return {**result,'audio_method':describe(result.get('models',{}).get('audio'),result.get('audio_resolution',5),'reconstructed')}
    return result


def prepare_emotion_audio(audio):
    """Constant analysis gain; never modify playback or the source array.

    Match the evaluated -20 dBFS control, preserving within-window dynamics.
    Digital silence stays silent; reject malformed samples before inference.
    """
    import numpy as np
    samples=np.asarray(audio,dtype=np.float32)
    if samples.ndim!=1 or not samples.size or not np.isfinite(samples).all():
        raise ValueError('Emotion analysis requires finite, nonempty mono audio')
    rms=float(np.sqrt(np.mean(samples.astype(np.float64)**2)))
    peak=float(np.max(np.abs(samples)))
    gain=min(.1/rms,.99/peak) if rms>1e-12 and peak>1e-12 else 1.
    return samples*gain, {'rms':rms,'analysis_gain_db':20*math.log10(gain)}


def prompt_diagnostics(pair_logits):
    """Two wording views, not independent raters or a confidence interval."""
    import numpy as np
    values=np.asarray(pair_logits,dtype=float)
    if values.shape!=(6,2) or not np.isfinite(values).all():
        raise ValueError('Expected six finite prompt pairs')
    exp=np.exp(values-values.max(axis=0,keepdims=True))
    scores=exp/exp.sum(axis=0,keepdims=True)
    valences=np.asarray(VALENCE)@scores
    return {'prompt_valence_min':float(valences.min()),
            'prompt_valence_max':float(valences.max()),
            'prompt_winners_agree':bool(scores[:,0].argmax()==scores[:,1].argmax())}


def describe_current(model,grid_seconds,data=None):
    base=describe(model,grid_seconds)
    if data is not None:
        from .prompt_presets import content
        prompts=content(data,'audio').splitlines()
        for i,label in enumerate(base['labels']):label['prompts']=prompts[2*i:2*i+2]
    return {**base,'id':CURRENT_METHOD,'mix':'mono-level-controlled',
            'level_control':{'target_rms_dbfs':-20,'peak_ceiling':.99,'scope':'context'},
            'temporal_filter':None,'features_used_in_valence':False,
            'note':'No handcrafted acoustic offsets. Prompt ranges describe wording sensitivity, not calibrated uncertainty.'}
