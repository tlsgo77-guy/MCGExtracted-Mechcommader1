#!/usr/bin/env python3
"""MechCommander Gold bitmap font (.FNT) reader / writer.

File format (little-endian)
---------------------------
    u32 version      = 11825 (ASCII "1." read as a little-endian dword)
    u32 count        = number of glyphs
    u32 height       = glyph height in pixels (all glyphs share it)
    u32 x            = unknown, preserved verbatim (10 for the 280-glyph
                       fonts, 254 for the 140-glyph ones)
    u32 offset[count]  absolute offsets from the file start
    glyphs: { u32 width; u8 pixels[width*height] }   row-major

Pixel value 0xFF is transparent, anything else is a palette index (the glyph
colour).  The glyph index is the byte value of the character.  Several
offsets may point at the same glyph record (the Korean fonts do this for the
shared blank cell), so the reader resolves glyphs through the offset table
rather than assuming they are stored back to back.

Library use
-----------
    import mcg_fnt
    f = mcg_fnt.read_fnt(path)
    w, px = f.glyphs[65]            # 'A'
    mcg_fnt.write_fnt(path, f)

CLI
---
    mcg_fnt.py info <fnt>
    mcg_fnt.py preview <fnt> <out.png> [text] [--scale N]

`text` may be ASCII or any text; it is encoded as EUC-KR (cp949 fallback) and
rendered with the Korean-layout index mapping when the font has the extended
(count > 256) layout.  Output is white-on-black, scaled 4x by default; the shadow pixels of the
drop-shadow fonts are mid-grey.
"""
import argparse
import struct
import sys

FNT_VERSION = 11825
TRANSPARENT = 0xFF
HEADER_SIZE = 16

# Korean layout (count == KOR_COUNT): 256 single-byte glyphs followed by a
# 94 x 94 EUC-KR double-byte grid.
KOR_COUNT = 256 + 94 * 94


class Glyph:
    """One glyph: width and row-major pixel bytes (len == width*height)."""

    __slots__ = ("width", "pixels")

    def __init__(self, width, pixels):
        self.width = width
        self.pixels = bytes(pixels)

    def __iter__(self):  # allows `w, px = font.glyphs[i]`
        yield self.width
        yield self.pixels

    def __repr__(self):
        return "Glyph(width=%d, %d bytes)" % (self.width, len(self.pixels))


class Font:
    def __init__(self, height, glyphs=None, version=FNT_VERSION, x=0):
        self.version = version
        self.height = height
        self.x = x
        self.glyphs = glyphs if glyphs is not None else []

    @property
    def count(self):
        return len(self.glyphs)

    def row(self, glyph, y):
        w = glyph.width
        return glyph.pixels[y * w:(y + 1) * w]


def parse_fnt(data):
    """Parse FNT bytes into a Font (offsets are followed, sharing preserved
    by returning the very same Glyph object for identical offsets)."""
    if len(data) < HEADER_SIZE:
        raise ValueError("file too short for an FNT header")
    version, count, height, x = struct.unpack_from("<4I", data, 0)
    if version != FNT_VERSION:
        raise ValueError("unexpected FNT version %d (want %d)" % (version, FNT_VERSION))
    table_end = HEADER_SIZE + 4 * count
    if table_end > len(data):
        raise ValueError("offset table runs past end of file")
    offsets = struct.unpack_from("<%dI" % count, data, HEADER_SIZE)
    cache = {}
    glyphs = []
    for i, off in enumerate(offsets):
        g = cache.get(off)
        if g is None:
            if off + 4 > len(data):
                raise ValueError("glyph %d offset 0x%x outside file" % (i, off))
            (width,) = struct.unpack_from("<I", data, off)
            n = width * height
            if off + 4 + n > len(data):
                raise ValueError("glyph %d data runs past end of file" % i)
            g = Glyph(width, data[off + 4:off + 4 + n])
            cache[off] = g
        glyphs.append(g)
    return Font(height, glyphs, version, x)


def read_fnt(path):
    with open(path, "rb") as fh:
        return parse_fnt(fh.read())


def build_fnt(font):
    """Serialise a Font.  Glyph objects that are the *same Python object*
    are stored once and share an offset; everything else is stored in index
    order."""
    count = len(font.glyphs)
    out = bytearray(struct.pack("<4I", font.version, count, font.height, font.x))
    offs_pos = len(out)
    out += b"\0" * (4 * count)
    placed = {}
    offsets = []
    for g in font.glyphs:
        if len(g.pixels) != g.width * font.height:
            raise ValueError("glyph pixel data does not match width*height")
        key = id(g)
        if key not in placed:
            placed[key] = len(out)
            out += struct.pack("<I", g.width)
            out += g.pixels
        offsets.append(placed[key])
    struct.pack_into("<%dI" % count, out, offs_pos, *offsets)
    return bytes(out)


def write_fnt(path, font):
    data = build_fnt(font)
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)


# ---------------------------------------------------------------------------
# Text -> glyph index mapping
# ---------------------------------------------------------------------------

