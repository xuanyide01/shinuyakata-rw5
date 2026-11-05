"""Bounded XP3 payload reading and checksum-validated two-region XOR recovery.

Boundary 0x17b/0x35a recovered by static inspection of the supplied module.
No native module or generated x86 is executed. NumPy computes candidate
Adler checksums from byte histograms, avoiding 256 large trial buffers.
"""
from pathlib import Path
import importlib.util
import zlib
import numpy as np

_spec = importlib.util.spec_from_file_location('xp3_metadata', Path(__file__).with_name('probe-xp3.py'))
metadata = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(metadata)
MOD = 65521
XORS = np.bitwise_xor(np.arange(256, dtype=np.int64)[:, None],
                      np.arange(256, dtype=np.int64)[None, :])


def checksums_by_key(raw):
    length = len(raw)
    counts = np.zeros(256, dtype=np.int64)
    weights = np.zeros(256, dtype=np.int64)
    for start in range(0, length, 1024 * 1024):
        part = np.frombuffer(raw, dtype=np.uint8, offset=start, count=min(1024 * 1024, length - start))
        counts += np.bincount(part, minlength=256)
        # Each chunk's integer-valued accumulation is below float64's exact
        # integer limit. Reduce between chunks to bound subsequent products.
        w = np.arange(length - start, length - start - len(part), -1, dtype=np.float64)
        weights = (weights + np.bincount(part, weights=w, minlength=256).astype(np.int64)) % MOD
    return (1 + XORS @ counts) % MOD, (length + XORS @ weights) % MOD


def recover(raw, expected):
    if zlib.adler32(raw) & 0xffffffff == expected:
        return raw, {'method': 'plaintext', 'adler32Verified': True}
    boundary = min(len(raw), (expected & 0x17b) + 0x35a)
    a1, b1 = checksums_by_key(memoryview(raw)[:boundary])
    a2, b2 = checksums_by_key(memoryview(raw)[boundary:])
    target_a, target_b = expected & 65535, expected >> 16
    aa = (a1[:, None] + a2[None, :] - 1) % MOD
    bb = (b1[:, None] + b2[None, :] + (len(raw) - boundary) * (a1[:, None] - 1)) % MOD
    choices = np.argwhere((aa == target_a) & (bb == target_b))
    if boundary == len(raw):
        choices = choices[choices[:, 1] == 0]
    if len(choices) != 1:
        raise ValueError(f'Expected one checksum-validated key pair, got {len(choices)}')
    first, second = map(int, choices[0])
    first_table = bytes(x ^ first for x in range(256))
    second_table = bytes(x ^ second for x in range(256))
    data = raw[:boundary].translate(first_table) + raw[boundary:].translate(second_table)
    if zlib.adler32(data) & 0xffffffff != expected:
        raise ValueError('Independent final Adler validation failed')
    return data, {'method': 'two-region-xor', 'boundary': boundary,
                  'firstKey': first, 'secondKey': second, 'adler32Verified': True}


def read_payload(archive, item):
    if item.get('metadataWarning'):
        raise ValueError('Refusing malformed metadata entry')
    if item['original'] > 256 * 1024 * 1024:
        raise ValueError('Payload exceeds research allocation cap')
    chunks = []
    with Path(archive).open('rb') as stream:
        for flags, offset, original, packed in item['segments']:
            stream.seek(offset)
            data = metadata.exact(stream, packed)
            if flags & 1:
                data = zlib.decompress(data)
            if len(data) != original:
                raise ValueError('Segment length mismatch')
            chunks.append(data)
    raw = b''.join(chunks)
    if len(raw) != item['original']:
        raise ValueError('Payload length mismatch')
    return recover(raw, item['adler32'])
