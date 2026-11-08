import {Analysis} from './types';
export type ExpressionRow={start:number;end:number;valence:number;arousal:number};

/** Replace only the displayed dimensional curve; never fabricate category scores. */
export function expressionTimeline(analysis:Analysis|null,rows:ExpressionRow[]|null):Analysis|null{
 if(!analysis||!rows?.length)return analysis;
 const audio=rows.map(row=>({...row,scores:{}}));
 let split:Analysis['split']=null;
 for(const row of audio){
  let covered=0,weighted=0;
  for(const lyric of analysis.lyrics){
   const overlap=Math.max(0,Math.min(row.end,lyric.end)-Math.max(row.start,lyric.start));
   covered+=overlap;weighted+=overlap*lyric.valence;
  }
  if(covered<=0||covered<(row.end-row.start)*.5)continue;
  const lyric=weighted/covered,gap=Math.abs(row.valence-lyric);
  if(!split||gap>split.gap)split={start:row.start,end:row.end,audio:row.valence,lyric,gap,lyric_coverage:Math.min(1,covered/(row.end-row.start))};
 }
 return {...analysis,audio,split};
}
