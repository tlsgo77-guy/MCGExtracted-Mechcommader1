"""Rebuild everything in localization/en/ (the English source texts of MechCommander Gold / Expansion).

    python tools/extract_text.py            # all steps
    python tools/extract_text.py strings    # EXE string table + which screen uses which id
    python tools/extract_text.py briefings  # briefing .txt inventory + markup.md
    python tools/extract_text.py fit        # player-facing FIT / CSV strings
    python tools/extract_text.py art        # TGA inventory + contact sheets (add --no-sheets to skip the PNGs)

Requirements: Python 3.10+, `pip install capstone pillow` (capstone is only needed for `strings` and the
`used_by_code` column of `art`; set MCG_CAPSTONE_PATH=<folder containing capstone> if it is not installed).
Inputs are read from the repo (MISSION.FST/, MISC.FST/, ART.FST/, data/objects/OBJECT2.PAK/) and from the local, git-ignored
game install in game-source/extracted/MCX/ (MCX.EXE, ART.FST, TERRAIN.FST, mcx_symbols.json next to it in ../rea-test/).
Nothing in the game files is modified.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from loc_common import OUT, utf8_stdout  # noqa: E402


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", nargs="?", default="all", choices=["all", "strings", "briefings", "fit", "art"])
    ap.add_argument("--no-sheets", action="store_true", help="art: only rewrite art.json, do not render the contact sheets")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.step in ("all", "strings"):
        import loc_strings
        loc_strings.run()
    if a.step in ("all", "briefings"):
        import loc_briefings
        entries, camp, ref = loc_briefings.run()
        print("briefings:", len(entries), dict(camp))
    if a.step in ("all", "fit"):
        import loc_fit
        loc_fit.run()
    if a.step in ("all", "art"):
        import loc_art
        loc_art.run(sheets=not a.no_sheets)


if __name__ == "__main__":
    main()
