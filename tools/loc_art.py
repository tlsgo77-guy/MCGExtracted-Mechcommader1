"""Inventory of the TGA art of ART.FST (and TERRAIN.FST) and contact sheets to find baked-in text.

Output (see extract_text.py):
    localization/en/art/*.png      contact sheets, every thumbnail labelled with file name + size
    localization/en/art.json       one entry per TGA: {file, width, height, bpp, has_text, text_guess, ...}

The reviewed verdicts (has_text / text_guess) are hand-written in localization/en/art/review.json by looking
at the sheets; this script merges them into art.json and marks everything else "unsure".

Source of the images: the local game install (game-source/extracted/MCX/ART.FST, the *complete* archive with
the data/art/logart/ sub-tree, 1398 TGA) and, if that is missing, the extracted repo folder ART.FST/ (483 TGA,
top level only).

review.json format:
    {"rules": [{"match": "<glob on the file stem, case-insensitive>", "has_text": true|false|"unsure",
                "text_guess": "...", "note": "..."}, ...],       # first matching rule wins
     "files": {"BG_ACCEPT": {"has_text": true, "text_guess": "ACCEPT"}, ...}}   # exact stem, overrides rules
"""
from __future__ import annotations

import fnmatch
import json
import re
import struct
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

from loc_common import ART, GAME, MISSION, OUT, REPO, md_cell, read_text, write_json, write_text
from loc_fst import FST

ART_OUT = OUT / "art"
REVIEW = ART_OUT / "review.json"


def open_pil():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as e:        # pragma: no cover
        raise SystemExit("Pillow is required: pip install pillow") from e
    return Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------------------- loading

def load_images():
    """-> list of dict(name, stem, fst_path, source, data)"""
    out = []
    fst_path = GAME / "ART.FST"
    if fst_path.exists():
        fst = FST(fst_path)
        for name, idx in fst.items():
            if name.lower().endswith(".tga"):
                out.append({"name": Path(name.replace("\\", "/")).name, "fst_path": name,
                            "source": "game ART.FST", "data": fst.read(idx)})
    else:
        for p in sorted(ART.glob("*.tga"), key=lambda p: p.name.lower()):
            out.append({"name": p.name, "fst_path": "data\\art\\" + p.name, "source": "repo ART.FST/", "data": p.read_bytes()})
    tfst = GAME / "TERRAIN.FST"
    if tfst.exists():
        fst = FST(tfst)
        for name, idx in fst.items():
            if name.lower().endswith(".tga"):
                out.append({"name": Path(name.replace("\\", "/")).name, "fst_path": name,
                            "source": "game TERRAIN.FST", "data": fst.read(idx)})
    for e in out:
        e["stem"] = Path(e["name"]).stem
    return out


def tga_info(data: bytes):
    idlen, cmtype, imtype = data[0], data[1], data[2]
    w, h = struct.unpack_from("<HH", data, 12)
    bpp = data[16]
    return {"width": w, "height": h, "bpp": bpp, "tga_type": imtype, "palette": bool(cmtype)}


def decode(Image, data: bytes):
    import io
    im = Image.open(io.BytesIO(data))
    im.load()
    return im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") and "transparency" in im.info else im.convert("RGB")


# ---------------------------------------------------------------------------------------- usage

def screen_fit_usage():
    """TGA stem -> list of 'mainscreen.fit element N (Button, callback 0: new cermak)' from the ART.FST screen FITs."""
    use = defaultdict(list)
    folder = ART if ART.exists() else None
    fits = []
    if folder:
        fits = [p for p in folder.iterdir() if p.suffix.lower() == ".fit"]
    for p in sorted(fits, key=lambda p: p.name.lower()):
        sec, info = None, {}
        elems = []
        for raw in read_text(p).splitlines():
            m = re.match(r"\s*\[(Element\d+)\]", raw)
            if m:
                sec = m.group(1)
                info = {"section": sec, "arts": [], "etype": "", "callback": "", "comment": ""}
                elems.append(info)
                continue
            if sec is None:
                continue
            m = re.match(r"\s*l\s+ElementType\s*=\s*(\d+)\s*(?://\s*(.*))?", raw)
            if m:
                info["etype"] = m.group(1)
                if m.group(2):
                    info["comment"] = m.group(2).strip()
            m = re.match(r"\s*l\s+Callback\s*=\s*(-?\d+)\s*(?://\s*(.*))?", raw)
            if m:
                info["callback"] = m.group(1)
                if m.group(2):
                    info["comment"] = (info["comment"] + " / " + m.group(2).strip()).strip(" /")
            m = re.match(r'\s*st\s+(\w+Art)\s*=\s*"([^"]*)"', raw)
            if m and m.group(2).upper() != "NONE":
                info["arts"].append((m.group(1), Path(m.group(2)).stem))
        for e in elems:
            for kind, stem in e["arts"]:
                desc = f"{p.name} {e['section']} {kind}" + (f" [{e['comment']}]" if e["comment"] else "")
                use[stem.lower()].append(desc)
    return use


