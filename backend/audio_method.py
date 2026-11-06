"""Versioned, inspectable parameters of the local audio emotion projection."""
from copy import deepcopy
import math

LABELS=['joy','calm','sadness','anger','fear','tenderness']
VALENCE=[1.,.3,-1.,-.7,-.75,.5]
AROUSAL=[.8,.15,.3,.95,.85,.3]
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
    result=[];h=features.get('harmony',{});key=h.get('key')
    for original in rows:
        row=deepcopy(original);mid=(row['start']+row['end'])/2;terms=[]
        def term(name,value,weight,reliability=1.):
            terms.append({'feature':name,'value':float(value),'weight':weight,'reliability':float(reliability),'contribution':float(value*weight*reliability)})
        silent=row.get('rms') is not None and row['rms']<1e-5
        if key and not silent:term('key_mode',1 if key['mode']=='major' else -1,.04,min(1,max(0,key['margin'])/.15))
        chord=next((c for c in h.get('chords',[]) if c['start']<=mid<c['end'] and c.get('label')),None)
        if chord and not silent:term('triad_mode',-1 if chord['label'].endswith('m') else 1,.06,min(1,chord['margin']/.15))
        tempo=features.get('bpm');regularity=features.get('beat_regularity') or 0
        if tempo and not silent:term('tempo',math.tanh((tempo-100)/60),.04,regularity)
        brightness=features.get('brightness_hz')
        if brightness is not None and not silent:term('brightness',math.tanh((brightness-2000)/2000),.02)
        adjustment=max(-.12,min(.12,sum(t['contribution'] for t in terms)))
        raw=row['valence'];row.update(clap_valence=raw,valence=max(-1,min(1,raw+adjustment)),musical_adjustment=adjustment,musical_contributions=terms)
        raw_arousal=row.get('arousal',.5);mean=features.get('rms_mean') or 0
        section=next((s for s in features.get('sections',[]) if s['start']<=mid<s['end']),None)
        energy=section.get('rms') if section else row.get('rms')
        dynamic=.12*math.tanh(math.log(max(1e-8,energy)/mean)) if energy is not None and mean>1e-8 else 0
        row.update(clap_arousal=raw_arousal,dynamic_arousal_adjustment=dynamic,arousal=max(0,min(1,raw_arousal+dynamic)))
        result.append(row)
    return result


def describe_musical(model,grid_seconds):
    return {**describe(model,grid_seconds),'id':'clap-musical-features-v5','features_used_in_valence':True,
            'valence_formula':'clip(clap_valence + clip(sum(feature * weight * reliability), -.12, .12), -1, 1)',
            'feature_weights':{'key_mode':.04,'triad_mode':.06,'tempo':.04,'brightness':.02},
            'arousal_formula':'clip(clap_arousal + .12 * tanh(log(local_rms / global_rms)), 0, 1)',
            'note':'Explicit Western major/minor and tempo/brightness heuristics; not a trained or calibrated emotion model. Dynamics affect arousal, not valence.'}


def with_method(result):
    if result.get('audio_method'):return result
    if result.get('mode')=='cloud':return {**result,'audio_method':{'id':'provider-audio','recording':'provider','model':result.get('models',{}).get('audio')}}
    # Only this documented, unchanged pipeline can be reconstructed for old caches.
    if str(result.get('pipeline_version','')).startswith('clap-ensemble-context-v4-features-grid5-coverage50:'):
        return {**result,'audio_method':describe(result.get('models',{}).get('audio'),result.get('audio_resolution',5),'reconstructed')}
    return result
