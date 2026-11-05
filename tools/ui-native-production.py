"""UI regression on the actual package; never advances beyond the opening line."""
from pathlib import Path
import json,time,urllib.request,io
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'reports/ui-native';O.mkdir(exist_ok=True)
U='http://127.0.0.1:43142';checks=[]
def get(p):
 with urllib.request.urlopen(U+p,timeout=90)as f:return f.read()
def click(x,y):get(f'/click?x={x}&y={y}');time.sleep(.32)
def cap(name):
 time.sleep(.25);p=O/(name+'.png')
 for i in range(30):
  data=get('/screen');im=Image.open(io.BytesIO(data)).convert('RGB')
  if len(im.resize((64,76)).getcolors(5000)or[])>16:break
  if i==8:get('/wake')
  time.sleep(.3)
 else:raise RuntimeError('No rendered screen: '+name)
 p.write_bytes(data);checks.append(name)
get('/start');time.sleep(1.0);cap('production-title')
click(160,418);cap('production-config')
assert (O/'production-title.png').read_bytes()!=(O/'production-config.png').read_bytes(),'UI did not change after CONFIG'
click(216,449);click(160,269);time.sleep(.6);click(216,486);cap('production-menu')
click(216,394);cap('production-reading')
click(216,486);click(330,50);cap('production-chapters-1')
click(343,473);cap('production-chapters-2');click(89,473);cap('production-chapters-back')
click(216,473);click(160,269);time.sleep(.5);click(216,486);click(120,145);cap('production-slots')
for i in range(7):click(343,473)
cap('production-slot30-page');click(120,220);cap('production-overwrite-confirm');click(216,244);cap('production-overwrite-cancel')
click(216,473);click(216,455);click(160,318);cap('production-load-slots')
for i in range(7):click(343,473)
cap('production-load-page8');click(216,473);cap('production-title-after-load')
(R/'reports/ui-native-production.json').write_text(json.dumps({'stage':'captured; visual verification pending','scope':'Actual final package; opening frame / UI only; preserves existing saves','screens':checks,'slot30WrittenAndLoaded':False,'actualSaveWriteTested':False,'overwriteCancelled':True},ensure_ascii=False,indent=2),'utf8')
print(json.dumps(checks))
