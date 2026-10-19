#!/usr/bin/env python3
"""Replace the English text baked into MechCommander Gold's 8-bit TGA art by Korean text.

The Korean text is rendered with the game's own (already built) Korean bitmap fonts
(game-source/extracted/MCX/lang/kor/data/fonts/WHITE*.FNT, see tools/mcg_fnt.py and tools/README-fonts.md);
the glyphs are used only as a shape mask and are painted with the palette index the original text used.
Only the pixel data of a TGA changes: the 18-byte header, the ID field, the colour map, the orientation
byte (image descriptor), the image type and any trailing bytes are copied verbatim (the tool refuses to
write a file when a re-read does not confirm that).

Usage
-----
    python -I tools/relabel_tga.py --extract            # unpack the TGAs named in art_labels.json from ART.FST
    python -I tools/relabel_tga.py                      # relabel everything in art_labels.json
    python -I tools/relabel_tga.py --only "data/art/logart/LSCBG*"   # subset (glob on the internal path)
    python -I tools/relabel_tga.py --info data/art/BH_ACCEPT.tga [x0 y0 x1 y1]   # palette usage / detection preview
    python -I tools/relabel_tga.py --labels L.json --names N.json --out DIR --review DIR   # tests / other label sets

Defaults (all relative to the repository root)
    labels   localization/ko/art_labels.json
    names    localization/ko/names_map.json
    source   game-source/extracted/MCX/ART.FST   (or the --work dir written by --extract, if the file is there)
    output   game-source/extracted/MCX/lang/kor/<internal path>      e.g. lang/kor/data/art/logart/LSCBG00.tga
    review   localization/ko/art_review/<group>[_n].png              original vs. result at 2x

art_labels.json
---------------
    {"_provisional": true,
     "data/art/logart/LSCBG00.tga": {"text": "메인 메뉴", "bbox": [20, 2, 205, 16]},
     "data/art/B[GHN]_ACCEPT.tga": {...},                      # keys are case-insensitive globs on the internal path
     "data/art/logart/LSCII*.tga": {"regions": [{"bbox": [..], "text": ".."}, ...]},
     "rules": [{"glob": "data/art/logart/LSCFLM*.tga", "names": "mechs", "bbox": [..]}]}

Matching entries are merged in file order (later keys override earlier ones, so put a broad glob first and
the exceptions after it).  Keys starting with "_" are comments.  Fields of an entry (also valid inside a
region, where they override the entry's value):

  what / where
    text      Korean label.   lines: ["..", null, ".."] = one label per detected text line, top to bottom,
              null = leave that line untouched.
    bbox      [x0, y0, x1, y1] (x1/y1 exclusive) = where the English text is AND the room the label may use
              (default: the whole image).  Never let it touch frames: whatever differs from the background
              inside the bbox is taken for text and erased.
    regions   [{bbox, text|lines, ...}, ...] for several texts in one image.   keep: true = leave a region alone.
    group     review sheet name (default: the contact-sheet name of localization/en/art.json).

  how the old text is found (the detected pixels are erased, then the Korean label is drawn)
    mode      rowbg: background = most common index of each row (read from `margin` columns at both bbox
              edges, default 3) -> gradient buttons and flat plates.
              set: text = palette indices that are rare outside the bbox (textured panels).
              auto (default): rowbg when >= 80% of the rows have a uniform margin, else set.
    colors    [idx, ..] = the text (and shadow) indices, explicit.   bg: [idx, ..] = the background indices
              (everything else is text).   exclude: [idx, ..] never text.
    luma_min  text = pixels at least that bright (white title on a photo); luma_soft = also grow `grow` times
              into neighbours at least that bright.   luma_max (+ luma_soft): the same for dark text.
    line_gap  blank rows allowed inside one detected text line (default 0).

  how the label is drawn
    font      8 | 10 | 12.  Default by the old text height: <=8 -> 8, <=10 -> 10, else 12 (shrunk one step at a
              time if it does not fit and `font` was not given).
    align     left | center | right | auto.  The anchor is the old text's own left edge / centre / right edge;
              auto = centre if the old text was centred in the bbox, right if the old lines share a right edge,
              else left.   dx, dy: nudge in pixels (before rotation).
    rotate    90 | -90: the old text runs top-to-bottom (90) / bottom-to-top (-90); the label is drawn in a
              rotated view and rotated back (vertical tabs).
    color     palette index of the new text (default: the old ink colour = the frequent index farthest from
              the background).
    shadow    idx | {"color": idx|"auto", "offsets": [[1, 1]], "outline": true}: drawn first (cyan panel labels:
              black at (+1,+1); briefing cards: black 8-neighbour outline; plates: [[1,1],[2,1]]).  Counts for
              alignment and fit.
    gradient  true = name-plate lettering: the new text takes the per-row ink colours of the old text and
              {"shadow": {"color": "auto"}} its dark colour.
    ink       with gradient: bright | dark | auto (default).  auto looks at the old text: lettering that is darker than
              the background it sits on (the disabled LSPFD* plates: dark teal on teal, no shadow) uses the dark half of
              the old text pixels as ink, bright lettering (live plates) the bright half.
    anchor_box  [x0, y0, x1, y1] relative to the bbox = the box used for alignment and vertical centring instead of the
              detected old-text box (name plates: a fixed baseline and left margin whatever the old English glyphs were,
              e.g. [1, 0, 100, 12] = left margin 1 px, vertically centred in the 12 px plate).  The erase still covers
              every detected pixel.  Single-label regions only.
    space     width of a blank in px (default: half the font height; the game's own space glyph is very wide).

  in-painting (erasing)
    fill      row (default with rowbg): average of the nearest unmasked pixels left/right on the row (gradients).
              texture (default otherwise): mirror of the rows above/below inside the bbox, else the nearest unmasked pixel of the column, else a pseudo-random pick among nearby unmasked pixels (stone panels).
              htexture: ping-pong copy of the pixels left/right on the row (banners with horizontal grain).
              vlerp: interpolation between the nearest unmasked pixels above/below (smooth logos, e.g. the briefing cards).
    pad       context pixels around the bbox the in-painting may read (default 3; never modified).

Names rules: {"glob": "...", "names": "mechs", <any field above>}: text = names_map[text_guess] with text_guess
from localization/en/art.json; a name missing from the map skips the file and is listed in the report.
names_map.json is flat {"ATLAS-A": "..."} or grouped {"mechs": {"ATLAS-A": "..."}}.

Report (stdout): detection per region (mode, colours, old text box, font, ink colour), per-group counts, labels
that do not fit (Korean wider than the bbox), blank glyphs, warnings.  Exit code 1 if the verification fails.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import struct
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mcg_fnt  # noqa: E402
from loc_fst import FST  # noqa: E402

REPO = HERE.parent
GAME = REPO / "game-source" / "extracted" / "MCX"
FST_PATH = GAME / "ART.FST"
KOR_ROOT = GAME / "lang" / "kor"
FONT_DIR = KOR_ROOT / "data" / "fonts"
KO = REPO / "localization" / "ko"
LABELS = KO / "art_labels.json"
NAMES = KO / "names_map.json"
ART_JSON = REPO / "localization" / "en" / "art.json"
REVIEW_DIR = KO / "art_review"
WORK_DIR = REPO / "game-source" / "work" / "art_orig"

FONT_FILES = {8: "WHITE.FNT", 10: "WHITE10.FNT", 12: "WHITE12.FNT"}
TRANSPARENT = 255


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------- TGA

class TGA:
    """Colour-mapped 8-bit TGA (image type 1 = raw, 9 = RLE).  `rows` holds the pixels top-down whatever the
    file's orientation; to_bytes() puts them back in file order.  Everything else is kept verbatim."""

    def __init__(self, data: bytes):
        self.raw = bytes(data)
        d = self.raw
        if len(d) < 18:
            raise ValueError("file too short for a TGA header")
        idlen, cmtype, imtype = d[0], d[1], d[2]
        cmstart, cmlen, cmbits = struct.unpack_from("<HHB", d, 3)
        self.xorg, self.yorg, self.w, self.h = struct.unpack_from("<HHHH", d, 8)
        bpp, desc = d[16], d[17]
        if imtype not in (1, 9) or cmtype != 1 or bpp != 8:
            raise ValueError("not an 8-bit colour-mapped TGA (type %d, cmtype %d, bpp %d)" % (imtype, cmtype, bpp))
        self.imtype, self.desc = imtype, desc
        self.top_down = bool(desc & 0x20)
        if desc & 0x10:
            raise ValueError("right-to-left TGA is not supported")
        off = 18 + idlen
        self.head = d[:off]                         # header + image ID, verbatim
        cmbytes = cmlen * ((cmbits + 7) // 8)
        self.cmap = d[off:off + cmbytes]            # colour map, verbatim
        off += cmbytes
        n = self.w * self.h
        if imtype == 1:
            pix = d[off:off + n]
            end = off + n
        else:
            pix, end = self._rle_decode(d, off, n)
        if len(pix) != n:
            raise ValueError("pixel data truncated")
        self.trailer = d[end:]                      # anything after the pixels (footer), verbatim
        rows = [bytearray(pix[y * self.w:(y + 1) * self.w]) for y in range(self.h)]
        if not self.top_down:
            rows.reverse()
        self.rows = rows
        self.palette = self._palette(cmstart, cmlen, cmbits)

    @staticmethod
    def _rle_decode(d, off, n):
        out = bytearray()
        while len(out) < n:
            p = d[off]
            off += 1
            cnt = (p & 0x7F) + 1
            if p & 0x80:
                out += d[off:off + 1] * cnt
                off += 1
            else:
                out += d[off:off + cnt]
                off += cnt
        return bytes(out[:n]), off

    def _rle_encode(self, flat):
        out = bytearray()
        for y in range(self.h):
            row = flat[y * self.w:(y + 1) * self.w]
            i = 0
            while i < len(row):
                j = i
                while j + 1 < len(row) and row[j + 1] == row[i] and j - i < 127:
                    j += 1
                if j > i:
                    out += bytes([0x80 | (j - i)]) + bytes([row[i]])
                    i = j + 1
                else:
                    k = i + 1
                    while k < len(row) and k - i < 128 and not (k + 1 < len(row) and row[k] == row[k + 1]):
                        k += 1
                    out += bytes([k - i - 1]) + bytes(row[i:k])
                    i = k
        return bytes(out)

    def _palette(self, cmstart, cmlen, cmbits):
        pal = [(0, 0, 0)] * 256
        bs = (cmbits + 7) // 8
        for i in range(cmlen):
            e = self.cmap[i * bs:(i + 1) * bs]
            if bs >= 3:
                pal[(cmstart + i) % 256] = (e[2], e[1], e[0])
            elif bs == 2:
                v = e[0] | (e[1] << 8)
                pal[(cmstart + i) % 256] = (((v >> 10) & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, (v & 31) * 255 // 31)
        return pal

    def to_bytes(self) -> bytes:
        rows = list(self.rows)
        if not self.top_down:
            rows.reverse()
        flat = b"".join(bytes(r) for r in rows)
        pix = flat if self.imtype == 1 else self._rle_encode(flat)
        return bytes(self.head) + bytes(self.cmap) + pix + bytes(self.trailer)

    def copy_rows(self):
        return [bytearray(r) for r in self.rows]


def rgb_of(tga, idx):
    return tga.palette[idx]


def pil_image(tga, rows=None):
    from PIL import Image
    rows = tga.rows if rows is None else rows
    im = Image.frombytes("P", (tga.w, tga.h), b"".join(bytes(r) for r in rows))
    flat = []
    for r, g, b in tga.palette:
        flat += [r, g, b]
    im.putpalette(flat)
    return im.convert("RGB")


# ----------------------------------------------------------------------------------------------- fonts

_FONTS = {}


def get_font(size):
    if size not in _FONTS:
        _FONTS[size] = mcg_fnt.read_fnt(FONT_DIR / FONT_FILES[size])
    return _FONTS[size]


def render(text, size, space=None):
    """-> (mask rows [list of bytearray 0/1], ink_w, ink_h, missing) with the blank columns/rows trimmed.
    `missing` lists characters whose glyph is blank (not in the font) although they are not spaces.
    The game's space glyph is wide (10 px in the 12 px font); `space` (default: half the font height) replaces it."""
    font = get_font(size)
    space = size // 2 if space is None else space
    idx = mcg_fnt.text_to_indices(text, font.count)
    chars = list(text)
    h = font.height
    rows = [bytearray() for _ in range(h)]
    for gi in idx:
        if gi == 32:
            for y in range(h):
                rows[y] += bytes([mcg_fnt.TRANSPARENT]) * space
            continue
        g = font.glyphs[gi] if gi < font.count else mcg_fnt.Glyph(0, b"")
        for y in range(h):
            rows[y] += g.pixels[y * g.width:(y + 1) * g.width]
    w = len(rows[0])
    mask = [bytearray(1 if v != mcg_fnt.TRANSPARENT else 0 for v in r) for r in rows]
    missing = []
    if len(idx) == len(chars):
        for ch, gi in zip(chars, idx):
            if not ch.isspace() and gi < font.count and not any(v != mcg_fnt.TRANSPARENT for v in font.glyphs[gi].pixels):
                missing.append(ch)
    cols = [x for x in range(w) if any(mask[y][x] for y in range(h))]
    ys = [y for y in range(h) if any(mask[y])]
    if not cols:
        return [], 0, 0, missing
    x0, x1, y0, y1 = cols[0], cols[-1] + 1, ys[0], ys[-1] + 1
    return [bytearray(mask[y][x0:x1]) for y in range(y0, y1)], x1 - x0, y1 - y0, missing


# ----------------------------------------------------------------------------------------------- geometry

def rot_cw(rows):
    h, w = len(rows), len(rows[0])
    return [bytearray(rows[h - 1 - j][i] for j in range(h)) for i in range(w)]


def rot_ccw(rows):
    h, w = len(rows), len(rows[0])
    return [bytearray(rows[j][w - 1 - i] for j in range(h)) for i in range(w)]


def rotate_rows(rows, deg):
    """rotate `rows` by deg degrees clockwise (deg in 0, 90, 180, 270, -90)"""
    deg %= 360
    for _ in range(deg // 90):
        rows = rot_cw(rows)
    return rows


# ----------------------------------------------------------------------------------------------- detection

def row_background(V, margin):
    """Per-row background index learned from the `margin` columns at both ends of every row.
    Returns (bg list, fraction of rows whose margin pixels are all the same index)."""
    h, w = len(V), len(V[0])
    m = max(1, min(margin, w // 4))
    bg, ok = [], 0
    for y in range(h):
        edge = list(V[y][:m]) + list(V[y][w - m:])
        c = Counter(edge)
        idx, n = c.most_common(1)[0]
        bg.append(idx)
        if n == len(edge):
            ok += 1
    return bg, ok / h


def luma(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def detect(V, ring_hist, p, palette=None):
    """Find the old text pixels in view V.  Returns (mask rows of 0/1, info dict)."""
    h, w = len(V), len(V[0])
    mode = p.get("mode", "auto")
    info = {}
    if p.get("luma_max") is not None and palette is not None:
        lx = p["luma_max"]
        mask = [bytearray(1 if (V[y][x] != TRANSPARENT and luma(palette[V[y][x]]) <= lx) else 0 for x in range(w)) for y in range(h)]
        soft = p.get("luma_soft")
        if soft is not None:        # anti-aliased fringe: 8-neighbours that are at most `soft` bright
            for _ in range(p.get("grow", 1)):
                new = [bytearray(r) for r in mask]
                for y in range(h):
                    for x in range(w):
                        if mask[y][x]:
                            for dy in (-1, 0, 1):
                                for dx in (-1, 0, 1):
                                    yy, xx = y + dy, x + dx
                                    if 0 <= yy < h and 0 <= xx < w and V[yy][xx] != TRANSPARENT and luma(palette[V[yy][xx]]) <= soft:
                                        new[yy][xx] = 1
                mask = new
        info.update(mode="luma_max", luma_max=lx, luma_soft=soft)
        p = dict(p, grow=0)
    elif p.get("luma_min") is not None and palette is not None:
        lm = p["luma_min"]
        mask = [bytearray(1 if (V[y][x] != TRANSPARENT and luma(palette[V[y][x]]) >= lm) else 0 for x in range(w)) for y in range(h)]
        soft = p.get("luma_soft")
        if soft is not None:        # grow into 8-neighbours that are at least `soft` bright (anti-aliased edge)
            for _ in range(p.get("grow", 1)):
                new = [bytearray(r) for r in mask]
                for y in range(h):
                    for x in range(w):
                        if mask[y][x]:
                            for dy in (-1, 0, 1):
                                for dx in (-1, 0, 1):
                                    yy, xx = y + dy, x + dx
                                    if 0 <= yy < h and 0 <= xx < w and V[yy][xx] != TRANSPARENT and luma(palette[V[yy][xx]]) >= soft:
                                        new[yy][xx] = 1
                mask = new
        info.update(mode="luma", luma_min=lm, luma_soft=soft)
        p = dict(p, grow=0)
    elif p.get("colors") is not None:
        textset = set(p["colors"])
        mask = [bytearray(1 if V[y][x] in textset else 0 for x in range(w)) for y in range(h)]
        info.update(mode="colors", colors=sorted(textset))
    elif p.get("bg") is not None:
        bgset = set(p["bg"])
        mask = [bytearray(1 if V[y][x] not in bgset else 0 for x in range(w)) for y in range(h)]
        info.update(mode="bg", bg=sorted(bgset))
    else:
        rbg, frac = row_background(V, p.get("margin", 3))
        if mode == "rowbg" or (mode == "auto" and frac >= 0.8):
            mask = [bytearray(1 if V[y][x] != rbg[y] else 0 for x in range(w)) for y in range(h)]
            info.update(mode="rowbg", uniform_rows="%.0f%%" % (100 * frac))
        else:
            hist = Counter(v for r in V for v in r)
            tol = p.get("ring_tol", 0.02)
            textset = {i for i, c in hist.items() if c >= p.get("min_count", 2) and ring_hist.get(i, 0) <= tol * c}
            textset.discard(TRANSPARENT)
            mask = [bytearray(1 if V[y][x] in textset else 0 for x in range(w)) for y in range(h)]
            info.update(mode="set", colors=sorted(textset), uniform_rows="%.0f%%" % (100 * frac))
    for ex in p.get("exclude", []):
        for y in range(h):
            for x in range(w):
                if V[y][x] == ex:
                    mask[y][x] = 0
    grow = p.get("grow", 0)
    for _ in range(grow):
        new = [bytearray(r) for r in mask]
        for y in range(h):
            for x in range(w):
                if mask[y][x]:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < h and 0 <= xx < w and V[yy][xx] != TRANSPARENT:
                                new[yy][xx] = 1
        mask = new
    return mask, info


def split_lines(mask, gap=0):
    """Row runs of the mask -> list of (y0, y1_exclusive); runs separated by <= gap empty rows are merged."""
    h = len(mask)
    rows = [y for y in range(h) if any(mask[y])]
    runs = []
    for y in rows:
        if runs and y - runs[-1][1] <= gap + 1:
            runs[-1][1] = y + 1
        else:
            runs.append([y, y + 1])
    return [tuple(r) for r in runs]


def mask_bbox(mask, y0, y1):
    xs = [x for y in range(y0, y1) for x in range(len(mask[0])) if mask[y][x]]
    return (min(xs), y0, max(xs) + 1, y1) if xs else None


def inpaint(V, mask, palette, texture=False, htexture=False, ctx_lo=0, ctx_hi=None, ylo=0, yhi=None, vlerp=False):
    """Replace every masked pixel by the nearest unmasked pixels on its row (left/right; averaged in RGB and
    mapped back to the nearest palette index in use when they differ); rows without any background fall back to
    the nearest unmasked pixel above/below.  texture=True (noisy backgrounds): runs longer than 2 px take the
    mirror image of the rows above/below the same column instead (keeps the grain, avoids flat streaks)."""
    h, w = len(V), len(V[0])
    ctx_hi = w if ctx_hi is None else ctx_hi
    yhi = h if yhi is None else yhi
    pools = {}
    lerp_cache = {}

    def pool_pick(x, y):
        # deterministic pseudo-random pick among the unmasked pixels of the nearby rows (inside the region only)
        if y not in pools:
            pools[y] = [V[yy][xx] for yy in range(max(ylo, y - 6), min(yhi, y + 7)) for xx in range(ctx_lo, ctx_hi)
                        if not mask[yy][xx] and V[yy][xx] != TRANSPARENT]
        pl = pools[y]
        return pl[((x * 73856093) ^ (y * 19349663)) % len(pl)] if pl else None
    used = sorted({V[y][x] for y in range(h) for x in range(w) if not mask[y][x] and V[y][x] != TRANSPARENT})
    cache = {}

    def mix(a, b):
        if a == b:
            return a
        key = (a, b)
        if key not in cache:
            ra, rb = palette[a], palette[b]
            tgt = tuple((ra[i] + rb[i]) / 2 for i in range(3))
            cache[key] = min(used or [a], key=lambda i: sum((palette[i][k] - tgt[k]) ** 2 for k in range(3)))
        return cache[key]

    out = [bytearray(r) for r in V]
    missing = 0
    for y in range(h):
        x = 0
        while x < w:
            if not mask[y][x]:
                x += 1
                continue
            xb = x
            while xb < w and mask[y][xb]:
                xb += 1
            left = V[y][x - 1] if x > 0 else None
            right = V[y][xb] if xb < w else None
            if htexture and xb - x > 2:
                # ping-pong copy of the unmasked pixels left (else right) of the run on the same row: keeps the
                # horizontal grain of banner/paper textures
                ctx = []
                xl = x - 1
                while xl >= ctx_lo and not mask[y][xl] and len(ctx) < 24:
                    ctx.append(V[y][xl])
                    xl -= 1
                if len(ctx) < 3:
                    ctx = []
                    xr = xb
                    while xr < ctx_hi and not mask[y][xr] and len(ctx) < 24:
                        ctx.append(V[y][xr])
                        xr += 1
                if len(ctx) >= 3:
                    period = 2 * len(ctx)
                    for i, xx in enumerate(range(x, xb)):
                        j = i % period
                        out[y][xx] = ctx[j] if j < len(ctx) else ctx[period - 1 - j]
                    x = xb
                    continue
            for xx in range(x, xb):
                if vlerp:
                    # vertical interpolation between the nearest unmasked pixels above and below (smooth logos / gradients)
                    up = next((yy for yy in range(y - 1, ylo - 1, -1) if not mask[yy][xx]), None)
                    dn = next((yy for yy in range(y + 1, yhi) if not mask[yy][xx]), None)
                    if up is not None and dn is not None:
                        t = (y - up) / float(dn - up)
                        ca, cb = palette[V[up][xx]], palette[V[dn][xx]]
                        tgt = tuple(ca[k] + (cb[k] - ca[k]) * t for k in range(3))
                        key = tuple(int(round(v / 4.0)) for v in tgt)
                        if key not in lerp_cache:
                            lerp_cache[key] = min(used or [V[up][xx]], key=lambda i: sum((palette[i][k] - tgt[k]) ** 2 for k in range(3)))
                        out[y][xx] = lerp_cache[key]
                        continue
                    if up is not None or dn is not None:
                        out[y][xx] = V[up if up is not None else dn][xx]
                        continue
                if texture and xb - x > 2:
                    # mirror the unmasked rows above/below this column's masked run (keeps the 2-D grain); only rows
                    # inside the region are used, otherwise a pseudo-random pick among nearby unmasked pixels
                    ya = y
                    while ya > ylo and mask[ya - 1][xx]:
                        ya -= 1
                    yb = y + 1
                    while yb < yhi and mask[yb][xx]:
                        yb += 1
                    up_src, dn_src = ya - 1 - (y - ya), yb + (yb - 1 - y)
                    cands = [up_src, dn_src] if (y - ya) <= (yb - 1 - y) else [dn_src, up_src]
                    src = next((c for c in cands if ylo <= c < yhi and not mask[c][xx]), None)
                    if src is not None:
                        out[y][xx] = V[src][xx]
                        continue
                    up = next((yy for yy in range(y - 1, ylo - 1, -1) if not mask[yy][xx]), None)
                    dn = next((yy for yy in range(y + 1, yhi) if not mask[yy][xx]), None)
                    if up is not None or dn is not None:
                        near = up if (dn is None or (up is not None and y - up <= dn - y)) else dn
                        out[y][xx] = V[near][xx]
                        continue
                    pv = pool_pick(xx, y)
                    if pv is not None:
                        out[y][xx] = pv
                        continue
                if left is not None and right is not None:
                    out[y][xx] = mix(left, right)
                elif left is not None or right is not None:
                    out[y][xx] = left if left is not None else right
                else:
                    up = next((yy for yy in range(y - 1, -1, -1) if not mask[yy][xx]), None)
                    dn = next((yy for yy in range(y + 1, h) if not mask[yy][xx]), None)
                    cand = [V[yy][xx] for yy in (up, dn) if yy is not None]
                    if cand:
                        out[y][xx] = mix(cand[0], cand[-1])
                    else:
                        missing += 1
            x = xb
    return out, missing


# ----------------------------------------------------------------------------------------------- region processing

def pick_size(h):
    return 8 if h <= 8 else 10 if h <= 10 else 12


def auto_align(lines_bbox, W):
    """lines_bbox: list of (x0, y0, x1, y1) of the old text lines inside a view of width W."""
    if len(lines_bbox) > 1:
        lefts = [b[0] for b in lines_bbox]
        rights = [b[2] for b in lines_bbox]
        if max(lefts) - min(lefts) <= 1:
            return "left"
        if max(rights) - min(rights) <= 1:
            return "right"
    b = lines_bbox[0]
    cx = (b[0] + b[2]) / 2
    return "center" if abs(cx - W / 2) <= max(2.0, 0.03 * W) else "left"


def ink_colour(counts, clean, a, b, mask, palette, vw):
    """Palette index of the old text: among the indices that are frequent in the old text (>= 35% of the most
    frequent one) the one farthest from the background that was under the text (anti-aliasing blends are
    often more numerous than the solid ink colour)."""
    if not counts:
        return 31
    top = counts.most_common(1)[0][1]
    cand = [i for i, n in counts.items() if n >= 0.35 * top]
    under = [palette[clean[y][x]] for y in range(a, b) for x in range(vw) if mask[y][x]]
    mean = [sum(c[k] for c in under) / len(under) for k in range(3)]
    return max(cand, key=lambda i: (sum((palette[i][k] - mean[k]) ** 2 for k in range(3)), counts[i]))


class Result:
    def __init__(self, name):
        self.name = name
        self.regions = []      # list of dict(info) per region
        self.warnings = []
        self.nofit = []
        self.changed_boxes = []
        self.missing_glyphs = []
        self.fits = []         # (room left in px, tag, text, font)


def process_region(img_rows, palette, W, H, reg, res, tag):
    """Relabel one region of the image (img_rows is modified in place).  `reg` = fully merged parameter dict."""
    if reg.get("keep"):
        return
    bbox = reg.get("bbox") or [0, 0, W, H]
    x0, y0, x1, y1 = bbox
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    rot = reg.get("rotate", 0) or 0
    # padded copy of the region: the pad (never detected/drawn) gives the in-painting real neighbours outside the bbox
    pad = reg.get("pad", 3)
    qx0, qy0, qx1, qy1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    subp = [bytearray(img_rows[y][qx0:qx1]) for y in range(qy0, qy1)]
    flag = [bytearray(1 if (x0 <= x < x1 and y0 <= y < y1) else 0 for x in range(qx0, qx1)) for y in range(qy0, qy1)]
    VP = rotate_rows(subp, -rot)             # horizontal view incl. pad
    FP = rotate_rows(flag, -rot)
    rows_c = [i for i, r in enumerate(FP) if any(r)]
    cols_c = [i for i in range(len(FP[0])) if any(r[i] for r in FP)]
    cy0, cy1, cx0, cx1 = rows_c[0], rows_c[-1] + 1, cols_c[0], cols_c[-1] + 1
    V = [bytearray(r[cx0:cx1]) for r in VP[cy0:cy1]]          # the view the detection works on
    vh, vw = len(V), len(V[0])
    # ring histogram: pixels around the bbox in image space
    ring = reg.get("ring", 6)
    rh = Counter()
    for y in range(max(0, y0 - ring), min(H, y1 + ring)):
        for x in range(max(0, x0 - ring), min(W, x1 + ring)):
            if not (x0 <= x < x1 and y0 <= y < y1):
                rh[img_rows[y][x]] += 1
    mask, info = detect(V, rh, reg, palette)
    lines = split_lines(mask, reg.get("line_gap", 0))
    texts = reg.get("lines") if reg.get("lines") is not None else [reg.get("text")]
    if not lines:
        res.warnings.append("%s: no text detected %s" % (tag, info))
        return
    if reg.get("lines") is None and len(lines) > 1:
        # single label but several detected lines: treat the whole region as one line
        lines = [(lines[0][0], lines[-1][1])]
    if len(lines) != len(texts):
        res.warnings.append("%s: detected %d text line(s) %s but %d label(s)" % (tag, len(lines), lines, len(texts)))
        return
    anchor = reg.get("anchor_box")
    anchored = bool(anchor and len(lines) == 1 and len(texts) == 1)
    if anchored:
        # fixed alignment box (name plates): the old text rows are widened to the anchor rows, the x range is replaced
        ay0, ay1 = max(0, min(vh, anchor[1])), max(0, min(vh, anchor[3]))
        lines = [(min(ay0, lines[0][0]), max(ay1, lines[0][1]))]
        boxes = [(anchor[0], ay0, anchor[2], ay1)]
    else:
        boxes = [mask_bbox(mask, a, b) for a, b in lines]
    # text colour: dominant index of the old text pixels (per line)
    cols = []
    for (a, b) in lines:
        c = Counter(V[y][x] for y in range(a, b) for x in range(vw) if mask[y][x])
        cols.append(c)
    # pixels to erase = mask pixels belonging to the lines being replaced
    erase = [bytearray(len(VP[0])) for _ in range(len(VP))]
    for (a, b), t in zip(lines, texts):
        if t is None:
            continue
        for y in range(a, b):
            for x in range(vw):
                erase[y + cy0][x + cx0] = mask[y][x]
    if not any(any(r) for r in erase):
        return
    fill = reg.get("fill")
    clean, miss = inpaint(VP, erase, palette, texture=(info.get("mode") != "rowbg" and fill not in ("row", "htexture", "vlerp")) or fill == "texture",
                          htexture=(fill == "htexture"), ctx_lo=cx0, ctx_hi=cx1, ylo=cy0, yhi=cy1, vlerp=(fill == "vlerp"))
    if miss:
        res.warnings.append("%s: %d pixel(s) could not be in-painted" % (tag, miss))
    clean_c = [bytearray(r[cx0:cx1]) for r in clean[cy0:cy1]]
    align = reg.get("align", "auto")
    if align == "auto":
        align = auto_align([b for b, t in zip(boxes, texts) if t is not None] or boxes, vw)
    shadow = reg.get("shadow")
    if isinstance(shadow, (int, str)) and shadow is not False:
        shadow = {"color": shadow}
    if shadow and shadow.get("outline"):
        offsets = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
    else:
        offsets = [tuple(o) for o in shadow.get("offsets", [[1, 1]])] if shadow else []
    lp, rp = max([-o[0] for o in offsets] + [0]), max([o[0] for o in offsets] + [0])      # shadow/outline padding
    tp, bp = max([-o[1] for o in offsets] + [0]), max([o[1] for o in offsets] + [0])
    ex_w, ex_h = lp + rp, tp + bp
    out = clean
    desc = []

    def put(X, Y, v):
        if 0 <= X < vw and 0 <= Y < vh:
            out[Y + cy0][X + cx0] = v

    for li, ((a, b), box, t, c) in enumerate(zip(lines, boxes, texts, cols)):
        if t is None:
            continue
        old_h = b - a
        forced = reg.get("font")
        size = forced or pick_size(old_h)
        avail_l, avail_r = 0, vw
        tries = [size] if forced else [s for s in (12, 10, 8) if s <= size]
        chosen = None
        for s in tries:
            mk, iw, ih, missing = render(t, s, reg.get("space"))
            if iw + ex_w <= avail_r - avail_l and ih + ex_h <= vh:
                chosen = (s, mk, iw, ih, missing)
                break
        shrunk = False
        if chosen is None:
            s = tries[-1]
            mk, iw, ih, missing = render(t, s, reg.get("space"))
            chosen = (s, mk, iw, ih, missing)
            res.nofit.append("%s line %d '%s': %d px wide at %d px font, room %d px" % (tag, li + 1, t, iw + ex_w, s, avail_r - avail_l))
        else:
            shrunk = chosen[0] != size
        s, mk, iw, ih, missing = chosen
        res.fits.append((vw - iw - ex_w, tag, t, s))
        if missing:
            res.missing_glyphs.append("%s '%s': no glyph for %s" % (tag, t, "".join(missing)))
        if not mk:
            res.warnings.append("%s: empty label '%s'" % (tag, t))
            continue
        iw_e, ih_e = iw + ex_w, ih + ex_h          # extents including the drop shadow / outline
        if align == "left":
            px = box[0]
        elif align == "right":
            px = box[2] - iw_e
        else:
            px = int(round((box[0] + box[2]) / 2 - iw_e / 2))
        py = a + (old_h - ih_e) // 2
        px += lp + reg.get("dx", 0)
        py += tp + reg.get("dy", 0)
        py = max(tp, min(py, vh - ih - bp)) if vh >= ih + ex_h else py        # keep the label inside the region
        if px - lp < 0 or px + iw + rp > vw:
            if not any(n.startswith("%s line %d" % (tag, li + 1)) for n in res.nofit):
                res.nofit.append("%s line %d '%s': needs x %d..%d, room 0..%d" % (tag, li + 1, t, px - lp, px + iw + rp, vw))
        color = reg.get("color")
        if color is None or color == "auto":
            color = ink_colour(c, clean_c, a, b, mask, palette, vw)
        row_colors = None
        sc_auto = None
        if reg.get("gradient"):
            # vertical gradient lettering (name plates): ink = the bright half of the old text pixels (the dark half for
            # lettering darker than its background, see `ink`); every row of the old ink gives the colour of the matching
            # row of the new text; the other half supplies the shadow colour
            pxs = [(y, x) for y in range(a, b) for x in range(vw) if mask[y][x]]
            ls = [luma(palette[V[y][x]]) for y, x in pxs]
            lo, hi = min(ls), max(ls)
            mid = lo + 0.5 * (hi - lo)
            ink_mode = reg.get("ink", "auto")
            if ink_mode == "auto":
                under = [luma(palette[clean_c[y][x]]) for y, x in pxs]
                ink_mode = "dark" if sum(ls) / len(ls) < sum(under) / len(under) else "bright"
            rows_c = defaultdict(Counter)
            dark = Counter()
            for (y, x), l in zip(pxs, ls):
                if (l <= mid) if ink_mode == "dark" else (l >= mid):
                    rows_c[y][V[y][x]] += 1
                else:
                    dark[V[y][x]] += 1
            if rows_c:
                r0, r1 = min(rows_c), max(rows_c)
                gcols = []
                for y in range(r0, r1 + 1):
                    gcols.append(rows_c[y].most_common(1)[0][0] if rows_c.get(y) else (gcols[-1] if gcols else color))
                row_colors = [gcols[min(len(gcols) - 1, int(yy * len(gcols) / ih))] for yy in range(ih)]
                color = gcols[len(gcols) // 2]
            sc_auto = dark.most_common(1)[0][0] if dark else None
        if shadow:
            sc = shadow.get("color", "auto")
            if sc == "auto" or sc is None:
                if sc_auto is not None:
                    sc = sc_auto
                else:
                    others = [(n, i) for i, n in c.items() if i != color]
                    sc = max(others)[1] if others else 16
            for yy in range(ih):
                for xx in range(iw):
                    if mk[yy][xx]:
                        for sdx, sdy in offsets:
                            put(px + xx + sdx, py + yy + sdy, sc)
        for yy in range(ih):
            for xx in range(iw):
                if mk[yy][xx]:
                    put(px + xx, py + yy, row_colors[yy] if row_colors else color)
        topc = c.most_common(3)
        desc.append("line%d %s %dx%d@%d,%d font %d%s %s col %s (old: %s) text '%s'" % (
            li + 1, "anchor" if anchored else "old", box[2] - box[0], old_h, box[0], a, s, "*" if shrunk else "", align, color,
            ",".join("%d:%d" % kv for kv in topc), t))
    back = rotate_rows(out, rot)
    for yy in range(qy1 - qy0):
        img_rows[qy0 + yy][qx0:qx1] = back[yy]
    res.changed_boxes.append((x0, y0, x1, y1))
    res.regions.append({"info": info, "lines": desc, "bbox": [x0, y0, x1, y1]})


# ----------------------------------------------------------------------------------------------- label file

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def glob_match(pattern, name):
    return fnmatch.fnmatchcase(name.lower(), pattern.lower())


def norm(name):
    return name.replace("\\", "/")


class Labels:
    """The expanded label file: internal path (forward slashes, as in the FST) -> merged spec."""

    def __init__(self, path, fst_names, names_map, art_guess):
        self.path = path
        self.data = load_json(path)
        self.specs = OrderedDict()
        self.missing_names = []
        self.unmatched = []
        names = [norm(n) for n in fst_names]
        for key, spec in self.data.items():
            if key.startswith("_") or key == "rules":
                continue
            hit = [n for n in names if glob_match(key, n)]
            if not hit:
                self.unmatched.append(key)
            for n in hit:
                self.specs.setdefault(n, {}).update(json.loads(json.dumps(spec)))
        for rule in self.data.get("rules", []):
            glob = rule["glob"]
            table = names_map.get(rule.get("names", ""), names_map) if isinstance(names_map.get(rule.get("names", "")), dict) else names_map
            hit = [n for n in names if glob_match(glob, n)]
            if not hit:
                self.unmatched.append(glob)
            for n in hit:
                guess = art_guess.get(n.lower(), "")
                if guess not in table:
                    self.missing_names.append((n, guess))
                    continue
                spec = {k: v for k, v in rule.items() if k not in ("glob", "names")}
                spec["text"] = table[guess]
                self.specs.setdefault(n, {}).update(spec)

    def files(self):
        return list(self.specs)


def regions_of(spec):
    base = {k: v for k, v in spec.items() if k not in ("regions", "group", "note")}
    if spec.get("regions"):
        out = []
        for r in spec["regions"]:
            m = dict(base)
            for k in ("text", "lines"):
                m.pop(k, None)
            m.update(r)
            out.append(m)
        return out
    return [base]


# ----------------------------------------------------------------------------------------------- source access

class Source:
    def __init__(self, work_dir):
        self.fst = FST(FST_PATH)
        self.index = {norm(n).lower(): (n, i) for n, i in self.fst.items()}
        self.work = Path(work_dir)

    def names(self):
        return [n for n, _ in self.fst.items()]

    def internal(self, name):
        return self.index[norm(name).lower()][0]

    def read(self, name):
        n, i = self.index[norm(name).lower()]
        w = self.work / norm(n)
        if w.exists():
            return w.read_bytes()
        return self.fst.read(i)


# ----------------------------------------------------------------------------------------------- verification

def verify(orig: TGA, new_bytes: bytes, out_rows_expected):
    """Re-read the output with this reader and with Pillow; everything except the pixels must be identical."""
    chk = TGA(new_bytes)
    problems = []
    if chk.head != orig.head:
        problems.append("header/ID differs")
    if chk.cmap != orig.cmap:
        problems.append("colour map differs")
    if chk.trailer != orig.trailer:
        problems.append("trailer differs")
    if (chk.w, chk.h, chk.imtype, chk.desc) != (orig.w, orig.h, orig.imtype, orig.desc):
        problems.append("geometry/type/descriptor differs")
    if [bytes(r) for r in chk.rows] != [bytes(r) for r in out_rows_expected]:
        problems.append("pixel round trip differs")
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(new_bytes))
        im.load()
        if im.size != (orig.w, orig.h) or im.mode != "P":
            problems.append("Pillow size/mode %s %s" % (im.size, im.mode))
        elif bytes(im.tobytes()) != b"".join(bytes(r) for r in out_rows_expected):
            problems.append("Pillow pixels differ")
    except Exception as e:  # pragma: no cover
        problems.append("Pillow: %s" % e)
    return problems


# ----------------------------------------------------------------------------------------------- review sheets

def find_font(size):
    from PIL import ImageFont
    for cand in ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(cand, size)
        except OSError:
            continue
    return ImageFont.load_default()


def crop_box(res, w, h):
    if w * h <= 40000 or not res.changed_boxes:
        return (0, 0, w, h)
    xs0 = min(b[0] for b in res.changed_boxes)
    ys0 = min(b[1] for b in res.changed_boxes)
    xs1 = max(b[2] for b in res.changed_boxes)
    ys1 = max(b[3] for b in res.changed_boxes)
    pad = 6
    return (max(0, xs0 - pad), max(0, ys0 - pad), min(w, xs1 + pad), min(h, ys1 + pad))


def build_review(items, out_dir, max_h=2600, width=1800, scale=2, wipe_all=True):
    """items: list of dict(group, name, orig TGA, rows (result), result Result).  One PNG (or several) per group.
    wipe_all=True deletes every old sheet first; False (used with --only) only the sheets of the groups written now."""
    import re
    from PIL import Image, ImageDraw
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = OrderedDict()
    for it in items:
        groups.setdefault(it["group"], []).append(it)
    for p in out_dir.glob("*.png"):
        if wipe_all or any(p.name == g + ".png" or re.fullmatch(re.escape(g) + r"_\d+\.png", p.name) for g in groups):
            p.unlink()
    f = find_font(12)
    written = []
    for group, its in groups.items():
        cells = []
        for it in its:
            t = it["tga"]
            box = crop_box(it["res"], t.w, t.h)
            a = pil_image(t).crop(box)
            b = pil_image(t, it["rows"]).crop(box)
            a = a.resize((a.width * scale, a.height * scale), Image.NEAREST)
            b = b.resize((b.width * scale, b.height * scale), Image.NEAREST)
            flag = " NOFIT" if it["res"].nofit else ""
            label = "%s %dx%d%s" % (Path(it["name"]).name, t.w, t.h, flag)
            if box != (0, 0, t.w, t.h):
                label += " crop %d,%d" % (box[0], box[1])
            cw = max(a.width, 8 * len(label) + 4)
            cells.append((label, a, b, cw, bool(it["res"].nofit)))
        # shelf packing
        shelves, cur, curw = [], [], 0
        for c in cells:
            if cur and curw + c[3] + 10 > width:
                shelves.append(cur)
                cur, curw = [], 0
            cur.append(c)
            curw += c[3] + 10
        if cur:
            shelves.append(cur)
        # split into parts by height
        parts, part, ph = [], [], 24
        for sh in shelves:
            sh_h = max(c[1].height * 2 + 38 for c in sh)
            if part and ph + sh_h > max_h:
                parts.append(part)
                part, ph = [], 24
            part.append(sh)
            ph += sh_h
        if part:
            parts.append(part)
        for n, part in enumerate(parts, 1):
            H = 24 + sum(max(c[1].height * 2 + 38 for c in sh) for sh in part)
            sheet = Image.new("RGB", (width, H), (40, 40, 48))
            dr = ImageDraw.Draw(sheet)
            dr.text((8, 4), "%s  (%d images; each cell: label / ORIGINAL / RESULT at %dx)%s" % (
                group, sum(len(s) for s in part), scale, "  part %d/%d" % (n, len(parts)) if len(parts) > 1 else ""),
                fill=(255, 255, 255), font=f)
            y = 24
            for sh in part:
                x = 8
                sh_h = max(c[1].height * 2 + 38 for c in sh)
                for label, a, b, cw, bad in sh:
                    dr.text((x, y), label, fill=(255, 120, 120) if bad else (220, 220, 160), font=f)
                    sheet.paste(a, (x, y + 16))
                    sheet.paste(b, (x, y + 20 + a.height))
                    dr.rectangle([x - 1, y + 15, x + a.width, y + 16 + a.height], outline=(90, 90, 110))
                    dr.rectangle([x - 1, y + 19 + a.height, x + b.width, y + 20 + a.height + b.height], outline=(110, 150, 110))
                    x += cw + 10
                y += sh_h
            name = group + ("_%d" % n if len(parts) > 1 else "") + ".png"
            sheet.save(out_dir / name)
            written.append(out_dir / name)
    return written


# ----------------------------------------------------------------------------------------------- commands

def art_guess_map():
    if not ART_JSON.exists():
        return {}, {}
    arr = load_json(ART_JSON)
    return {e["file"].lower(): e.get("text_guess", "") for e in arr}, {e["file"].lower(): e.get("sheet", "other") for e in arr}


def cmd_extract(args):
    src = Source(args.work)
    guess, _ = art_guess_map()
    names_map = load_json(args.names) if Path(args.names).exists() else {}
    labels = Labels(args.labels, src.names(), names_map, guess)
    n = 0
    for name in labels.files():
        internal = src.internal(name)
        i = src.index[norm(internal).lower()][1]
        data = src.fst.read(i)
        dst = Path(args.work) / norm(internal)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        n += 1
    print("extracted %d TGA(s) from %s into %s" % (n, FST_PATH, args.work))
    if labels.unmatched:
        print("keys matching no file:", labels.unmatched)


def cmd_info(args):
    src = Source(args.work)
    name = src.internal(args.info[0])
    t = TGA(src.read(name))
    box = [int(v) for v in args.info[1:5]] if len(args.info) >= 5 else [0, 0, t.w, t.h]
    x0, y0, x1, y1 = box
    print("%s  %dx%d  type %d  descriptor 0x%02x (%s)  colour map %d bytes  id %d bytes  trailer %d bytes" % (
        name, t.w, t.h, t.imtype, t.desc, "top-down" if t.top_down else "bottom-up", len(t.cmap), len(t.head) - 18, len(t.trailer)))
    V = [bytearray(t.rows[y][x0:x1]) for y in range(y0, y1)]
    c = Counter(v for r in V for v in r)
    print("palette usage in bbox %s" % box)
    for i, n in c.most_common(30):
        print("  %3d  %-16s %5d" % (i, t.palette[i], n))
    ring = Counter()
    for y in range(max(0, y0 - 6), min(t.h, y1 + 6)):
        for x in range(max(0, x0 - 6), min(t.w, x1 + 6)):
            if not (x0 <= x < x1 and y0 <= y < y1):
                ring[t.rows[y][x]] += 1
    params = {}
    if args.colors:
        params["colors"] = [int(v) for v in args.colors.split(",")]
    if args.bg:
        params["bg"] = [int(v) for v in args.bg.split(",")]
    if args.mode:
        params["mode"] = args.mode
    if args.luma:
        params["luma_min"] = float(args.luma)
        params["luma_soft"] = float(args.luma) * 0.6
    if args.luma_max:
        params["luma_max"] = float(args.luma_max)
    mask, info = detect(V, ring, params, t.palette)
    lines = split_lines(mask)
    print("detected:", info, "lines:", [(a, b, mask_bbox(mask, a, b)) for a, b in lines])
    for a, b in lines:
        cc = Counter(V[y][x] for y in range(a, b) for x in range(len(V[0])) if mask[y][x])
        print("  line %d-%d colours %s" % (a, b, cc.most_common(5)))
    if args.dump:
        for y in range(y0, y1):
            print("%3d " % y + "".join("#" if mask[y - y0][x - x0] else "." for x in range(x0, x1)))


def cmd_run(args):
    src = Source(args.work)
    guess, sheets = art_guess_map()
    names_map = load_json(args.names) if Path(args.names).exists() else {}
    labels = Labels(args.labels, src.names(), names_map, guess)
    out_root = Path(args.out)
    todo = labels.files()
    if args.only:
        todo = [n for n in todo if any(glob_match(p, n) for p in args.only)]
    per_group = Counter()
    items, problems, all_nofit, all_warn, all_missing, report = [], [], [], [], [], []
    all_fits = []
    for name in todo:
        internal = src.internal(name)
        spec = labels.specs[norm(internal)] if norm(internal) in labels.specs else labels.specs[name]
        data = src.read(internal)
        orig = TGA(data)
        rows = orig.copy_rows()
        res = Result(norm(internal))
        regs = regions_of(spec)
        for ri, reg in enumerate(regs):
            process_region(rows, orig.palette, orig.w, orig.h, reg, res, "%s#%d" % (Path(internal.replace("\\", "/")).name, ri + 1))
        group = spec.get("group") or sheets.get(norm(internal).lower(), "other")
        if not res.changed_boxes:
            all_warn += res.warnings
            if not res.warnings:
                all_warn.append("%s: nothing changed" % norm(internal))
            continue
        new = TGA.__new__(TGA)
        new.__dict__.update(orig.__dict__)
        new.rows = rows
        out_bytes = new.to_bytes()
        pr = verify(orig, out_bytes, rows)
        if pr:
            problems.append((norm(internal), pr))
        elif not args.dry_run:
            dst = out_root / norm(internal)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(out_bytes)
        per_group[group] += 1
        all_nofit += res.nofit
        all_fits += res.fits
        all_warn += res.warnings
        all_missing += res.missing_glyphs
        items.append({"group": group, "name": norm(internal), "tga": orig, "rows": rows, "res": res})
        if args.verbose or True:
            print("%s  [%s]" % (norm(internal), group))
            for r in res.regions:
                det = {k: v for k, v in r["info"].items()}
                print("    bbox %s detect %s" % (r["bbox"], det))
                for l in r["lines"]:
                    print("      " + l)
    written = []
    if items and not args.no_review:
        written = build_review(items, Path(args.review), scale=args.scale, wipe_all=not args.only, max_h=args.max_h)
    print()
    print("=" * 70)
    print("processed %d file(s)%s" % (len(items), " (dry run, nothing written)" if args.dry_run else " -> " + str(out_root)))
    for g, n in sorted(per_group.items()):
        print("  %-36s %d" % (g, n))
    if labels.unmatched:
        print("label keys that match no file:", labels.unmatched)
    if labels.missing_names:
        print("names missing from the names map (%d):" % len(labels.missing_names))
        for n, g in labels.missing_names[:args.max_list]:
            print("   %s  text_guess=%r" % (n, g))
        if len(labels.missing_names) > args.max_list:
            print("   ... and %d more (distinct names: %d; --max-list N shows more)" % (
                len(labels.missing_names) - args.max_list, len({g for _, g in labels.missing_names})))
    if all_nofit:
        print("labels that do NOT fit (%d):" % len(all_nofit))
        for s in all_nofit:
            print("   " + s)
    if all_fits:
        tight = sorted(all_fits)[:12]
        print("tightest labels (room left in the bbox, px): " + "; ".join("%s '%s' %d" % (t.split('.')[0], x, r) for r, t, x, _s in tight))
    if all_missing:
        print("labels using characters missing from the Korean font:")
        for s in all_missing:
            print("   " + s)
    if all_warn:
        print("warnings (%d):" % len(all_warn))
        for s in all_warn:
            print("   " + s)
    if problems:
        print("VERIFICATION FAILED:")
        for n, pr in problems:
            print("   %s: %s" % (n, "; ".join(pr)))
        sys.exit(1)
    for p in written:
        print("review sheet:", p)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Replace English text baked into MCG TGAs by Korean text",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--labels", default=str(LABELS))
    ap.add_argument("--names", default=str(NAMES))
    ap.add_argument("--work", default=str(WORK_DIR), help="dir for --extract (and read first if the file is there)")
    ap.add_argument("--out", default=str(KOR_ROOT), help="output root (internal paths are created below it)")
    ap.add_argument("--review", default=str(REVIEW_DIR))
    ap.add_argument("--scale", type=int, default=2, help="review sheet magnification (default 2)")
    ap.add_argument("--max-h", dest="max_h", type=int, default=3000,
                    help="review sheet height in px before a group is split into _1, _2.. (default 3000)")
    ap.add_argument("--extract", action="store_true", help="unpack the TGAs named in the labels file into --work")
    ap.add_argument("--only", action="append", help="glob on the internal path; repeatable")
    ap.add_argument("--info", nargs="+", metavar="NAME [x0 y0 x1 y1]", help="print palette usage + detection for one TGA")
    ap.add_argument("--dump", action="store_true", help="with --info: print the detected mask")
    ap.add_argument("--colors", help="with --info: comma separated text colour indices")
    ap.add_argument("--bg", help="with --info: comma separated background colour indices")
    ap.add_argument("--mode", help="with --info: rowbg | set")
    ap.add_argument("--luma", help="with --info: luma_min threshold")
    ap.add_argument("--luma-max", dest="luma_max", help="with --info: luma_max threshold (dark text)")
    ap.add_argument("--max-list", type=int, default=40, help="how many missing names to list (default 40)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-review", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    utf8_stdout()
    if args.extract:
        return cmd_extract(args)
    if args.info:
        return cmd_info(args)
    return cmd_run(args)


if __name__ == "__main__":
    main()
