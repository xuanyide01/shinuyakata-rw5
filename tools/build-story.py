"""Compile reviewed excerpts and all original route metadata; no original script evaluation."""
from pathlib import Path
import argparse,hashlib,json,re,collections
from PIL import Image
R=Path(__file__).resolve().parents[1];LIB=R.parent/'可调用资源';C=R/'converted';COMMON=R/'src/common'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Patch scripts whose speaker/text columns are shifted by the fan translation
# exporter; fall back to the structurally correct data version and translate it.
LAYOUT_BROKEN_PATCH={'s304_1.txt'}
# Japanese speaker labels from the original scripts mapped to the Chinese names
# used everywhere in the packaged text.
SPEAKERS={'美亜':'美亚','美亚':'美亚','永遠生':'永远生','夏花':'夏花','心々乃':'心乃',
 '愛夢':'爱梦','みあ':'米亚','メイド':'女仆','客人の女':'女客','女性客人':'女客',
 '上位種族の男':'上位种族的男人','腐る男':'腐烂的男人','永遠性':'永远生','女性':'女客',
 '上位种族的呢':'上位种族的男人'}
def speaker(raw):
 value=(raw or '').strip()
 if not value:return ''
 if value in SPEAKERS:return SPEAKERS[value]
 if len(value)>8 or any(c in value for c in '「」。、！？…'):return ''
 return SPEAKERS.get(value,value)
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
NAME_FIX=lambda t:t.replace('女性客人','女客').replace('愛夢','爱梦').replace('美亜','美亚').replace('永遠生','永远生')
def canonical(storage,index):return 'n_'+storage[:-4].replace('-','_')+'_'+str(index)
def chapter_short(storage):
 """Compact corner label: 第N章 + script number only (never wraps on 432px)."""
 base=storage[:-4]
 m=re.match(r's(\d)(\d\d)',base)
 if not m:return base[:8]
 top=m.group(1)
 head='支线'if top=='5'else('终章'if top=='6'else'第%s章'%top)
 tag=base[1:].upper()
 if len(tag)>8:tag=tag[:8]
 return f'{head} {tag}'

def chapter_label(storage,label='',scene=0):
 """Readable, short chapter name: 第N章 · script, plus a whitelisted scene tag."""
 base=storage[:-4]
 m=re.match(r's(\d)(\d\d)',base)
 if not m:return base[:12]
 top,mid=m.group(1),m.group(2)
 if top in '56':head='支线'if base.startswith('s5')else'终章'
 else:head='第'+top+'章'
 tag=base[1:].upper()
 if len(tag)>10:tag=tag[:10]
 lab=(label or '').lstrip('*')
 tag_name={'start':'开场','dummyselect':'分歧','dummyselect1':'分歧','replay':'回想',
           'dummy':'过渡','dummy1':'过渡','return':'回归'}.get(re.sub(r'\d+$','',lab),'')
 if lab and not tag_name:
  tag_name={'开端':'开场'}.get(lab,'')
 if tag_name and tag_name!='开场':return f'{head} · {tag} {tag_name}'
 return f'{head} · {tag}'

def clean(text):
 text=re.sub(r'%[pf][^;]*;','',text).replace('\\n','\n').replace('\r\n','\n')
 text=text.replace('\\表现得n','表现得')
 return re.sub(r'(?m)^[ \t\u3000]+','',text).strip()
END_PUNCT='。！？…!?」』）~～—ー♪♪'
def reflow(text):
 """Drop hard line breaks that fall mid-sentence; keep paragraph boundaries."""
 lines=[x.strip(' \t\u3000')for x in text.split('\n')]
 out=[]
 for line in lines:
  if not line:
   if out and out[-1]!='':out.append('')
   continue
  if out and out[-1]!='':
   joined=out[-1]+line
   prev=out[-1];open_quote=(prev.count('「')>prev.count('」') or prev.count('『')>prev.count('』') or prev.count('（')>prev.count('）') or prev.count('(')>prev.count(')'))
   if open_quote or out[-1][-1] not in END_PUNCT:
    out[-1]=joined
    continue
  out.append(line)
 return '\n'.join(out).strip('\n')

def expression(text):
 if not text:return None
 if '&&'in text:return {'all':[expression(x.strip())for x in text.split('&&')]}
 match=re.fullmatch(r'f\.(\w+)\s*==\s*(\d+)',text)
 if match:return {'key':match[1],'equals':int(match[2])}
 match=re.fullmatch(r'f\.(\w+)',text)
 if match:return {'key':match[1]}
 raise ValueError('Unsupported route condition: '+text)
