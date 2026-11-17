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
