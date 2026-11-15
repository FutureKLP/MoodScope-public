/** Run the separate profiling build in a fresh Chromium profile using local CDP.
 * No browser packages or changes to the user's browser profile are needed.
 * node scripts/performance_browser.mjs --browser <existing Chromium executable>
 *   --output .tools/performance-browser-run
 */
import {spawn,execFileSync} from 'node:child_process';
import {createServer} from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,sep,extname} from 'node:path';
import {createHash} from 'node:crypto';
const args=Object.fromEntries(process.argv.slice(2).reduce((a,v,i,all)=>i%2===0?[...a,[v.replace(/^--/,''),all[i+1]]]:a,[]));
if(!args.browser||!args.output)throw Error('Provide --browser and a fresh --output below .tools');
const root=process.cwd(),area=resolve(args.output),tools=resolve('.tools');
if(!area.startsWith(tools+sep))throw Error('Output must be below .tools');
await mkdir(area,{recursive:false});
const dist=resolve('.tools/performance-web');
// Actual media decoding/playback, deterministic silence (180 s, mono 8 kHz).
let wav;
if(args.audio){
 wav=await readFile(resolve(args.audio));
 if(wav.toString('ascii',0,4)!=='RIFF'||wav.toString('ascii',8,12)!=='WAVE')throw Error('Provide a local WAV for playback');
}else{
 wav=Buffer.alloc(44+180*8000*2);wav.write('RIFF');wav.writeUInt32LE(wav.length-8,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(8000,24);wav.writeUInt32LE(16000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(wav.length-44,40);
}
const server=createServer(async(req,res)=>{try{
 const pathname=new URL(req.url,'http://localhost').pathname;
 if(/^\/api\/tracks\/[ab]\/audio$/.test(pathname)){
  const range=/bytes=(\d+)-(\d*)/.exec(req.headers.range||'');const start=range?Number(range[1]):0,end=range&&range[2]?Math.min(Number(range[2]),wav.length-1):wav.length-1;
  res.writeHead(range?206:200,{'Content-Type':'audio/wav','Accept-Ranges':'bytes','Content-Length':end-start+1,...(range?{'Content-Range':`bytes ${start}-${end}/${wav.length}`}:{})});res.end(wav.subarray(start,end+1));return;
 }
 const file=resolve(dist,'.'+decodeURIComponent(pathname==='/'?'/index.html':pathname));
 if(!file.startsWith(dist+sep))throw Error('Invalid path');
 const body=await readFile(file);res.writeHead(200,{'Content-Type':{'.js':'application/javascript','.css':'text/css','.html':'text/html'}[extname(file)]||'application/octet-stream'});res.end(body);
 }catch{res.writeHead(404);res.end()}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const port=server.address().port;
const browser=spawn(args.browser,['--headless=new','--disable-extensions','--remote-debugging-port=0',`--user-data-dir=${resolve(area,'profile')}`,'--no-first-run','--no-default-browser-check','--autoplay-policy=no-user-gesture-required','--window-size=1440,1000','about:blank'],{windowsHide:true,stdio:'ignore'});
let ws;let id=0;const pending=new Map();
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function call(method,params={}){return new Promise((resolve,reject)=>{const key=++id;const timeout=setTimeout(()=>{pending.delete(key);reject(Error('CDP timeout: '+method))},15000);pending.set(key,{resolve,reject,timeout});ws.send(JSON.stringify({id:key,method,params}))})}
try{
 let debug;
 for(let i=0;i<100;i++){try{debug=(await readFile(resolve(area,'profile/DevToolsActivePort'),'utf8')).split('\n');break}catch{await sleep(100)}}
 if(!debug)throw Error('Chromium debugging endpoint unavailable');
 let target;
 for(let i=0;i<100;i++){const pages=await (await fetch(`http://127.0.0.1:${debug[0]}/json/list`)).json();target=pages.find(p=>p.type==='page');if(target)break;await sleep(100)}
 if(!target)throw Error('Chromium page target unavailable');
 ws=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((r,j)=>{ws.addEventListener('open',r,{once:true});ws.addEventListener('error',j,{once:true})});
 ws.addEventListener('message',event=>{const message=JSON.parse(event.data);if(message.id&&pending.has(message.id)){const p=pending.get(message.id);pending.delete(message.id);clearTimeout(p.timeout);message.error?p.reject(Error(message.error.message)):p.resolve(message.result)}});
 await call('Performance.enable');await call('Page.enable');
 const baseline=await call('Performance.getMetrics');
 const start=performance.now();await call('Page.navigate',{url:`http://127.0.0.1:${port}/`});
 let result;const samples=[];
 for(let i=0;i<900;i++){
  const response=await call('Runtime.evaluate',{expression:'JSON.stringify({report:window.benchmarkReport,error:window.benchmarkError,phase:window.benchmarkPhase})',returnByValue:true});
  const value=JSON.parse(response.result.value||'{}');if(value.error)throw Error(value.error);if(value.report){result=value.report;break}
  samples.push({elapsed_ms:performance.now()-start,phase:value.phase,metrics:(await call('Performance.getMetrics')).metrics});await sleep(100);
 }
 if(!result)throw Error('Benchmark did not complete in 90 seconds');
 result.total_runner_ms=performance.now()-start;
 result.sample_interval_ms=100;result.renderer_samples=samples;
 result.cdp_before=baseline.metrics;result.cdp_after=(await call('Performance.getMetrics')).metrics;
 result.browser=(await call('Browser.getVersion')).product;
 result.source_commit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
 result.harness_sha256={};for(const name of ['scripts/performance_browser.mjs','scripts/performance/frontend.tsx'])result.harness_sha256[name]=createHash('sha256').update(await readFile(resolve(root,name))).digest('hex');
 result.instrumentation='Production profiling adds overhead; headless browser is not native WebView2 or a visible-GPU frame-rate acceptance';
 result.extensions_disabled=true;
 result.playback_media={source:args.audio?'supplied local WAV':'generated silence',sha256:createHash('sha256').update(wav).digest('hex')};
 await writeFile(resolve(area,'report.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({passed:true,browser:result.browser,rows:result.rows.map(r=>({name:r.name,commits:r.commits,react_ms:r.react_actual_ms,frames:r.frame_interval_ms}))},null,2));
 await call('Browser.close');
}finally{
 ws?.close();browser.kill();await new Promise(r=>server.close(r));
 for(const p of pending.values()){clearTimeout(p.timeout);p.reject(Error('Browser closed'))}
}
