from pathlib import Path
import hashlib, io, json, shutil, zipfile
from PIL import Image
from fontTools.ttLib import TTFont
from rpk_signature import audit

R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'src/manifest.json').read_text('utf8'))
_tr=R/'converted/translation-zh.json';translations=json.loads(_tr.read_text('utf8'))if _tr.exists()else{}
for _frag in sorted((R/'converted/translations').glob('*.json'))if (R/'converted/translations').exists()else[]:translations.update(json.loads(_frag.read_text('utf8')))
END_PUNCT='。！？…!?」』）~～—ー♪♪'
def reflow(text):
 lines=[x.strip(' \t\u3000')for x in text.split('\n')]
 out=[]
 for line in lines:
  if not line:
   if out and out[-1]!='':out.append('')
   continue
  if out and out[-1]!='':
   prev=out[-1];open_quote=(prev.count('「')>prev.count('」') or prev.count('『')>prev.count('』') or prev.count('（')>prev.count('）') or prev.count('(')>prev.count(')'))
   if open_quote or prev[-1] not in END_PUNCT:
    out[-1]=prev+line
    continue
  out.append(line)
 return '\n'.join(out).strip('\n')
def nfix(t):return t.replace('女性客人','女客').replace('愛夢','爱梦').replace('美亜','美亚').replace('永遠生','永远生')
f=R/'dist'/f'{m["package"]}.debug.{m["versionName"]}.rpk'
report=audit(f);assert report['bytes']<25000000
z=zipfile.ZipFile(f);assert json.loads(z.read('manifest-watch.json'))==m
expected={str(p.relative_to(R/'src')).replace('\\','/')for p in(R/'src/common').rglob('*')if p.is_file()and p.suffix!='.js'}
actual={n for n in z.namelist()if n.startswith('common/')and not n.endswith('/')}
assert actual==expected,(actual-expected,expected-actual)
for n in actual:assert(R/'src'/n).read_bytes()==z.read(n),n
assert not any(n.lower().endswith(('.xp3','.scn','.tlg','.exe','.dll','.pem','.key','.ogg','.wmv'))for n in z.namelist())
catalog=json.loads((R/'converted/catalog.json').read_text('utf8'))
allowed={v.replace('/common/','')for v in catalog.get('assets',{}).values()if str(v).startswith('/common/')}|{'logo.png','ui/logo.png','ui/title.jpg','ui/transparent.png','images/black.jpg'}|{str(x.relative_to(R/'src/common')).replace('\\','/')for x in (R/'src/common/ui2').glob('*')if x.suffix in ('.png','.jpg')}
images={n[7:]for n in actual if n.endswith(('.png','.jpg'))};assert images==allowed,(images-allowed,allowed-images)
for name in images:
 im=Image.open(io.BytesIO(z.read('common/'+name)));im.load();assert im.width<=432 and im.height<=(514 if name.startswith('ui2/') else 286)
icon=Image.open(io.BytesIO(z.read('common/logo.png')));assert icon.size==(192,192)and icon.mode=='RGBA'
assert all(icon.getpixel(pt)[3]==0 for pt in[(0,0),(0,191),(191,0),(191,191)])
proof=json.loads((R/'reports/watch-content-whitelist.json').read_text('utf8'))
for row in proof['reviewedAssets']:
 sources=row['source']if isinstance(row['source'],list)else[row['source']]
 hashes=row['sourceSha256']if isinstance(row['sourceSha256'],list)else[row['sourceSha256']]
 for source,digest in zip(sources,hashes):assert sha(P/source)==digest
reviewed=json.loads((R/'converted/reviewed-original-text.json').read_text('utf8'))
assert len(reviewed)==53
cache={}
for row in reviewed:
 source=P/row['source']
 if source not in cache:
  assert sha(source)==row['sourceSha256'];cache[source]=json.loads(source.read_text('utf-8-sig'))
 t=cache[source]['scenes'][row['sourceScene']]['texts'][row['sourceTextIndex']]
 assert(t[0]or'')==row['speaker']and t[2]==row['text']
 expected_id=f"{cache[source]['name']}:start:{row['sourceTextIndex']}"
 ops=json.loads(z.read('common/story/'+row['scene']+'.txt'))
 op=next(x for x in ops if x['id']==expected_id);assert op['text']==row['text']and op['speaker']==row['speaker']
source_ops=json.loads((R/'converted/text-source.json').read_text('utf8'))
for scene,ops in source_ops.items():assert json.loads(z.read('common/story/'+scene+'.txt'))==ops
cmap=TTFont(io.BytesIO(z.read('common/watch.otf'))).getBestCmap()
text=''.join(p.read_text('utf8')for p in(R/'src').rglob('*')if p.is_file()and p.suffix in{'.ux','.js','.txt','.json'})
assert all(c.isspace()or ord(c)<32 or ord(c)in cmap for c in text)
story_report=json.loads((R/'reports/story-build.json').read_text('utf8'))if(R/'reports/story-build.json').exists()else{}
if story_report:
 from importlib.machinery import SourceFileLoader
 cleaner=SourceFileLoader('story_builder',str(R/'tools/build-story.py')).load_module().clean
 full=json.loads((R/'converted/reviewed-story-text.json').read_text('utf8'));cache={}
 for row in full:
  source=P/'可调用资源'/row['source']
  if source not in cache:
   assert sha(source)==row['sourceSha256'];cache[source]=json.loads(source.read_text('utf-8-sig'))
  raw=cache[source]['scenes'][row['sourceScene']]['texts'][row['sourceTextIndex']]
  assert cleaner(raw[2])==row['text']and hashlib.sha256(raw[2].encode()).hexdigest()==row['rawTextSha256']
 assert len(full)==story_report['includedOriginalRecords']
 # Independently join the packaged text back to its inspected source records.
 catalog=json.loads((R/'converted/catalog.json').read_text('utf8'))
 inspected={(x['scene'],x['sourceTextIndex']):x for x in full};seen=set()
 for scene in catalog['scenes']:
  if not scene.get('chapterKey'):continue
  for op in json.loads(z.read('common/story/'+scene['file'])):
   if op['type']!='text':continue
   if op.get('omitted'):
    assert op['speaker']=='内容说明'and op['text'].startswith('本段未收录。\n来源：')
    continue
   if 'sourceStart'not in op:
    assert op['id'].endswith((':end-notice',':transition'))and op['speaker']in{'流程说明','场景切换'}
    continue
   assert op['sourceStart']==op['sourceEnd']
   key=(scene['chapterKey'],op['sourceStart']);row=inspected[key]
   assert op['speaker']==row['speaker'];assert op['text']==reflow(nfix(translations.get(op['id'])or row['text']));assert key not in seen
   seen.add(key)
 assert seen==set(inspected),'Packaged original text differs from the inspected whitelist'
report.update(result='passed',originalTextRecords=story_report.get('includedOriginalRecords',53),legacyOriginalRecords=53,reviewedImageFiles=len(images),circularIcon=True,
 packagedContentMatchesWhitelist=True,allSourceResourcesMatch=True,completeFontCoverage=True,
 fullOriginalStory=False,physicalDeviceTested=False,saveSlots=30)
(R/'reports/package-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=False))