def assignment(text):
 if isinstance(text,list):text=text[0]+'='+str(text[1])
 if text.startswith('sf.'):return [] # gallery/roll flags do not affect story routing
 match=re.fullmatch(r'f\.(\w+)\s*(=|\+=)\s*(true|false|\d+)',text)
 if not match:raise ValueError('Unsupported state assignment: '+text)
 key,operator,value=match.groups();value={'true':True,'false':False}.get(value,int(value)if value.isdigit()else value)
 return [{'key':key,'add'if operator=='+='else'value':value}]

OPTIONS={
 's303.txt':['对沉睡的男人动手','说服夏花：这样杀不了他'],
 's303_1.txt':['寻找米亚','与夏花一起逃离'],
 's304.txt':['闭上眼睛选择一个人','提出由自己代替'],
 's405.txt':['阻止心乃','取得爱梦的血液'],
 's405_1h.txt':['留在这个房间','躲进厨房'],
 's512.txt':['相信女仆','只靠自己执行','接受客人的提议'],
 's512_1_3.txt':['只靠自己执行','接受客人的提议'],
 's601.txt':['留在原地等待','采取行动'],
 's601_2.txt':['与爱梦交谈','与公馆的男人决一死战'],
 's601_2_2.txt':['前往食材储藏室','寻找爱梦的房间'],
 's602.txt':['遵从米亚的指示','寻找能协助她的方法']}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--version');args=parser.parse_args()
 manifest=json.loads((R/'src/manifest.json').read_text('utf8'));version=args.version or manifest['versionName']
 legacy=C/'legacy-0.1.0-catalog.json'
 if not legacy.exists():write(legacy,json.loads((C/'catalog.json').read_text('utf8')))
 base=json.loads(legacy.read_text('utf8'));review=json.loads((C/'story-review.json').read_text('utf8'))
 assets=json.loads((C/'asset-map.json').read_text('utf8'));assetsById=assets['assets'];fbg={}
 stage_map={};event_map={}
 for row in json.loads((C/'asset-requests.json').read_text('utf8'))['requests']:
  if row['kind'] not in ('stage','event'):continue
  key=row['kind']+':'+row['file']+':'+json.dumps(row.get('options') or {},sort_keys=True,ensure_ascii=False)
  aid=assets['map'].get(key)
  if not aid:continue
  (stage_map if row['kind']=='stage' else event_map)[row['file']]=aid
  for use in row.get('uses',[]):fbg[(use['node'],use['textIndex'])]=aid
 portraits=json.loads((C/'portrait-map.json').read_text('utf8'));fpt={}
 for name,aid in portraits['map'].items():
  node,_,idx=name.rpartition(':');fpt[(node,int(idx))]=aid
 assetsById.update(portraits['assets'])
 _dims={}
 def portrait_dims(aid):
  if aid in _dims:return _dims[aid]
  rel=assetsById.get(aid,'')
  if not rel:return None
  try:w,h=Image.open(R/'src'/rel.lstrip('/')).size
  except Exception:return None
  _dims[aid]=(w,h);return _dims[aid]
 tr_file=C/'translation-zh.json'
 translations=json.loads(tr_file.read_text('utf8'))if tr_file.exists()else{}
 for frag in sorted((C/'translations').glob('*.json'))if (C/'translations').exists()else[]:
  translations.update(json.loads(frag.read_text('utf8')))
 previous=json.loads((C/'catalog.json').read_text('utf8'))
 catalog=json.loads((LIB/'resource_catalog.json').read_text('utf8'));effective={}
 for row in catalog['resources']:
  if row['kind']!='json'or not re.search(r'/s\d[^/]*\.txt\.scn$',row['originalPath']):continue
  name=Path(row['originalPath']).name[:-4].lower()
  if name in LAYOUT_BROKEN_PATCH and row['originalPath'].startswith('patch/'):continue
  if name not in effective or row['originalPath'].startswith('patch/'):effective[name]=row
 originals={};nodes={};source_rows=[]
 for name,row in sorted(effective.items()):
  source=LIB/row['path'];assert sha(source)==row['sha256'],'Converted source changed: '+row['path']
  obj=json.loads(source.read_text('utf-8-sig'));originals[name]=obj
  for i,s in enumerate(obj['scenes']):nodes[(name,s['label'].lower())]={'id':canonical(name,i),'storage':name,'sourceScene':i,'raw':s,'resource':row}
 def target(storage,label=None):
  key=(storage.lower(),(label or '*start').lower())
  if key not in nodes:raise ValueError('Unresolved story destination '+repr(key))
  return nodes[key]['id']
 reviewed={(x['storage'],x['scene']):x for x in review['scenes']};runtime=[];index=[];pending=[];kept=[];choices=0;unresolved=[]
 for (name,label),node in nodes.items():
  s=node['raw'];sid=node['id'];si=node['sourceScene'];texts=s.get('texts',[]);decision=reviewed.get((name,si),{});allowed=set(decision.get('include',[]));reason=decision.get('excludedReason','pending-review')
  assert all(isinstance(i,int)and 0<=i<len(texts)for i in allowed)
  ops=[];i=0;last_stage_file=None;last_event_file=None;last_stage_bg='black';last_bg='black';last_portrait=''
  while i<len(texts):
   if i in allowed:
    t=texts[i];snapshot=t[-1]if isinstance(t[-1],dict)else{};stage_file=None;event_file=None;stage_present=False;event_present=False
    for layer in snapshot.get('data',[]):
     if not isinstance(layer,list)or len(layer)<3 or not isinstance(layer[2],dict):continue
     kind=layer[1];d=layer[2];redraw=d.get('redraw',{});redraw=redraw if isinstance(redraw,dict)else{};image=redraw.get('imageFile',{});image=image if isinstance(image,dict)else{};file=str(image.get('file',''))
     if kind=='stage':
      stage_present=True
      if file:stage_file=file
     if kind=='event':
      event_present=True
      if file:event_file=file
    has_env=bool(snapshot.get('data'))
    if stage_file:last_stage_file=stage_file
    if event_file:last_event_file=event_file
    if stage_present and last_stage_file and stage_map.get(last_stage_file):last_stage_bg=stage_map[last_stage_file]
    if not has_env:
     bg=last_bg
     portrait=last_portrait
    elif event_present:
     bg=event_map.get(last_event_file)or last_stage_bg
     portrait=''
    else:
     bg=last_stage_bg
     portrait=fpt.get((sid,i),'')
    last_bg=bg;last_portrait=portrait
    dims=portrait_dims(portrait)if portrait else None
    pw=round(dims[0]*254/dims[1])if dims and dims[1]else 320
    ph=254
    text=clean(t[2]);op={'id':name+':'+label[1:]+':'+str(i),'type':'text','speaker':speaker(t[0]),'text':text,'background':bg,'portrait':portrait,'pw':pw,'ph':ph,'art':(event_file or stage_file or ''),'artMissing':bool((event_file or stage_file) and bg=='black' and (event_file or stage_file).lower()!='black'),'sourceStart':i,'sourceEnd':i}
    zh=translations.get(op['id'])
    if zh:op['text']=zh;op['translated']=True
    op['text']=reflow(NAME_FIX(op['text']))
    ops.append(op);kept.append({'scene':sid,'storage':name,'source':node['resource']['path'],'sourceSha256':node['resource']['sha256'],'sourceScene':si,'sourceTextIndex':i,'speaker':op['speaker'],'text':text,'rawTextSha256':hashlib.sha256(t[2].encode()).hexdigest()});i+=1
   else:
    start=i
    while i<len(texts)and i not in allowed:i+=1
    gap={'id':sid+':gap:'+str(start),'type':'text','speaker':'内容说明','text':'本段未收录。\n来源：'+name+' · '+str(si)+'\n文本位置：'+str(start)+'—'+str(i-1)+'\n后续可按开发索引逐段审核、补充。','background':'black','portrait':'','sourceStart':start,'sourceEnd':i-1,'omitted':True}
    ops.append(gap);pending.append({'node':sid,'storage':name,'sourceScene':si,'start':start,'end':i-1,'count':i-start,'reason':reason,'resourceId':node['resource']['id'],'source':node['resource']['path'],'sourceSha256':node['resource']['sha256']})
  rawchoices=s.get('selects',[])
  if rawchoices:
   translated=OPTIONS[name];assert len(translated)==len(rawchoices);items=[]
   for option,label_zh in zip(rawchoices,translated):items.append({'text':label_zh,'scene':target(option['storage'],option.get('target')),'changes':assignment(option['exp'])if option.get('exp')else[]})
   _cbg=last_bg;_cpt=last_portrait
   _cd=portrait_dims(_cpt)if _cpt else None
   _cpw=round(_cd[0]*254/_cd[1])if _cd and _cd[1]else 320
   ops.append({'id':sid+':choice','type':'choice','items':items,'background':_cbg,'portrait':_cpt,'pw':_cpw,'ph':254});choices+=1
  routes=[];ending='';rawnext=s.get('nexts',[])
  for edge in rawnext:
   storage=edge.get('storage','').lower()
   if storage=='start.ks'and edge.get('target')=='*gameend_title':ending='原作结局出口';continue
   try:dest=target(storage,edge.get('target'))
   except ValueError:
    unresolved.append({'node':sid,'edge':edge});ending='未解析的原作出口';continue
   routes.append({'target':dest,'when':expression(edge.get('eval'))})
  if not rawchoices and not routes:
   ops.append({'id':sid+':end-notice','type':'text','speaker':'流程说明','text':('已到达原作脚本的结局返回点。\n全剧情已收录，此处为原作返回标题的出口。'if ending=='原作结局出口'else'已到达原作未解析的脚本出口。\n该出口在原作元数据中即为占位，未接入剧情。'),'background':'black','portrait':''})
  if not ops:ops=[{'id':sid+':transition','type':'text','speaker':'场景切换','text':'原作流程连接节点。','background':'black','portrait':''}]
  # Fixed original-index buckets permit adding earlier text without moving later saves.
  buckets=collections.OrderedDict()
  for op in ops:
   bucket=op.get('sourceStart',len(texts))//128;buckets.setdefault(bucket,[]).append(op)
  parts=list(buckets.items());ids=[sid if k==0 else sid+'_b'+str(b)for k,(b,o)in enumerate(parts)]
  for k,((bucket,page),rid)in enumerate(zip(parts,ids)):
   file=rid+'.txt';(COMMON/'story'/file).write_text(json.dumps(page,ensure_ascii=False,separators=(',',':')),'utf8')
   info={'id':rid,'name':chapter_label(name,s['label'],si),'group':'主线','file':file,'length':len(page),'next':ids[k+1]if k+1<len(ids)else None,'chapterKey':sid,'entry':si==0 and k==0,'shortLabel':chapter_short(name),'onExit':[]}
   if k+1==len(ids):
    info['routes']=routes if routes else None;info['ending']=ending
    info['onExit']=[v for exp in s.get('postevals',[])for v in assignment(exp)]
   runtime.append(info)
  index.append({'id':sid,'storage':name,'label':s['label'],'sourceScene':si,'resourceId':node['resource']['id'],'source':node['resource']['path'],'sourceSha256':node['resource']['sha256'],'originalTexts':len(texts),'includedTexts':len(allowed),'runtimePages':ids,'nexts':rawnext,'selects':rawchoices,'onExit':[v for exp in s.get('postevals',[])for v in assignment(exp)]})
  cg_groups={}
 for _aid in sorted(assetsById):
  if not _aid.startswith('event_'):continue
  _m=re.match(r'event_(.+?)([a-z]*)$',_aid)
  if not _m:continue
  cg_groups.setdefault(_m.group(1),[]).append(_aid)
 cg_gallery=[{'id':'cg_'+_g,'name':'CG %02d'%(n+1),'variants':_v}for n,(_g,_v) in enumerate(sorted(cg_groups.items()))]
 base['contentVersion']=version;base.setdefault('assets',{}).update(assetsById);base['scenes']=runtime;base['demo']=None;base['initial']=runtime[0]['id']
 base['gallery']=cg_gallery
 for _g in base['gallery']:
  if _g['id']=='forest':_g['name']='森林'
  elif _g['id']=='room':_g['name']='房间'
 expected={x['file']for x in runtime}
 for old in previous['scenes']:
  name=old['file']
  if old['id'].startswith('n_')and name not in expected:
   path=(COMMON/'story'/name).resolve()
   assert path.parent==(COMMON/'story').resolve()and path.suffix=='.txt'
   if path.exists():path.unlink()
 write(C/'catalog.json',base);(COMMON/'catalog.js').write_text('export const catalog='+json.dumps(base,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
 write(C/'story-source-index.json',{'schema':1,'scripts':len(effective),'scenes':len(nodes),'nodes':index})
 write(C/'story-pending-index.json',{'schema':1,'segments':pending})
 write(C/'reviewed-story-text.json',kept)
 summary={'version':version,'effectiveScripts':len(effective),'sourceScenes':len(nodes),'originalTextRecords':sum(len(n['raw'].get('texts',[]))for n in nodes.values()),'includedOriginalRecords':len(kept),'pendingSegments':len(pending),'omittedOriginalRecords':sum(x['count']for x in pending),'choices':choices,'runtimeFlowPages':len(runtime),'unresolvedExits':unresolved,'fullOriginalStory':False,'fullGraphIndexed':True,'maxChapterFileBytes':max((COMMON/'story'/x['file']).stat().st_size for x in runtime)}
 write(R/'reports/story-build.json',summary);print(json.dumps(summary,ensure_ascii=False))
 manifest.update(versionName=version,versionCode=manifest['versionCode']+1);write(R/'src/manifest.json',manifest)
 package=json.loads((R/'package.json').read_text('utf8'));package['version']=version;write(R/'package.json',package)

if __name__=='__main__':main()
