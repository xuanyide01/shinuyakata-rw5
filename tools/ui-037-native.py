"""Targeted native regression for menu feedback, opaque panels and lifecycle exit."""
from pathlib import Path
import argparse,io,json,time,urllib.request
from PIL import Image
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args()
kind='preview'if a.preview else'production';O=R/'reports'/('ui037-'+kind);O.mkdir(exist_ok=True)
U='http://127.0.0.1:43142';checks=[];edgeChecks=[]
def get(s):
 with urllib.request.urlopen(U+s,timeout=90)as f:return f.read()
def click(x,y):get(f'/click?x={x}&y={y}');time.sleep(.4)
def capture(name,clean=False,cg=False):
 time.sleep(.25)
 for i in range(50):
  b=get('/screen');im=Image.open(io.BytesIO(b)).convert('RGB')
  if len(im.resize((64,76)).getcolors(5000)or[])>16:break
  if i==10:get('/wake')
  time.sleep(.3)
 else:raise RuntimeError('No rendered UI: '+name)
 (O/(name+'.png')).write_bytes(b);checks.append(name)
 if clean:
  for x,y in [(x,y)for x in range(432)for y in range(514)if x<8 or x>=424 or y<8 or y>=506]:
   if cg and 104<=y<347:continue
   assert im.getpixel((x,y))not in[(0,255,0),(255,0,0)],('Scene leaks through panel edge',name,x,y)
  edgeChecks.append(name)
 return im
expected='com.codex.yakata.uipreview'if a.preview else'com.codex.yakata.rw5'
assert json.loads(get('/info'))['packageName']==expected,'Wrong controller package'
get('/start');time.sleep(1);capture('title')
click(160,269);time.sleep(.4);im=capture('opening')
if a.preview:assert sum(n for n,c in im.getcolors(300000)if c==(0,255,0))>50000
click(216,486);before=capture('menu-auto-off',True)
click(300,221);on=capture('menu-auto-on',True)
region=(220,188,402,253)
assert before.crop(region).tobytes()!=on.crop(region).tobytes(),'Auto label did not refresh'
speed=(28,264,210,330);old=on.crop(speed).tobytes();states=[]
for i in range(3):click(120,296);states.append(capture('menu-speed-'+str(i+1),True).crop(speed).tobytes())
assert len(set(states))==3 and states[-1]==old,'Speed label does not cycle immediately through three states'
if a.preview:
 click(216,394);time.sleep(7);capture('auto-stopped-at-choice',True)
 logPath=R.parent/'研究/vela-environment/emulator.log';pid=json.loads((logPath.parent/'controller-pid.json').read_text('utf8'))
 log=logPath.read_bytes()[pid['logOffset']:].decode('utf8','replace');assert 'YAKATA_RW5 choice fixture 2' in log,'Autoplay did not reach the synthetic choice'
 click(85,471);capture('choice-menu',True)
 click(300,296);capture('settings',True);click(216,449)
 click(120,145);capture('save-slots',True);click(216,473)
 click(300,145);capture('load-slots',True);click(216,473)
 click(330,50);capture('chapters',True);click(343,473);capture('chapters-next',True);click(216,473)
 click(160,369);capture('gallery',True);click(120,170);capture('cg-view',True,True);click(216,439);click(216,473)
else:
 click(216,455)
capture('title-before-exit')
click(160,469);time.sleep(1.5)
(O/'desktop-after-exit.png').write_bytes(get('/screen'));checks.append('desktop-after-exit')
logPath=R.parent/'研究/vela-environment/emulator.log';pid=json.loads((logPath.parent/'controller-pid.json').read_text('utf8'))
log=logPath.read_bytes()[pid['logOffset']:].decode('utf8','replace')
assert 'YAKATA_RW5 exit requested' in log and 'YAKATA_RW5 app destroyed' in log,'Lifecycle exit was not observed'
assert 'panic:'not in log and 'YAKATA_RW5 error'not in log,'Native/runtime error during checks'
(R/'reports'/('ui037-'+kind+'-boot.log')).write_text(log,'utf8')
report={'result':'passed','kind':kind,'package':expected,'version':'0.3.7','versionCode':95,'screens':checks,'edgeChecks':edgeChecks,'autoLabelChangedImmediately':True,'threeSpeedLabelsCycleImmediately':True,'autoAdvancedToChoice':bool(a.preview),'exitLifecycleObserved':True,'panicOrAppErrors':[]}
(R/'reports'/('ui037-'+kind+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=False))