def code_usage(images):
    """TGA stem -> sorted list of screens, from the file-name patterns embedded in MCX.EXE and the functions using them."""
    try:
        from loc_strings import CodeIndex, demangle, func_rule
    except SystemExit:
        return {}
    import struct as st
    ci = CodeIndex()
    d = ci.d
    pats = []
    for m in re.finditer(rb"[\x20-\x7e]*\.[tT][gG][aA]\x00", d[0x17A000:0x1AA000]):
        s = m.group().rstrip(b"\0").decode()
        va = 0x600000 + 0x17A000 + m.start()
        refs = set()
        pat = st.pack("<I", va)
        j = 0
        while True:
            j = d.find(pat, j)
            if j < 0 or j > 0x179000:
                break
            fn = demangle(ci.func_of(0x600000 + j)[1])
            refs.add((func_rule(fn)[0], fn))
            j += 1
        if not refs:
            continue
        base = s.replace("\\", "/").split("/")[-1]
        stem = base[:-4]
        rx = re.escape(stem.lower())
        rx = re.sub(r"%0?(\d?)[dic]", lambda m_: r"\d{%s}" % (m_.group(1) or "1,"), rx.replace("\\%", "%"))
        rx = rx.replace("%c", "[a-z]").replace("%i", r"\d+").replace("%s", ".*")
        try:
            pats.append((re.compile("^" + rx + "$"), refs))
        except re.error:
            continue
    use = {}
    for im in images:
        s = im["stem"].lower()
        hits = set()
        for rx, refs in pats:
            if rx.match(s):
                hits |= refs
        if hits:
            use[s] = sorted(hits)
    return use


# ---------------------------------------------------------------------------------------- sheets

TRIPLET_RES = [   # (regex on stem, state letter group index, key group)
    re.compile(r"^(BG|BH|BN)_(.+)$", re.I),
    re.compile(r"^(MM_)(BG|BH|BN)(\d+)$", re.I),
    re.compile(r"^(mm_x)(bg|bh|bn)(\d+)$", re.I),
    re.compile(r"^(MM_SS)(G|H|N)(\d+)$", re.I),
    re.compile(r"^(SES_)(BG|BH|BN)_(.+)$", re.I),
    re.compile(r"^(lsc)(bg|bh|bn)(\d+)$", re.I),
    re.compile(r"^(X_)?(MFD..)(BG|BH|BN)(\d+)$", re.I),
]


def triplet_key(stem):
    """Return (family_key, state) when `stem` belongs to a normal/highlight/pressed button set, else None."""
    m = TRIPLET_RES[0].match(stem)
    if m:
        return ("BG_BH_BN:" + m.group(2).lower(), m.group(1).upper())
    for rx in TRIPLET_RES[1:6]:
        m = rx.match(stem)
        if m:
            g = m.groups()
            return (g[0].lower() + g[2].lower(), g[1].upper())
    return None


