"""Build (or dump) the Korean UI string table read by the patched cLoadString().

Input: UTF-8 JSON object mapping decimal string-resource ids to text,
    {"1": "목표 %i: %s --  ", "2": "미완료", ...}
Output: lang\\kor\\strings.bin
    u32 magic 'KSTR' (0x5254534B LE), u32 count, u32 ids[count] (ascending),
    u32 offsets[count] (from file start), then NUL-terminated EUC-KR strings.

Text is encoded strictly as EUC-KR (KS X 1001): the game font only has those
2350 Hangul syllables, so a character outside the set is an error, not a '?'.
Hanja (lead byte >= 0xCA) only warns.  '\\r' is rejected (the game expects
plain text; '\\n' is allowed), and strings longer than 255 bytes warn because
most callers use 256-byte buffers (cLoadString truncates to size-1).

usage: python build_strings_bin.py <strings.json> <strings.bin>
       python build_strings_bin.py --dump <strings.bin>
"""
import json
import struct
import sys

MAGIC = 0x5254534B
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def encode(sid, text):
    if "\r" in text:
        raise SystemExit(f"id {sid}: carriage return in text")
    if "\0" in text:
        raise SystemExit(f"id {sid}: NUL in text")
    try:
        raw = text.encode("euc_kr")
    except UnicodeEncodeError as e:
        bad = text[e.start:e.end]
        raise SystemExit(f"id {sid}: {bad!r} (U+{ord(bad[0]):04X}) is outside KS X 1001 / EUC-KR") from None
    # Python's euc_kr codec encodes syllables outside the 2350 as KS X 1001:1998
    # annex-3 jamo sequences (A4D4 filler + jamo) instead of failing; reject those,
    # and require every multibyte unit to be a proper 0xA1-0xFE / 0xA1-0xFE cell.
    i = 0
    while i < len(raw):
        if raw[i] < 0x80:
            i += 1
            continue
        lead, trail = raw[i], raw[i + 1] if i + 1 < len(raw) else 0
        if not (0xA1 <= lead <= 0xFE and 0xA1 <= trail <= 0xFE):
            raise SystemExit(f"id {sid}: byte pair {raw[i:i+2].hex()} is not a KS X 1001 cell")
        if lead == 0xA4 and trail == 0xD4:
            raise SystemExit(f"id {sid}: a Hangul syllable outside the KS X 1001 set (2350 syllables) near "
                             f"{text!r}; rewrite it with a standard syllable")
        if lead >= 0xCA:
            print(f"warning: id {sid}: Hanja {raw[i:i+2].decode('euc_kr')!r} (no glyph in the font)", file=sys.stderr)
        i += 2
    if len(raw) > 255:
        print(f"warning: id {sid}: {len(raw)} bytes (most callers pass 256-byte buffers)", file=sys.stderr)
    return raw


def build(table):
    ids = sorted(int(k) for k in table)
    if len(ids) != len(table) or any(i < 0 for i in ids):
        raise SystemExit("ids must be distinct non-negative integers")
    encoded = [encode(i, table[str(i)]) for i in ids]
    pos = 8 + 8 * len(ids)
    offsets = []
    for raw in encoded:
        offsets.append(pos)
        pos += len(raw) + 1
    out = bytearray(struct.pack("<II", MAGIC, len(ids)))
    out += struct.pack(f"<{len(ids)}I", *ids)
    out += struct.pack(f"<{len(ids)}I", *offsets)
    for raw in encoded:
        out += raw + b"\0"
    return bytes(out)


def dump(data):
    magic, count = struct.unpack_from("<II", data, 0)
    if magic != MAGIC:
        raise SystemExit("bad magic")
    ids = struct.unpack_from(f"<{count}I", data, 8)
    offsets = struct.unpack_from(f"<{count}I", data, 8 + 4 * count)
    table = {}
    for sid, off in zip(ids, offsets):
        end = data.index(b"\0", off)
        table[str(sid)] = data[off:end].decode("euc_kr")
    return table


def main(argv):
    if len(argv) == 3 and argv[1] == "--dump":
        table = dump(open(argv[2], "rb").read())
        sys.stdout.reconfigure(encoding="utf-8")
        json.dump(table, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0
    if len(argv) != 3:
        print(__doc__); return 1
    with open(argv[1], encoding="utf-8") as f:
        table = json.load(f)
    if not isinstance(table, dict):
        raise SystemExit("JSON root must be an object of id -> text")
    data = build(table)
    assert dump(data) == {str(int(k)): v for k, v in table.items()}
    open(argv[2], "wb").write(data)
    print(f"wrote {argv[2]}: {len(table)} strings, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
