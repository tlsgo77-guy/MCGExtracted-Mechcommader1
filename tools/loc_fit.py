"""Collect the player-facing `st` strings of the FIT / CSV data files.

Output (see extract_text.py):
    localization/en/fit_strings.json          [{file, section, key, text, category, scope, ...}]
    localization/en/fit_strings_summary.md    per-file counts + notes on ambiguous sources

Identifiers (file names, art names, brains, profiles, palettes, movie names ...) are deliberately left out.
A FIT line looks like   `st Key = "text"   // comment`   inside a `[Section]`; types other than `st`
carry numbers only.
"""
from __future__ import annotations

import csv
import io
import re
from collections import Counter, OrderedDict, defaultdict

from loc_briefings import mission_campaign
from loc_common import MISC, MISSION, OUT, md_cell, read_text, write_json, write_text

SECTION_RE = re.compile(r"^\s*\[([^\]]*)\]")
ST_RE = re.compile(r"^\s*st\s+(.+?)\s*=\s*\"")


def parse_st(line: str):
    """Return (key, text) for a `st Key = "text" // comment` line, else None.  The closing quote is the last
    quote followed only by whitespace or a // comment."""
    m = ST_RE.match(line)
    if not m:
        return None
    start = m.end()
    for j in range(len(line) - 1, start - 1, -1):
        if line[j] != '"':
            continue
        rest = line[j + 1:].strip()
        if rest == "" or rest.startswith("//"):
            return m.group(1), line[start:j]
    return None


def fit_lines(path):
    """Yield (section, key, text) for every `st` line of a FIT file."""
    section = ""
    for raw in read_text(path).splitlines():
        m = SECTION_RE.match(raw)
        if m:
            section = m.group(1)
            continue
        r = parse_st(raw)
        if r:
            yield section, r[0], r[1]


def rel(path):
    return f"{path.parent.name}/{path.name}"


def unique_fits(folder, pattern_re):
    """Case-insensitive unique file list (Windows globs are case-insensitive, duplicates must be avoided)."""
    seen, out = set(), []
    for p in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if p.name.lower() in seen:
            continue
        if re.fullmatch(pattern_re, p.name, re.I):
            seen.add(p.name.lower())
            out.append(p)
    return out


def compbas_names():
    """component id -> (name, abbr) from MISC.FST/compbas.csv"""
    out = OrderedDict()
    p = MISC / "compbas.csv"
    if not p.exists():
        return out
    for row in csv.reader(io.StringIO(read_text(p))):
        if not row or row[0].strip().startswith("//") or not row[0].strip().isdigit() or len(row) < 3:
            continue
        out[int(row[0])] = (row[1].strip(), row[2].strip())
    return out