SHEETS = [   # (file, title, predicate on (path_lower, stem_lower), max_scale, columns hint)
    ("01_buttons_BG_BH_BN", "ART.FST buttons BG_/BH_/BN_ (bg=pressed, bh=normal/over, bn=grey)",
     lambda p, s: re.match(r"(bg|bh|bn)_", s) is not None and "logart" not in p, 3),
    ("02_mainmenu_MM", "Main menu, load/save/prefs buttons MM_/mm_",
     lambda p, s: s.startswith("mm_") and "logart" not in p, 2),
    ("03_screens_misc", "Prefs / LAN / modem / serial / ready room / session screens, dialogs",
     lambda p, s: re.match(r"(prefs_|lan0|modem|serial|rroom|ses_|access|asked|dbox_|pause)", s) is not None
     and "logart" not in p, 1),
    ("04_pilot_portraits", "Pilot portraits", lambda p, s: s.startswith("pilot"), 1),
    ("05_results_MR", "Mission results screen (MR_/MRM_/GUIMR)", lambda p, s: re.match(r"(x_)?(mr_|mrm_|guimr|mrmbkgd|x_mr)", s) is not None, 1),
    ("05b_hud_text_candidates", "In-mission HUD pieces that may carry text (3x, expansion X_ copies not repeated)",
     lambda p, s: re.match(r"(mfd(.ts\d\d|ddb[ghn]\d\d|sb[ghn]\d\d|sts\d\d|ddwn0\d|dwn0\d|mwn0\d|swn0\d|cwn0\d|bwn0\d)|guiubf\d|guiub0\d)$", s) is not None, 3),
    ("06_hud_MFD_GUI", "In-mission HUD (MFD*/GUI*/X_*)", lambda p, s: re.match(r"(x_)?(mfd|gui)", s) is not None, 1),
    ("10_logart_briefing_LSB", "Logistics: mission briefing LSB*", lambda p, s: "logart" in p and s.startswith(("lsb", "lsc_op")), 1),
    ("11_logart_buttons_LSC", "Logistics: buttons / dialogs LSC*", lambda p, s: "logart" in p and re.match(r"lsc(bg|bh|bn|sb|up|dw|ii|_p)", s) is not None, 2),
    ("12_logart_purchase_dialog_LSPCB", "Logistics: purchase dialog LSPCB* / LSPBK / LSPBI*", lambda p, s: "logart" in p and re.match(r"lsp(cb|bk|bi)", s) is not None, 1),
    ("13_logart_repair_LSR", "Logistics: repair screen LSR*", lambda p, s: "logart" in p and s.startswith("lsr"), 1),
    ("14_logart_fonts", "Font bitmaps and scroll art", lambda p, s: "logart" in p and re.match(r"(blkfnt|blue|green|gryfnt|red|white|yell|invblock|scroll|sdnbup|supbup|splash|mcxcard)", s) is not None, 1),
    ("15_logart_mech_icons", "Logistics: mech pictures (LSCFLM/LSCDSM/LSPFLM/LSPFDM/MMASK)", lambda p, s: "logart" in p and re.match(r"(lscflm|lscdsm|lscddm|lscicm|lspflm|lspfdm|lspbim|mmask|lsrupm)", s) is not None, 0.5),
    ("16_logart_vehicle_icons", "Logistics: vehicle pictures (LSCFLV/LSPFLV/LSPFDV/VMASK/LSCDDV/LSCICV)", lambda p, s: "logart" in p and re.match(r"(lscflv|lspflv|lspfdv|vmask|lscddv|lscicv)", s) is not None, 0.5),
    ("17_logart_component_icons", "Logistics: component pictures (LSCICC/LSPFDC/LSPIDC/LSPILC/LSPFLC/LSPFLP)", lambda p, s: "logart" in p and re.match(r"(lscicc|lspfdc|lspidc|lspilc|lspflc|lspflp)", s) is not None, 0.5),
    ("18_logart_pilots", "Logistics pilot portraits (logart/PILOT*)", lambda p, s: "logart" in p and s.startswith("pilot"), 1),
    ("30_terrain_tacmaps", "TERRAIN.FST TGA (tactical map images; *.log.tga = briefing-screen version with F1..F3 / objective markers)",
     lambda p, s: p.startswith("data\\terrain") or "terrain" in p, 0.25),
]


def sheet_name(im):
    """Name of the contact sheet an image lands on (first matching entry of SHEETS)."""
    for fname, _title, pred, _scale in SHEETS:
        if pred(im["fst_path"].lower(), im["stem"].lower()):
            return fname
    return "99_other"


