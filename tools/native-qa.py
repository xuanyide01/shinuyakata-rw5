"""Run after the documented manual setup (demo choice, empty save page 1)."""
from pathlib import Path
import json,time,urllib.request
R=Path(__file__).resolve().parents[1];ENV=R.parent/'研究/vela-environment';LOG=ENV/'emulator.log';OUT=R/'reports'
base='http://127.0.0.1:43142';events=[]
def call(route):
 with urllib.request.urlopen(base+route,timeout=40)as r:return r.read()
def click(x,y,delay=.4):
 call(f'/click?x={x}&y={y}');time.sleep(delay);events.append({'click':[x,y]})
def screen(name):
 (OUT/('native-'+name+'.png')).write_bytes(call('/screen'))
def log():return LOG.read_text('utf8',errors='replace')
start=len(log());click(130,143,.6);assert 'YAKATA_RW5 saved 1'in log()[start:]
for _ in range(7):click(365,474,.35)
screen('slots-29-30');click(120,231,.6);assert 'YAKATA_RW5 saved 30'in log()[start:]
screen('saved-30');click(216,474);click(308,151);click(130,143,.5)
assert 'YAKATA_RW5 loaded 1'in log()[start:];screen('restored-choice')
click(190,234,2.5);assert 'YAKATA_RW5 frame demo 5'in log()[start:];screen('night-branch')
click(353,488,.4);click(180,370,.3);screen('long-text-top')
old=log().count('YAKATA_RW5 frame')
call('/drag?x0=200&y0=440&x1=200&y1=345');time.sleep(.5);screen('long-text-scrolled')
assert old==log().count('YAKATA_RW5 frame'),'Dragging unexpectedly advanced text'
click(353,488,2.4);click(211,488);click(302,229);click(108,304);click(211,397,5.5)
assert 'YAKATA_RW5 excerpt end demo'in log()[start:];screen('demo-end')
click(179,290);time.sleep(.5)
events.append({'note':'Autoplay completed the demo; inspect end screenshot before further steps.'})
(OUT/'native-qa-stage.json').write_text(json.dumps({'stage':'runtime interactions passed','events':events,'checks':['save slot 1','save slot 30','restore pending choice','night branch','long-text scroll does not advance','autoplay ends safely'],'logStartCharacter':start},indent=2),'utf8')
print(json.dumps({'result':'passed','checks':6}))
