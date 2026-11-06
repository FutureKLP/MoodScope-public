import numpy as np
from backend import harmony
from backend.insights import acoustic_features,audio_evidence


def test_chord_templates_reject_single_note_and_noise():
    assert harmony.estimate_chord(np.eye(12)[0])['label'] is None
    assert harmony.estimate_chord(np.ones(12))['label'] is None
    for label,indexes in [('C',[0,4,7]),('Am',[9,0,4])]:
        vector=np.zeros(12);vector[indexes]=1
        assert harmony.estimate_chord(vector)['label']==label


def test_actual_synthetic_chord_audio_and_dynamic_measurements():
    sr=22050;t=np.arange(sr*4)/sr
    signal=sum(np.sin(2*np.pi*f*t) for f in [261.6256,329.6276,391.9954])*.08
    features=acoustic_features(signal.astype('float32'),sr)
    h=features['harmony']
    assert any(c['label']=='C' for c in h['chords'])
    assert h['key'] is not None and h['chords'][-1]['end']==4
    assert np.isfinite(features['crest_factor_db'])
    analysis={'audio':[{'start':0,'end':4,'valence':0,'scores':{}}],'features':features}
    assert 'C ' in audio_evidence(analysis)
    assert 'Estimated chords' in audio_evidence(analysis,language='en')


def test_harmony_silence_has_no_key_or_chords():
    result=harmony.analyse(np.zeros(22050*4,dtype='float32'),22050)
    assert result['key'] is None and result['chords']==[]


def test_musical_projection_is_bounded_explained_and_keeps_raw_inference():
    from backend.audio_method import musical_projection
    rows=[{'start':0,'end':5,'valence':.98,'arousal':.5,'rms':.2,'scores':{'joy':1}}]
    f={'bpm':180,'beat_regularity':1,'brightness_hz':4000,'rms_mean':.1,
       'harmony':{'key':{'mode':'major','margin':.2},'chords':[{'start':0,'end':5,'label':'C','margin':.2}]}}
    result=musical_projection(rows,f)[0]
    assert result['clap_valence']==.98 and result['valence']==1
    assert 0<result['musical_adjustment']<=.12 and len(result['musical_contributions'])==4
    assert result['arousal']>.5 and rows[0]['valence']==.98
    assert musical_projection([{**rows[0],'rms':0}],f)[0]['musical_adjustment']==0

def test_major_minor_transitions_are_weighted_by_actual_overlap():
    from backend.audio_method import musical_projection
    rows=[{'start':0,'end':2,'valence':0,'scores':{}}]
    features={'harmony':{'chords':[{'start':0,'end':1,'label':'C','margin':.15},{'start':1,'end':2,'label':'Cm','margin':.15}]}}
    result=musical_projection(rows,features)[0]
    assert result['musical_contributions'][0]['feature']=='triad_mode'
    assert abs(result['musical_adjustment'])<1e-8


def test_extended_chords_and_minor_seventh_keep_correct_polarity():
    from backend.audio_method import musical_projection
    for label,notes in [('C7',[0,4,7,10]),('Cmaj7',[0,4,7,11]),('Cm7',[0,3,7,10]),('Cdim',[0,3,6])]:
        vector=np.zeros(12);vector[notes]=1;vector[0]=1.15
        estimated=harmony.estimate_chord(vector)
        assert estimated['label']==label
    row={'start':0,'end':2,'valence':0,'scores':{}}
    result=musical_projection([row],{'harmony':{'chords':[{'start':0,'end':2,'label':'Cm7','mode':'minor','margin':.2}]}})[0]
    assert result['valence']<0


def test_temporal_filter_is_explicit_bounded_and_preserves_inference():
    from backend.audio_method import musical_projection
    rows=[{'start':i*2,'end':i*2+2,'valence':v,'scores':{}} for i,v in enumerate([-.8,.8,-.8])]
    result=musical_projection(rows,{})
    assert abs(result[1]['valence'])<abs(result[1]['clap_valence'])
    assert result[1]['feature_valence']==.8 and result[1]['temporal_adjustment']<0
    assert rows[1]['valence']==.8

def test_real_cqt_progression_and_tempo_against_authored_signals():
    import librosa
    sr=22050;segments=[];expected=['C','Am','F','G7','C']
    for notes in [[60,64,67],[57,60,64],[53,57,60],[55,59,62,65],[60,64,67]]:
        t=np.arange(sr*3)/sr
        wave=sum(np.sin(2*np.pi*librosa.midi_to_hz(note)*t) for note in notes)*.05
        wave+=np.sin(2*np.pi*librosa.midi_to_hz(notes[0]-12)*t)*.035
        segments.append(wave)
    result=harmony.analyse(np.concatenate(segments).astype('float32'),sr)
    predictions=[next((c['label'] for c in result['chords'] if c['start']<=i*3+1.5<c['end']),None) for i in range(5)]
    assert predictions==expected
    assert result['changes_per_minute']>0 and result['key_regions']
    clicks=librosa.clicks(times=np.arange(.5,12,.5),sr=sr,length=sr*12)
    measured=acoustic_features(clicks,sr)['bpm']
    assert measured is not None and min(abs(measured-120),abs(measured-60))<2
