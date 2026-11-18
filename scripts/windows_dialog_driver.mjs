// Supervised native acceptance: observe, inspect, then act in a separate cell.
// Numeric accessibility clicks in the native file dialog were observed activating
// Save for an index labelled Cancel. Bind clicks to a fresh non-helper image.
export function createDesktopDriver(sky, {app, exportDirectory, importDirectory=exportDirectory, timeoutMs=10000}) {
  let current=null, serial=0;
  const directory=exportDirectory.replaceAll('\\','/').replace(/\/$/,'').toLowerCase();
  if(!/^[a-z]:\//.test(directory)||!directory.includes('/.tools/'))throw Error('Use an absolute isolated .tools export directory');
  const inputs=importDirectory.replaceAll('\\','/').replace(/\/$/,'').toLowerCase();
  if(!/^[a-z]:\//.test(inputs)||!inputs.includes('/.tools/'))throw Error('Use an absolute isolated .tools import directory');
  const titles={main:/^MoodScope 0\.3$/,dialog:/^(WAV exportieren|Export WAV)$/,audio:/^(Audio importieren|Import audio)$/,lyrics:/^(LRC importieren|Import LRC)$/};
  const title=kind=>titles[kind];
  async function observe(kind) {
    current=null;
    if(!Object.hasOwn(titles,kind))throw Error('Unknown window kind');
    const deadline=Date.now()+timeoutMs;
    while(Date.now()<deadline) {
      const owned=(await sky.list_windows()).filter(w=>w.app===app);
      const windows=owned.filter(w=>title(kind).test(w.title||''));
      if(windows.length>1)throw Error('Ambiguous native window');
      const parents=owned.filter(w=>title('main').test(w.title||''));
      if(!windows.length&&parents.length>1)throw Error('Ambiguous native parent');
      if((!windows.length&&!(kind!=='main'&&parents.length===1))||(kind==='main'&&owned.some(w=>Object.entries(titles).some(([key,pattern])=>key!=='main'&&pattern.test(w.title||''))))) {
        await new Promise(resolve=>setTimeout(resolve,100));
        continue;
      }
      // Owned native dialogs may be exposed only beneath the parent. Require an
      // exact nested dialog title and a disabled parent before binding through it.
      const state=await sky.get_window_state({window:windows[0]||parents[0],include_screenshot:true,include_text:true});
      const nested=[...new Set((state.accessibility?.tree||'').split('\n').filter(line=>/window \(dialog\)/.test(line)).map(line=>line.trim()))];
      if(kind==='main'&&nested.length){await new Promise(resolve=>setTimeout(resolve,100));continue;}
      if(!windows.length&&!(nested.length===1&&title(kind).test(nested[0].split('window (dialog) ')[1]?.split(' Secondary Actions:')[0]||'')&&/window \(disabled\) MoodScope 0\.3/.test(state.accessibility?.tree||''))){
        await new Promise(resolve=>setTimeout(resolve,100));continue;
      }
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
    if(!Object.hasOwn(titles,next))throw Error('Specify the expected next window');
    await sky.click({window:value.state.window,screenshotId,x,y});
    return observe(next);
  }
  async function setFilename({token,path}) {
    const value=consume(token),normalized=path.replaceAll('\\','/').toLowerCase();
    // Import edits (1148) are exposed with stale indexes in the owned-dialog
    // tree. Select by a fresh image or type literally after verified image focus.
    if(value.kind!=='dialog')throw Error('Import filename input requires a fresh image; indexed edits are disabled');
    const leaf=normalized.slice(directory.length+1);
    if(!normalized.startsWith(directory+'/')||!leaf||leaf.includes('/')||/[<>:"|?*\x00-\x1f]/.test(leaf)||! /\.wav$/.test(leaf))throw Error('Filename must be an allowed file directly inside the isolated export directory');
    const matches=[...new Set(value.state.accessibility?.tree.split('\n').filter(line=>/text field \(edit\).*ID: 1001$/.test(line)&&/File name:|Dateiname:/.test(line)).map(line=>line.trim())||[])];
    if(matches.length!==1)throw Error('Filename edit is missing or ambiguous');
    const index=Number(matches[0].trim().match(/^\d+/)[0]);
    await sky.set_value({window:value.state.window,element_index:index,value:path});
    const result=await observe(value.kind);
    if(!result.tree.includes('Value: '+path+' ID: 1001'))throw Error('Filename value was not confirmed');
    return result;
  }
  async function escape({token}) {
    const value=consume(token);
    if(value.kind==='main'||/Confirm Save As/.test(value.state.accessibility?.tree||''))throw Error('Observe the intended file dialog before Escape');
    await sky.press_key({window:value.state.window,key:'Escape'});
    return observe('main');
  }
  return {observe,clickAt,setFilename,escape};
}
