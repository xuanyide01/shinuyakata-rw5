import {catalog} from './catalog.js';
export const SAVE_SCHEMA=1;
export const SLOT_COUNT=30;
function copy(x){return JSON.parse(JSON.stringify(x));}
export function sceneInfo(id){const row=catalog.scenes.filter(x=>x.id===id)[0];if(!row)throw Error('章节尚未接入');return row;}
export function newState(id){sceneInfo(id||catalog.initial);return {schema:1,scene:id||catalog.initial,cursor:0,variables:{},positionId:'',history:[],ended:false};}
export function snapshot(s){return {schema:SAVE_SCHEMA,scene:s.scene,cursor:s.cursor,variables:copy(s.variables),positionId:s.positionId||'',sourceIndex:Number.isInteger(s.sourceIndex)?s.sourceIndex:null,ended:!!s.ended};}
export function restore(raw){
 const s=typeof raw==='string'?JSON.parse(raw):raw;
 if(!s||s.schema!==SAVE_SCHEMA||!Number.isInteger(s.cursor)||s.cursor<0)throw Error('存档格式不兼容');
 const info=sceneInfo(s.scene);if(s.cursor>info.length)throw Error('存档位置无效');
 if(!s.variables||typeof s.variables!=='object'||Array.isArray(s.variables)||Object.keys(s.variables).length>32)throw Error('存档状态无效');
 for(const k of Object.keys(s.variables)){if(k==='__proto__'||k==='constructor'||!['string','number','boolean'].includes(typeof s.variables[k]))throw Error('存档变量无效');}
 const n=Object.assign(newState(s.scene),copy(s),{history:[]});n.pendingPosition=!!s.positionId;return n;
}
function remember(s){s.history.push(snapshot(s));if(s.history.length>8)s.history.shift();}
export function condition(c,v){if(!c)return true;if(c.all)return c.all.every(x=>condition(x,v));if(c.equals!==undefined)return (v[c.key]===undefined?0:v[c.key])===c.equals;return !!v[c.key];}
function changes(s,items){for(const x of items||[]){if(!x.key||x.key==='__proto__'||x.key==='constructor')throw Error('状态变量无效');s.variables[x.key]=x.add!==undefined?(Number(s.variables[x.key])||0)+x.add:x.value;}}
export function exitTarget(s,info){changes(s,info.onExit);if(info.routes){for(const route of info.routes)if(condition(route.when,s.variables))return route.target;throw Error('没有匹配的剧情出口');}return info.next;}
export function read(s,ops){
 if(s.pendingPosition){if(!ops[s.cursor]||ops[s.cursor].id!==s.positionId){let i=ops.findIndex(x=>x.id===s.positionId);if(i<0&&Number.isInteger(s.sourceIndex))i=ops.findIndex(x=>x.sourceStart<=s.sourceIndex&&x.sourceEnd>=s.sourceIndex);if(i<0)throw Error('此存档对应的内容已改变');s.cursor=i;}s.pendingPosition=false;}
 for(let i=0;i<64;i++){
  const op=ops[s.cursor];
  if(!op){const info=sceneInfo(s.scene),next=exitTarget(s,info);if(next){sceneInfo(next);s.scene=next;s.cursor=0;s.positionId='';s.sourceIndex=null;return {type:'load'};}s.ended=true;return {type:'end',ending:info.ending||''};}
  s.positionId=op.id;
  if(Number.isInteger(op.sourceStart))s.sourceIndex=op.sourceStart;
  if(op.type==='jump'){if(!Number.isInteger(op.to)||op.to<0||op.to>=ops.length)throw Error('跳转位置无效');s.cursor=op.to;continue;}
  if(op.type!=='text'&&op.type!=='choice')throw Error('此指令尚不支持');
  return op;
 }
 throw Error('剧情跳转超过安全限制');
}
export function advance(s){if(s.ended)return;remember(s);s.cursor++;s.positionId='';}
export function choose(s,ops,index){
 const op=ops[s.cursor];if(!op||op.type!=='choice'||!Number.isInteger(index)||!op.items[index])throw Error('选项无效');
 const item=op.items[index];if(item.scene)sceneInfo(item.scene);else if(!Number.isInteger(item.to)||item.to<0||item.to>=ops.length)throw Error('选项目标无效');
 remember(s);if(item.set){const k=item.set[0];if(!k||k==='__proto__'||k==='constructor')throw Error('选项变量无效');s.variables[k]=item.set[1];}
 changes(s,item.changes);if(item.scene){s.scene=item.scene;s.cursor=0;}else s.cursor=item.to;s.positionId='';s.sourceIndex=null;s.ended=false;
}
export function previous(s){const last=s.history.pop();if(!last)return false;const history=s.history;Object.assign(s,last,{history,pendingPosition:false});return true;}
export function skipChapter(s,ops){
 remember(s);
 for(let count=0;count<256;count++){
  const op=read(s,ops);if(op.type!=='text')return op;s.cursor++;s.positionId='';
 }
 throw Error('章节超过当前跳跃限制');
}
export function slotKey(n){if(!Number.isInteger(n)||n<0||n>=SLOT_COUNT)throw Error('栏位无效');return 'yakata_rw5_slot_v1_'+(n+1);}
export function autoWait(speed,length){return [2600,1500,800][speed]+Math.min(5000,Math.max(0,length-60)*55);}
export function asset(id){return catalog.assets[id]||'';}
