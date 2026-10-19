"""Minimal reader for the MechCommander *.FST fast-file archives.

Layout (little endian): u32 count, then `count` entries of 262 bytes
    u32 offset, u32 packedSize, u32 realSize, char name[250]   (name = 'data\\art\\logart\\LSBBK00.tga')
Every entry is an LZ/LZW stream (same codec as the .PKK/.PAK packets, see mcg_pkk.lz_decompress).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcg_pkk  # noqa: E402


class FST:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        n = struct.unpack_from("<I", self.data, 0)[0]
        self.entries = []
        for i in range(n):
            o = 4 + i * 262
            off, packed, real = struct.unpack_from("<III", self.data, o)
            name = self.data[o + 12:o + 262].split(b"\0")[0].decode("latin1")
            self.entries.append((name, off, packed, real))

    def names(self):
        return [e[0] for e in self.entries]

    def read(self, index: int) -> bytes:
        name, off, packed, real = self.entries[index]
        raw = self.data[off:off + packed]
        if packed == real:
            return raw
        return mcg_pkk.lz_decompress(raw, real)

    def items(self):
        for i, e in enumerate(self.entries):
            yield e[0], i
