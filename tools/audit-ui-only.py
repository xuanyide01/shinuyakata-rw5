"""Compare UI release with supplied 0.3.5 by bytes. Never decodes or prints story/CG."""
from pathlib import Path
import hashlib,json,zipfile,re
from PIL import Image
from fontTools.ttLib import TTFont
from rpk_signature import audit
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
base=json.loads((R/'reports/ui-baseline-sha256.json').read_text('utf8'))
m=json.loads((R/'src/manifest.json').read_text('utf8'))
with zipfile.ZipFile(base['archive'])as old:
 protected=[n for n in old.namelist()if n.startswith(('src/','converted/','tests/'))and not n.endswith('/')]
 changed=[]
 for n in protected:
  p=R/n
  assert p.is_file(),n
  if sha(p.read_bytes())!=sha(old.read(n)):changed.append(n)
 assert all(n in ['src/manifest.json','src/pages/index/index.ux']or n.startswith('src/common/ui2/')for n in changed),changed
 original=old.read('src/pages/index/index.ux').decode('utf8').replace('\r\n','\n').split('<script>')[1].split('</script>')[0]
 current=(R/'src/pages/index/index.ux').read_text('utf8').split('<script>')[1].split('</script>')[0]
 delta=json.loads((R/'reports/ui-037-controller-delta.json').read_text('utf8'))
 assert current.count(delta['exitMethod'])==1 and current.count(delta['newEndHandler'])==1
 current=current.replace(delta['exitMethod'],'',1).replace(delta['newEndHandler'],delta['originalEndHandler'],1)
 current=current.replace("private:{activeTitle:'',","private:{",1)
 current=current.replace("titlePress(id){this.activeTitle=id;},\n titleRelease(){this.activeTitle='';},\n ",'',1)
 current=current.replace("titleAction(id){this.activeTitle='';","titleAction(id){",1)
 current=current.replace("onHide(){this.activeTitle='';","onHide(){",1)
 for k in ['start','load','gallery','settings','end']:current=current.replace(f",over:'/common/ui2/title-{k}-over.png'",'',1)
 assert current==original,'Non-UI controller logic differs from supplied 0.3.5'

f=R/'dist'/f'{m["package"]}.debug.{m["versionName"]}.rpk'
report=audit(f);assert report['bytes']<25000000
baseline=Path(base['archive']).parent/'死馆-RW5-0.3.5.rpk'
with zipfile.ZipFile(baseline)as old,zipfile.ZipFile(f)as new:
 oldnames={n for n in old.namelist()if not n.endswith('/')}
 newnames={n for n in new.namelist()if not n.endswith('/')}
 removed=sorted(oldnames-newnames);assert not removed,removed
 added=sorted(newnames-oldnames)
 modified=sorted(n for n in oldnames&newnames if sha(old.read(n))!=sha(new.read(n)))
 def allowed(n):return n.startswith('common/ui2/')or n in ['manifest.json','manifest-watch.json','pages/index/index.js','app.js','META-INF/CERT','META-INF/build.txt']
 assert all(allowed(n)for n in added+modified),(added,modified)
 def normalize_app(data):
  s=data.decode('utf8').replace('"versionName":"'+m['versionName']+'"','"versionName":"0.3.5"').replace('"versionCode":'+str(m['versionCode']),'"versionCode":91')
  ids=re.findall(r'(?<=[{,])(\d+)(?=:e=>)',s)
  for i,k in enumerate(ids):
   s=re.sub(r'(?<=[{,])'+k+r'(?=:e=>)','MODULE'+str(i),s)
   s=s.replace('o('+k+')','o(MODULE'+str(i)+')')
  return s
 assert normalize_app(old.read('app.js'))==normalize_app(new.read('app.js')),'App lifecycle changed'
 assert re.sub(r'timeStamp=.*','timeStamp=<build>',old.read('META-INF/build.txt').decode())==re.sub(r'timeStamp=.*','timeStamp=<build>',new.read('META-INF/build.txt').decode())
 for n in newnames:
  if n.startswith('common/'):
   p=R/'src'/n;assert p.is_file()and p.read_bytes()==new.read(n),n
 expected=json.loads(new.read('manifest-watch.json'))
 assert expected==m and m['versionCode']>91
 unchanged=len(oldnames&newnames)-len(modified)
 for p in(R/'src/common/ui2').glob('*.png'):
  with Image.open(p)as im:assert im.width<=432 and im.height<=514 and p.stat().st_size<250000
 cmap=TTFont(R/'src/common/watch.otf').getBestCmap()
 missing=sorted({c for c in(R/'src/pages/index/index.ux').read_text('utf8')if ord(c)>=32 and not c.isspace()and ord(c)not in cmap})
 assert not missing,('Missing UI glyphs',missing)
 report.update({'result':'passed','scope':'UI-only mechanical comparison','baseVersion':'0.3.5','sourceChanges':changed,'addedPackageEntries':added,'modifiedPackageEntries':modified,'unchangedPackageEntries':unchanged,'protectedFilesCompared':len(protected),'nonUiControllerLogicIdentical':True,'authorizedUiBehaviorChange':'END GAME uses lifecycle exit; menu binds scalars directly; opaque cover hides scene','storyEngineCatalogFontsAndPicturesByteIdentical':True,'completeUiFontCoverage':True,'physicalDeviceTested':False})
(R/'reports/ui-only-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({k:report[k]for k in ['result','version','bytes','sha256','unchangedPackageEntries','protectedFilesCompared','addedPackageEntries','modifiedPackageEntries']},ensure_ascii=False,indent=2))
