"""Prepare reproducible build metadata and a subset font; original media stays read-only."""
from pathlib import Path
import json, re, shutil
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT.parent.parent/'parquet-rw5/源码'
manifest={'package':'com.codex.yakata.rw5','name':'死馆','versionName':'0.1.0','versionCode':1,
 'minPlatformVersion':1000,'minAPILevel':1,'icon':'/common/logo.png','deviceTypeList':['watch'],
 'features':[{'name':x}for x in ['system.storage','system.file','system.prompt']],
 'config':{'designWidth':432,'logLevel':'log'},'router':{'entry':'pages/index','pages':{'pages/index':{'component':'index'}}}}
(ROOT/'src/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
(ROOT/'src/config-watch.json').write_text('{}\n','utf8')
(ROOT/'src/app.ux').write_text('<script>\nexport default {onCreate(){console.log("YAKATA_RW5 app created");},onDestroy(){console.log("YAKATA_RW5 app destroyed");}};\n</script>\n','utf8')
(ROOT/'package.json').write_text(json.dumps({'name':'shinuyakata-rw5','version':'0.1.0','private':True,
 'description':'Reviewed prologue excerpts and extensible REDMI Watch 5 visual novel framework',
 'license':'MIT','author':'xuanyide','scripts':{'build':'node tools/build.cjs','test':'node --test tests/*.test.cjs'}},indent=2)+'\n','utf8')
for name in ['build.cjs','repack-rpk.cjs']:
 text=(REF/'tools'/name).read_text('utf8').replace('com.codex.parquet.rw5','com.codex.yakata.rw5')
 text=text.replace('10000000','25000000').replace('10,000,000','25,000,000').replace('15000000','25000000').replace('15,000,000','25,000,000')
 (ROOT/'tools'/name).write_text(text,'utf8')
shutil.copyfile(REF/'quickapp.config.js',ROOT/'quickapp.config.js')
shutil.copyfile(ROOT.parent/'研究/NotoSansCJK-OFL.txt',ROOT/'licenses/NotoSansCJK-OFL.txt')
shutil.copyfile(ROOT/'licenses/NotoSansCJK-OFL.txt',ROOT/'src/common/font-license.txt')
font_source=ROOT.parent/'研究/NotoSansCJKsc-Regular.otf'
all_text=''.join(p.read_text('utf8')for p in (ROOT/'src').rglob('*')if p.is_file()and p.suffix in {'.js','.ux','.txt','.json'})
chars=set(all_text)|set(chr(i)for i in range(32,127))|set('确认取消空栏位保存成功读取失败重新尝试序章框架演示已完成')
font=TTFont(font_source)
options=subset.Options();options.desubroutinize=True;options.hinting=False;options.layout_features=[]
options.drop_tables+=['BASE','GSUB','GPOS','VORG','vhea','vmtx']
sub=subset.Subsetter(options=options);sub.populate(unicodes=[ord(c)for c in chars]);sub.subset(font)
for rec in font['name'].names:
 if rec.nameID in {1,2,3,4,6,16,17}:
  name={1:'YakataWatchText',2:'Regular',3:'YakataWatchText-Regular',4:'YakataWatchText Regular',6:'YakataWatchText-Regular',16:'YakataWatchText',17:'Regular'}[rec.nameID]
  rec.string=name.encode(rec.getEncoding())
if 'CFF 'in font:
 font['CFF '].cff.fontNames=['YakataWatchText-Regular']
 top=font['CFF '].cff.topDictIndex[0];top.FullName='YakataWatchText Regular';top.FamilyName='YakataWatchText'
out=ROOT/'src/common/watch.otf';font.save(out)
check=TTFont(out);cmap=check.getBestCmap();missing=sorted(c for c in chars if ord(c)>=32 and ord(c)not in cmap)
if missing:raise ValueError('Missing font characters: '+repr(missing))
(ROOT/'reports/font-coverage.json').write_text(json.dumps({'result':'passed','characters':len(chars),'glyphs':len(cmap),'bytes':out.stat().st_size,'missing':missing,'font':'YakataWatchText','source':str(font_source)},ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'fontBytes':out.stat().st_size,'characters':len(cmap)}))
