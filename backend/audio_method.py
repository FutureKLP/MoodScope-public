"""Versioned, inspectable parameters of the local audio emotion projection."""
from copy import deepcopy

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


def with_method(result):
    if result.get('audio_method'):return result
    if result.get('mode')=='cloud':return {**result,'audio_method':{'id':'provider-audio','recording':'provider','model':result.get('models',{}).get('audio')}}
    # Only this documented, unchanged pipeline can be reconstructed for old caches.
    if str(result.get('pipeline_version','')).startswith('clap-ensemble-context-v4-features-grid5-coverage50:'):
        return {**result,'audio_method':describe(result.get('models',{}).get('audio'),result.get('audio_resolution',5),'reconstructed')}
    return result
