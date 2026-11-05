"""Inspect an explicit allowlist of interface configuration; no scenario/CG export."""
import argparse
import hashlib
import json
from pathlib import Path
import zlib

from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('probe_xp3', Path(__file__).with_name('probe-xp3.py'))
xp3 = module_from_spec(spec)
spec.loader.exec_module(xp3)

ALLOW = {
    'AppConfig.tjs', 'Config.tjs', 'title.csv', 'title.func', 'title_release.func',
    'message.csv', 'conf.csv', 'file.csv', 'file_load.csv', 'file_save.csv',
    'gallery.csv', 'backlog.csv',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('game', type=Path)
    a = p.parse_args()
    archive = a.game / 'patch.xp3'
    out = Path(__file__).resolve().parents[1] / 'reports/interface-config'
    out.mkdir(parents=True, exist_ok=True)
    items, _ = xp3.index(archive)
    reports = []
    for item in items:
        if item['name'] not in ALLOW:
            continue
        if item['flags'] != 0 or item.get('metadataWarning') or item['original'] > 1024 * 1024:
            raise ValueError('Interface resource not suitable for direct reading')
        blocks = []
        with archive.open('rb') as stream:
            for flag, offset, original, packed in item['segments']:
                stream.seek(offset)
                data = xp3.exact(stream, packed)
                if flag & 1:
                    data = zlib.decompress(data)
                if len(data) != original:
                    raise ValueError('Interface segment size mismatch')
                blocks.append(data)
        data = b''.join(blocks)
        if len(data) != item['original'] or zlib.adler32(data) & 0xffffffff != item['adler32']:
            failure = {'result': 'failed', 'file': item['name'],
                       'reason': 'Interface checksum mismatch; bytes were not exported or interpreted',
                       'expectedBytes': item['original'], 'actualBytes': len(data),
                       'expectedAdler32': item['adler32'],
                       'actualAdler32': zlib.adler32(data) & 0xffffffff,
                       'originalResourcesReadOnly': True, 'scenarioOrCGExported': False}
            (out / 'inspection.json').write_text(json.dumps(failure, ensure_ascii=False, indent=2) + '\n', 'utf8')
            raise ValueError('Interface checksum mismatch for ' + item['name'])
        # Keep exact configuration bytes for independently checking the source layout.
        (out / item['name']).write_bytes(data)
        if data.startswith(b'\xff\xfe'):
            text = data[2:].decode('utf-16-le')
            encoding = 'utf-16-le'
        elif data.startswith(b'\xfe\xfe\x01\xff\xfe'):
            chars = memoryview(data)[5:]
            if len(chars) % 2:
                raise ValueError('Invalid encoded interface text')
            text = ''.join(chr(((v & 0xaaaa) >> 1) | ((v & 0x5555) << 1))
                           for v in (int.from_bytes(chars[n:n + 2], 'little') for n in range(0, len(chars), 2)))
            encoding = 'KiriKiri mode-1 encoded UTF-16'
        elif data.startswith(b'\xef\xbb\xbf'):
            text = data[3:].decode('utf8')
            encoding = 'utf-8-sig'
        else:
            encoding = 'utf-8'
            try:
                text = data.decode(encoding)
            except UnicodeDecodeError:
                encoding = 'cp932'
                text = data.decode(encoding)
        (out / (item['name'] + '.utf8.txt')).write_text(text, 'utf8')
        reports.append({'file': item['name'], 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(),
                        'adler32Verified': True, 'encoding': encoding})
    if {x['file'] for x in reports} != ALLOW:
        raise ValueError('Some expected interface configuration is absent')
    report = {'result': 'passed', 'method': 'Read only allowlisted plaintext interface configuration from patch.xp3',
              'originalResourcesReadOnly': True, 'gameCodeExecuted': False,
              'scenarioOrCGExported': False, 'resources': reports}
    (out / 'inspection.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps({'result': 'passed', 'interfaceConfigurationFiles': len(reports),
                      'scenarioOrCGExported': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
