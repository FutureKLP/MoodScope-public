import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createDesktopDriver} from '../scripts/windows_dialog_driver.mjs';

function fixture() {
  const calls=[];
  const sky={
    list_windows:async()=>[{app:'fixture',id:1,title:'WAV exportieren'}],
    get_window_state:async()=>({window:{app:'fixture',id:1},accessibility:{tree:'3 text field (edit) (settable, string) File name: Value: fixture.wav ID: 1001'},
      screenshots:[{id:'helper',width:16,height:16,url:'excluded'},{id:'dialog',width:946,height:533,url:'excluded'}]}),
    click:async value=>calls.push(value),set_value:async value=>calls.push(value),
  };
  return {calls,sky,driver:createDesktopDriver(sky,{app:'fixture',exportDirectory:'C:/project/.tools/desktop-fixture/exports',timeoutMs:50})};
}
test('rejects helper geometry and consumes invalid observations before input',async()=>{
 const {driver,calls}=fixture(),observed=await driver.observe('dialog');
 assert.deepEqual(observed.screenshots.map(s=>s.id),['dialog']);
 await assert.rejects(driver.clickAt({token:observed.token,screenshotId:'helper',x:1,y:1,next:'dialog'}),/non-helper/);
 await assert.rejects(driver.clickAt({token:observed.token,screenshotId:'dialog',x:884,y:502,next:'dialog'}),/Stale/);
 assert.equal(calls.length,0);
});
test('rejects filename escape and sibling targets before changing the dialog',async()=>{
 const {driver,calls}=fixture();
 for(const path of ['C:/project/data/original.wav','C:/project/.tools/desktop-fixture/exports-sibling/out.wav','C:/project/.tools/desktop-fixture/exports/../original.wav']) {
   const observed=await driver.observe('dialog');
   await assert.rejects(driver.setFilename({token:observed.token,path}),/isolated export/);
 }
 assert.equal(calls.length,0);
});
test('never retries failed native input with stale coordinates',async()=>{
 const {driver,sky,calls}=fixture();
 sky.click=async value=>{calls.push(value);throw Error('window bounds changed')};
 const observed=await driver.observe('dialog');
 await assert.rejects(driver.clickAt({token:observed.token,screenshotId:'dialog',x:884,y:502,next:'dialog'}),/bounds changed/);
 await assert.rejects(driver.clickAt({token:observed.token,screenshotId:'dialog',x:884,y:502,next:'dialog'}),/Stale/);
 assert.equal(calls.length,1);
});

test('binds owned import dialogs through a disabled parent and forbids indexed filename edits',async()=>{
 const {sky,calls}=fixture();
 for(const [kind,title] of [['audio','Audio importieren'],['lyrics','Import LRC']]){
  const line=`9 window (dialog) ${title} Secondary Actions: Raise`;
  sky.list_windows=async()=>[{app:'fixture',id:2,title:'MoodScope 0.3'}];
  sky.get_window_state=async()=>({window:{app:'fixture',id:2},accessibility:{tree:`0 window (disabled) MoodScope 0.3\n${line}\n${line}`},screenshots:[{id:'picker',width:946,height:533,url:'excluded'}]});
  const driver=createDesktopDriver(sky,{app:'fixture',exportDirectory:'C:/project/.tools/desktop-fixture/exports',importDirectory:'C:/project/.tools/desktop-fixture/sources'});
  const observed=await driver.observe(kind);
  assert.ok(observed.tree.includes(title));
  await assert.rejects(driver.setFilename({token:observed.token,path:'C:/project/.tools/desktop-fixture/sources/source.wav'}),/indexed edits are disabled/);
 }
 assert.equal(calls.length,0);
});

test('fails closed for a foreign, unknown or ambiguous owned dialog',async()=>{
 const {sky,calls}=fixture();
 sky.list_windows=async()=>[{app:'fixture',id:2,title:'MoodScope 0.3'},{app:'other-process',id:3,title:'Audio importieren'}];
 for(const tree of ['0 window MoodScope 0.3\n9 window (dialog) Audio importieren','0 window (disabled) MoodScope 0.3\n9 window (dialog) Unknown','0 window (disabled) MoodScope 0.3\n9 window (dialog) Audio importieren\n10 window (dialog) Audio importieren']){
  sky.get_window_state=async()=>({window:{app:'fixture',id:2},accessibility:{tree},screenshots:[{id:'picker',width:946,height:533,url:'excluded'}]});
  const driver=createDesktopDriver(sky,{app:'fixture',exportDirectory:'C:/project/.tools/desktop-fixture/exports',timeoutMs:1});
  await assert.rejects(driver.observe('audio'),/readiness deadline/);
 }
 assert.equal(calls.length,0);
});
