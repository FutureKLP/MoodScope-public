"""Bounded local chroma/template estimates, independent of emotion inference."""
import numpy as np

NOTES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
VERSION='harmonic-chroma-templates-v1'


def templates():
    rows=[]
    for mode,third in [('major',4),('minor',3)]:
        for root in range(12):
            row=np.zeros(12);row[[root,(root+third)%12,(root+7)%12]]=1
            rows.append((NOTES[root]+('' if mode=='major' else 'm'),row/np.linalg.norm(row)))
    return rows


def estimate_chord(chroma):
    vector=np.asarray(chroma,dtype=float)
    if vector.sum()<1e-8:return {'label':None,'similarity':0.,'margin':0.}
    vector=vector/max(1e-9,np.linalg.norm(vector))
    scores=sorted([(float(vector@v),name,v) for name,v in templates()],key=lambda r:r[0],reverse=True)
    score,name,triad=scores[0];margin=score-scores[1][0]
    # Refuse isolated notes, broad noise and ambiguous triads rather than inventing chords.
    members=vector[triad>0]
    accepted=score>=.8 and margin>=.04 and members.min()>=.16
    return {'label':name if accepted else None,'similarity':score,'margin':margin}


def estimate_key(chroma):
    vector=np.asarray(chroma,dtype=float);vector=vector-vector.mean()
    if np.linalg.norm(vector)<1e-8:return None
    # Explicit heuristic degree weights; no probability/accuracy claim.
    profiles={'major':[1,.1,.6,.1,.8,.7,.1,.9,.1,.6,.1,.5],
              'minor':[1,.1,.6,.8,.1,.7,.1,.9,.7,.1,.6,.1]}
    scores=[]
    for mode,profile in profiles.items():
        for root in range(12):
            p=np.roll(profile,root);p=p-p.mean()
            scores.append({'tonic':NOTES[root],'mode':mode,
                           'similarity':float(vector@p/(np.linalg.norm(vector)*np.linalg.norm(p)))})
    scores.sort(key=lambda row:row['similarity'],reverse=True)
    return {**scores[0],'margin':scores[0]['similarity']-scores[1]['similarity'],
            'alternatives':scores[1:3]}


def analyse(audio,sr):
    import librosa
    duration=len(audio)/sr
    timeline=[];total=np.zeros(12);active=0
    # Thirty-second blocks keep spectral arrays bounded even for long imports.
    for start in range(0,len(audio),sr*30):
        from .cancellation import check
        check()
        block=audio[start:start+sr*30]
        if len(block)<4096 or np.max(np.abs(block))<1e-5:continue
        spectrum=np.abs(librosa.stft(block,n_fft=4096,hop_length=1024))
        harmonic,_=librosa.decompose.hpss(spectrum,kernel_size=17)
        chroma=librosa.feature.chroma_stft(S=harmonic**2,sr=sr,n_fft=4096,hop_length=1024,tuning=0,norm=None)
        for second in range(int(np.ceil(len(block)/sr))):
            a=int(second*sr/1024);b=max(a+1,int((second+1)*sr/1024))
            vector=chroma[:,a:b].mean(axis=1)
            sample=block[second*sr:(second+1)*sr]
            if len(sample)==0 or np.sqrt(np.mean(sample**2))<1e-5:vector=np.zeros(12)
            normalized=vector/max(1e-9,vector.sum());total+=normalized
            active+=int(vector.sum()>1e-8)
            row={'start':start/sr+second,'end':min(duration,start/sr+second+1),**estimate_chord(normalized)}
            if timeline and timeline[-1]['label']==row['label'] and timeline[-1]['end']==row['start']:
                previous=timeline[-1];previous['end']=row['end'];previous['similarity']=min(previous['similarity'],row['similarity']);previous['margin']=min(previous['margin'],row['margin'])
            else:timeline.append(row)
    key=estimate_key(total) if active>=3 else None
    return {'version':VERSION,'key':key,'chords':timeline,'active_seconds':active,
            'method':'Harmonic STFT chroma; heuristic key profiles and major/minor triad cosine templates. One-second chord grid; fixed concert tuning.',
            'limitations':'Estimates, not a score transcription. Detuning, inversions, extensions, modulation, vocals and percussion can cause errors. Margins are not probabilities.'}


def evidence(features,position=None,language='de'):
    h=features.get('harmony',{});key=h.get('key');en=language=='en';parts=[]
    if key:
        name=key['tonic']+' '+({'major':'major','minor':'minor'} if en else {'major':'Dur','minor':'Moll'})[key['mode']]
        parts.append((f'Local key estimate: {name}; profile similarity {key["similarity"]:.2f}, runner-up margin {key["margin"]:.2f}. ' if en else f'Lokale Tonartschätzung: {name}; Profilähnlichkeit {key["similarity"]:.2f}, Abstand zum zweiten Profil {key["margin"]:.2f}. '))
    chords=[c for c in h.get('chords',[]) if c.get('label') and (position is None or c['start']<=position<c['end'])]
    if chords:
        parts.append(('Estimated triads: ' if en else 'Geschätzte Dreiklänge: ')+', '.join(f'{c["start"]:.0f}–{c["end"]:.0f}s {c["label"]}' for c in chords[:12])+'. ')
    if h:parts.append('Template matches are uncertain and do not establish an emotional cause. ' if en else 'Die Vorlagenvergleiche sind unsicher und belegen keine emotionale Ursache. ')
    if features.get('crest_factor_db') is not None:
        parts.append((f'Peak-to-RMS crest factor: {features["crest_factor_db"]:.1f} dB. ' if en else f'Spitzenpegel-RMS-Abstand (Crest-Faktor): {features["crest_factor_db"]:.1f} dB. '))
    return ''.join(parts)