def font(ImageFont, size=12):
    for cand in ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(cand, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_sheet(items, title, max_scale, out_path, Image, ImageDraw, ImageFont, width=1800, cell_pad=8):
    """items: list of rows; a row is a list of (label, PIL image)"""
    f = font(ImageFont, 12)
    ft = font(ImageFont, 15)
    rows = []
    for row in items:
        cells = []
        for label, im in row:
            s = max_scale
            w, h = im.size
            if w * s > width / 2:
                s = (width / 2) / w
            if s >= 1:
                s = int(s) if abs(s - round(s)) < 1e-6 or s > 1 else 1
                s = max(1, int(s))
                im2 = im.resize((w * s, h * s), Image.NEAREST)
            else:
                im2 = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
            cells.append((label, im2))
        rows.append(cells)
    # shelf packing: concatenate rows horizontally until the width is exceeded
    shelves, cur, curw = [], [], 0
    for cells in rows:
        rw = sum(max(im.width, 90) + cell_pad for _l, im in cells) + 2 * cell_pad
        if cur and curw + rw > width:
            shelves.append(cur)
            cur, curw = [], 0
        cur.append(cells)
        curw += rw
    if cur:
        shelves.append(cur)
    H = 30
    for shelf in shelves:
        H += max(im.height for cells in shelf for _l, im in cells) + 34
    sheet = Image.new("RGB", (width, max(H, 60)), (40, 40, 48))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 6), f"{title}  ({sum(len(r) for r in rows)} images)", fill=(255, 255, 255), font=ft)
    y = 30
    for shelf in shelves:
        x = cell_pad
        sh = max(im.height for cells in shelf for _l, im in cells)
        for cells in shelf:
            for label, im in cells:
                cw = max(im.width, 90)
                sheet.paste(im.convert("RGB"), (x, y))
                dr.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(90, 90, 110))
                dr.text((x, y + sh + 3), label[:cw // 6 + 6], fill=(220, 220, 160), font=f)
                x += cw + cell_pad
            x += cell_pad
        y += sh + 34
    sheet.save(out_path)
    return sheet.size


def build_sheets(images, Image, ImageDraw, ImageFont, split=250):
    ART_OUT.mkdir(parents=True, exist_ok=True)
    for p in ART_OUT.glob("*.png"):
        p.unlink()
    assigned, sheets = set(), []
    for fname, title, pred, scale in SHEETS:
        sel = [im for im in images if id(im) not in assigned and pred(im["fst_path"].lower(), im["stem"].lower())]
        if not sel:
            continue
        for im in sel:
            assigned.add(id(im))
        sheets.append((fname, title, sel, scale))
    rest = [im for im in images if id(im) not in assigned]
    if rest:
        sheets.append(("99_other", "Everything else", rest, 1))
    made = []
    for fname, title, sel, scale in sheets:
        # group triplets into rows
        rows, seen_keys = [], {}
        for im in sorted(sel, key=lambda i: i["stem"].lower()):
            k = triplet_key(im["stem"])
            pil = decode(Image, im["data"])
            lab = f"{im['stem']} {pil.width}x{pil.height}"
            if k:
                row = seen_keys.get(k[0])
                if row is None:
                    row = []
                    seen_keys[k[0]] = row
                    rows.append(row)
                row.append((lab, pil))
            else:
                rows.append([(lab, pil)])
        # split long sheets
        parts = [rows[i:i + split] for i in range(0, len(rows), split)] or [[]]
        for n, part in enumerate(parts, 1):
            suffix = f"_{n}" if len(parts) > 1 else ""
            path = ART_OUT / f"{fname}{suffix}.png"
            size = render_sheet(part, title + (f" [part {n}/{len(parts)}]" if len(parts) > 1 else ""), scale, path, Image, ImageDraw, ImageFont)
            made.append((path.name, title, sum(len(r) for r in part), size))
    return made


# ---------------------------------------------------------------------------------------- art.json

def load_review():
    if REVIEW.exists():
        return json.loads(REVIEW.read_text(encoding="utf-8"))
    return {"rules": [], "files": {}}


def verdict(review, stem, source=""):
    """Exact (case-insensitive) file verdict first, then the first matching rule.  A rule may restrict itself with
    `"source_contains": "TERRAIN"` (matched against the archive the image came from)."""
    f = review.setdefault("_files_lc", {k.lower(): v for k, v in review.get("files", {}).items()})
    if stem.lower() in f:
        return f[stem.lower()]
    for r in review.get("rules", []):
        if r.get("source_contains") and r["source_contains"].lower() not in source.lower():
            continue
        if fnmatch.fnmatch(stem.lower(), r["match"].lower()):
            return r
    return None


def run(sheets=True):
    Image, ImageDraw, ImageFont = open_pil()
    images = load_images()
    review = load_review()
    uses_fit = screen_fit_usage()
    uses_code = code_usage(images)
    entries = []
    for im in images:
        info = tga_info(im["data"])
        v = verdict(review, im["stem"], im["source"]) or {}
        e = OrderedDict()
        e["file"] = im["fst_path"].replace("\\", "/")
        e["width"], e["height"], e["bpp"] = info["width"], info["height"], info["bpp"]
        e["tga_type"] = "palettized (type 1)" if info["palette"] else f"true colour (type {info['tga_type']})"
        e["has_text"] = v.get("has_text", "unsure")
        e["text_guess"] = v.get("text_guess", "")
        s = im["stem"].lower()
        if uses_fit.get(s):
            e["used_by_screen_fit"] = uses_fit[s]
        if uses_code.get(s):
            e["used_by_code"] = sorted({f"{scr}: {fn}" for scr, fn in uses_code[s]})[:6]
        if v.get("note"):
            e["note"] = v["note"]
        e["source"] = im["source"]
        e["sheet"] = sheet_name(im)          # file name prefix of the contact sheet(s) in localization/en/art/
        entries.append(e)
    entries.sort(key=lambda e: (e["file"].lower()))
    write_json(OUT / "art.json", entries, indent=1)
    made = []
    if sheets:
        made = build_sheets(images, Image, ImageDraw, ImageFont)
    c = Counter(str(e["has_text"]) for e in entries)
    print("TGA:", len(entries), dict(c), "sheets:", len(made))
    return entries, made


if __name__ == "__main__":
    from loc_common import utf8_stdout
    utf8_stdout()
    run()
