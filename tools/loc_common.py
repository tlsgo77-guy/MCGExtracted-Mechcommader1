"""Shared helpers for the localization extraction scripts (tools/extract_text.py and friends).

All paths are derived from the repository root (the parent of this tools/ folder) so the
scripts can be rerun from anywhere:

    python tools/extract_text.py all
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "localization" / "en"
MISSION = REPO / "MISSION.FST"
MISC = REPO / "MISC.FST"
ART = REPO / "ART.FST"
GAME = REPO / "game-source" / "extracted" / "MCX"          # git-ignored local game install
EXE = GAME / "MCX.EXE"
SYMBOLS = REPO / "game-source" / "extracted" / "rea-test" / "mcx_symbols.json"


def utf8_stdout() -> None:
    """Python on Windows may default to cp949; force UTF-8 for console output."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def write_json(path: Path, obj, indent: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_text(path: Path) -> str:
    """Read an old DOS/Win32-era text file (CRLF, ASCII or cp1252)."""
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def md_cell(s: object) -> str:
    """Escape a value for a Markdown table cell."""
    return str(s).replace("|", "\\|").replace("\n", "\\n").replace("\r", "")
