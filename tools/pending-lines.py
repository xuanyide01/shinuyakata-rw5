"""Print the pending Japanese lines of one story chunk, ready to translate.

Usage:
    python tools/pending-lines.py <file>        # e.g. n_s501_0_b2.txt
    python tools/pending-lines.py --files       # all files and remaining counts
    python tools/pending-lines.py --status      # overall progress

Output lines are: <opIndex>\t<speaker or ->\t<text with ⏎ marking newlines>
The op id for a translation key is "<storage>:start:<opIndex>", where <storage>
is the source script name shown by --files detail mode.
"""
import glob
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
SRC = json.loads((R / 'converted/translation-source.json').read_text('utf8'))['lines']


def translations():
    tr = {}
    p = R / 'converted/translation-zh.json'
    if p.exists():
        tr.update(json.loads(p.read_text('utf8')))
    for f in sorted((R / 'converted/translations').glob('*.json')):
        tr.update(json.loads(f.read_text('utf8')))
    return tr


def todo():
    tr = translations()
    return [r for r in SRC if r['key'] not in tr]


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('--help', '-h'):
        print(__doc__)
        return
    if args[0] == '--status':
        left = todo()
        print(json.dumps({'translated': len(SRC) - len(left), 'remaining': len(left),
                          'remainingChars': sum(len(r['jp']) for r in left),
                          'files': len({r['file'] for r in left})}, ensure_ascii=False))
        return
    left = todo()
    if args[0] == '--files':
        counts = {}
        for r in left:
            counts[r['file']] = counts.get(r['file'], 0) + 1
        for name, count in sorted(counts.items()):
            print(f'{name}\t{count}')
        return
    name = args[0]
    rows = [r for r in left if r['file'] == name]
    if not rows:
        print(f'no pending lines for {name}')
        return
    print(f'# {name}: {len(rows)} lines')
    for r in rows:
        print(r['key'].split(':')[-1] + '\t' + (r['speaker'] or '-') + '\t'
              + r['jp'].replace('\n', '⏎'))


if __name__ == '__main__':
    main()
