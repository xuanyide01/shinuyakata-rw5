"""Statically inspect a research copy of the CXDEC module; never execute PE code."""
from pathlib import Path
import sys, struct, json, time

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent / '研究'
sys.path.insert(0, str(RESEARCH / 'python-deps'))
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_OP_IMM

path = RESEARCH / 'bug02_yakata.tpm.research-copy'
raw = path.read_bytes()
pe = pefile.PE(data=raw)
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
md.skipdata = True
seeds = {0, 1}
# Bootstrap dispatch recovered from this module's table at RVA 0x3a78.
# Values describe adjacent-bit swap, pair swap, nibble rotation, bit rotation.
assert __import__('hashlib').sha256(raw).hexdigest() == '5c54514a90a19d0fc4249b3bb78d5f9bb1022705adb35d9e8fc8c756df39a46b'
order = [{0x38d3: 1, 0x38fc: 3, 0x38ef: 2, 0x38e3: 0}[va - pe.OPTIONAL_HEADER.ImageBase]
         for va in struct.unpack('<4I', pe.get_data(0x3a78, 16))]
for section in pe.sections:
    if not section.Characteristics & 0x20000000:
        continue
    if section.Name.rstrip(b'\0') == b'.decc':
        target = section
        continue
    for instruction in md.disasm(section.get_data(), pe.OPTIONAL_HEADER.ImageBase + section.VirtualAddress):
        if instruction.id == 0 or instruction.mnemonic not in ('mov', 'push'):
            continue
        for operand in instruction.operands:
            if operand.type == CS_OP_IMM:
                value = operand.imm & 0xffffffff
                if value > 0xff and not pe.OPTIONAL_HEADER.ImageBase <= value < pe.OPTIONAL_HEADER.ImageBase + pe.OPTIONAL_HEADER.SizeOfImage:
                    seeds.add(value)

encoded = raw[target.PointerToRawData:target.PointerToRawData + target.Misc_VirtualSize]
lcg = struct.pack('<I', 1103515245)
report = {'originalModuleExecuted': False, 'method': 'Static byte permutation analysis', 'candidateSeeds': len(seeds), 'bootstrapOrder': order}
started = time.time()
found = None
for number, seed in enumerate([0x35a]):
    state = seed
    out = bytearray(len(encoded))
    for i, value in enumerate(encoded):
        old = state
        state = (((old * 12869 + 0x1b01) & 0xffffffff) ^ (old >> 3))
        mode = order[state & 3]
        out[i] = (((value << 1) | (value >> 7)) & 255 if mode == 0 else
                  ((value & 0x55) << 1) | ((value >> 1) & 0x55) if mode == 1 else
                  ((value << 4) | (value >> 4)) & 255 if mode == 2 else
                  ((value & 0x33) << 2) | ((value >> 2) & 0x33))
    # This module's generator differs from the classic LCG. Accept only the
    # recovered bootstrap seed and the verified initial routine/switch header.
    if seed == 0x35a and out.startswith(bytes.fromhex('0fb6c083c09f83f81977680fb680')):
        decoded = bytearray(raw)
        decoded[target.PointerToRawData:target.PointerToRawData + len(out)] = out
        (RESEARCH / 'module-static-decoded.bin').write_bytes(decoded)
        found = seed
        break
    if number % 100 == 0:
        print(json.dumps({'tried': number + 1, 'total': len(seeds), 'seconds': round(time.time() - started, 2)}), flush=True)
report.update(result='static-decoded' if found is not None else 'not-recognized', seed=found,
              elapsedSeconds=time.time() - started)
(ROOT / 'reports/module-static-analysis.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
print(json.dumps(report), flush=True)
