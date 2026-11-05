"""Subset the original title font (MotoyaLMaru, embedded as MTLmr3m.ttf) for the watch menu."""
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

R = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码')
SRC = R.parent / '可调用资源/files/data/sysscn/MTLmr3m.ttf'
OUT = R / 'src/common/title-font.ttf'

catalog = json.loads((R / 'converted/catalog.json').read_text('utf8'))
labels = ''.join(row.get('label', '') + row.get('zh', '') for row in [
    {'label': 'NEW GAME'}, {'label': 'LOAD GAME'}, {'label': 'CHAPTER'},
    {'label': 'GALLERY'}, {'label': 'CONFIG'},
])
chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 :·-—/.,!?()「」『』')
font = TTFont(str(SRC))
options = subset.Options()
options.desubroutinize = True
options.hinting = False
options.layout_features = []
options.notdef_outline = True
sub = subset.Subsetter(options=options)
sub.populate(unicodes=[ord(c) for c in chars])
sub.subset(font)

for rec in font['name'].names:
    if rec.nameID in {1, 2, 3, 4, 6, 16, 17}:
        val = {1: 'YakataTitle', 2: 'Regular', 3: 'YakataTitle-Regular', 4: 'YakataTitle Regular',
               6: 'YakataTitle-Regular', 16: 'YakataTitle', 17: 'Regular'}[rec.nameID]
        try:
            rec.string = val.encode(rec.getEncoding())
        except Exception:
            pass
font.save(str(OUT))

check = TTFont(str(OUT))
cmap = check.getBestCmap()
missing = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if ord(c) not in cmap]
print(json.dumps({'bytes': OUT.stat().st_size, 'glyphs': len(cmap), 'missingAscii': missing,
                  'source': str(SRC.name)}, ensure_ascii=False))
