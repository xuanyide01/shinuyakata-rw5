const test=require('node:test'),assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..');
const cat=JSON.parse(fs.readFileSync(path.join(root,'converted/catalog.json'),'utf8'));
const readOps=id=>fs.readFileSync(path.join(root,'src/common/story',id+'.txt'),'utf8');
const CHOICE_SCENE=(()=>{for(const sc of cat.scenes){if(readOps(sc.id).includes('"type":"choice"'))return sc.id;}throw Error('no choice');})();
const PLAIN_SCENE=cat.initial;
function app(){
 let id=0,now=0;const timers=new Map(),queue=[];const context={console:{log(){}},Date:{now:()=>now},setTimeout(fn,ms){timers.set(++id,{fn,ms});return id;},clearTimeout(id){timers.delete(id);},storage:{get(o){o.success('');},set(o){if(o.success)o.success();}},file:{readText(o){queue.push(o);}},prompt:{showToast(){}}};vm.createContext(context);
 const cat=fs.readFileSync(path.join(root,'src/common/catalog.js'),'utf8').replace('export const catalog=','const catalog=');
 const eng=fs.readFileSync(path.join(root,'src/common/engine.js'),'utf8').replace(/import .*?;\r?\n/,'').replace(/export /g,'');
 const ux=fs.readFileSync(path.join(root,'src/pages/index/index.ux'),'utf8').split('<script>')[1].split('</script>')[0].replace(/^import .*?;\r?\n/gm,'').replace('export default','const component=');
 vm.runInContext(cat+'\n'+eng+'\n'+ux+'\nthis.component=component;this.newState=newState;',context);
 const instance={...context.component.private,...context.component,$element:()=>({scrollTo(){}})};instance.onInit();
 return {a:instance,timers,queue,next(){const item=timers.entries().next().value;if(!item)return false;timers.delete(item[0]);now+=item[1].ms;item[1].fn();return true;},state:context.newState};
}
test('autoplay pauses at a choice, resumes after picking, and never keeps timers in menus/background',()=>{
 const q=app(),a=q.a;a.state=q.state(CHOICE_SCENE);a.ops=JSON.parse(readOps(CHOICE_SCENE));a.cacheScene=CHOICE_SCENE;a.autoEnabled=true;a.render();
 for(let n=0;n<1000&&a.mode!=='choice';n++)assert(q.next());assert.equal(a.mode,'choice');assert(q.next());assert.equal(a.choiceVisible,true);assert.equal(q.timers.size,0);
 a.pick(0);while(q.queue.length)q.queue.shift().success({text:readOps(a.state.scene)});assert.equal(a.mode,'play');assert(q.timers.size>0);a.openMenu();assert.equal(q.timers.size,0);a.resume();a.onHide();assert.equal(q.timers.size,0);a.onShow();assert.equal(q.timers.size,1);a.onShow();assert.equal(q.timers.size,1);a.onDestroy();assert.equal(q.timers.size,0);
});
test('delayed file completion while hidden is rendered after returning; destroy invalidates callbacks',()=>{
 const q=app(),a=q.a;a.startScene(PLAIN_SCENE);assert.equal(q.queue.length,1);a.onHide();q.queue.shift().success({text:readOps(PLAIN_SCENE)});assert(a.deferredRender);a.onShow();assert.equal(a.mode,'play');a.onDestroy();assert.equal(q.timers.size,0);
 const t=app();t.a.startScene(PLAIN_SCENE);t.a.onDestroy();t.queue.shift().success({text:'invalid'});assert.notEqual(t.a.mode,'error');
});
test('dragging cannot advance; first tap completes typing and second advances',()=>{
 const q=app(),a=q.a;a.state=q.state(PLAIN_SCENE);a.ops=JSON.parse(readOps(PLAIN_SCENE));a.cacheScene=PLAIN_SCENE;a.render();a.dragged=true;a.readingTap();assert.equal(a.state.cursor,0);a.dragged=false;a.lastScroll=-1000;a.readingTap();assert.equal(a.state.cursor,0);assert.equal(a.displayText,a.fullText);a.readingTap();assert.equal(a.state.cursor,1);a.onDestroy();assert.equal(q.timers.size,0);
});
