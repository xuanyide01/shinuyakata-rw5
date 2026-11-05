const test=require('node:test'),assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),vm=require('vm');
const R=path.resolve(__dirname,'..');
function app(){
 let count=0,token=0;const timers=new Map(),writes=[];
 const c={console:{log(){}},setTimeout(f,ms){timers.set(++token,{f,ms});return token;},clearTimeout(id){timers.delete(id);},Date,storage:{get(o){o.success('');},set(o){writes.push(JSON.parse(o.value));o.success?.();}},file:{readText(){}},prompt:{showToast(){}}};vm.createContext(c);
 const cat={initial:'test',scenes:[{id:'test',file:'test.txt',length:2}],assets:{},gallery:[]};
 const eng=fs.readFileSync(path.join(R,'src/common/engine.js'),'utf8').replace(/^import .*?;\r?\n/gm,'').replace(/export /g,'');
 const script=fs.readFileSync(path.join(R,'src/pages/index/index.ux'),'utf8').split('<script>')[1].split('</script>')[0].replace(/^import .*?;\r?\n/gm,'').replace('export default','const component=');
 vm.runInContext('const catalog='+JSON.stringify(cat)+';\n'+eng+'\n'+script+'\nthis.component=component;',c);
 const a={...c.component.private,...c.component,$element:()=>({scrollTo(){}}),$app:{exit(){count++;}}};a.onInit();a.state={schema:1,scene:'test',cursor:0,variables:{},history:[]};a.cacheScene='test';a.ops=[{id:'a',type:'text',text:'界面检查'},{id:'b',type:'text',text:'继续检查'}];
 return{a,timers,writes,schedule:c.setTimeout,exits:()=>count};
}
test('menu autoplay and speed change immediately, remain paused in menu and arm on resume',()=>{
 const q=app(),a=q.a;a.mode='play';a.fullText='界面检查';a.displayText=a.fullText;a.openMenu();a.menuAction('auto');assert.equal(a.autoEnabled,true);assert.equal(q.timers.size,0);
 const start=a.autoSpeed;for(let i=1;i<=3;i++){a.menuAction('speed');assert.equal(a.autoSpeed,(start+i)%3);assert.equal(q.writes.at(-1).autoSpeed,a.autoSpeed);assert(a.autoSpeedLabel.endsWith(['慢速','标准','快速'][a.autoSpeed]));}
 a.resume();assert.equal(q.timers.size,1);a.openMenu();assert.equal(q.timers.size,0);a.menuAction('auto');assert.equal(a.autoEnabled,false);a.resume();assert.equal(q.timers.size,0);
});
test('END GAME exits through app lifecycle after cancelling timers and stale callbacks',()=>{
 const q=app(),a=q.a;a.mode='title';a.autoEnabled=true;a.timer=q.schedule(()=>assert.fail('stale typing'),20);a.autoTimer=q.schedule(()=>assert.fail('stale auto'),30);a.paintTimer=q.schedule(()=>assert.fail('stale paint'),40);const load=a.loadToken,slot=a.slotToken;
 a.titleAction('end');assert.equal(q.exits(),1);assert.equal(a.autoEnabled,false);assert.equal(a.timer,null);assert.equal(a.autoTimer,null);assert.equal(a.paintTimer,null);assert.equal(q.timers.size,0);assert(a.loadToken>load&&a.slotToken>slot);
});
test('exit respects in-progress storage writes',()=>{const q=app();q.a.storageBusy=true;q.a.titleAction('end');assert.equal(q.exits(),0);q.a.storageBusy=false;q.a.titleAction('end');assert.equal(q.exits(),1);});
