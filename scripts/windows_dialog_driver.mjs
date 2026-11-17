// Supervised native acceptance: observe, inspect, then act in a separate cell.
// Numeric accessibility clicks in the native file dialog were observed activating
// Save for an index labelled Cancel. Bind clicks to a fresh non-helper image.
export function createDesktopDriver(sky, {app, exportDirectory, timeoutMs=10000}) {
  let current=null, serial=0;
  const directory=exportDirectory.replaceAll('\\','/').replace(/\/$/,'').toLowerCase();
  if(!/^[a-z]:\//.test(directory)||!directory.includes('/.tools/'))throw Error('Use an absolute isolated .tools export directory');
  const title=kind=>kind==='main'?/^MoodScope 0\.3$/:/^(WAV exportieren|Export WAV)$/;
  async function observe(kind) {
    current=null;
    if(!['main','dialog'].includes(kind))throw Error('Unknown window kind');
    const deadline=Date.now()+timeoutMs;
    while(Date.now()<deadline) {
      const owned=(await sky.list_windows()).filter(w=>w.app===app);
      const windows=owned.filter(w=>title(kind).test(w.title||''));
      if(windows.length>1)throw Error('Ambiguous native window');
      if(!windows.length||(kind==='main'&&owned.some(w=>title('dialog').test(w.title||'')))) {
        await new Promise(resolve=>setTimeout(resolve,100));
        continue;
      }
      const state=await sky.get_window_state({window:windows[0],include_screenshot:true,include_text:true});
      const regions=state.screenshots.filter(s=>(s.width||0)>=300&&(s.height||0)>=100);
      if(!regions.length)throw Error('Only helper-window geometry available; restore and reobserve');
      current={kind,state,regions,token:++serial};
      return {token:serial,window:state.window,tree:state.accessibility?.tree||'',
        focus:state.accessibility?.focused_element,screenshots:regions.map(({url,...metadata})=>metadata)};
    }
    throw Error('Native window readiness deadline exceeded');
  }
  function consume(token) {
    const value=current;
    current=null;
    if(!value||value.token!==token)throw Error('Stale observation; observe again');
    return value;
  }
  async function clickAt({token,screenshotId,x,y,next}) {
    const value=consume(token),region=value.regions.find(s=>s.id===screenshotId);
    if(!region||!Number.isFinite(x)||!Number.isFinite(y)||x<0||y<0||x>=region.width||y>=region.height)throw Error('Point must belong to an observed non-helper screenshot');
    if(!['main','dialog'].includes(next))throw Error('Specify the expected next window');
    await sky.click({window:value.state.window,screenshotId,x,y});
    return observe(next);
  }
  async function setFilename({token,path}) {
    const value=consume(token),normalized=path.replaceAll('\\','/').toLowerCase();
    const leaf=normalized.slice(directory.length+1);
    if(value.kind!=='dialog'||!normalized.startsWith(directory+'/')||!leaf||leaf.includes('/')||/[<>:"|?*\x00-\x1f]/.test(leaf)||!leaf.endsWith('.wav'))throw Error('Filename must be a WAV directly inside the isolated export directory');
    const matches=value.state.accessibility?.tree.split('\n').filter(line=>/text field \(edit\).*ID: 1001$/.test(line)&&/File name:|Dateiname:/.test(line))||[];
    if(matches.length!==1)throw Error('Filename edit is missing or ambiguous');
    const index=Number(matches[0].trim().match(/^\d+/)[0]);
    await sky.set_value({window:value.state.window,element_index:index,value:path});
    const result=await observe('dialog');
    if(!result.tree.includes('Value: '+path+' ID: 1001'))throw Error('Filename value was not confirmed');
    return result;
  }
  async function escape({token}) {
    const value=consume(token);
    if(value.kind!=='dialog'||/Confirm Save As/.test(value.state.accessibility?.tree||''))throw Error('Observe the intended save dialog before Escape');
    await sky.press_key({window:value.state.window,key:'Escape'});
    return observe('main');
  }
  return {observe,clickAt,setFilename,escape};
}
