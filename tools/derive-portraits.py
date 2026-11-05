"""Derive per-frame portraits from the env snapshot only (presence == on screen).

KiriKiri snapshots list every layer currently on screen, so a character that leaves the
scene disappears from `env.data`.  Carrying the last portrait forward across such a gap
is what made portraits show up in scenes they never belonged to; this version tracks
each character independently and hides it as soon as the engine drops the layer.
"""
import json
import re
from pathlib import Path

from PIL import Image

from prepare_portraits import compose, watch_size, slug

R = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码')
LIB = R.parent / '可调用资源'
OUT = R / 'src/common/portraits'
OUT.mkdir(parents=True, exist_ok=True)

SPEAKER_ALIASES = {'美亚': '美亜', '米亚': 'みあ'}
catalog = json.loads((LIB / 'resource_catalog.json').read_text('utf8'))
effective = {}
for row in catalog['resources']:
    if row['kind'] != 'json' or not re.search(r'/s\d[^/]*\.txt\.scn$', row['originalPath']):
        continue
    name = Path(row['originalPath']).name[:-4].lower()
    if name not in effective or row['originalPath'].startswith('patch/'):
        effective[name] = row


def char_key(obj):
    rd = obj.get('redraw') or {}
    image = rd.get('imageFile')
    if not isinstance(image, dict):
        return None
    f = image.get('file') or ''
    if not f.endswith('.stand'):
        return None
    opts = image.get('options') or {}
    return (f[:-6], opts.get('pose') or '基本', opts.get('dress') or '', opts.get('face') or '')


keys, per_text = set(), {}
stats = {'frames': 0, 'withVisible': 0, 'mapped': 0, 'hiddenByCg': 0}
for name, row in sorted(effective.items()):
    obj = json.loads((LIB / row['path']).read_text('utf-8-sig'))
    for si, scene in enumerate(obj.get('scenes', [])):
        node = 'n_' + name[:-4].replace('-', '_') + '_' + str(si)
        known = {}
        for i, t in enumerate(scene.get('texts', [])):
            stats['frames'] += 1
            env = t[-1] if len(t) > 4 and isinstance(t[-1], dict) else {}
            visible, event_on = {}, False
            for layer in env.get('data', []):
                if not isinstance(layer, list) or len(layer) < 3 or not isinstance(layer[2], dict):
                    continue
                kind = layer[1]
                if kind == 'event' and layer[2].get('showmode') not in (0, None):
                    event_on = True
                if kind not in ('character', 'character2'):
                    continue
                k = char_key(layer[2])
                if k:
                    known[layer[0]] = k
                    visible[layer[0]] = k
                    keys.add(k)
                elif layer[0] in known:
                    visible[layer[0]] = known[layer[0]]
            if event_on:
                stats['hiddenByCg'] += 1
                continue
            if not visible:
                continue
            stats['withVisible'] += 1
            speaker = (t[0] or '').strip()
            speaker = SPEAKER_ALIASES.get(speaker, speaker)
            pick = visible.get(speaker) or next(iter(visible.values()))
            per_text[(node, i)] = pick
            stats['mapped'] += 1

assets, made = {}, 0
for key in sorted(keys):
    try:
        im, _ = compose(*key)
    except Exception:
        im = None
    if im is None:
        continue
    im = watch_size(im)
    aid = 'p_' + '_'.join(slug(x) for x in key)
    dest = OUT / (aid + '.png')
    if not dest.exists():
        im.quantize(colors=255, method=Image.Quantize.FASTOCTREE,
                    dither=Image.Dither.NONE).save(dest, 'PNG', optimize=True)
        made += 1
    assets[key] = aid

mapping = {}
for (node, i), key in per_text.items():
    aid = assets.get(key)
    if aid:
        mapping[f'{node}:{i}'] = aid

(R / 'converted/portrait-map.json').write_text(json.dumps({
    'assets': {a: '/common/portraits/' + a + '.png' for a in set(assets.values())},
    'map': mapping, 'failures': [], 'portraits': len(set(assets.values())),
    'bytes': sum(p.stat().st_size for p in OUT.glob('*.png'))},
    ensure_ascii=False, indent=1), 'utf8')
print(json.dumps({'distinctKeys': len(keys), 'composed': len(assets), 'newImages': made,
                  'mappedTexts': len(mapping), **stats}, ensure_ascii=False))
