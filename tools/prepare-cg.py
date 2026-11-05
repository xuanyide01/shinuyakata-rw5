"""Convert every referenced stage/event image to a watch-sized asset and emit the id map.

Inputs: converted/asset-requests.json (703 requests, from the original scenes),
可调用资源/images (decoded original art).
Outputs: src/common/images/<slug>.jpg + converted/asset-map.json
"""
import json
import re
from pathlib import Path

from PIL import Image

R = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码')
LIB = R.parent / '可调用资源' / 'images'
OUT = R / 'src/common/images'
OUT.mkdir(parents=True, exist_ok=True)
W, H = 432, 243
QUALITY = 62

reqs = json.loads((R / 'converted/asset-requests.json').read_text('utf8'))['requests']

CANDIDATES = ['data/bgimage', 'evimage', 'patch', 'data/main', 'data']


def find(file):
    for folder in CANDIDATES:
        p = LIB / folder / (file + '.png')
        if p.exists():
            return p
    hits = list(LIB.rglob(file + '.png'))
    return hits[0] if hits else None


def slug(kind, file):
    s = re.sub(r'[^0-9A-Za-z\u3040-\u30ff\u4e00-\u9fff]+', '_', file)
    return f'{kind}_{s}'[:60]


def to_watch(src):
    im = Image.open(src).convert('RGBA')
    im.thumbnail((W, H), Image.Resampling.LANCZOS)
    bg = Image.new('RGB', (im.width, im.height), (0, 0, 0))
    bg.paste(im, mask=im.getchannel('A'))
    return bg


assets = {}
mapping = {}
missing = []
total = 0
for r in reqs:
    kind, file = r['kind'], r['file']
    if kind not in ('stage', 'event'):
        continue
    key = f'{kind}:{file}:{json.dumps(r.get("options") or {}, sort_keys=True, ensure_ascii=False)}'
    if file.lower() in ('black', '', 'none'):
        if 'black' not in assets:
            Image.new('RGB', (W, H), (0, 0, 0)).save(OUT / 'bg_black.jpg', 'JPEG', quality=80)
            assets['black'] = '/common/images/bg_black.jpg'
        mapping[key] = 'black'
        continue
    src = find(file)
    if not src:
        missing.append(key)
        continue
    name = slug(kind, file) + '.jpg'
    dest = OUT / name
    if not dest.exists():
        to_watch(src).save(dest, 'JPEG', quality=QUALITY, optimize=True)
        total += dest.stat().st_size
    aid = slug(kind, file)
    assets[aid] = '/common/images/' + name
    mapping[key] = aid

(R / 'converted/asset-map.json').write_text(
    json.dumps({'assets': assets, 'map': mapping, 'missing': missing,
                'bytes': sum(p.stat().st_size for p in OUT.glob('*.jpg'))},
               ensure_ascii=False, indent=1), 'utf8')
print(json.dumps({'images': len(assets), 'missing': len(missing),
                  'totalMB': round(sum(p.stat().st_size for p in OUT.glob('*.jpg')) / 1e6, 2),
                  'missingSample': missing[:5]}, ensure_ascii=False))
