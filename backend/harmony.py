"""Bounded local chroma/template estimates, independent of emotion inference."""
import numpy as np

NOTES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
VERSION='harmonic-cqt-sequence-v2'
QUALITIES={'':('major',[0,4,7]),'m':('minor',[0,3,7]),'7':('major',[0,4,7,10]),'maj7':('major',[0,4,7,11]),'m7':('minor',[0,3,7,10]),'dim':('diminished',[0,3,6]),'aug':('augmented',[0,4,8]),'sus2':('suspended',[0,2,7]),'sus4':('suspended',[0,5,7]),'m7b5':('diminished',[0,3,6,10])}


def templates():
    rows=[]
    for suffix,(_,intervals) in QUALITIES.items():
        for root in range(12):
            row=np.zeros(12);row[[(root+i)%12 for i in intervals]]=1;row[root]=1.15
            rows.append((NOTES[root]+suffix,row/np.linalg.norm(row)))
    return rows


def estimate_chord(chroma):
    vector=np.asarray(chroma,dtype=float)
    if vector.sum()<1e-8:return {'label':None,'similarity':0.,'margin':0.}
    vector=vector/max(1e-9,np.linalg.norm(vector))
    scores=sorted([(float(vector@v),name,v) for name,v in templates()],key=lambda r:r[0],reverse=True)
    score,name,triad=scores[0];margin=score-scores[1][0]
    # Refuse isolated notes, broad noise and ambiguous triads rather than inventing chords.
    members=vector[triad>0]
    accepted=score>=.8 and margin>=.025 and members.min()>=.13
    root=next(n for n in sorted(NOTES,key=len,reverse=True) if name.startswith(n));suffix=name[len(root):]
    return {'label':name if accepted else None,'root':root if accepted else None,'quality':suffix if accepted else None,'mode':QUALITIES[suffix][0] if accepted else None,'similarity':score,'margin':margin,'alternatives':[{'label':v[1],'similarity':v[0]} for v in scores[1:3]]}