def collect():
    E = []

    def add(path, section, key, text, category, scope, **extra):
        e = {"file": rel(path), "section": section, "key": key, "text": text, "category": category, "scope": scope}
        e.update({k: v for k, v in extra.items() if v not in ("", None)})
        E.append(e)

    # ---- mission FITs: objective names -------------------------------------------------------------------
    for p in unique_fits(MISSION, r".*\.fit"):
        campaign = mission_campaign(p.name, "BriefingFile")
        txt = read_text(p)
        if "[Objective" in txt:
            camp = campaign
            if re.search(r'^\s*st\s+(IS|Clan)BriefingFile', txt, re.M | re.I):
                camp = "multiplayer"
            for section, key, text in fit_lines(p):
                if re.fullmatch(r"Objective\d+", section) and key == "Name":
                    add(p, section, key, text, "mission objective name", "in-mission + results", campaign=camp)

    # ---- pilots ------------------------------------------------------------------------------------------
    for p in unique_fits(MISSION, r"(war\d+a?|PMW\d+|PCREW[A-Z])\.fit"):
        is_dev = p.name.lower().startswith("war")
        for section, key, text in fit_lines(p):
            if section == "General" and key in ("Name", "Callsign"):
                cat = "pilot name" if key == "Name" else "pilot callsign"
                if p.name.lower().startswith("pcrew"):
                    cat = "vehicle crew " + cat.split()[1]
                add(p, section, key, text, cat, "pre-mission (pilot roster) + results",
                    note="developer test pilot (war*.fit, names are dev-team members)" if is_dev else "")

    # ---- mech / vehicle / elemental profiles (designations, not the displayed names) ----------------------
    for p in unique_fits(MISSION, r"(PM\d+|PV\d+|PE\d+|Pem\d+)\.fit"):
        txt = read_text(p)
        ftype = (re.search(r'FileType\s*=\s*"(\w+)"', txt) or [None, ""])[1]
        d = re.search(r"DescIndex\s*=\s*(\d+)", txt)
        sid = None
        if d:
            sid = int(d.group(1)) + (300 if ftype == "MechProfile" else 700)
        for section, key, text in fit_lines(p):
            if section == "General" and key in ("Name", "MechType"):
                cat = {"MechProfile": "mech variant", "GroundVehicleProfile": "vehicle"}.get(ftype, "profile")
                extra = {"exe_string_id": sid} if sid else {}
                add(p, section, key, text, f"{cat} designation ({key})", "reference only",
                    note="not drawn by the logistics screens: the displayed name is the EXE string table entry "
                         "DescIndex+300 (mechs) / +700 (vehicles)", **extra)

    # ---- MISC.FST ------------------------------------------------------------------------------------------
    comp = compbas_names()
    p = MISC / "desc.fit"
    if p.exists():
        cur_comment = {}
        sec = None
        for raw in read_text(p).splitlines():
            m = SECTION_RE.match(raw)
            if m:
                sec = m.group(1)
                c = re.search(r"\]\s*//\s*(.*)$", raw)
                cur_comment[sec] = c.group(1).strip() if c else ""
        for section, key, text in fit_lines(p):
            n = re.fullmatch(r"Desc(\d+)", section)
            extra = {}
            if n:
                cid = int(n.group(1))
                extra["component_id"] = cid
                if cid in comp:
                    extra["component_name"] = comp[cid][0]
                if cur_comment.get(section):
                    extra["developer_comment"] = cur_comment[section]
            if "REPORT IT AS A BUG" in text:
                extra["note"] = "placeholder shown only for components without a real description"
            add(p, section, key, text, "component description (SMUTI markup)", "pre-mission (purchase / inventory / repair)", **extra)
    p = MISC / "MECHTEXT.FIT"
    if p.exists():
        for section, key, text in fit_lines(p):
            add(p, section, key, text, "mech panel heading / location / damage state", "pre-mission + in-mission (mech detail panels)")
    p = MISC / "MECHREP.FIT"
    if p.exists():
        for section, key, text in fit_lines(p):
            if key.lower() == "name":
                add(p, section, key, text, "mech repair diagram box label", "pre-mission (repair screen)")
    p = MISC / "Menus.fit"
    if p.exists():
        for section, key, text in fit_lines(p):
            if key.startswith("ItemHelp"):
                add(p, section, key, text, "command-palette tooltip", "in-mission",
                    note="only 2 of the palette items define a tooltip (developer jokes: 'Baby, you move me!', 'Get Mad!')")
    # compbas.csv: component names / abbreviations
    p = MISC / "compbas.csv"
    for cid, (name, abbr) in comp.items():
        if name.lower() in ("undefined", "na", ""):
            continue
        add(p, f"component {cid}", "name", name, "component name", "pre-mission (purchase / inventory / repair)", component_id=cid)
        if abbr.lower() not in ("undefined", "na", "") and abbr != name:
            add(p, f"component {cid}", "abbr", abbr, "component abbreviation", "pre-mission (inventory tables)", component_id=cid)
    return E


