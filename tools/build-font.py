from pathlib import Path
import os,json
from fontTools import subset
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
font_source=Path(os.environ.get('YAKATA_FONT_SOURCE',str(ROOT.parent/'研究/NotoSansCJKsc-Regular.otf')))
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
