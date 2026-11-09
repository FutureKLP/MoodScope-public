import {Analysis} from './types';
export const MUSIC_TAGS=['happy','calm','sad','melancholic','hopeful','romantic','powerful','energetic','relaxing'] as const;
export type ExpressionRow={start:number;end:number;valence:number;arousal:number;tags?:Record<string,number>;context_start?:number;context_end?:number;outside_training_scale?:boolean};

/** Replace only the displayed dimensional curve; never fabricate category scores. */
export function expressionTimeline(analysis:Analysis|null,rows:ExpressionRow[]|null):Analysis|null{
 if(!analysis||!rows?.length)return analysis;
 const audio=rows.map(row=>({...row,score_source:'music2emo_tags' as const,scores:Object.fromEntries(MUSIC_TAGS.filter(tag=>Number.isFinite(row.tags?.[tag])&&row.tags![tag]>=0&&row.tags![tag]<=1).map(tag=>[tag,row.tags![tag]]))}));
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
