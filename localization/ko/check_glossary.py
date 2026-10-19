"""Validate localization/ko/glossary.json (Korean terminology for the pre-mission scope).

    python -I localization/ko/check_glossary.py [--quiet]

Checks
  1. every `ko` is renderable by the Korean game fonts: printable ASCII plus the 2,350
     KS X 1001 Hangul syllables only (EUC-KR lead byte 0xB0..0xC8).  NOTE: Python's
     `euc_kr` codec does NOT fail on syllables outside KS X 1001 (e.g. 똠, 햏, 힣): it
     emits an 8-byte KS X 1001:1998 annex-3 jamo sequence (A4 D4 ...), which the fonts
     draw as blanks.  Hanja, jamo (row A4), fullwidth forms (row A3) are rejected too;
     symbol rows A1/A2 are reported as warnings (allowed by the font, discouraged by STYLE.md).
  2. no `en` maps to two different `ko` (error inside a category, warning across categories).
  3. coverage against localization/en: mech/vehicle string ids 700-783 / 1200-1255, every
     compbas.csv name and abbreviation, MECHTEXT/MECHREP labels, the 30 player pilots and
     every name-plate text of art.json.
  4. byte limits of shared short strings (ids 79-82, 100-102: 15-byte buffer -> 14 bytes).
  5. pixel widths of the baked name plates and of compbas abbreviations, measured with the
     Korean .FNT files in game-source/extracted/MCX/lang/kor/data/fonts (skipped if absent).
Exit code 1 if any error.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
EN = REPO / "localization" / "en"
KOR_FONTS = REPO / "game-source" / "extracted" / "MCX" / "lang" / "kor" / "data" / "fonts"
MISC = REPO / "MISC.FST"

sys.stdout.reconfigure(encoding="utf-8")
quiet = "--quiet" in sys.argv
errors, warnings = [], []


def char_problem(ch):
    """None if `ch` renders, else (severity, reason)."""
    o = ord(ch)
    if 0x20 <= o <= 0x7E:
        return None
    try:
        raw = ch.encode("euc_kr")
    except UnicodeEncodeError:
        return ("error", "not in EUC-KR")
    if len(raw) != 2:
        return ("error", f"not a KS X 1001 syllable (codec emitted {len(raw)}-byte jamo sequence {raw.hex()})")
    lead = raw[0]
    if 0xB0 <= lead <= 0xC8:
        return None
    if lead in (0xA1, 0xA2):
        return ("warning", f"KS X 1001 symbol {raw.hex()} (use ASCII instead)")
    if lead == 0xA3:
        return ("error", "fullwidth form (row A3)")
    if lead == 0xA4:
        return ("error", "Hangul jamo (row A4, no glyph)")
    if 0xCA <= lead <= 0xFD:
        return ("error", "Hanja (no glyph in the Korean fonts)")
    return ("error", f"EUC-KR row {lead:02X} has no glyph")


def load(name):
    return json.load(open(EN / name, encoding="utf-8"))


gl = json.load(open(HERE / "glossary.json", encoding="utf-8"))

# ---- 1 + 2: characters and consistency
by_en = defaultdict(set)
index = defaultdict(dict)  # category -> en -> ko
for catname, entries in gl.items():
    if not isinstance(entries, list):
        errors.append(f"{catname}: not a list")
        continue
    for e in entries:
        if set(e) - {"en", "ko", "note"} or "en" not in e or "ko" not in e:
            errors.append(f"{catname}: bad entry {e}")
            continue
        en, ko = e["en"], e["ko"]
        for ch in ko:
            pb = char_problem(ch)
            if pb:
                (errors if pb[0] == "error" else warnings).append(f"{catname}: {en!r} -> {ko!r}: {ch!r} {pb[1]}")
        if "  " in ko.strip() and catname not in ("briefing_terms", "fixed_phrases"):
            warnings.append(f"{catname}: {en!r} -> {ko!r}: double space")
        if en in index[catname] and index[catname][en] != ko:
            errors.append(f"{catname}: {en!r} has two translations {index[catname][en]!r} / {ko!r}")
        index[catname][en] = ko
        by_en[en].add(ko)
for en, kos in sorted(by_en.items()):
    if len(kos) > 1:
        warnings.append(f"cross-category: {en!r} -> {sorted(kos)}")


def has(cat, en):
    return en in index.get(cat, {})


# ---- 3: coverage
strings = {s["id"]: s for s in load("strings.json")}
for i in range(700, 772):
    chassis, letter = strings[i]["text"].rsplit(" ", 1)
    if letter not in "AWJ" or not has("mech_chassis", chassis):
        errors.append(f"coverage: mech id {i} {strings[i]['text']!r} (chassis {chassis!r}) missing")
for i in range(772, 784):
    if not has("mech_chassis", strings[i]["text"]):
        errors.append(f"coverage: named mech id {i} {strings[i]['text']!r} missing")
for i in range(1200, 1256):
    if not has("vehicles", strings[i]["text"]):
        errors.append(f"coverage: vehicle id {i} {strings[i]['text']!r} missing")

fit = load("fit_strings.json")
for e in fit:
    f = e["file"]
    if f.endswith("compbas.csv") and not has("weapons_components", e["text"]):
        errors.append(f"coverage: compbas {e['key']} {e['text']!r} missing")
    if (f.endswith("MECHTEXT.FIT") or f.endswith("MECHREP.FIT")) and not has("mech_locations", e["text"]):
        errors.append(f"coverage: {f.split('/')[-1]} {e['text']!r} missing from mech_locations")
    m = re.search(r"PMW(\d{5})\.FIT$", f, re.I)
    if m and (51 <= int(m.group(1)) <= 80 or 86 <= int(m.group(1)) <= 109) and e["key"] == "Name":
        if not has("pilots", e["text"]):
            errors.append(f"coverage: player pilot {e['text']!r} ({f}) missing")

art = load("art.json")
plate_re = re.compile(r"(LSCFLM|LSPFLM|LSPFDM|LSCFLV|LSPFLV|LSPFDV|LSPFLC|LSPFDC|LSPFLP)", re.I)
for a in art:
    n = a["file"].split("/")[-1]
    if plate_re.match(n) and not has("art_plates", a["text_guess"]):
        errors.append(f"coverage: plate {n} {a['text_guess']!r} missing from art_plates")

# ---- 4: byte limits of shared short strings
SHORT = {"Light": 14, "Medium": 14, "Heavy": 14, "Assault": 14, "Very Lgt": 14, "Moderate": 14, "Very Hvy": 14}
for en, limit in SHORT.items():
    ko = index["game_terms"].get(en)
    if ko is None:
        errors.append(f"game_terms: {en!r} missing")
    elif len(ko.encode("euc_kr")) > limit:
        errors.append(f"game_terms: {en!r} -> {ko!r} is {len(ko.encode('euc_kr'))} bytes > {limit}")

# ---- 5: pixel widths
report = []
if (KOR_FONTS / "WHITE.FNT").exists():
    sys.path.insert(0, str(REPO / "tools"))
    import mcg_fnt as F

    kf = {h: F.read_fnt(str(KOR_FONTS / n)) for h, n in ((8, "WHITE.FNT"), (10, "WHITE10.FNT"), (12, "WHITE12.FNT"))}
    ef = F.read_fnt(str(MISC / "WHITE.FNT"))

    def px(font, text):
        return sum(font.glyphs[i].width if i < font.count else 0 for i in F.text_to_indices(text, font.count))

    worst = []
    for e in gl.get("art_plates", []):
        m = re.match(r"(\d+)x12 px", e.get("note", ""))
        if not m:
            continue
        width = int(m.group(1))
        w8, w10, w12 = (px(kf[h], e["ko"]) for h in (8, 10, 12))
        if w8 > width - 2:
            errors.append(f"plate {e['en']!r} -> {e['ko']!r}: {w8} px at 8 px font > {width - 2} px usable")
        elif w10 > width - 2:
            warnings.append(f"plate {e['en']!r} -> {e['ko']!r}: {w10} px at 10 px font > {width - 2} px (8 px font only)")
        worst.append((w8 / width, e["en"], e["ko"], width, w8, w10, w12))
    worst.sort(reverse=True)
    report.append("tightest plates (ratio at 8px, en, ko, plate px, 8/10/12 px widths):")
    report += [f"  {r[0]:.2f} {r[1]!r} -> {r[2]!r}: {r[3]} px plate, {r[4]}/{r[5]}/{r[6]} px" for r in worst[:8]]

    abbr = {e["text"] for e in fit if e["file"].endswith("compbas.csv") and e["key"] == "abbr"}
    rows = []
    for en in sorted(abbr):
        ko = index["weapons_components"].get(en)
        if ko is None:
            continue
        we, wk = px(ef, en), px(kf[8], ko)
        rows.append((wk - we, en, ko, we, wk))
        if wk > we * 1.35 + 4:
            warnings.append(f"abbr {en!r} ({we} px) -> {ko!r} ({wk} px at 8 px): much wider than the English")
    rows.sort(reverse=True)
    report.append("widest compbas abbreviations vs English (delta px, en, ko, en px, ko px at 8 px):")
    report += [f"  {r[0]:+d} {r[1]!r} -> {r[2]!r}: {r[3]} -> {r[4]}" for r in rows[:8]]
else:
    warnings.append(f"Korean fonts not found in {KOR_FONTS}: pixel checks skipped")

# ---- summary
counts = {k: len(v) for k, v in gl.items() if isinstance(v, list) and not k.startswith("_")}
print("entries per category:", json.dumps(counts, ensure_ascii=False))
print("total entries:", sum(counts.values()))
if not quiet:
    for line in report:
        print(line)
    for w in warnings:
        print("WARNING", w)
for e in errors:
    print("ERROR", e)
print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
