#!/usr/bin/env python3
"""Build Korean versions of the MechCommander Gold bitmap fonts from Galmuri.

Usage
-----
    python build_korean_fonts.py --src  <MISC.FST dir with the original *.FNT>
                                 --galmuri <dir with Galmuri7/9/11.ttf (+ .bdf)>
                                 --out  <lang/kor/data/fonts dir>
                                 [--preview <contact-sheet.png>] [--no-verify]

Output FNT layout (count = 256 + 94*94 = 9092)
----------------------------------------------
    index 0..255      original glyphs, unchanged (padded with width-0 glyphs
                      if the original has fewer than 256, truncated if more)
    256 + (L-0xA1)*94 + (T-0xA1)
                      glyph for the EUC-KR byte pair (L, T), L,T in 0xA1..0xFE
Filled cells: KS X 1001 Hangul syllables (rows 0xB0..0xC8, 2350 chars) and the
symbol rows 0xA1..0xA3.  Every other cell points at one shared blank glyph
whose width equals the Hangul advance.

Rendering
---------
Galmuri7 / 9 / 11 are rendered 1-bit with Pillow at their native pixel size
(Pillow ppem 8 / 10 / 12 -- see README-fonts.md: the TTFs' "design size" is
the Hangul advance, i.e. em + 1 px of spacing).  When the .bdf files are next
to the TTFs, every glyph is also compared against the BDF bitmap, which is
the author's exact pixel grid, so any rasteriser difference is caught.

Placement
---------
The Hangul em box (7/9/11 rows) is placed so that its bottom row is one row
below the Latin cap baseline of the font being converted, clamped to the cell.
Drop-shadow fonts (BLUEDRP, YELLDRP) get a copy in the shadow colour at the
detected shadow offset, then the main colour on top.
"""
import argparse
import itertools
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcg_fnt  # noqa: E402
from mcg_fnt import Glyph, Font, TRANSPARENT, KOR_COUNT  # noqa: E402

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

FAMILIES = ["BLKFNT", "BLUE", "GREEN", "GRYFNT", "RED", "WHITE", "YELLOW"]
SIZE_SUFFIX = {8: "", 10: "10", 12: "12"}
EXTRA = ["BLUEDRP", "YELLDRP"]  # 8 px drop-shadow fonts

# font height -> (Galmuri TTF, Pillow pixel size that equals the native grid)
GALMURI = {
    8: ("Galmuri7", 8),
    10: ("Galmuri9", 10),
    12: ("Galmuri11", 12),
}

# KS X 1001 areas to fill: (first lead byte, last lead byte)
SYMBOL_ROWS = (0xA1, 0xA3)
HANGUL_ROWS = (0xB0, 0xC8)

SAMPLE = "메크 커맨더 골드 1280x1024 Mad Cat 출격 준비 완료 ABC abc"


# ---------------------------------------------------------------------------
# Original-font analysis
# ---------------------------------------------------------------------------

def a_to_z(font):
    return [font.glyphs[i] for i in range(ord("A"), ord("Z") + 1)]