def write_outputs(E):
    write_json(OUT / "fit_strings.json", E, indent=1)
    by_file = OrderedDict()
    for e in E:
        by_file.setdefault(e["file"], Counter())[e["category"]] += 1
    groups = OrderedDict()
    for f, c in by_file.items():
        name = f.split("/")[1]
        g = ("MISSION.FST mission FITs (objectives)" if f.startswith("MISSION.FST") and "mission objective name" in c
             else "MISSION.FST pilots (war*/PMW*/PCREW*)" if re.match(r"(war|pmw|pcrew)", name, re.I)
             else "MISSION.FST mech/vehicle profiles (PM*/PV*/PE*)" if f.startswith("MISSION.FST")
             else f)
        groups.setdefault(g, [0, 0])
        groups[g][0] += 1
        groups[g][1] += sum(c.values())
    L = ["# FIT / CSV strings that matter before (and around) a mission", "",
         f"{len(E)} entries in `fit_strings.json` (fields: file, section, key, text, category, scope + extras).", "",
         "## Counts per source", "", "| source | files | strings |", "|---|---:|---:|"]
    for g, (nf, ns) in groups.items():
        L.append(f"| {md_cell(g)} | {nf} | {ns} |")
    L.append(f"| **total** | **{len(by_file)}** | **{len(E)}** |")
    uniq = len({e['text'] for e in E})
    cat = Counter(e["category"] for e in E)
    L += ["", f"Unique texts: {uniq}.  Entries per category:", ""]
    L += [f"* {c}: {n}" for c, n in cat.most_common()]
    objs = [e for e in E if e["category"] == "mission objective name"]
    per_campaign = Counter(e.get("campaign") for e in objs)
    L += ["", "Objective names per campaign (entries, duplicates across variant FITs included): " +
          ", ".join(f"{k} {v}" for k, v in per_campaign.items()) +
          f"; unique objective texts: {len({e['text'] for e in objs})}.", "",
          "## Per-file counts", ""]
    skipped = 0
    for f, c in by_file.items():
        if re.match(r"MISSION\.FST/(PMW|PM\d|PV|Pv|PE|Pem|PCREW|war)", f, re.I):
            skipped += 1
            continue
        L.append(f"* `{f}`: {sum(c.values())}")
    L.append(f"* ({skipped} pilot / crew / mech / vehicle profile files with 1-2 strings each are not listed one by one)")
    L += ["", "## Notes and ambiguous sources", "",
          "* **Objective names** (`[ObjectiveN] st Name`) are the only free text in a mission FIT.  They are shown in the in-mission "
          "objective list and on the results screen (`MissionResultsScreen::drawObjectives`), not on the briefing screen "
          "(the briefing prose lives in `brfXXXX.txt`, see `briefings.json`).  There is no mission *title* field: titles such as "
          "`***LIBERATE WORK CAMPS***` are the first lines of the briefing text.",
          "* **`campaign*.fit`, `mechcmdr1.fit`, `Xmechcmdr1.fit`, `purchase*.fit`, `xpurchase*.fit`, `solopurchase.fit`, "
          "`soloispurchase.fit`, `netpur.fit`, `clanpur.fit`, `ispur.fit`, `xpur.fit`**: no player-facing text at all "
          "(movie names, mission file names, purchase file names, numbers).  Nothing extracted.",
          "* **Pilots**: `PMW*.FIT` carry the roster names and callsigns (`Hitman / HITMAN`, `Countess`, ...) plus a portrait name "
          "(`Picture = pilot16.TGA`, see `art.json`).  `war*.fit` are developer test pilots (Amy Bios, Kermit, Piggy ...).  Many `PMW` "
          "files are generic AI crews (`Allied`, `Clan`, `CLAN GREEN`).  There are **no pilot bios** in any FIT (`DescIndex` is empty).",
          "* **Mech / vehicle profiles**: `General.Name` (`COM-A`) and `General.MechType` (`Commando A`) are developer designations; the "
          "logistics screens show the EXE string `DescIndex + 300` (mechs) / `+ 700` (vehicles) instead (`LogMechList::addMech`).  They are "
          "listed with `exe_string_id` so the two can be kept consistent.",
          "* **`desc.fit`** uses the `%` markup of `markup.md`; `Desc<N>` = component id `N` of `compbas.csv` (name added as `component_name`).  "
          "Entries containing `IF YOU SEE THIS DESCRIPTION PLEASE REPORT IT AS A BUG` are placeholders for components that never got text.",
          "* **`compbas.csv`**: only the `name` and `abbr` columns are text; `type` (Engine, Actuator, ...) and `side` (IS/Clan/Both) are "
          "parsed by the game as keywords and must not be translated.  Rows named `undefined` are skipped.",
          "* **`MECHTEXT.FIT`** headings are used by the mech status panels (both in the logistics repair/purchase screens and in the mission); "
          "`MECHREP.FIT` `name` fields label the damage diagram boxes.",
          "* **`Menus.fit`**: `ItemHelp` exists for two command-palette entries only.  The menu items themselves are art (`Action`, `Att`, `Role` "
          "shape sets).  In-mission.",
          "* **`radio.csv`**: pure data (`RADIO_MOVETO,priority,shelflife,movie,...`); the spoken text is audio.  In-mission only, nothing to translate.",
          "* **`IFACE.FIT`, `windows.fit`, `allcomp.fit`, `CAMERAS.FIT`, `Palette*.fit`, `cursor.fit`**: shape/palette/layout data, no text "
          "(`allcomp.fit` has the component names only in `//` comments).",
          "* **ART.FST screen FITs** (`mainscreen`, `prefscreen`, `lanscreen`, `loadscreen`, `savescreen`, `modem`, `readyroom`, `mpscreen`, "
          "`serial`) contain *no* text: every label of those screens is baked into the TGA buttons, see `art.json`.  Their `//` comments "
          "(`// new cermak`, `// save`, `// multi-player` ...) were used to annotate the art.",
          "* **ABL scripts** (`*.ABL`, 774 files) contain only developer debug strings (`Gametime: `, `Moving to Step `...), no player text.", ""]
    write_text(OUT / "fit_strings_summary.md", "\n".join(L))


def run():
    E = collect()
    write_outputs(E)
    print("fit strings:", len(E), Counter(e["category"] for e in E).most_common())
    return E


if __name__ == "__main__":
    from loc_common import utf8_stdout
    utf8_stdout()
    run()
