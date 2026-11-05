"""Build only the explicitly reviewed SFW subset; never bulk-copy resource folders."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1];P=R.parent;C=P/'可调用资源';RAW=P/'原始资源解码'
COMMON=R/'src/common';COMMON.mkdir(parents=True,exist_ok=True)
for x in ['images','story','ui']:(COMMON/x).mkdir(exist_ok=True)
proof=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(source,target,size=(432,243)):
 im=Image.open(source).convert('RGB');im=im.resize(size,Image.Resampling.LANCZOS)
 im.save(COMMON/target,'JPEG',quality=72,optimize=True)
 proof.append({'source':str(source.relative_to(P)),'sourceSha256':sha(source),'target':target,'review':'manually inspected ordinary non-explicit image'})
 return '/common/'+target

assets={}
assets['forest']=art(C/'images/evimage/ev01a.png','images/forest.jpg')
assets['room']=art(C/'images/data/bgimage/館_美亜の部屋_昼.png','images/room.jpg')
assets['roomNight']=art(C/'images/data/bgimage/館_美亜の部屋_夜.png','images/room-night.jpg')
assets['title']=art(C/'images/data/main/title_bg.png','ui/title.jpg')
black=Image.new('RGB',(432,243),(2,4,8));black.save(COMMON/'images/black.jpg','JPEG');assets['black']='/common/images/black.jpg'

# Exact original layer positions, common scale for the dressed body and face.
base=C/'images/fgimage/美亜/美亜1_0_959.tlg.png'
for key,number in [('neutral',1040),('sad',1277)]:
 face=C/('images/fgimage/美亜/美亜1_0_'+str(number)+'.tlg.png')
 canvas=Image.new('RGBA',(3543,6200));canvas.alpha_composite(Image.open(base).convert('RGBA'),(119,1186));canvas.alpha_composite(Image.open(face).convert('RGBA'),(445,1412))
 # Common upper-body crop retains head, face and dress, and reaches the dialog boundary.
 portrait=canvas.crop((0,1186,3543,4000));portrait.thumbnail((320,286),Image.Resampling.LANCZOS)
 dst=COMMON/('images/mia-'+key+'.png');portrait.save(dst,optimize=True)
 assets[key]='/common/images/mia-'+key+'.png'
 proof.append({'source':[str(base.relative_to(P)),str(face.relative_to(P))],'sourceSha256':[sha(base),sha(face)],'target':'images/mia-'+key+'.png','review':'clothed summer outfit and ordinary expression; original layer coordinates','width':portrait.width,'height':portrait.height})
 if key=='neutral':
  icon=canvas.crop((650,1200,2850,3400)).resize((192,192),Image.Resampling.LANCZOS)
  mask=Image.new('L',(192,192));ImageDraw.Draw(mask).ellipse((0,0,191,191),fill=255);icon.putalpha(mask);icon.save(COMMON/'logo.png',optimize=True)

logo=RAW/'patch/title@logo%layer.png';im=Image.open(logo).convert('RGBA');im.thumbnail((228,159));im.save(COMMON/'ui/logo.png',optimize=True)
proof.append({'source':str(logo.relative_to(P)),'sourceSha256':sha(logo),'target':'ui/logo.png','review':'original title typography only'})

story={};sources=[]
selections=[('intro','s101.txt.scn.json',[0,7,8,9,10,11,12,13,14,16,18,22,23,24,25,26,31,32,33,34,35,37]),
            ('room','s102.txt.scn.json',[0,1,2,3,4,6,9,10,11,12,20,21,22,26,27,28,30,33,35,39,40,41,44,45,48,49,50,51,52,81,82])]
for scene,file,indices in selections:
 f=C/'json/patch'/file;j=json.loads(f.read_text('utf-8-sig'));rows=j['scenes'][0]['texts'];ops=[]
 for i in indices:
  t=rows[i];speaker=t[0]or'';text=t[2]
  assert isinstance(text,str)
  # These indices were separately read and approved, not selected by keywords.
  background='black'if scene=='intro'and i<24 else'forest'if scene=='intro'else'room'
  portrait='sad'if scene=='room'and i>=39 else''
  ops.append({'id':f'{j["name"]}:start:{i}','type':'text','speaker':speaker,'text':text,'background':background,'portrait':portrait})
  sources.append({'scene':scene,'source':str(f.relative_to(P)),'sourceSha256':sha(f),'sourceScene':0,'sourceTextIndex':i,'speaker':speaker,'text':text})
 story[scene]=ops

story['room'].append({'id':'excerpt-complete','type':'text','speaker':'本版说明','text':'本版序章节选到此结束。部分原作段落尚未接入。可在标题的「框架演示」中体验选项、自动播放及存读档功能。','background':'room','portrait':''})
story['demo']=[
 {'id':'demo-0','type':'text','speaker':'框架演示','text':'以下是独立功能演示，不是原作剧情。这里使用普通房间背景和已核对的穿衣立绘。轻点正文可推进，拖动可以滚动长文。','background':'room','portrait':'neutral'},
 {'id':'demo-1','type':'text','speaker':'框架演示','text':'接下来会出现一个演示选项。从菜单选择「下一章」也会停在该选项，等待手动选择。存档会保留当前位置和选择状态。','background':'room','portrait':'neutral'},
 {'id':'demo-choice','type':'choice','background':'room','portrait':'neutral','items':[{'text':'查看白天的房间','to':3,'set':['demoNight',False]},{'text':'查看夜晚的房间','to':5,'set':['demoNight',True]}]},
 {'id':'demo-day','type':'text','speaker':'框架演示','text':'选择的是白天场景。该选择已写入本次进度，保存后重启也能恢复。这里的选择不代表原作分支。','background':'room','portrait':'neutral'},
 {'id':'demo-join-day','type':'jump','to':6},
 {'id':'demo-night','type':'text','speaker':'框架演示','text':'选择的是夜晚场景。游戏仅载入当前场景所需的图片；未审核素材不会通过这个演示入口加载。','background':'roomNight','portrait':'neutral'},
 {'id':'demo-long','type':'text','speaker':'长文与存档演示','text':'这是用于检查换行和滚动的独立说明文字。\n\n应用提供三十个独立存档栏位。保存时需要选择具体栏位；覆盖已有存档前会再次确认。读取界面也由玩家自行选择栏位。\n\n自动播放包含慢速、标准和快速三档。每句话逐字显示结束后会等待一会，再进入下一句。进入菜单、存读档、触摸滚动或切换后台时会暂停；选完选项回到正文后可以继续。\n\n后续内容应通过独立场景编号和已审核素材表接入。当前只是第一版框架与序章节选，不代表全剧情或全部结局已经完成。','background':'room','portrait':''},
 {'id':'demo-finish','type':'text','speaker':'框架演示','text':'功能演示结束。可以返回标题重新开始，或读取刚才保存的任意栏位。','background':'room','portrait':'neutral'}]

catalog={'schema':1,'contentVersion':'0.1.0','initial':'intro','demo':'demo','scenes':[
 {'id':'intro','name':'序章·日常与森林（节选）','file':'intro.txt','length':len(story['intro']),'next':'room','group':'原作非露骨节选'},
 {'id':'room','name':'序章·陌生的房间（节选）','file':'room.txt','length':len(story['room']),'next':None,'group':'原作非露骨节选'},
 {'id':'demo','name':'框架演示（独立内容）','file':'demo.txt','length':len(story['demo']),'next':None,'group':'功能演示'}],
 'gallery':[{'id':'forest','name':'森林中的美亚','variants':['forest']},{'id':'room','name':'美亚的房间','variants':['room','roomNight']}],
 'assets':assets}
for scene,ops in story.items():(COMMON/'story'/(scene+'.txt')).write_text(json.dumps(ops,ensure_ascii=False,separators=(',',':')),'utf8')
(COMMON/'catalog.js').write_text('export const catalog='+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
(R/'converted').mkdir(exist_ok=True)
(R/'converted/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),'utf8')
(R/'converted/reviewed-original-text.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),'utf8')
(R/'converted/text-source.json').write_text(json.dumps(story,ensure_ascii=False,indent=2),'utf8')
(R/'reports/watch-content-whitelist.json').write_text(json.dumps({'scope':'Only reviewed non-explicit excerpts and independent framework demo','fullOriginalStoryIncluded':False,'originalTextRecords':len(sources),'reviewedAssets':proof,'allOtherResourcesExcluded':True},ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'originalTextRecords':len(sources),'scenes':len(story),'demoChoiceCount':1,'artAssets':len(assets)},ensure_ascii=False))