def ink_positions(glyph, height, value):
    w = glyph.width
    return {(i % w, i // w) for i, v in enumerate(glyph.pixels) if v == value}


def detect_colors(font):
    """Return (main, shadow, offsets) for the Latin capitals.

    Plain fonts have a single colour -> (colour, None, []).  Drop-shadow fonts
    have two.  For each (main, shadow) assignment we collect every offset d in
    [-2, 2]^2 for which "main shifted by d, minus main" lies inside the shadow
    pixels of every capital; the shadow of these fonts is the union of
    several such shifts (BLUEDRP/YELLDRP use (1,0), (0,1) and (1,1)).  The
    assignment whose offsets reproduce the shadow pixels best wins."""
    counts = Counter()
    for g in a_to_z(font):
        counts.update(v for v in g.pixels if v != TRANSPARENT)
    values = sorted(counts)
    if len(values) == 1:
        return values[0], None, []
    if len(values) != 2:
        raise ValueError("unexpected colour set %r in A..Z" % (values,))
    sets = {v: [ink_positions(g, font.height, v) for g in a_to_z(font)] for v in values}
    best = None
    for main, shadow in itertools.permutations(values):
        offs = []
        for dx, dy in itertools.product(range(-2, 3), repeat=2):
            if (dx, dy) == (0, 0):
                continue
            if all({(x + dx, y + dy) for x, y in m} - m <= s
                   for m, s in zip(sets[main], sets[shadow])):
                offs.append((dx, dy))
        miss = 0
        for m, s in zip(sets[main], sets[shadow]):
            pred = set()
            for dx, dy in offs:
                pred |= {(x + dx, y + dy) for x, y in m}
            miss += len((pred - m) ^ s)
        if best is None or miss < best[0]:
            best = (miss, main, shadow, offs)
    miss, main, shadow, offs = best
    if miss or not offs:
        print("  warning: shadow model leaves %d mismatching pixels (offsets %s)" % (miss, offs))
    return main, shadow, offs


def cap_bottom_row(font, main):
    """Bottom row of the Latin capitals (mode over A..Z, main colour only)."""
    rows = []
    for g in a_to_z(font):
        w = g.width
        ys = [i // w for i, v in enumerate(g.pixels) if v == main]
        if ys:
            rows.append(max(ys))
    return Counter(rows).most_common(1)[0][0]


# ---------------------------------------------------------------------------
# Galmuri rendering
# ---------------------------------------------------------------------------

def euckr_chars(rows):
    """Yield (lead, trail, char) for every decodable EUC-KR pair in rows."""
    for lead in range(rows[0], rows[1] + 1):
        for trail in range(0xA1, 0xFF):
            try:
                ch = bytes([lead, trail]).decode("euc_kr")
            except UnicodeDecodeError:
                continue
            yield lead, trail, ch


def load_bdf(path):
    """Parse a BDF into {codepoint: (dwidth, (w, h, xo, yo), [hex rows])}."""
    out = {}
    enc = dw = bbx = bm = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("ENCODING "):
                enc = int(line.split()[1])
                bm = None
            elif line.startswith("DWIDTH "):
                dw = int(line.split()[1])
            elif line.startswith("BBX "):
                bbx = tuple(int(v) for v in line.split()[1:5])
            elif line == "BITMAP":
                bm = []
            elif line == "ENDCHAR":
                if enc is not None and enc >= 0:
                    out[enc] = (dw, bbx, bm)
                bm = None
            elif bm is not None:
                bm.append(line)
    return out


def bdf_ink(rec, baseline):
    """Ink set (x, y) of a BDF glyph with its baseline edge at row `baseline`."""
    _dw, (w, h, xo, yo), bm = rec
    ink = set()
    for r, hexrow in enumerate(bm):
        v = int(hexrow, 16)
        nbits = len(hexrow) * 4
        for c in range(w):
            if (v >> (nbits - 1 - c)) & 1:
                ink.add((xo + c, baseline - yo - h + r))
    return ink


class GalmuriRenderer:
    """Renders single characters at a fixed baseline and returns ink sets in
    cell coordinates (x to the right, y down, origin = cell top-left)."""

    MARGIN = 12

    def __init__(self, ttf_path, ppem, bdf_path=None):
        self.ttf_path = ttf_path
        self.ppem = ppem
        self.font = ImageFont.truetype(ttf_path, ppem)
        self.adv = int(round(self.font.getlength("한")))
        self.em = self.adv - 1
        self.bdf = load_bdf(bdf_path) if bdf_path and os.path.exists(bdf_path) else None
        self.cache = {}
        self.verified = 0  # glyphs compared against the BDF (see verify())
        self.notdef = self._raw_ink("͸", 0)  # unassigned code point -> .notdef
        if self.bdf is not None:
            # Hangul advance / em must match the BDF's DWIDTH / BBX.
            dw, (w, h, _xo, _yo), _bm = self.bdf[ord("한")]
            if (dw, w, h) != (self.adv, self.em, self.em):
                raise SystemExit("Galmuri %s: TTF grid (%d) disagrees with BDF (%d,%d,%d)"
                                 % (os.path.basename(ttf_path), self.adv, dw, w, h))

    def _raw_ink(self, ch, baseline):
        """Unclipped ink set with the baseline edge at row `baseline`."""
        m = self.MARGIN
        size = 2 * m + 40
        img = Image.new("L", (size, size), 0)
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        by = m + 20  # baseline row inside the scratch canvas
        d.text((m, by), ch, font=self.font, fill=255, anchor="ls")
        px = img.load()
        ink = set()
        for y in range(size):
            for x in range(size):
                if px[x, y] >= 128:
                    ink.add((x - m, y - by + baseline))
        return ink

    def ink(self, ch, baseline):
        key = (ch, baseline)
        v = self.cache.get(key)
        if v is None:
            v = self._raw_ink(ch, baseline)
            self.cache[key] = v
        return v

    def has_glyph(self, ch):
        if self.bdf is not None:
            return ord(ch) in self.bdf
        return self.ink(ch, 0) != self.notdef

    def verify(self, ch, baseline):
        """Compare Pillow's rendering with the BDF bitmap; return True/False/None."""
        if self.bdf is None:
            return None
        rec = self.bdf.get(ord(ch))
        if rec is None:
            return True  # not in the font at all; nothing to compare
        self.verified += 1
        return self.ink(ch, baseline) == bdf_ink(rec, baseline)


# ---------------------------------------------------------------------------
# Font construction
# ---------------------------------------------------------------------------

def shadow_footprint(ink, offsets):
    """Pixels covered by the shadow (before the main colour is drawn on top)."""
    out = set()
    for dx, dy in offsets:
        out |= {(x + dx, y + dy) for x, y in ink}
    return out


def fit_into_cell(ink, offsets, adv, height):
    """Shift an over-hanging glyph (ink + shadow) back into the cell when it
    fits entirely; returns (dx, dy).  Glyphs that are too big are left alone
    and get clipped by make_cell."""
    foot = ink | shadow_footprint(ink, offsets)
    xs = [x for x, _ in foot]
    ys = [y for _, y in foot]
    dx = dy = 0
    if max(xs) - min(xs) < adv:
        dx = -min(xs) if min(xs) < 0 else (adv - 1 - max(xs) if max(xs) >= adv else 0)
    if max(ys) - min(ys) < height:
        dy = -min(ys) if min(ys) < 0 else (height - 1 - max(ys) if max(ys) >= height else 0)
    return dx, dy


def make_cell(ink, adv, height, main, shadow, offsets):
    """Rasterise ink (and, if `shadow` is set, its shadow drawn first at each
    of `offsets`) into a clipped adv x height cell.

    Returns (pixel bytes, clipped_pixel_count)."""
    buf = bytearray([TRANSPARENT]) * (adv * height)
    clipped = 0
    if shadow is not None:
        for x, y in shadow_footprint(ink, offsets):
            if 0 <= x < adv and 0 <= y < height:
                buf[y * adv + x] = shadow
            elif (x, y) not in ink:
                clipped += 1
    for x, y in ink:
        if 0 <= x < adv and 0 <= y < height:
            buf[y * adv + x] = main
        else:
            clipped += 1
    return bytes(buf), clipped


def build_font(orig, rend, report):
    """Convert one original Font into the 9092-glyph Korean layout."""
    height = orig.height
    main, shadow, offsets = detect_colors(orig)
    cap_bottom = cap_bottom_row(orig, main)
    adv, em = rend.adv, rend.em

    # Hangul em box: bottom row = cap_bottom + 1, clamped into the cell.
    bottom = cap_bottom + 1
    top = bottom - (em - 1)
    top = max(0, min(top, height - em))
    baseline = top + em  # edge just below the em box
    report.update(height=height, main=main, shadow=shadow, offsets=offsets, cap_bottom=cap_bottom,
                  top=top, bottom=top + em - 1, adv=adv, em=em)

    # Indices 0..255 straight from the original.
    empty = Glyph(0, b"")
    glyphs = [orig.glyphs[i] if i < orig.count else empty for i in range(256)]
    report["padded"] = max(0, 256 - orig.count)
    report["dropped"] = max(0, orig.count - 256)

    blank = Glyph(adv, bytes([TRANSPARENT]) * (adv * height))
    glyphs += [blank] * (94 * 94)

    clipped_total = 0
    missing = []
    filled = {"hangul": 0, "symbol": 0}
    mismatch = []
    refit = []
    clip_chars = []
    for area, rows in (("symbol", SYMBOL_ROWS), ("hangul", HANGUL_ROWS)):
        for lead, trail, ch in euckr_chars(rows):
            idx = mcg_fnt.euckr_index(lead, trail)
            if not rend.has_glyph(ch):
                missing.append(ch)
                continue
            ok = rend.verify(ch, baseline)
            if ok is False:
                mismatch.append(ch)
            ink = rend.ink(ch, baseline)
            if not ink:
                continue  # genuinely blank glyph (e.g. ideographic space)
            if area == "symbol":
                fx, fy = fit_into_cell(ink, offsets, adv, height)
                if fx or fy:
                    ink = {(x + fx, y + fy) for x, y in ink}
                    refit.append(ch)
            pix, clipped = make_cell(ink, adv, height, main, shadow, offsets)
            if clipped:
                clip_chars.append(ch)
            clipped_total += clipped
            glyphs[idx] = Glyph(adv, pix)
            filled[area] += 1
    report.update(missing=missing, clipped=clipped_total, filled=filled,
                  mismatch=mismatch, refit=refit, clip_chars=clip_chars)
    return Font(height, glyphs, orig.version, orig.x)


# ---------------------------------------------------------------------------
# Validation and contact sheet
# ---------------------------------------------------------------------------

def validate(path, orig, report):
    """Re-read the written file and check the invariants the engine relies on."""
    f = mcg_fnt.read_fnt(path)
    assert f.count == KOR_COUNT, "count"
    assert f.height == orig.height and f.x == orig.x and f.version == orig.version
    for i in range(min(256, orig.count)):
        assert f.glyphs[i].width == orig.glyphs[i].width, "glyph %d width" % i
        assert f.glyphs[i].pixels == orig.glyphs[i].pixels, "glyph %d pixels" % i
    for i in range(orig.count, 256):
        assert f.glyphs[i].width == 0, "pad glyph %d" % i
    adv = report["adv"]
    # The blank cell must be shared and have the Hangul advance.
    blank_idx = mcg_fnt.euckr_index(0xCA, 0xA1)  # Hanja row, never filled
    blank = f.glyphs[blank_idx]
    assert blank.width == adv and set(blank.pixels) == {TRANSPARENT}
    n_shared = sum(1 for g in f.glyphs[256:] if g is blank)
    # Every filled cell has the Hangul advance.
    for g in f.glyphs[256:]:
        assert g.width == adv
    return f, n_shared


def contact_sheet(entries, out_png, scale=3):
    """entries: list of (label, Font, shadow_value).  Rendered with mcg_fnt."""
    rows = []
    for label, font, shadow in entries:
        idx = mcg_fnt.text_to_indices(SAMPLE, font.count)
        w, h, px_rows = mcg_fnt.render_line(font, idx)
        rows.append((label, font.height, w, px_rows, shadow))
    label_w = 150
    max_w = max(r[2] for r in rows)
    pad = 6
    group_gap = 8
    total_h = pad
    ys = []
    prev_family = None
    for label, h, w, px_rows, shadow in rows:
        family = label.split()[0].rstrip("0123456789") if label else ""
        if prev_family is not None and family != prev_family:
            total_h += group_gap
        prev_family = family
        ys.append(total_h)
        total_h += h * scale + pad
    img = Image.new("RGB", (label_w + max_w * scale + 2 * pad, total_h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    lab_font = ImageFont.load_default()
    for (label, h, w, px_rows, shadow), y0 in zip(rows, ys):
        d.text((pad, y0 + (h * scale) // 2 - 5), label, fill=(150, 200, 150), font=lab_font)
        for y in range(h):
            row = px_rows[y]
            for x in range(w):
                v = row[x]
                if v == TRANSPARENT:
                    continue
                col = (110, 110, 130) if (shadow is not None and v == shadow) else (255, 255, 255)
                x0 = label_w + x * scale
                yy = y0 + y * scale
                d.rectangle([x0, yy, x0 + scale - 1, yy + scale - 1], fill=col)
    img.save(out_png)
    return img.size


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def font_list():
    out = []
    for fam in FAMILIES:
        for h in (8, 10, 12):
            out.append((fam + SIZE_SUFFIX[h] + ".FNT", h))
    for name in EXTRA:
        out.append((name + ".FNT", 8))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", required=True, help="directory with the original *.FNT (MISC.FST)")
    ap.add_argument("--galmuri", required=True, help="directory with Galmuri7/9/11 .ttf (+ .bdf)")
    ap.add_argument("--out", required=True, help="output directory (lang/kor/data/fonts)")
    ap.add_argument("--preview", help="contact sheet PNG (default: <out>/../../fonts_preview.png)")
    ap.add_argument("--no-verify", action="store_true", help="skip the BDF cross-check")
    args = ap.parse_args(argv)

    if getattr(sys.stdout, "reconfigure", None):
        sys.stdout.reconfigure(errors="replace")
    os.makedirs(args.out, exist_ok=True)
    preview = args.preview or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(args.out))),
                                           "fonts_preview.png")

    renderers = {}
    for h, (name, ppem) in GALMURI.items():
        ttf = os.path.join(args.galmuri, name + ".ttf")
        if not os.path.exists(ttf):
            sys.exit("missing %s" % ttf)
        bdf = None if args.no_verify else os.path.join(args.galmuri, name + ".bdf")
        renderers[h] = GalmuriRenderer(ttf, ppem, bdf)
        r = renderers[h]
        print("%s: ppem %d, Hangul advance %d, em %d, BDF check %s"
              % (name, ppem, r.adv, r.em, "on" if r.bdf is not None else "OFF"))

    entries = []
    summary = []
    any_problem = False
    for fname, h in font_list():
        src = os.path.join(args.src, fname)
        orig = mcg_fnt.read_fnt(src)
        assert orig.height == h, "%s: height %d != %d" % (fname, orig.height, h)
        rep = {}
        font = build_font(orig, renderers[h], rep)
        dst = os.path.join(args.out, fname)
        size = mcg_fnt.write_fnt(dst, font)
        loaded, n_shared = validate(dst, orig, rep)
        rep["size"] = size
        summary.append((fname, rep))
        entries.append((fname[:-4] + " (%dpx)" % h, loaded, rep["shadow"]))
        problems = []
        if rep["mismatch"]:
            problems.append("%d BDF mismatches" % len(rep["mismatch"]))
        if rep["refit"]:
            problems.append("%d symbols shifted into cell" % len(rep["refit"]))
        if rep["clip_chars"]:
            problems.append("%d symbols clipped (%d px): %s" % (
                len(rep["clip_chars"]), rep["clipped"], "".join(rep["clip_chars"])))
        any_problem = any_problem or bool(rep["mismatch"])
        print("%-13s count %d h %2d  main %3d%s  cap-bottom row %d  Hangul rows %d-%d  adv %d  "
              "size %7d  hangul %d symbols %d missing %d  %s"
              % (fname, loaded.count, h, rep["main"],
                 ("  shadow %d@%s" % (rep["shadow"], rep["offsets"])) if rep["shadow"] is not None else "",
                 rep["cap_bottom"], rep["top"], rep["bottom"], rep["adv"], size,
                 rep["filled"]["hangul"], rep["filled"]["symbol"], len(rep["missing"]),
                 ("[" + "; ".join(problems) + "]") if problems else "OK"))

    # Report glyphs Galmuri lacks (same per size).
    print()
    seen = {}
    for fname, rep in summary:
        seen.setdefault(rep["height"], rep["missing"])
    for h, miss in sorted(seen.items()):
        print("Galmuri%d lacks %d of the KS X 1001 rows A1-A3/B0-C8 characters: %s"
              % ({8: 7, 10: 9, 12: 11}[h], len(miss), "".join(miss) if miss else "(none)"))

    for h, r in sorted(renderers.items()):
        if r.bdf is not None:
            print("Galmuri%d: %d glyph comparisons against the BDF bitmap, %d mismatches"
                  % ({8: 7, 10: 9, 12: 11}[h], r.verified,
                     sum(len(rep["mismatch"]) for _n, rep in summary if rep["height"] == h)))
    size = contact_sheet(entries, preview)
    print("contact sheet: %s (%dx%d)" % (preview, size[0], size[1]))
    if any_problem:
        sys.exit("BDF cross-check reported mismatches")


if __name__ == "__main__":
    main()