def estimate_key(chroma):
    vector=np.asarray(chroma,dtype=float);vector=vector-vector.mean()
    if np.linalg.norm(vector)<1e-8:return None
    # Krumhansl-Kessler empirical pitch-class profiles; similarity is not probability.
    profiles={'major':[6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88],
              'minor':[6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,2.98,2.69,3.34,3.17]}
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
    timeline=[];total=np.zeros(12);active=0;regions=[];tuning=0.
    if len(audio)>=sr and np.max(np.abs(audio))>=1e-5:
        tuning=float(librosa.estimate_tuning(y=audio[:sr*30],sr=sr))
    # Thirty-second blocks keep spectral arrays bounded even for long imports.
    for start in range(0,len(audio),sr*30):
        from .cancellation import check
        check()
        block=audio[start:start+sr*30]
        if len(block)<4096 or np.max(np.abs(block))<1e-5:continue
        stft=librosa.stft(block,n_fft=4096,hop_length=1024);spectrum=np.abs(stft)
        harmonic,_=librosa.decompose.hpss(spectrum,kernel_size=17)
        harmonic_audio=librosa.istft(harmonic*np.exp(1j*np.angle(stft)),hop_length=1024,length=len(block))
        if len(harmonic_audio)<sr*4:harmonic_audio=np.pad(harmonic_audio,(0,sr*4-len(harmonic_audio)))
        chroma=librosa.feature.chroma_cqt(y=harmonic_audio,sr=sr,hop_length=512,fmin=librosa.note_to_hz('C1'),n_octaves=7,tuning=tuning,norm=None)
        local_key=estimate_key(chroma.mean(axis=1))
        regions.append({'start':start/sr,'end':min(duration,(start+len(block))/sr),'key':local_key})
        for half in range(int(np.ceil(len(block)/sr*2))):
            second=half/2
            a=int(second*sr/512);b=max(a+1,int((second+.5)*sr/512))
            vector=chroma[:,a:b].mean(axis=1)
            sample=block[int(second*sr):int((second+.5)*sr)]
            if len(sample)==0 or np.sqrt(np.mean(sample**2))<1e-5:vector=np.zeros(12)
            normalized=vector/max(1e-9,vector.sum());total+=normalized
            active+=.5*int(vector.sum()>1e-8)
            row={'start':start/sr+second,'end':min(duration,start/sr+second+.5),**estimate_chord(normalized)}
            if timeline and timeline[-1]['label']==row['label'] and timeline[-1]['end']==row['start']:
                previous=timeline[-1];previous['end']=row['end'];previous['similarity']=min(previous['similarity'],row['similarity']);previous['margin']=min(previous['margin'],row['margin'])
            else:timeline.append(row)
    key=estimate_key(total) if active>=3 else None
    for index,row in enumerate(timeline):
        local=next((r['key'] for r in regions if r['start']<=row['start']<r['end']),None) or key
        row['resolution']=False
        if local and row.get('root'):
            delta=(NOTES.index(row['root'])-NOTES.index(local['tonic']))%12
            row['degree']=['I','bII','II','bIII','III','IV','#IV','V','bVI','VI','bVII','VII'][delta]
            if row.get('mode')=='minor':row['degree']=row['degree'].lower()
            if index and delta==0 and timeline[index-1].get('root'):
                row['resolution']=(NOTES.index(timeline[index-1]['root'])-NOTES.index(local['tonic']))%12==7
    transitions=sum(a.get('label')!=b.get('label') and bool(a.get('label') and b.get('label')) for a,b in zip(timeline,timeline[1:]))
    return {'version':VERSION,'key':key,'key_regions':regions,'tuning_cents':tuning*100,'chords':timeline,'active_seconds':active,'changes_per_minute':transitions/max(duration/60,1e-8),

            'method':'HPSS harmonic CQT chroma with estimated tuning; Krumhansl-Kessler key profiles, thirty-second local key candidates, major/minor/seventh/diminished/augmented/suspended chord templates on a half-second grid. Functional degrees and V-to-I candidates.',
            'limitations':'Estimates, not a score transcription or validated professional transcription model. Inversions, extensions, modulations and overlapping vocals remain uncertain. Symmetric/ambiguous chords may remain blank. Key profiles assume Western tonal music. Margins are not probabilities.'}


def evidence(features,position=None,language='de'):
    h=features.get('harmony',{});key=h.get('key');en=language=='en';parts=[]
    if key:
        name=key['tonic']+' '+({'major':'major','minor':'minor'} if en else {'major':'Dur','minor':'Moll'})[key['mode']]
        parts.append((f'Local key estimate: {name}; profile similarity {key["similarity"]:.2f}, runner-up margin {key["margin"]:.2f}. ' if en else f'Lokale Tonartschätzung: {name}; Profilähnlichkeit {key["similarity"]:.2f}, Abstand zum zweiten Profil {key["margin"]:.2f}. '))
    chords=[c for c in h.get('chords',[]) if c.get('label') and (position is None or c['start']<=position<c['end'])]
    if chords:
        parts.append(('Estimated chords: ' if en else 'Geschätzte Akkorde: ')+', '.join(f'{c["start"]:.0f}–{c["end"]:.0f}s {c["label"]}' for c in chords[:12])+'. ')
    if h:parts.append('Template matches are uncertain and do not establish an emotional cause. ' if en else 'Die Vorlagenvergleiche sind unsicher und belegen keine emotionale Ursache. ')
    if features.get('crest_factor_db') is not None:
        parts.append((f'Peak-to-RMS crest factor: {features["crest_factor_db"]:.1f} dB. ' if en else f'Spitzenpegel-RMS-Abstand (Crest-Faktor): {features["crest_factor_db"]:.1f} dB. '))
    return ''.join(parts)
