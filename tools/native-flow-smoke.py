"""Native UI regression on the dedicated virtual watch, starting at its title."""
from pathlib import Path
import urllib.request,time,io,json
from PIL import Image
R=Path(__file__).resolve().parents[1];OUT=R/'reports';checks=[]
def call(route):return urllib.request.urlopen('http://127.0.0.1:43142'+route,timeout=30).read()
def click(x,y):call(f'/click?x={x}&y={y}');time.sleep(.5)
def capture(name,area=None,minimum=0):
 for _ in range(20):
  data=call('/screen');im=Image.open(io.BytesIO(data)).convert('RGB')
  count=sum(1 for p in im.crop(area).getdata()if min(p)>80)if area else minimum
  if count>=minimum:break
  time.sleep(.15)
 (OUT/('v011-final-'+name+'.png')).write_bytes(data)
 assert count>=minimum,'Native content did not redraw: '+name
 checks.append(name)

click(111,327);click(123,232);capture('choice-cold',(25,80,405,280),1500)
for n in range(5):
 click(57,450);click(309,151);click(123,232);capture('choice-repeat-'+str(n),(25,80,405,280),1500)
click(183,235);capture('original-play',(25,335,405,465),150)
click(212,488);click(110,151);click(123,318);time.sleep(.7)
click(215,474);click(309,151);click(123,318);capture('play-restored',(25,335,405,465),150)
for n in range(2):
 click(212,488);click(309,151);click(123,318);capture('play-repeat-'+str(n),(25,335,405,465),150)
click(212,488);click(309,151)
for _ in range(7):click(365,474)
click(123,232);capture('legacy-slot30',(25,80,405,280),1500)
click(57,450);click(213,451);click(111,370)
for _ in range(19):click(365,457)
capture('chapter-page20');click(160,261);capture('japanese',(25,335,405,465),150)
click(212,488);click(110,226);capture('ending-notice',(25,335,405,465),150)
click(352,488);capture('ending')
(OUT/'native-flow-smoke.json').write_text(json.dumps({'result':'passed','checks':checks,'choiceReloads':5,'playReloads':3,'legacySlot':30,'note':'Pixel checks establish visible text after native rendering; scene/state logs are retained separately.'},ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'result':'passed','checks':len(checks)}))
