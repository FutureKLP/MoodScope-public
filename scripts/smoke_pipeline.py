"""Opt-in real local integration probe, isolated from the user's library and browser."""
import json
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from fastapi import HTTPException
import backend.app as app


if __name__=='__main__':
    temporary_root=Path(__file__).resolve().parents[1]/'.tools'
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='moodscope-local-integration-',dir=temporary_root) as directory:
        app.DATA=Path(directory)
        sr=48000;t=np.arange(sr*12)/sr
        audio=(.1*np.sin(2*np.pi*220*t)*(1+.3*np.sin(2*np.pi*2*t))).astype('float32')
        source=app.DATA/'authored-calibration.wav';sf.write(source,audio,sr)
        track=app.import_path(source,'authored-calibration.wav')
        identity=track['id']
        lyrics='[00:00.00]Heute vermisse ich dich. Alles fühlt sich leer an.\n[00:05.00]\n[00:06.00]Morgen hoffe ich auf einen neuen Anfang.\n[00:12.00]'
        request=app.AnalyzeRequest(lyrics=lyrics)
        app.jobs['analysis']={'status':'running'}
        app.run_job('analysis',identity,request)
        assert app.jobs['analysis']['status']=='done',app.jobs['analysis']
        first=app.jobs['analysis']['result']
        assert len(first['audio'])==3 and len(first['lyrics'])==2
        actual_audio=app.engines.audio
        def forbidden(*args):raise AssertionError('Cache hit must not run audio inference')
        app.engines.audio=forbidden
        app.run_job('analysis',identity,request)
        assert app.jobs['analysis']['status']=='done' and app.jobs['analysis']['result']['cached']
        app.engines.audio=actual_audio
        notes=app.Notes(interpretation='Disposable integration note',instruments='Manually entered test value')
        app.save_notes(identity,notes)
        app.jobs['details']={'status':'running'};app.run_details('details',identity)
        assert app.jobs['details']['status']=='done',app.jobs['details']
        app.jobs['interpretation']={'status':'running'}
        app.run_interpretation('interpretation',identity,app.InterpretationRequest(time=1.))
        assert app.jobs['interpretation']['status']=='done',app.jobs['interpretation']
        deleted=app.delete_analysis_cache(identity)
        assert app.get_notes(identity)['interpretation']==notes.interpretation
        assert (app.DATA/f'{identity}.wav').exists()
        try:app.stored_analysis(identity)
        except HTTPException as exc:assert exc.status_code==404
        else:raise AssertionError('Deleted analysis still available')
        app.run_job('analysis',identity,app.AnalyzeRequest(lyrics=lyrics,force=True))
        assert app.jobs['analysis']['status']=='done' and not app.jobs['analysis']['result']['cached']
        summary={'device':first['device'],'audio_bins':len(first['audio']),'lyric_lines':len(first['lyrics']),
                 'cache_skips_inference':True,'notes_preserved_after_delete':True,'force_reanalysis':True,
                 'instrument_candidates':len(app.jobs['details']['result']['instruments']),
                 'interpretation_characters':len(app.jobs['interpretation']['result']['text']),
                 'deleted_cache_entries':deleted['deleted_cache_entries']}
        print(json.dumps(summary,indent=2))
        output=Path(__file__).resolve().parents[1]/'data'/'pipeline-smoke-v02.json'
        output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(summary,indent=2),encoding='utf-8')
