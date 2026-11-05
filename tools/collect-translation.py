"""Collect every still-Japanese story line into a translation queue.

Writes converted/translation-source.json: [{key, node, index, speaker, jp, context}]
where key is the stable story op id used by build-story.py.
"""
import json
import re
from pathlib import Path

R = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码')
STORY = R / 'src/common/story'
OUT = R / 'converted/translation-source.json'

rows = []
for f in sorted(STORY.glob('*.txt')):
    ops = json.loads(f.read_text('utf8'))
    for i, op in enumerate(ops):
        if op.get('type') != 'text':
            continue
        t = op.get('text', '')
        if not re.search(r'[\u3040-\u30ff]', t):
            continue
        prev = ops[i - 1].get('text', '') if i else ''
        nxt = ops[i + 1].get('text', '') if i + 1 < len(ops) else ''
        rows.append({'key': op['id'], 'file': f.name, 'scene': op.get('sceneId', ''),
                     'speaker': op.get('speaker', ''), 'jp': t,
                     'prev': prev[-40:], 'next': nxt[:40]})

OUT.write_text(json.dumps({'count': len(rows), 'lines': rows}, ensure_ascii=False, indent=1), 'utf8')
print(json.dumps({'japaneseLines': len(rows), 'files': len({r['file'] for r in rows})}, ensure_ascii=False))
