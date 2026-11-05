"""Opt-in real local whole-song interpretation using authored text only."""
import json
from pathlib import Path
from backend.models import engines,ROOT
from backend.insights import interpretation,interpretation_context


if __name__=='__main__':
    lines=[{'start':0,'end':10,'text':'Seit du fort bist, fühlt sich unser Zimmer leer an.'},
           {'start':10,'end':20,'text':'Ich gehe allein durch den Regen und frage nach dem Sinn.'},
           {'start':20,'end':30,'text':'Doch ich öffne das Fenster und lasse neues Licht herein.'},
           {'start':30,'end':40,'text':'Morgen wage ich den ersten Schritt, auch wenn die Erinnerung bleibt.'}]
    analysis={'lyrics':lines,'audio':[]}
    context=interpretation_context(analysis)
    assert context['scope']=='whole_song' and all(row['text'] in context['full_text'] for row in lines)
    result=interpretation(ROOT/'data',engines,analysis,{})
    assert len(result['text'])>200 and result['time'] is None
    destination=ROOT/'data'/'whole-interpretation-probe.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'device':engines.device(),'characters':len(result['text']),
        'input_truncated':result.get('input_truncated'),'output_truncated':result.get('output_truncated'),
        'whole_song_context':True}))
