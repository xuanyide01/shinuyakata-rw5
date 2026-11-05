raise SystemExit('Archived 0.3.6 installer; use build-ui-only.py in 0.3.7')
"""UI-only conversion from the supplied 0.3.5 UX. Never rebuilds story or fonts."""
from pathlib import Path
import json,zipfile
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'reports/ui-baseline-sha256.json').read_text('utf8'))
with zipfile.ZipFile(base['archive'])as z:s=z.read('src/pages/index/index.ux').decode('utf8').replace('\r\n','\n')
old='<image class="title-logo" src="/common/ui/logo.png" />'
s=s.replace(old,'<image class="title-shade" src="/common/ui2/title-shade.png" />\n   '+old)
s=s.replace('class="title-row" onclick="titleAction($item.id)"','class="title-row" ontouchstart="titlePress($item.id)" ontouchend="titleRelease" ontouchcancel="titleRelease" onclick="titleAction($item.id)"')
s=s.replace('src="{{$item.src}}" /></div></div>','src="{{activeTitle === $item.id ? $item.over : $item.src}}" /></div></div>',1)
s=s.replace('private:{galleryPage:0,','private:{activeTitle:\'\',galleryPage:0,',1)
for k in ['start','load','gallery','settings','end']:
 s=s.replace(f"src:'/common/ui2/title-{k}.png'",f"src:'/common/ui2/title-{k}.png',over:'/common/ui2/title-{k}-over.png'",1)
s=s.replace('titleAction(id){if(this.loading)return;',"titlePress(id){this.activeTitle=id;},\n titleRelease(){this.activeTitle='';},\n titleAction(id){this.activeTitle='';if(this.loading)return;",1)
s=s.replace('onHide(){this.hidden=true;',"onHide(){this.activeTitle='';this.hidden=true;",1)
s=s.replace('class="heading">READING MENU','class="heading">MENU',1)
s=s.replace('<text class="heading">MENU</text>','<text class="heading menu-heading">MENU</text><text class="section-link" onclick="openChapters">章节选择 ›</text>',1)
s=s.replace('class="heading">EXTRA','class="heading">GALLERY',1)
s=s.replace('<div class="row"><text class="button muted" onclick="galleryStep(-1)">上一页</text><text class="button muted" onclick="toTitle">返回标题</text><text class="button muted" onclick="galleryStep(1)">下一页</text></div>','<div class="pager"><text class="pager-item" onclick="galleryStep(-1)">‹ 上一页</text><text class="pager-item" onclick="toTitle">返回</text><text class="pager-item" onclick="galleryStep(1)">下一页 ›</text></div>')
s=s.replace('class="heading">{{cgName}}','class="heading cg-heading">{{cgName}}',1)
# A class on repeated choice and gallery labels avoids unsupported descendant CSS selectors.
s=s.replace('tid="id" class="button" onclick="pick($idx)"','tid="id" class="button option-button" onclick="pick($idx)"',1)
s=s.replace('class="card-name">{{$item.name}}</text><text class="card-meta">{{$item.count}}','class="card-name gallery-name">{{$item.name}}</text><text class="card-meta">{{$item.count}}',1)
css=(R/'tools/ui-source/classic.css').read_text('utf8').replace('.choices .button','.option-button').replace('.gallery-card .card-name','.gallery-name')
s=s.split('<style>')[0]+'<style>\n'+css+'\n</style>\n'
(R/'src/pages/index/index.ux').write_text(s,'utf8')
m=json.loads((R/'src/manifest.json').read_text('utf8'));m['versionName']='0.3.6';m['versionCode']=94
(R/'src/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
p=json.loads((R/'package.json').read_text('utf8'));p['version']='0.3.6'
(R/'package.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf8')
print('UI-only 0.3.6 applied; content catalog, engine, fonts, story and pictures unchanged.')
