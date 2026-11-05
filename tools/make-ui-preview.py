"""Build input for a separate UI test app containing only synthetic text and UI pictures."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];W=R.parent/'研究/UI-0.3.7-preview'
W.mkdir(parents=True,exist_ok=True)
for n in ['src/app.ux','src/config-watch.json','quickapp.config.js','tools/build.cjs','tools/repack-rpk.cjs','src/pages/index/index.ux','src/common/engine.js','src/common/watch.otf','src/common/title-font.ttf','src/common/font-license.txt','src/common/logo.png']:
 p=R/n
 if p.is_file():(W/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,W/n)
for d in ['ui','ui2']:
 shutil.copytree(R/'src/common'/d,W/'src/common'/d,dirs_exist_ok=True)
m=json.loads((R/'src/manifest.json').read_text('utf8'));m['package']='com.codex.yakata.uipreview';m['name']='死馆 UI'
(W/'src/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(W/'package.json').write_text(json.dumps({'name':'yakata-ui-preview','version':'0.3.7','private':True}),'utf8')
build=(W/'tools/build.cjs').read_text('utf8').replace('com.codex.yakata.rw5','com.codex.yakata.uipreview')
(W/'tools/build.cjs').write_text(build,'utf8')
ops=[{'id':'fixture:text','type':'text','speaker':'UI','background':'test','text':'界面检查。'},
 {'id':'fixture:next','type':'text','speaker':'UI','background':'test2','text':'自动已推进。'},
 {'id':'fixture:choice','type':'choice','items':[{'text':'继续检查界面','scene':'fixture_end'},{'text':'检查长选项的自动换行和完整显示','scene':'fixture_end'}]}]
end=[{'id':'fixture:end','type':'text','speaker':'UI','background':'test','text':'界面检查完成。'}]
S=W/'src/common/story';S.mkdir(parents=True,exist_ok=True)
for n,data in [('fixture',ops),('fixture_end',end)]:
 (S/(n+'.txt')).write_text(json.dumps(data,ensure_ascii=False),'utf8')
scenes=[]
for i in range(70):
 k='fixture'if i==0 else 'fixture_end'if i==1 else 'fixture_'+str(i)
 scenes.append({'id':k,'file':'fixture.txt'if i!=1 else 'fixture_end.txt','length':3 if i!=1 else 1,'name':'界面检查 '+str(i+1),'entry':True,'shortLabel':'UI','chapterKey':k,'ending':'界面检查结束'})
gallery=[{'id':'ui'+str(i),'name':'普通画面 '+str(i+1),'variants':['test','test2']}for i in range(56)]
cat={'contentVersion':'UI PREVIEW','initial':'fixture','scenes':scenes,'gallery':gallery,'assets':{'test':'/common/ui2/test-green.png','test2':'/common/ui2/test-red.png'}}
(W/'src/common/catalog.js').write_text('export const catalog='+json.dumps(cat,ensure_ascii=False)+';','utf8')
# The fixed black base is used only before a synthetic line has rendered.
black=W/'src/common/images/black.jpg';black.parent.mkdir(parents=True,exist_ok=True)
from PIL import Image
Image.new('RGB',(432,243),'black').save(black)
Image.new('RGB',(432,243),(0,255,0)).save(W/'src/common/ui2/test-green.png')
Image.new('RGB',(432,243),(255,0,0)).save(W/'src/common/ui2/test-red.png')
print(W)
