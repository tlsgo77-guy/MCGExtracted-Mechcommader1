"""MechCommander Gold packet-file (.PKK / .PAK / .HSP) reader and LZ decompressor.

Ported from the engine code recovered from MCX.EXE (ScenarioMap/PacketFile symbols)
and the public MechCommander 2 MCLib sources (lzdecomp.cpp, Packet.cpp), which share
the same format:

  header  : u32 version (0xFEEDFACE) or, for checksummed files such as save games,
            the checksum of the rest of the file; then u32 table[numPackets] where
            table[0] is at byte 8 and the first packet starts at table[0] & OFFSET_MASK,
            so numPackets = (firstOffset / 4) - 2.  The top 3 bits of each entry hold
            the storage type (0 RAW, 1 FWF, 2 LZD, 3 HF, 4 ZLIB, 7 NUL).
  LZD     : u32 unpackedSize followed by an LZW stream (9..12-bit codes, LSB first,
            256 = clear, 257 = end, first free code 258).

usage:  python mcg_pkk.py list  <file.pkk>
        python mcg_pkk.py extract <file.pkk> <outdir>
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

OFFSET_MASK = (1 << 29) - 1
TYPE_NAMES = {0: "RAW", 1: "FWF", 2: "LZD", 3: "HF", 4: "ZLIB", 7: "NUL"}
HASH_CLEAR, HASH_EOF, HASH_FREE = 256, 257, 258
BASE_BITS, MAX_BITS = 9, 12


def lz_decompress(src: bytes, expected: int | None = None) -> bytes:
    """LZDecomp() from MCLib: returns the decompressed bytes."""
    buf = src + b"\0\0\0\0"
    end = len(src) - 3                      # LZSrcBufEnd: last position a 4-byte read may start
    pos = 0                                 # esi (byte index)
    bit = 0                                 # cl  (bit offset inside buf[pos])
    bits = BASE_BITS                        # ch  (code width)
    mask = (1 << BASE_BITS) - 1             # LZCodeMask
    max_index = 1 << BASE_BITS              # LZMaxIndex
    free = HASH_FREE                        # LZFreeIndex
    chain_tab = [0] * 4096                  # HashStruct.Chain
    suffix_tab = [0] * 4096                 # HashStruct.Suffix
    old_chain = 0
    old_suffix = 0
    out = bytearray()

    def get_code():
        nonlocal pos, bit
        if pos > end:
            return None
        word = struct.unpack_from("<I", buf, pos)[0]
        code = (word >> bit) & mask
        bit += bits
        pos += bit >> 3
        bit &= 7
        return code

    while True:
        code = get_code()
        if code is None or code == HASH_EOF:
            break
        if code == HASH_CLEAR:
            bits, mask, max_index, free = BASE_BITS, (1 << BASE_BITS) - 1, 1 << BASE_BITS, HASH_FREE
            code = get_code()
            if code is None:
                break
            old_chain = code
            old_suffix = code & 0xFF
            out.append(old_suffix)
            continue
        stack = []
        chain = code
        if code >= free:                    # code not in table yet (KwKwK case)
            stack.append(old_suffix)
            suffix_tab[code] = old_suffix
            chain_tab[code] = old_chain
            cur = old_chain
        else:
            cur = code
        while cur > 255:
            stack.append(suffix_tab[cur])
            cur = chain_tab[cur]
        old_suffix = cur & 0xFF
        stack.append(old_suffix)
        out.extend(reversed(stack))
        suffix_tab[free] = old_suffix
        chain_tab[free] = old_chain
        free += 1
        old_chain = chain
        if free >= max_index and bits != MAX_BITS:
            bits += 1
            mask = mask * 2 + 1
            max_index *= 2
    if expected is not None and len(out) != expected:
        raise ValueError(f"decompressed {len(out)} bytes, expected {expected}")
    return bytes(out)


def checksum(data: bytes) -> int:
    """PacketFile::checkSumFile(): sum of all bytes after the 4-byte header, mod 2**32."""
    return sum(data[4:]) & 0xFFFFFFFF


class PacketFile:
    def __init__(self, data: bytes):
        self.data = data
        self.header = struct.unpack_from("<I", data, 0)[0]
        first = struct.unpack_from("<I", data, 8)[0] & OFFSET_MASK
        self.num_packets = first // 4 - 2
        self.table = [struct.unpack_from("<I", data, 8 + 4 * i)[0] for i in range(self.num_packets)]
        self.is_versioned = self.header == 0xFEEDFACE
        self.checksum_ok = self.is_versioned or self.header == checksum(data)

    def packet_info(self, i: int) -> tuple[int, int, int]:
        """(storage_type, offset, packed_size)"""
        entry = self.table[i]
        off = entry & OFFSET_MASK
        nxt = (self.table[i + 1] & OFFSET_MASK) if i + 1 < self.num_packets else len(self.data)
        return entry >> 29, off, nxt - off

    def read_packet(self, i: int) -> bytes:
        t, off, size = self.packet_info(i)
        raw = self.data[off:off + size]
        if t in (0, 1):
            return raw
        if t == 2:
            unpacked = struct.unpack_from("<I", raw, 0)[0]
            return lz_decompress(raw[4:], unpacked)
        if t == 7:
            return b""
        raise NotImplementedError(f"storage type {TYPE_NAMES.get(t, t)} not supported")


def build_packet_file(packets: list[bytes], versioned: bool = False) -> bytes:
    """Write packets uncompressed (RAW).  Save games use the checksum header."""
    n = len(packets)
    first = (n + 2) * 4
    table, body, off = [], bytearray(), first
    for p in packets:
        table.append(off if p else (off | (7 << 29)))     # empty -> NUL
        body += p
        off += len(p)
    out = bytearray(struct.pack("<I", 0xFEEDFACE if versioned else 0))
    out += struct.pack("<I", first)                       # same value the game writes here
    for e in table:
        out += struct.pack("<I", e)
    out += body
    if not versioned:
        struct.pack_into("<I", out, 0, checksum(out))
    return bytes(out)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 1
    cmd, path = argv[1], Path(argv[2])
    pf = PacketFile(path.read_bytes())
    print(f"{path.name}: header=0x{pf.header:08x} versioned={pf.is_versioned} "
          f"checksum_ok={pf.checksum_ok} packets={pf.num_packets}")
    outdir = Path(argv[3]) if cmd == "extract" and len(argv) > 3 else None
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)
    for i in range(pf.num_packets):
        t, off, size = pf.packet_info(i)
        try:
            data = pf.read_packet(i)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{i:2}] {TYPE_NAMES.get(t, t):4} off={off:6} packed={size:6}  ERROR {exc}")
            continue
        if outdir:
            (outdir / f"packet{i:02}.bin").write_bytes(data)
        # preview only the ASCII part: Korean overlay packets hold EUC-KR bytes that a
        # cp949 console cannot print as latin-1 characters
        head = bytes(b if 32 <= b < 127 else 0x2E for b in data[:40]).decode("ascii")
        print(f"  [{i:2}] {TYPE_NAMES.get(t, t):4} off={off:6} packed={size:6} unpacked={len(data):6}  {head!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
