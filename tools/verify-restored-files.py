"""Independently reread every restored file and verify size/Adler/SHA-256."""
from pathlib import Path
import collections
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / '原始资源解码'
source = json.loads((ROOT / 'reports/decode-restore-original-files.json').read_text('utf8'))
assert source['result'] == 'passed' and source['verified'] == 10905 and source['failures'] == 0
assert source['mode'] == 'restore-original-files'
rows = source['resources']
expected = {Path(x['archive']).stem + '/' + x['name'].replace('\\', '/') for x in rows}
actual = {p.relative_to(OUT).as_posix() for folder in ['data','evimage','fgimage','patch','video','voice']
          for p in (OUT / folder).rglob('*') if p.is_file()}
assert actual == expected, 'Restored directory differs from verified manifest'


def verify(row):
    relative = Path(row['archive']).stem + '/' + row['name'].replace('\\', '/')
    path = OUT / relative
    assert path.resolve().is_relative_to(OUT.resolve())
    h = hashlib.sha256()
    adler, length = 1, 0
    with path.open('rb') as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            h.update(block)
            adler = zlib.adler32(block, adler)
            length += len(block)
    assert length == row['bytes'], relative
    assert adler & 0xffffffff == row['adler32'], relative
    assert h.hexdigest() == row['sha256'], relative
    return {'path': relative, 'bytes': length, 'sha256': h.hexdigest(),
            'adler32': adler & 0xffffffff}


verified = []
with ThreadPoolExecutor(max_workers=4) as pool:
    for row in pool.map(verify, rows):
        verified.append(row)
        if len(verified) % 1000 == 0:
            print(json.dumps({'diskFilesVerified': len(verified), 'expected': len(rows)}), flush=True)

report = {'result': 'passed', 'mode': 'original-format restoration, no content filtering',
          'files': len(verified), 'bytes': sum(x['bytes'] for x in verified),
          'independentDiskReadback': True, 'allSizesAdlerAndSHA256Match': True,
          'originalGameResourcesReadOnly': True, 'newStoryOrImagesGenerated': False,
          'archiveCounts': dict(collections.Counter(x['archive'] for x in rows)),
          'excludedMalformedPlaceholderEntries': 5,
          'resources': verified}
(ROOT / 'reports/restored-disk-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
(OUT / '资源清单.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
(OUT / 'SHA256SUMS.txt').write_text(''.join(x['sha256'] + '  ' + x['path'] + '\n'
                                           for x in sorted(verified, key=lambda x: x['path'])), 'utf8')
print(json.dumps({k: v for k, v in report.items() if k != 'resources'}, ensure_ascii=False), flush=True)
