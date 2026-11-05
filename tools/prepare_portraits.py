"""Compose every requested portrait from original STAND layers and emit the id map.

Reuses the layer tables proven on the probe; falls back to the first dress/face row
when the request names a variant rig (e.g. dress "血" selects <base>血<n>).
"""
import json
import re
import zlib
from pathlib import Path

from PIL import Image

R = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码')
RAW = R.parent / '原始资源解码'
LIBTXT = R.parent / '可调用资源' / 'text'
LIBIMG = R.parent / '可调用资源' / 'images' / 'fgimage'
OUT = R / 'src/common/portraits'
OUT.mkdir(parents=True, exist_ok=True)
HEIGHT = 272
MAXW = 432


def split_tjs_array(text):
    out = []
    pos = 0
    while True:
        k = text.find('%[', pos)
        if k < 0:
            break
        i = k + 2
        depth = 1
        start = i
        while i < len(text):
            c = text[i]
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    out.append(text[start:i])
                    break
            i += 1
        pos = i + 1
    return out


def stand_entries(character):
    p = LIBTXT / 'fgimage' / f'{character}.stand.utf8.txt'
    if not p.exists():
        return []
    entries = []
    for body in split_tjs_array(p.read_text('utf8')):
        name = re.search(r'"name"\s*=>\s*"([^"]*)"', body)
        fn = re.search(r'"filename"\s*=>\s*"([^"]*)"', body)
        if name and fn:
            entries.append({'pose': name.group(1), 'base': fn.group(1)})
    return entries


def layer_table(base):
    p = RAW / 'fgimage' / f'{base}_0.txt'
    if not p.exists():
        hits = list((RAW / 'fgimage').rglob(f'{base}_0.txt'))
        if not hits:
            return None, None
        p = hits[0]
    b = p.read_bytes()
    i = b.find(b'\x78\x9c')
    if i < 0:
        return None, None
    lines = [l for l in zlib.decompress(b[i:]).decode('utf-16-le').splitlines() if l.strip()]
    header = lines[0].lstrip('#').split('\t')
    rows = []
    for line in lines[2:]:
        cells = line.split('\t')
        if len(cells) < len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows, lines[1].split('\t')


def info(base):
    p = LIBTXT / 'fgimage' / f'{base}_info.txt.utf8.txt'
    if not p.exists():
        return None
    dress, face = [], []
    for line in p.read_text('utf8').splitlines():
        cells = line.split('\t')
        if cells and cells[0] == 'dress' and len(cells) >= 5:
            dress.append((cells[1].strip(), cells[4].strip()))
        elif cells and cells[0] == 'face' and len(cells) >= 4:
            face.append((cells[1].strip(), cells[3].strip()))
    return {'dress': dress, 'face': face}


def pick_base(character, pose, dress):
    entries = stand_entries(character)
    for want in (pose, pose + '・' + dress):
        for e in entries:
            if e['pose'] == want:
                return e
    for e in entries:
        if e['pose'].startswith(pose):
            return e
    return entries[0] if entries else None


def compose(character, pose, dress, face):
    e = pick_base(character, pose, dress)
    if not e:
        return None, 'no-stand'
    rows, canvas = layer_table(e['base'])
    meta = info(e['base'])
    if not rows or not meta:
        return None, 'no-table'
    dl = [l for n, l in meta['dress'] if n == dress] or ([meta['dress'][0][1]] if meta['dress'] else [])
    fl = [l for n, l in meta['face'] if n == face] or ([meta['face'][0][1]] if meta['face'] else [])
    want = dl + fl
    if not want:
        return None, 'no-match'
    byname = {r['name'].strip(): r for r in rows}
    W, H = int(canvas[3] or 3543), int(canvas[4] or 6200)
    im = Image.new('RGBA', (W, H))
    used = 0
    for name in want:
        r = byname.get(name)
        if not r:
            continue
        png = LIBIMG / character / f"{e['base']}_0_{r['layer_id']}.tlg.png"
        if not png.exists():
            continue
        layer = Image.open(png).convert('RGBA')
        op = int(r.get('opacity') or 255)
        if op != 255:
            layer.putalpha(layer.getchannel('A').point(lambda n: n * op // 255))
        im.alpha_composite(layer, (int(r['left']), int(r['top'])))
        used += 1
    if not used:
        return None, 'no-layer'
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    return im, 'ok'


def watch_size(im):
    h = min(HEIGHT, im.height)
    w = max(1, round(im.width * h / im.height))
    if w > MAXW:
        w = MAXW
        h = max(1, round(im.height * w / im.width))
    return im.resize((w, h), Image.Resampling.LANCZOS)


def slug(s):
    return re.sub(r'[^0-9A-Za-z\u3040-\u30ff\u4e00-\u9fff]+', '_', s)[:40]


reqs = json.loads((R / 'converted/asset-requests.json').read_text('utf8'))['requests']
assets, mapping, failures = {}, {}, []
cache = {}
for r in reqs:
    if r['kind'] != 'character':
        continue
    o = r.get('options') or {}
    character = r['file'][:-len('.stand')] if r['file'].endswith('.stand') else r['file']
    key = (character, o.get('pose', ''), o.get('dress', ''), o.get('face', ''))
    if key not in cache:
        try:
            im, status = compose(*key)
        except Exception as err:
            im, status = None, 'error:' + str(err)[:40]
        if im is None:
            cache[key] = (None, status)
        else:
            im = watch_size(im)
            name = 'p_' + '_'.join(slug(x) for x in key) + '.png'
            dest = OUT / name
            q = im.quantize(colors=255, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            q.save(dest, 'PNG', optimize=True)
            aid = 'p_' + '_'.join(slug(x) for x in key)
            assets[aid] = '/common/portraits/' + name
            cache[key] = (aid, 'ok')
    aid, status = cache[key]
    if aid:
        for use in r.get('uses', []):
            mapping[f"{use['node']}:{use['textIndex']}"] = aid
    else:
        failures.append({'key': key, 'status': status})

total = sum(p.stat().st_size for p in OUT.glob('*.png'))
(R / 'converted/portrait-map.json').write_text(json.dumps(
    {'assets': assets, 'map': mapping, 'failures': failures[:40],
     'portraits': len(assets), 'bytes': total}, ensure_ascii=False, indent=1), 'utf8')
print(json.dumps({'portraits': len(assets), 'mappedTexts': len(mapping),
                  'failures': len(failures), 'MB': round(total / 1e6, 2),
                  'failureSample': failures[:3]}, ensure_ascii=False))
