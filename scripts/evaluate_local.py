"""Small authored regression probe; not a representative music/lyrics benchmark."""
import json
from pathlib import Path
from backend.models import engines

CASES=[
    ('My closest friend has died.','I am falling apart.','Everything feels empty.',-1),
    ('At last we won the tournament.','I can hardly believe it.','Everyone is cheering with joy.',1),
    ('I have lost everything that mattered.','I am not happy anymore.','Each day feels heavier.',-1),
    ('The danger is over and my family is safe.','I can finally breathe.','Relief and happiness fill the room.',1),
    ('Nobody came to help me.','What a wonderful day.','I am being sarcastic; this hurts terribly.',-1),
    ('My friend surprised me with good news.','This is amazing.','We celebrated our reunion.',1),
    ('Mein bester Freund ist gestorben.','Ich zerbreche innerlich.','Alles fühlt sich leer an.',-1),
    ('Wir haben endlich gewonnen.','Ich kann es kaum glauben.','Alle jubeln vor Freude.',1),
    ('Ich habe alles verloren.','Ich bin nicht mehr glücklich.','Jeder Tag tut weh.',-1),
    ('Die Gefahr ist vorbei und alle sind sicher.','Endlich kann ich aufatmen.','Ich bin voller Freude und Erleichterung.',1),
    ('Meine Familie ist endlich wieder zusammen.','Heute fühle ich mich geliebt.','Ich bin dankbar und glücklich.',1),
    ('Ich bin allein und niemand hört mich.','Ich vermisse dich schrecklich.','Die Trauer lässt mich nicht los.',-1),
]


if __name__=='__main__':
    rows=[]
    for i,(before,text,after,expected) in enumerate(CASES):
        lines=[{'start':j*4.,'end':(j+1)*4.,'text':part} for j,part in enumerate([before,text,after])]
        baseline=engines.lyrics(lines,lambda *a:None,context_weight=0)[1]['valence']
        contextual=engines.lyrics(lines,lambda *a:None,context_weight=.3)[1]['valence']
        rows.append({'case':i,'expected_sign':expected,'line_only':baseline,'with_context':contextual})
    summary={'kind':'12 authored bilingual diagnostic cases, not a general accuracy benchmark',
             'line_only_sign_accuracy':sum(r['line_only']*r['expected_sign']>0 for r in rows)/len(rows),
             'context_sign_accuracy':sum(r['with_context']*r['expected_sign']>0 for r in rows)/len(rows),
             'cases':rows}
    Path('data').mkdir(exist_ok=True)
    Path('data/local-quality-probe.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='cases'},indent=2))