def euckr_index(lead, trail):
    return 256 + (lead - 0xA1) * 94 + (trail - 0xA1)


def text_to_indices(text, font_count):
    """Encode `text` into glyph indices.  With the Korean layout
    (count == KOR_COUNT) double-byte EUC-KR sequences map to the 94x94 grid;
    otherwise only single bytes are produced."""
    try:
        raw = text.encode("euc_kr")
    except UnicodeEncodeError:
        raw = text.encode("cp949", errors="replace")
    korean = font_count >= KOR_COUNT
    out = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if (korean and 0xA1 <= b <= 0xFE and i + 1 < len(raw)
                and 0xA1 <= raw[i + 1] <= 0xFE):
            out.append(euckr_index(b, raw[i + 1]))
            i += 2
        elif b >= 0x80 and not korean:
            out.append(b if b < font_count else 0x20)
            i += 1
        else:
            out.append(b)
            i += 1
    return out


def render_line(font, indices, gap=0):
    """Render glyph indices to a 2-D list of ints (0 / 1 ink mask) plus the
    unmasked palette values.  Returns (width, height, rows) where rows holds
    palette bytes (0xFF = transparent)."""
    h = font.height
    rows = [bytearray() for _ in range(h)]
    for idx in indices:
        if idx >= font.count:
            g = Glyph(0, b"")
        else:
            g = font.glyphs[idx]
        w = g.width
        for y in range(h):
            rows[y] += g.pixels[y * w:(y + 1) * w]
            rows[y] += bytes([TRANSPARENT]) * gap
    width = len(rows[0]) if rows else 0
    return width, h, rows


def detect_shadow_value(font):
    """Return 16 when the capitals use two colours one of which is index 16
    (the drop-shadow convention of BLUEDRP / YELLDRP), else None."""
    vals = set()
    for i in range(ord("A"), min(ord("Z") + 1, font.count)):
        vals.update(v for v in font.glyphs[i].pixels if v != TRANSPARENT)
    return 16 if len(vals) == 2 and 16 in vals else None


def render_mask_image(font, text, scale=4, pad=2):
    """Render `text` white-on-black and return a PIL image (mode 'L').
    Drop-shadow pixels (index 16 in the *DRP fonts) are drawn mid-grey so
    the shadow stays distinguishable."""
    from PIL import Image
    idx = text_to_indices(text, font.count)
    w, h, rows = render_line(font, idx)
    shadow = detect_shadow_value(font)
    img = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    px = img.load()
    for y in range(h):
        r = rows[y]
        for x in range(w):
            if r[x] != TRANSPARENT:
                px[x + pad, y + pad] = 110 if r[x] == shadow else 255
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    return img


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_info(args):
    f = read_fnt(args.fnt)
    ws = [g.width for g in f.glyphs]
    from collections import Counter
    uniq = len({id(g) for g in f.glyphs})
    print("file     : %s" % args.fnt)
    print("version  : %d (0x%X)" % (f.version, f.version))
    print("count    : %d%s" % (f.count, "  (Korean layout: 256 + 94*94)" if f.count == KOR_COUNT else ""))
    print("height   : %d" % f.height)
    print("x        : %d" % f.x)
    print("widths   : min %d  max %d  mean %.2f" % (min(ws), max(ws), sum(ws) / len(ws)))
    print("distinct glyph records: %d (shared offsets: %d)" % (uniq, f.count - uniq))
    hist = Counter(ws)
    print("width histogram: " + ", ".join("%d:%d" % (w, hist[w]) for w in sorted(hist)))
    vals = Counter()
    for g in f.glyphs:
        vals.update(g.pixels)
    vals.pop(TRANSPARENT, None)
    print("pixel values (non-transparent): " +
          ", ".join("%d:%d" % (v, n) for v, n in sorted(vals.items(), key=lambda t: -t[1])))
    if f.count > 65:
        print("'A' glyph: width %d" % f.glyphs[65].width)


def cmd_preview(args):
    f = read_fnt(args.fnt)
    text = args.text if args.text else "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789"
    img = render_mask_image(f, text, scale=args.scale)
    img.save(args.out)
    print("wrote %s (%dx%d)" % (args.out, img.width, img.height))


def main(argv=None):
    ap = argparse.ArgumentParser(description="MechCommander Gold FNT tool")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info", help="print header and glyph statistics")
    p.add_argument("fnt")
    p.set_defaults(fn=cmd_info)
    p = sub.add_parser("preview", help="render a string to a PNG (white on black)")
    p.add_argument("fnt")
    p.add_argument("out")
    p.add_argument("text", nargs="?", default=None)
    p.add_argument("--scale", type=int, default=4)
    p.set_defaults(fn=cmd_preview)
    args = ap.parse_args(argv)
    # Make CLI text arguments safe on Windows consoles.
    if getattr(sys.stdout, "reconfigure", None):
        sys.stdout.reconfigure(errors="replace")
    args.fn(args)


if __name__ == "__main__":
    main()
