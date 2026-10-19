"""Inventory of the mission briefing text files (MISSION.FST/*.txt) and of the `%` markup they use.

Output (see extract_text.py):
    localization/en/briefings.json   one entry per .txt file: size, referencing mission FIT(s), campaign
    localization/en/markup.md        every `%` code with counts and its meaning

Where the briefing files are used
    Mission FITs carry `st BriefingFile = "xxx.txt"` (single-player campaigns, solo missions) or
    `st ISBriefingFile` / `st ClanBriefingFile` (two-sided missions: multiplayer maps and the
    stand-alone skirmish maps).  Logistics::getCurrentMission stores the name and hands the file to
    SMUTI::init(file, port, width), which reads the whole file, zeroes the byte at [len-2] (the trailing
    CR LF) and renders it with SMUTI::process.  The same SMUTI renderer is used for the component
    descriptions (MISC.FST/desc.fit `DescString`), the item-drag popup of the repair screen and the
    chat windows, so the markup below applies to all of them.

SMUTI::process (VA 0x728ed0) decoded
    '%' + c   (case-insensitive) dispatched through a jump table at 0x729398:
        %%    literal percent sign
        %c    centre the following text (up to the next '%'; max 80 characters are measured)
        %n    end the line: flush the pending text, x = 0, y += font height + 1
        %tN   N = decimal digits; skip N pixels horizontally (no glyph drawn)
        %f?   font control, 2nd letter (case-insensitive):
                c + ONE digit D  -> colour D           (fonts[D][size])
                s                -> size index 0       (<name>.fnt)
                m                -> size index 1       (<name>10.fnt)
                l                -> size index 2       (<name>12.fnt)
              any other letter -> ignored
        %<other>  emitted literally as '%' followed by the character
    Characters below 0x20 (CR, LF, TAB) are ignored: line breaks in the .txt only come from %n.
    Wrapping happens at the last space (0x20) when the pen would pass the port width.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from loc_common import MISC, MISSION, OUT, md_cell, read_text, write_json, write_text

# fonts[colour][size] as filled by aSystem::start (VA 0x612c10); size index 0/1/2 = s/m/l
FONT_COLOURS = {
    0: ("black", "blkfnt.fnt", "blkfnt10.fnt", "blkfnt12.fnt"),
    1: ("red", "red.fnt", "red10.fnt", "red12.fnt"),
    2: ("yellow", "yellow.fnt", "yellow10.fnt", "yellow12.fnt"),
    3: ("green", "green.fnt", "green10.fnt", "green12.fnt"),
    4: ("blue", "blue.fnt", "blue10.fnt", "blue12.fnt"),
    5: ("grey", "gryfnt.fnt", "gryfnt10.fnt", "gryfnt12.fnt"),
    6: ("white", "white.fnt", "white10.fnt", "white12.fnt"),
    7: ("dim", "dim.fnt", "dim10.fnt", "dim12.fnt"),
    8: ("yellow drop-shadow", "yelldrp.fnt", "(dim10.fnt?)", "(not set)"),
    9: ("blue drop-shadow", "bluedrp.fnt", "(dim10.fnt?)", "(not set)"),
}

NAME_PATTERNS = [  # (regex on file name, kind)
    (r"^(brf\d+)([a-z]*)\.txt$", "single-player mission briefing (original campaign)"),
    (r"^xbrf\d+\.txt$", "expansion campaign briefing"),
    (r"^xsbrf\d+\.txt$", "expansion solo-mission briefing"),
    (r"^cbrf\d+", "multiplayer briefing, Clan side"),
    (r"^isbrf\d+", "multiplayer briefing, Inner Sphere side"),
    (r"^c(?!brf)", "named map briefing, Clan side"),
    (r"^is(?!brf)", "named map briefing, Inner Sphere side"),
]

SUFFIX_NOTE = {   # suffixes of unreferenced variants; the meaning is a guess from the name only
    "k": "variant with suffix 'k' of the base briefing; no FIT references it",
    "hh": "variant with suffix 'hh' of the base briefing; no FIT references it",
    "mb": "variant with suffix 'mb' of the base briefing; no FIT references it",
    "rs": "variant with suffix 'rs' of the base briefing; no FIT references it",
    "rsc": "variant with suffix 'rsc' of the base briefing; no FIT references it",
    "c": "variant with suffix 'c' of the base briefing; no FIT references it",
    "s": "variant with suffix 's' of the base briefing; no FIT references it",
    "m": "variant with suffix 'm' of the base briefing; no FIT references it",
}
CAMPAIGN_PRIORITY = ["original", "expansion", "solo", "multiplayer", "dev/test", "unknown"]


def fit_files():
    return sorted(p for p in MISSION.iterdir() if p.suffix.lower() == ".fit")


def mission_campaign(fit_name: str, key: str) -> str:
    """Campaign a mission FIT belongs to (decided from the FIT name, confirmed by mechcmdr1.fit / Xmechcmdr1.fit)."""
    n = fit_name.lower()
    if re.match(r"mis\d{4}", n):
        return "original"
    if re.match(r"mcxs\d{4}", n):
        return "solo"            # MCXS04xx: the expansion's stand-alone solo missions (listed in mechcmdr1.fit, not in Xmechcmdr1.fit)
    if re.match(r"mcx\d{4}", n):
        return "expansion"
    if n.startswith(("acehunt", "paredux", "theguns")):
        return "solo"
    if n.startswith("mp") or n.startswith("mxm"):
        return "multiplayer"
    if key in ("ISBriefingFile", "ClanBriefingFile"):
        return "multiplayer"     # named maps (Achilles, Bakwoods, ...): two-sided briefings, no objectives of their own
    if n.startswith(("e3_", "testmis", "mise")):
        return "dev/test"
    return "unknown"


def scan_references():
    refs = defaultdict(list)       # lower-case txt name -> [{fit, key}]
    empty = []
    for p in fit_files():
        txt = read_text(p)
        for m in re.finditer(r'^\s*st\s+((?:IS|Clan)?BriefingFile)\s*=\s*"([^"]*)"', txt, re.M | re.I):
            key, val = m.group(1), m.group(2).strip()
            if not val:
                empty.append(p.name)
                continue
            refs[val.lower()].append({"fit": p.name, "key": key})
    return refs, empty


def tokenize(text: str):
    """Yield (code, argument, position) following SMUTI::process semantics."""
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch != "%":
            i += 1
            continue
        if i + 1 >= n:
            yield ("%<eof>", None, i)
            break
        c = text[i + 1]
        lc = c.lower()
        if lc == "%":
            yield ("%%", None, i)
            i += 2
        elif lc in "cn":
            yield ("%" + lc, None, i)
            i += 2
        elif lc == "t":
            j = i + 2
            while j < n and text[j].isdigit():
                j += 1
            yield ("%t", text[i + 2:j], i)
            i = j
        elif lc == "f":
            if i + 2 >= n:
                yield ("%f<eof>", None, i)
                break
            s = text[i + 2].lower()
            if s == "c":
                d = text[i + 3] if i + 3 < n else ""
                yield ("%fc", d, i)
                i += 4
            elif s in "sml":
                yield ("%f" + s, None, i)
                i += 3
            else:
                yield ("%f" + text[i + 2], "ignored", i)
                i += 3
        else:
            yield ("%" + c, "literal", i)
            i += 2


def code_label(code, arg):
    if code == "%fc":
        return f"%fc{arg}" if arg.isdigit() else f"%fc<{arg!r}>"
    if code == "%t":
        return "%tN"
    return code


def analyse_text(text: str):
    counts = Counter()
    tabs = Counter()
    for code, arg, _pos in tokenize(text):
        counts[code_label(code, arg)] += 1
        if code == "%t":
            tabs[arg] += 1
    return counts, tabs


def run():
    refs, empty_refs = scan_references()
    txts = sorted((p for p in MISSION.iterdir() if p.suffix.lower() == ".txt"), key=lambda p: p.name.lower())
    entries = []
    all_counts = Counter()
    all_tabs = Counter()
    files_using = defaultdict(set)
    nonascii_files = []
    unref = []
    for p in txts:
        raw = p.read_bytes()
        text = raw.decode("cp1252")
        counts, tabs = analyse_text(text)
        all_counts.update(counts)
        all_tabs.update(tabs)
        for k in counts:
            files_using[k].add(p.name)
        if any(b > 127 for b in raw):
            nonascii_files.append(p.name)
        r = refs.get(p.name.lower(), [])
        # campaign from the referencing FITs
        camps = sorted({mission_campaign(x["fit"], x["key"]) for x in r}, key=CAMPAIGN_PRIORITY.index)
        if not r:
            camps_from_name = None
            n = p.name.lower()
            if re.match(r"brf\d{4}", n):
                camps_from_name = "original"
            elif re.match(r"xbrf", n):
                camps_from_name = "expansion"
            elif re.match(r"xsbrf", n):
                camps_from_name = "solo"
            elif re.match(r"(c|is)brf07", n) or "mxm" in n:
                camps_from_name = "multiplayer"
            elif re.match(r"(c|is)[a-z]", n):
                camps_from_name = "multiplayer"
            else:
                camps_from_name = "unknown"
            camps = [camps_from_name]
            unref.append(p.name)
        kind = next((k for rx, k in NAME_PATTERNS if re.search(rx, p.name.lower())), "briefing")
        m = re.match(r"(?:c|is)?brf\d{4}([a-z0-9]*)\.txt", p.name.lower())
        suffix = m.group(1) if m else ""
        e = {
            "file": f"MISSION.FST/{p.name}",
            "game_path": f"data\\missions\\{p.name}",
            "size_bytes": len(raw),
            "lines": text.count("\n") + (0 if text.endswith("\n") else 1),
            "kind": kind,
            "campaign": camps[0],
            "also_used_by_campaigns": camps[1:],
            "referenced_by": [f"{x['fit']} ({x['key']})" for x in r],
            "referenced": bool(r),
            "markup_codes": dict(sorted(counts.items())),
            "briefing_like": bool(counts),
        }
        if not r:
            e["campaign_basis"] = "file name only (no mission FIT references it)"
        if not r:
            e["note"] = SUFFIX_NOTE.get(suffix, "not referenced by any mission FIT in MISSION.FST")
        entries.append(e)

    camp_counts = Counter(e["campaign"] for e in entries)
    ref_counts = Counter(e["campaign"] for e in entries if e["referenced"])
    write_json(OUT / "briefings.json", {
        "summary": {
            "txt_files": len(entries),
            "briefing_like_files": sum(1 for e in entries if e["briefing_like"]),
            "referenced_by_a_mission_fit": sum(1 for e in entries if e["referenced"]),
            "unreferenced": [e["file"].split("/")[1] for e in entries if not e["referenced"]],
            "files_per_campaign": dict(camp_counts),
            "total_bytes": sum(e["size_bytes"] for e in entries),
            "non_ascii_files": nonascii_files,
            "fits_with_empty_briefing_file": sorted(set(empty_refs)),
            "campaign_meaning": {
                "original": "MechCommander Gold campaign (MIS0101..MIS0507, brf*.txt)",
                "expansion": "MechCommander Expansion campaign (MCX0101..MCX0304 = Xmechcmdr1.fit; xbrf*.txt)",
                "solo": "expansion stand-alone solo missions MCXS0401/0402, AceHunt, PARedux, TheGuns (xsbrf*.txt, "
                        "campaignAceHunt.fit ...), started from the 'solo' load screen",
                "multiplayer": "two-sided briefings (IS* / C*): MP07xx maps, MXM0502 and the named maps Achilles, Bakwoods, "
                               "caldera, CaptIsld, DValley, HvrDmmt, KingIsle, MouseTrp, Urbana, WetNWild",
            },
        },
        "files": entries,
    })
    write_markup(all_counts, all_tabs, files_using, len(entries))
    return entries, camp_counts, ref_counts


def desc_fit_markup():
    """Same renderer is used for MISC.FST/desc.fit (component descriptions)."""
    p = MISC / "desc.fit"
    if not p.exists():
        return Counter(), Counter(), 0
    counts, tabs = Counter(), Counter()
    n = 0
    for m in re.finditer(r'st\s+DescString\s*=\s*"(.*)"', read_text(p)):
        n += 1
        c, t = analyse_text(m.group(1))
        counts.update(c)
        tabs.update(t)
    return counts, tabs, n


MEANING = {
    "%n": ("newline", "flush the pending text and start a new line (x=0, y += font height + 1). Plain CR/LF in the file are ignored."),
    "%c": ("centre", "centre the text that follows, up to the next `%` code (at most 80 characters are measured)."),
    "%fs": ("font size 0", "small font of the current colour (`<name>.fnt`, e.g. `white.fnt`)."),
    "%fm": ("font size 1", "medium font (`<name>10.fnt`)."),
    "%fl": ("font size 2", "large font (`<name>12.fnt`)."),
    "%tN": ("horizontal gap", "`%t` + decimal digits N: advance the pen by N pixels (hanging indents, column alignment). No glyph is drawn."),
    "%%": ("literal %", "a single percent sign."),
}


def write_markup(counts, tabs, files_using, nfiles):
    dcounts, dtabs, ndesc = desc_fit_markup()
    colour_codes = sorted((k for k in counts if re.fullmatch(r"%fc\d", k)), key=lambda k: int(k[3:]))
    other = sorted(k for k in counts if k not in MEANING and k not in colour_codes)
    L = ["# Text markup (`%` codes) used in briefings and descriptions", "",
         "Decoded from `SMUTI::process` in MCX.EXE (VA 0x728ed0).  SMUTI renders the briefing `.txt` files "
         "(`Logistics::getCurrentMission` -> `SMUTI::init`), the component descriptions of `MISC.FST/desc.fit` "
         "(`DescString`), the drag-icon popup of the repair screen and the chat windows.", "",
         f"Counts below are over the {nfiles} `.txt` files in `MISSION.FST` (column *briefings*) and over the "
         f"{ndesc} `DescString` values of `MISC.FST/desc.fit` (column *desc.fit*).  Codes are case-insensitive "
         "(`%FC1` = `%fc1`); counts fold the two spellings together only where noted.", "",
         "## Codes", "", "| code | meaning | briefings (uses) | briefings (files) | desc.fit (uses) | reading |", "|---|---|---:|---:|---:|---|"]
    for k in ("%n", "%c", "%fs", "%fm", "%fl", "%tN", "%%"):
        nm, rd = MEANING[k]
        L.append(f"| `{k}` | {nm} | {counts.get(k, 0)} | {len(files_using.get(k, ()))} | {dcounts.get(k, 0)} | {rd} |")
    for k in colour_codes:
        idx = int(k[3:])
        nm = FONT_COLOURS.get(idx, ("?",))[0]
        L.append(f"| `{k}` | colour {idx} ({nm}) | {counts[k]} | {len(files_using[k])} | {dcounts.get(k, 0)} | "
                 f"`%fc` + one digit selects the colour row of the font table: {FONT_COLOURS.get(idx, ('?', '?'))[1]} |")
    for k in sorted(set(dcounts) - set(counts) - set(MEANING)):
        if k not in colour_codes and k.startswith("%fc"):
            idx = int(k[3:]) if k[3:].isdigit() else None
            nm = FONT_COLOURS.get(idx, ("?",))[0] if idx is not None else "?"
            L.append(f"| `{k}` | colour {idx} ({nm}) | 0 | 0 | {dcounts[k]} | desc.fit only |")
    for k in other:
        L.append(f"| `{k}` | not a SMUTI code | {counts[k]} | {len(files_using[k])} | {dcounts.get(k, 0)} | emitted literally ('%' + the character) |")
    L += ["", "### `%tN` values seen", "",
          "briefings: " + ", ".join(f"`%t{k}` x{v}" for k, v in sorted(tabs.items(), key=lambda kv: int(kv[0] or 0))) if tabs else "none",
          "", "desc.fit: " + (", ".join(f"`%t{k}` x{v}" for k, v in sorted(dtabs.items(), key=lambda kv: int(kv[0] or 0))) or "none"),
          "", "## Colour / size table (`fonts[colour][size]`, filled in `aSystem::start`)", "",
          "| `%fcN` | colour | `%fs` | `%fm` | `%fl` |", "|---:|---|---|---|---|"]
    for idx, (nm, a, b, c) in FONT_COLOURS.items():
        L.append(f"| {idx} | {nm} | {a} | {b} | {c} |")
    L += ["", "Font files are in `MISC.FST` (`*.FNT`, bitmaps in `ART.FST/data/art/logart/*.tga`).  Colours 8 and 9 only "
          "define the base size; `%fm/%fl` after them select the entries that `aSystem::start` leaves partly unset "
          "(the disassembly assigns `dim10.fnt` to slots 25 and 28), so avoid size changes after `%fc8/%fc9`.", "",
          "## Behaviour that matters for translation", "",
          "* **Line breaks** in the file are meaningless: CR, LF and TAB (anything below 0x20) are skipped. Only `%n` ends a line. "
          "A blank line is `%n%n`.",
          "* **Word wrap** is automatic at the last space (0x20) before the pen passes the port width; there is no hyphenation. "
          "Text without spaces wraps only at the very last character that fits.",
          "* **Last two bytes dropped**: `SMUTI::init` reads the whole file and writes a NUL at `length-2`.  Every file therefore "
          "needs at least two trailing bytes (the usual CR LF) after the last visible character, otherwise the last "
          "characters are cut.",
          "* **Pending text buffer** is 256 bytes (`SMUTI+0x20..+0x120`); wrapping flushes it, but a single unbroken run longer "
          "than that between two codes overflows.",
          "* **`%c` measures at most 80 characters** (stack buffer of 0x50 bytes) and centres a single line.",
          "* **Per-byte rendering**: every byte is looked up in the current `aFont` with `aFont::width(byte)`; there is no "
          "multi-byte (DBCS) handling in SMUTI itself.",
          "* **Apostrophes**: the text uses a back-tick for some apostrophes (`` `Mechs``) and a straight quote for others "
          "(`'Mechs`).  Both glyphs exist in the fonts; keep whichever the original used when copying names such as `'Mech`.",
          "* **`%d`-style printf codes are not interpreted** here (`%s`, `%i` ... belong to the EXE string table, see `strings.json`); "
          "a bare `%` followed by an unknown letter prints the percent sign and the letter.", ""]
    write_text(OUT / "markup.md", "\n".join(L))


if __name__ == "__main__":
    from loc_common import utf8_stdout
    utf8_stdout()
    entries, camp, ref = run()
    print("txt files:", len(entries), dict(camp), "referenced:", dict(ref))
