// A local clock avoids a seventh HTTP audio connection in the six-source mixer.
// Eight-bit mono silence uses at most 14.4 MB for the supported 30-minute limit.
export function silentTransport(duration:number):Blob {
  if(!Number.isFinite(duration)||duration<=0||duration>1800)throw new RangeError('Invalid transport duration');
  const rate=8000,frames=Math.ceil(duration*rate),size=44+frames+(frames%2);
  const bytes=new Uint8Array(size),view=new DataView(bytes.buffer);
  const text=(at:number,value:string)=>{for(let i=0;i<value.length;i++)bytes[at+i]=value.charCodeAt(i)};
  text(0,'RIFF');view.setUint32(4,size-8,true);text(8,'WAVE');text(12,'fmt ');
  view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);
  view.setUint32(24,rate,true);view.setUint32(28,rate,true);view.setUint16(32,1,true);view.setUint16(34,8,true);
  text(36,'data');view.setUint32(40,frames,true);bytes.fill(128,44,44+frames);
  return new Blob([bytes],{type:'audio/wav'});
}
