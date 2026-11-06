import {Point} from './types';

/** Visual interpolation only; never changes cached analysis measurements. */
export function interpolatePoint(points:Point[],time:number):Point|undefined{
 if(!points.length)return;
 const first=points[0];if(time<=(first.start+first.end)/2)return first;
 for(let i=1;i<points.length;i++){
  const right=points[i],left=points[i-1],a=(left.start+left.end)/2,b=(right.start+right.end)/2;
  if(time<=b){const ratio=Math.max(0,Math.min(1,(time-a)/Math.max(.001,b-a)));
   const blend=(key:'valence'|'arousal'|'rms')=>{const x=left[key],y=right[key];return x!==undefined&&y!==undefined?x+(y-x)*ratio:x??y};
   const scores=Object.fromEntries([...new Set([...Object.keys(left.scores),...Object.keys(right.scores)])].map(key=>[key,(left.scores[key]??0)+((right.scores[key]??0)-(left.scores[key]??0))*ratio]));
   return {...left,scores,valence:blend('valence')!,arousal:blend('arousal'),rms:blend('rms')};
  }
 }
 return points.at(-1);
}

export function chartTime(clientX:number,left:number,width:number,duration:number){
 return Math.max(0,Math.min(duration,((clientX-left)/Math.max(1,width)*1000-26)/948*duration));
}
