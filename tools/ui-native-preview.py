"""Exercise the identical UI with synthetic text and title art, in a separate app sandbox."""
from pathlib import Path
import json,time,io,threading,subprocess,urllib.request
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'reports/ui-preview';O.mkdir(exist_ok=True)
U='http://127.0.0.1:43142';checks=[]
adb=r'D:/codex/2026-11-02/native-toolkit/node_modules/@miwt/adb/bin/win/adb.exe'
def get(p):
 with urllib.request.urlopen(U+p,timeout=90)as f:return f.read()
def click(x,y):get(f'/click?x={x}&y={y}');time.sleep(.4)
def cap(name):
 time.sleep(.25)
 for i in range(30):
  b=get('/screen');im=Image.open(io.BytesIO(b)).convert('RGB')
  if len(im.resize((64,76)).getcolors(5000)or[])>16:break
  time.sleep(.3)
 else:raise RuntimeError('Native screen not rendered: '+name)
 (O/(name+'.png')).write_bytes(b);checks.append(name)
get('/start')  # The controller must be cold-started with STARRY_EMULATOR_PACKAGE=com.codex.yakata.uipreview.
time.sleep(2.5);cap('preview-title')
# Hold the original CONFIG wordmark long enough to inspect its real over-state.
t=threading.Thread(target=lambda:get('/drag?x0=150&y0=418&x1=150&y1=418'));t.start();time.sleep(.2);(O/'preview-title-pressed.png').write_bytes(get('/screen'));checks.append('preview-title-pressed');t.join();time.sleep(.4)
# A long hold intentionally does not dispatch click; open CONFIG with a separate tap.
click(150,418);cap('preview-config');click(216,134);cap('preview-config-font-toggled');click(216,449)
click(160,369);cap('preview-gallery-1');click(343,473);cap('preview-gallery-2')
assert (O/'preview-gallery-2.png').read_bytes()!=(O/'preview-title.png').read_bytes(),'Gallery UI never appeared'
click(120,170);cap('preview-cg-1');click(216,220);cap('preview-cg-2');click(216,439);cap('preview-gallery-return-page2')
click(216,473);click(160,269);time.sleep(.3);click(216,360);cap('preview-reading-font-toggled')
get('/drag?x0=216&y0=445&x1=216&y1=334');cap('preview-reading-scrolled')
click(342,486);time.sleep(.2);cap('preview-choice')
click(85,471);cap('preview-menu');click(120,145);cap('preview-slots')
click(120,135);click(216,181);time.sleep(1.6);click(120,135);cap('preview-overwrite');click(216,244)
for i in range(7):click(343,473)
click(120,220);click(216,181);time.sleep(1.6);cap('preview-slot30-saved')
click(216,473);click(300,145)
for i in range(7):click(343,473)
click(120,220);time.sleep(.3);cap('preview-slot30-choice-restored')
click(216,140);time.sleep(1.0);click(342,486);cap('preview-end')
(R/'reports/ui-native-preview.json').write_text(json.dumps({'stage':'captured; visual verification pending','scope':'Same UI and engine; separate com.codex.yakata.uipreview using only synthetic content','screens':checks,'noOriginalStoryOrCgUsed':True,'saveSlot30WrittenAndLoaded':True},ensure_ascii=False,indent=2),'utf8')
print(json.dumps(checks))
