#!/usr/bin/env python3
"""Build localization/ko/names_map.json (the name-plate texts for tools/relabel_tga.py) from glossary.json.

    python -I tools/build_names_map.py            # writes localization/ko/names_map.json
    python -I tools/build_names_map.py --check    # only report coverage

Source: the `art_plates` category of localization/ko/glossary.json ({en, ko, note}: `en` = the text baked into the
plate TGA, i.e. the `text_guess` of the plate in localization/en/art.json).  Result (grouped, as relabel_tga.py reads it):

    {"mechs": {"ATLAS-A": "..."}, "vehicles": {...}, "components": {...}, "pilots": {...}}

Every plate TGA of the families LSCFL[MV], LSPFL[MVCP], LSPFD[MVC] (data/art/logart) is looked up by its `text_guess`;
plates whose text is not in the glossary are listed (they are skipped by relabel_tga.py: names are never guessed).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KO = REPO / "localization" / "ko"
GLOSSARY = KO / "glossary.json"
ART_JSON = REPO / "localization" / "en" / "art.json"
OUT = KO / "names_map.json"

FAMILY = {"m": "mechs", "v": "vehicles", "c": "components", "p": "pilots"}
PLATE = re.compile(r"data/art/logart/ls[cp]f[ld]([mvcp])\w+\.tga$", re.I)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    gloss = json.loads(GLOSSARY.read_text(encoding="utf-8"))["art_plates"]
    ko = {}
    for e in gloss:
        if e["en"] in ko and ko[e["en"]] != e["ko"]:
            sys.exit("conflicting glossary entries for %r: %r / %r" % (e["en"], ko[e["en"]], e["ko"]))
        ko[e["en"]] = e["ko"]
    groups = {g: {} for g in FAMILY.values()}
    missing = []
    for e in json.loads(ART_JSON.read_text(encoding="utf-8")):
        m = PLATE.search(e["file"])
        if not m:
            continue
        guess = e.get("text_guess", "")
        if guess in ko:
            groups[FAMILY[m.group(1).lower()]][guess] = ko[guess]
        else:
            missing.append((e["file"], guess))
    unused = sorted(set(ko) - {k for g in groups.values() for k in g})
    for g, d in groups.items():
        print("%-11s %3d texts" % (g, len(d)))
    print("plates whose text is not in the glossary: %d" % len(missing))
    for f, g in missing:
        print("   %s  %r" % (f, g))
    if unused:
        print("glossary art_plates entries no plate uses:", unused)
    if not args.check:
        OUT.write_text(json.dumps(groups, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("wrote", OUT)


if __name__ == "__main__":
    main()
