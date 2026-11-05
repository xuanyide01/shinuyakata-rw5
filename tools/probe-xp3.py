"""Read XP3 directory metadata only. Never extract or execute game content."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import struct
import zlib

MAGIC = b'XP3\r\n \n\x1a\x8bg\x01'
MAX_INDEX = 64 * 1024 * 1024


def exact(stream, count):
    value = stream.read(count)
    if len(value) != count:
        raise ValueError('Truncated archive metadata')
    return value


def chunks(data):
    cursor = 0
    while cursor < len(data):
        if cursor + 12 > len(data):
            raise ValueError('Truncated directory chunk')
        tag, size = struct.unpack_from('<4sQ', data, cursor)
        cursor += 12
        if cursor + size > len(data):
            raise ValueError('Directory chunk exceeds index')
        yield tag, data[cursor:cursor + size]
        cursor += size


def index(archive):
    archive_bytes = archive.stat().st_size
    entries, seen = [], set()
    with archive.open('rb') as stream:
        if exact(stream, 11) != MAGIC:
            raise ValueError('Not a standard XP3 archive')
        offset = struct.unpack('<Q', exact(stream, 8))[0]
        while True:
            if offset in seen or not 19 <= offset < archive_bytes:
                raise ValueError('Invalid or repeated index offset')
            if len(seen) >= 64:
                raise ValueError('Index chain exceeds limit')
            seen.add(offset)
            stream.seek(offset)
            flag = exact(stream, 1)[0]
            packed = struct.unpack('<Q', exact(stream, 8))[0]
            unpacked = struct.unpack('<Q', exact(stream, 8))[0] if flag & 1 else packed
            if max(packed, unpacked) > MAX_INDEX:
                raise ValueError('Index exceeds allocation limit')
            data = exact(stream, packed)
            if flag & 1:
                decoder = zlib.decompressobj()
                data = decoder.decompress(data, MAX_INDEX + 1)
                if not decoder.eof or decoder.unconsumed_tail:
                    raise ValueError('Invalid or oversized compressed index')
            if len(data) != unpacked:
                raise ValueError('Index size mismatch')
            for tag, body in chunks(data):
                if tag != b'File':
                    continue
                item = {}
                for subtag, value in chunks(body):
                    if subtag == b'info':
                        if len(value) < 22:
                            raise ValueError('Truncated file info')
                        flags, original, size, chars = struct.unpack_from('<IQQH', value)
                        if len(value) < 22 + chars * 2:
                            raise ValueError('Truncated filename')
                        name = value[22:22 + chars * 2].decode('utf-16-le')
                        path = PurePosixPath(name.replace('\\', '/'))
                        if path.is_absolute() or '..' in path.parts or ':' in name or '\x00' in name:
                            raise ValueError('Unsafe archived path')
                        item.update(name=name, flags=flags, original=original, packed=size)
                    elif subtag == b'segm':
                        if len(value) % 28:
                            raise ValueError('Invalid segment metadata')
                        item['segments'] = [list(struct.unpack_from('<IQQQ', value, n))
                                            for n in range(0, len(value), 28)]
                    elif subtag == b'adlr':
                        if len(value) != 4:
                            raise ValueError('Invalid checksum metadata')
                        item['adler32'] = struct.unpack('<I', value)[0]
                if not {'name', 'segments', 'original', 'packed'} <= item.keys():
                    raise ValueError('Missing required file metadata')
                if sum(seg[2] for seg in item['segments']) != item['original']:
                    item['metadataWarning'] = 'Segment length total differs from file info; not safe for extraction'
                if any(seg[1] + seg[3] > archive_bytes for seg in item['segments']):
                    raise ValueError('Segment outside archive')
                entries.append(item)
            if not flag & 0x80:
                break
            offset = struct.unpack('<Q', exact(stream, 8))[0]
    return entries, len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'reports/xp3')
    args = parser.parse_args()
    game = args.game.resolve(strict=True)
    output = args.output.resolve()
    if output == game or game in output.parents:
        raise ValueError('Reports must be stored outside the original game directory')
    output.mkdir(parents=True, exist_ok=True)
    report = {'method': 'Read XP3 directory metadata only',
              'originalResourcesReadOnly': True, 'payloadsExtracted': False,
              'executablesRun': False, 'archives': []}
    for archive in sorted(game.glob('*.xp3')):
        entries, blocks = index(archive)
        (output / (archive.name + '.index.json')).write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + '\n', 'utf8')
        summary = {'archive': archive.name, 'archiveBytes': archive.stat().st_size,
                   'entries': len(entries), 'indexBlocks': blocks,
                   'unpackedBytes': sum(item['original'] for item in entries),
                   'extensions': dict(Counter(Path(item['name']).suffix.lower() for item in entries)),
                   'entryFlags': dict(Counter(str(item['flags']) for item in entries)),
                   'examples': [item['name'] for item in entries[:5]]}
        report['archives'].append(summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    report['result'] = 'metadata-read'
    (output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')


if __name__ == '__main__':
    main()
