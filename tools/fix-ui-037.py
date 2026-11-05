"""Apply the three requested UI fixes to the preserved 0.3.6 view. No content conversion."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'src/pages/index/index.ux';s=p.read_text('utf8')
assert 'exitApplication(){'not in s,'Already applied'
s=s.replace('<div class="scene">','<div show="{{mode === \'play\'}}" class="scene">',1)
s=s.replace('  <div if="{{mode === \'title\'}}" class="title">','  <div if="{{mode !== \'play\'}}" class="screen-cover"></div>\n  <div if="{{mode === \'title\'}}" class="title">',1)
old='<div class="menu-grid"><div for="{{menuRows}}" tid="id" class="menu-cell" onclick="menuAction($item.id)"><text class="menu-text">{{$item.label}}</text></div></div>'
new='''<div class="menu-grid">
    <text class="menu-cell" onclick="menuAction('save')">保存进度</text>
    <text class="menu-cell" onclick="menuAction('load')">读取进度</text>
    <text class="menu-cell" onclick="menuAction('skip')">下一章</text>
    <text class="menu-cell" onclick="menuAction('auto')">{{autoEnabled ? '自动：开启' : '自动：关闭'}}</text>
    <text class="menu-cell menu-speed" onclick="menuAction('speed')">{{autoSpeedLabel}}</text>
    <text class="menu-cell" onclick="menuAction('settings')">阅读设置</text>
   </div>'''
assert old in s;s=s.replace(old,new,1)
old_end="else if(id==='end')prompt.showToast({message:'手表端不提供退出：请按侧键返回桌面'});"
new_end="else if(id==='end')this.exitApplication();"
assert old_end in s;s=s.replace(old_end,new_end,1)
method=" exitApplication(){if(this.loading||this.storageBusy)return;this.stopTimers();this.autoEnabled=false;this.loadToken++;this.slotToken++;this.activeTitle='';console.log('YAKATA_RW5 exit requested');this.$app.exit();},\n"
s=s.replace(' startScene(id){',method+' startScene(id){',1)
s=s.replace('.page {','.screen-cover { position:absolute; left:0px; top:0px; width:432px; height:514px; background-color:#0b0912; }\n.page {',1)
s=s.replace('background-image:url(\'/common/ui2/panel_full.png\');','background-color:#0b0912; background-image:url(\'/common/ui2/panel_full.png\');')
s=s.replace('.menu-text {','.menu-cell { padding-top:21px; font-size:21px; color:#eadfed; text-align:center; }\n.menu-speed { font-size:18px; }\n.menu-text {',1)
p.write_text(s,'utf8')
css=s.split('<style>')[1].split('</style>')[0];(R/'tools/ui-source/classic.css').write_text(css,'utf8')
m=json.loads((R/'src/manifest.json').read_text('utf8'));m.update(versionName='0.3.7',versionCode=95)
(R/'src/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
q=json.loads((R/'package.json').read_text('utf8'));q['version']='0.3.7';(R/'package.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf8')
(R/'reports/ui-037-controller-delta.json').write_text(json.dumps({'exitMethod':method,'originalEndHandler':old_end,'newEndHandler':new_end},ensure_ascii=False,indent=2),'utf8')
print('Applied actual exit, reactive text controls and opaque full-screen cover.')
