r"""Build the Korean overlay of MechCommander Gold from the UTF-8 translation sources.

Reads  localization/ko/            (UTF-8 JSON / text written by the translators)
Writes <game-dir>\lang\kor\        (EUC-KR, CRLF; only files that differ from the originals)

The patched MCX.EXE (patches/patch_korean_io.py), when prefs `l Language=1`, reads UI strings from
lang\kor\strings.bin and tries lang\kor\data\... before every data\... file; files that are not in the
overlay fall back to the originals.

Sources (every one is optional, a missing one is skipped with a note):

  strings    localization/ko/strings.json          {"31": "..."}      -> lang\kor\strings.bin
                                                   (tools/build_strings_bin.py does the encoding + validation)
  briefings  localization/ko/briefings/<name>.txt                     -> lang\kor\data\missions\<name>.txt
             UTF-8 -> EUC-KR + CRLF, trailing CRLF guaranteed (SMUTI drops the last two bytes), `%` markup
             codes compared with the English original (warn), `%c` segments > 80 bytes (error), lines > 253
             bytes (warn)
  fit        localization/ko/fit_strings.json      [{file, section, key, en, ko}]
             -> a copy of every touched MISSION.FST / MISC.FST text file with only the `st Key = "..."` values
                (or compbas.csv name/abbr cells) replaced; the destination is the file's own path inside the
                game's FST (lang\kor\data\missions\..., ...\warriors\..., ...\profiles\..., data\objects\...,
                data\iface\...)
  pilots     localization/ko/pilots.json           {"Hawk": {"name": ..., "callsign": ...}}
             -> lang\kor\data\savegame\START0.PKK / XSTART0.PKK (the installed roster files with the warrior
                packets' `st Name` / `st Callsign` replaced, RAW packets + checksum header)
             --warrior-fits additionally writes Korean copies of the warrior profiles (PMW*.FIT hireable pilots,
             war*.fit ...) whose [General] Name is in pilots.json, unless fit_strings.json already translates the file

Text is encoded strictly as KS X 1001 (Python's euc_kr codec silently writes 8-byte jamo sequences for
syllables outside the 2350 set; build_strings_bin.encode() rejects them and so does this tool).

usage: python tools/build_korean_overlay.py [--game-dir DIR] [--repo DIR] [--out DIR]
                                            [--only strings|briefings|fit|pilots] [--check] [--strict]
                                            [--warrior-fits] [--roster-dir DIR] [-v]
Exit status 1 if any source has a hard error (bad encoding, %c overflow, unknown FIT key ...).  Files with an
error are not written; `--check` validates everything and writes nothing.  Output is deterministic.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import build_strings_bin as bsb  # noqa: E402  (strict KS X 1001 encoder / strings.bin writer)
import loc_fst  # noqa: E402  (FST archive reader)
import mcg_pkk  # noqa: E402  (PacketFile / build_packet_file)

REPO = TOOLS.parent
SOURCES = ("strings", "briefings", "fit", "pilots")
CENTRE_LIMIT = 80          # SMUTI measures at most 80 bytes after %c (stack buffer 0x50)
LINE_WARN = 253            # warn above this many bytes per line
FMT_RE = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?[hlL]?[diuxXfFeEgGcsp]|%%")     # same as loc_strings.FMT_RE
SECTION_RE = re.compile(rb"^\s*\[([^\]]*)\]")                                 # same as loc_fit.SECTION_RE
ST_RE = re.compile(rb"^\s*st\s+(.+?)\s*=\s*\"")                               # same as loc_fit.ST_RE
# longest English values in the rosters / pilot FITs (localization/en/fit_strings.json): 25 and 16 characters
PILOT_NAME_WARN = 25
PILOT_CALLSIGN_WARN = 16
FORBIDDEN_OVERLAY_DIRS = (("data", "art"), ("data", "fonts"))       # written by other tools


# ----------------------------------------------------------------------------------------------- reporting
@dataclass
class Out:
    rel: str                  # path below the overlay root, backslash separated
    path: Path
    data: bytes
    status: str = ""          # written / unchanged / would write / would create
    derived: bool = False     # generated from pilots.json (--warrior-fits); yields to an explicit fit_strings.json entry


@dataclass
class Source:
    name: str
    skipped: str = ""
    outputs: list = field(default_factory=list)
    warnings: list = field(default_factory=list)     # (label, message)
    errors: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    info: str = ""            # short "what was read" text for the table

    def warn(self, label, msg):
        self.warnings.append((label, msg))

    def err(self, label, msg):
        self.errors.append((label, msg))

    def note(self, msg):
        self.notes.append(msg)


# ----------------------------------------------------------------------------------------------- encoding
def nfc(text: str) -> str:
    """Hangul typed on macOS or pasted from some editors arrives as decomposed jamo; the font needs syllables."""
    return unicodedata.normalize("NFC", text)


def encode_text(label: str, text: str, src: Source, *, string_table: bool = False):
    """Strict KS X 1001 encoding through build_strings_bin.encode(); returns bytes or None (error recorded).

    Its stderr warnings (Hanja) become warnings of `src`; the 255-byte warning is specific to UI strings
    (256-byte cLoadString buffers) and is only kept for strings.bin.  Symbols / jamo outside the syllable
    rows are valid cells but have no (or discouraged) glyphs, so they are reported as warnings.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            raw = bsb.encode(label, text)
    except SystemExit as e:
        msg = str(e.code)
        prefix = f"id {label}: "
        src.err(label, msg[len(prefix):] if msg.startswith(prefix) else msg)
        return None
    prefix = f"warning: id {label}: "
    for line in buf.getvalue().splitlines():
        if "most callers pass" in line and not string_table:
            continue
        src.warn(label, line[len(prefix):] if line.startswith(prefix) else line)
    odd = []
    i = 0
    while i < len(raw):
        if raw[i] < 0x80:
            i += 1
            continue
        if raw[i] < 0xB0 and raw[i:i + 2].decode("euc_kr", "replace") not in odd:
            odd.append(raw[i:i + 2].decode("euc_kr", "replace"))
        i += 2
    if odd:
        src.warn(label, "symbol/jamo cells outside the syllable rows (blank or discouraged, see STYLE.md): "
                 + " ".join(f"{c!r} (U+{ord(c[0]):04X})" for c in odd))
    return raw


# ----------------------------------------------------------------------------------------------- SMUTI markup
def scan_codes(b: bytes):
    """Tokenise the SMUTI `%` codes of a byte string: list of (token, start, end).

    %n %c %% | %t<digits> (token '%t') | %fs %fm %fl | %fc<digit> | anything else is reported as '%<char>'.
    Codes are case-insensitive.  Korean bytes are >= 0x80 and can never be 0x25, so a plain byte scan is safe.
    """
    out, i, n = [], 0, len(b)
    while i < n:
        if b[i] != 0x25:
            i += 1
            continue
        nxt = b[i + 1:i + 2].lower()
        if nxt in (b"n", b"c", b"%"):
            end = i + 2
            tok = "%" + nxt.decode()
        elif nxt == b"t":
            end = i + 2
            while end < n and 0x30 <= b[end] <= 0x39:
                end += 1
            tok = "%t"
        elif nxt == b"f":
            k = b[i + 2:i + 3].lower()
            if k in (b"s", b"m", b"l"):
                end, tok = i + 3, "%f" + k.decode()
            elif k == b"c" and i + 3 < n and 0x30 <= b[i + 3] <= 0x39:
                end, tok = i + 4, "%fc" + chr(b[i + 3])
            else:
                end, tok = i + 2, "%f?"
        else:
            end = i + 2
            if not nxt:
                tok = "%<end>"
            else:
                ch = nxt.decode("latin-1")
                tok = "%" + (ch if ch.isprintable() else repr(ch)[1:-1])
        out.append((tok, i, end))
        i = end
    return out


def compare_codes(ko: bytes, en: bytes):
    """Differences of the `%` code counts: list of 'code en->ko' strings."""
    a = Counter(t for t, _, _ in scan_codes(en))
    b = Counter(t for t, _, _ in scan_codes(ko))
    return [f"{t} {a[t]}->{b[t]}" for t in sorted(set(a) | set(b)) if a[t] != b[t]]


def centre_overflows(data: bytes):
    """(offset, length, segment) of every %c segment longer than CENTRE_LIMIT bytes.  The segment is the text after
    %c up to the next `%` code; CR/LF/TAB (< 0x20) are skipped by the renderer and do not count."""
    codes = scan_codes(data)
    out = []
    for k, (tok, _s, end) in enumerate(codes):
        if tok != "%c":
            continue
        stop = codes[k + 1][1] if k + 1 < len(codes) else len(data)
        seg = bytes(x for x in data[end:stop] if x >= 0x20)
        if len(seg) > CENTRE_LIMIT:
            out.append((end, len(seg), seg))
    return out


def shown(raw: bytes, limit=40) -> str:
    s = raw.decode("euc_kr", "replace")
    return s if len(s) <= limit else s[:limit] + "..."


def check_markup(label: str, ko: bytes, en: bytes | None, src: Source, with_line: bool = False) -> None:
    """Shared `%` validation of a briefing / SMUTI string: count differences warn, %c overflow is an error."""
    if en is not None:
        diff = compare_codes(ko, en)
        if diff:
            src.warn(label, "`%` codes differ from the English original (code original->Korean): " + ", ".join(diff))
    for off, n, seg in centre_overflows(ko):
        where = ("line %d: " % (ko.count(b"\n", 0, off) + 1)) if with_line else ""
        src.err(label, f"{where}%c segment of {n} bytes exceeds the {CENTRE_LIMIT}-byte limit: {shown(seg)!r}")


# ----------------------------------------------------------------------------------------------- briefings
def convert_briefing(name: str, ko_text: str, en: bytes | None, src: Source):
    """UTF-8 text -> EUC-KR + CRLF bytes (always ending with CRLF), or None if there were errors."""
    if ko_text.startswith("﻿"):
        ko_text = ko_text[1:]
        src.warn(name, "UTF-8 BOM removed")
    text = nfc(ko_text).replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        src.err(name, "file is empty")
        return None
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    raws, failed = [], False
    for n, line in enumerate(lines, 1):
        raw = encode_text(f"{name} line {n}", line, src)
        if raw is None:
            failed = True
        else:
            raws.append(raw)
    if failed:
        return None
    data = b"\r\n".join(raws) + b"\r\n"
    nerr = len(src.errors)
    check_markup(name, data, en, src, with_line=True)
    if len(src.errors) != nerr:
        return None
    en_max = max((len(x) for x in en.splitlines()), default=0) if en is not None else 0
    for n, raw in enumerate(raws, 1):
        if len(raw) > LINE_WARN:
            src.warn(name, f"line {n} is {len(raw)} bytes (> {LINE_WARN}; longest original line: {en_max})")
    return data


class Context:
    def __init__(self, repo: Path, game: Path, out: Path):
        self.repo, self.game, self.out = repo, game, out
        self._fst: dict = {}
        self._dirs: dict = {}

    def ko(self, *parts) -> Path:
        return self.repo.joinpath("localization", "ko", *parts)

    def fst(self, name: str):
        """(loc_fst.FST, {lower basename: [(internal path, index, real size)]}) of <game>/<name>; cached."""
        if name not in self._fst:
            path = self.game / name
            if not path.is_file():
                raise FileNotFoundError(f"cannot read {path} (needed to look up the in-game path of the files)")
            fst = loc_fst.FST(path)
            idx = defaultdict(list)
            for i, (internal, _off, _packed, real) in enumerate(fst.entries):
                idx[internal.replace("/", "\\").rsplit("\\", 1)[-1].lower()].append((internal, i, real))
            self._fst[name] = (fst, idx)
        return self._fst[name]

    def lookup(self, fst_name: str, basename: str):
        """(internal path, entry index, real size) for a basename inside an FST, case-insensitive; error text if
        the file is missing or ambiguous."""
        _fst, idx = self.fst(fst_name)
        hits = idx.get(basename.lower(), [])
        if not hits:
            raise KeyError(f"{basename} is not in {fst_name}")
        if len({h[0].lower() for h in hits}) > 1:
            raise KeyError(f"{basename} exists several times in {fst_name}: " + ", ".join(h[0] for h in hits))
        return hits[0]

    def original(self, fst_name: str, basename: str):
        """(bytes, internal path, note) of an original text file: the extracted copy in <repo>/<fst_name>/ if it
        exists, else the FST entry itself."""
        internal, i, real = self.lookup(fst_name, basename)
        folder = self.repo / fst_name
        if folder not in self._dirs:
            self._dirs[folder] = {p.name.lower(): p for p in folder.iterdir()} if folder.is_dir() else {}
        p = self._dirs[folder].get(basename.lower())
        note = ""
        if p is not None:
            data = p.read_bytes()
            if len(data) != real:
                note = f"extracted copy is {len(data)} bytes but the game's {fst_name} entry has {real}"
        else:
            data = self.fst(fst_name)[0].read(i)
        return data, internal, note

    def overlay_path(self, internal: str) -> Path:
        parts = internal.replace("/", "\\").split("\\")
        low = tuple(x.lower() for x in parts)
        if any(x in ("", ".", "..") or ":" in x for x in parts):
            raise ValueError(f"unsafe overlay path {internal!r}")
        for forbidden in FORBIDDEN_OVERLAY_DIRS:
            if low[:len(forbidden)] == forbidden:
                where = "\\".join(forbidden)
                raise ValueError(f"{internal!r} is under lang\\kor\\{where}, which another tool writes")
        return self.out.joinpath(*parts)

    def add_out(self, src: Source, internal: str, data: bytes, derived: bool = False) -> None:
        src.outputs.append(Out(internal.replace("/", "\\"), self.overlay_path(internal), data, derived=derived))


def run_briefings(ctx: Context) -> Source:
    src = Source("briefings")
    folder = ctx.ko("briefings")
    if not folder.is_dir():
        src.skipped = "no localization/ko/briefings/"
        return src
    files = sorted((p for p in folder.iterdir() if p.is_file()), key=lambda p: p.name.lower())
    txt = [p for p in files if p.suffix.lower() == ".txt"]
    for p in files:
        if p not in txt:
            src.note(f"{p.name}: ignored (not a .txt file)")
    if not txt:
        src.skipped = "localization/ko/briefings/ has no .txt files"
        return src
    src.info = f"{len(txt)} files"
    try:
        ctx.fst("MISSION.FST")
    except FileNotFoundError as e:
        src.err("MISSION.FST", str(e))
        return src
    for p in txt:
        try:
            en, internal, note = ctx.original("MISSION.FST", p.name)
        except (KeyError, FileNotFoundError) as e:
            src.err(p.name, f"no English original: {e}")
            continue
        if note:
            src.warn(p.name, note)
        try:
            text = p.read_bytes().decode("utf-8")
        except UnicodeDecodeError as e:
            src.err(p.name, f"not valid UTF-8: {e}")
            continue
        data = convert_briefing(p.name, text, en, src)
        if data is not None:
            ctx.add_out(src, internal, data)
    return src


# ----------------------------------------------------------------------------------------------- strings
def run_strings(ctx: Context) -> Source:
    src = Source("strings")
    path = ctx.ko("strings.json")
    if not path.is_file():
        src.skipped = "no localization/ko/strings.json"
        return src
    try:
        table = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        src.err("strings.json", f"cannot read: {e}")
        return src
    if not isinstance(table, dict):
        src.err("strings.json", "JSON root must be an object of id -> text")
        return src
    clean = {}
    for k, v in table.items():
        if not (isinstance(k, str) and k.isdigit() and k == str(int(k))):
            src.err("strings.json", f"key {k!r} is not a canonical decimal id")
        elif not isinstance(v, str):
            src.err(k, "value is not a string")
        else:
            clean[k] = nfc(v)
    src.info = f"{len(clean)} strings"
    en_table = {}
    en_path = ctx.repo / "localization" / "en" / "strings.json"
    if en_path.is_file():
        en_table = {str(e["id"]): e["text"] for e in json.loads(en_path.read_text(encoding="utf-8"))}
    for k in sorted(clean, key=int):
        raw = encode_text(k, clean[k], src, string_table=True)
        if raw is None:
            continue
        if en_table:
            if k not in en_table:
                src.warn(k, "id is not in the English string table (localization/en/strings.json)")
            elif FMT_RE.findall(en_table[k]) != FMT_RE.findall(clean[k]):
                src.warn(k, f"printf placeholders differ: original {FMT_RE.findall(en_table[k])} "
                            f"-> Korean {FMT_RE.findall(clean[k])} (the game fills them in a fixed order)")
    if src.errors:
        return src
    with contextlib.redirect_stderr(io.StringIO()):          # warnings were reported above, per string
        try:
            data = bsb.build(clean)
        except SystemExit as e:
            src.err("strings.json", str(e.code))
            return src
    if bsb.dump(data) != clean:
        src.err("strings.json", "strings.bin does not read back to the input table")
        return src
    ctx.add_out(src, "strings.bin", data)
    return src


# ----------------------------------------------------------------------------------------------- FIT / CSV
def parse_st(line: bytes):
    """(key, start, end) of an `st Key = "text"  // comment` line: bytes [start:end) is the text between the quotes.
    Mirrors loc_fit.parse_st (the closing quote is the last quote followed only by whitespace or a // comment)."""
    m = ST_RE.match(line)
    if not m:
        return None
    start = m.end()
    for j in range(len(line) - 1, start - 1, -1):
        if line[j] != 0x22:
            continue
        rest = line[j + 1:].strip()
        if rest == b"" or rest.startswith(b"//"):
            return m.group(1), start, j
    return None


class FitDoc:
    """A FIT file as raw lines (line endings kept) plus the location of every `st` value; unmodified lines are
    never touched, so everything except the replaced values stays byte-identical."""

    def __init__(self, data: bytes):
        self.lines = data.splitlines(keepends=True)
        self.st: dict = {}
        section = ""
        for i, ln in enumerate(self.lines):
            body = ln.rstrip(b"\r\n")
            m = SECTION_RE.match(body)
            if m:
                section = m.group(1).decode("latin-1")
                continue
            p = parse_st(body)
            if p:
                self.st.setdefault((section, p[0].decode("latin-1")), []).append((i, p[1], p[2]))

    def value(self, loc) -> bytes:
        i, s, e = loc
        return self.lines[i].rstrip(b"\r\n")[s:e]

    def tail(self, loc) -> bytes:
        """The text after the closing quote (whitespace and the `//` comment)."""
        i, _s, e = loc
        return self.lines[i].rstrip(b"\r\n")[e:]

    def replace(self, loc, raw: bytes) -> int:
        """Replace the value, return the new length of the line (without line ending)."""
        i, s, e = loc
        body = self.lines[i].rstrip(b"\r\n")
        eol = self.lines[i][len(body):]
        new = body[:s] + raw + body[e:]
        self.lines[i] = new + eol
        return len(new)

    def tobytes(self) -> bytes:
        return b"".join(self.lines)


def check_value(label: str, ko: str, src: Source):
    """Encode one FIT / CSV / roster value; the characters that would end the quoted value or the line are errors."""
    ko = nfc(ko)
    bad = [c for c in ("\r", "\n", "\0", '"') if c in ko]
    if bad:
        src.err(label, "value contains " + ", ".join(repr(c) for c in bad) + " (breaks the quoted FIT value)")
        return None
    return encode_text(label, ko, src)


def apply_fit(label: str, orig: bytes, entries: list, src: Source):
    """Replace `st` values of a FIT file.  entries: [{section, key, en?, ko}] (ko non-empty).  Returns bytes/None."""
    doc = FitDoc(orig)
    first_error = len(src.errors)
    wanted: dict = {}                                   # (section, key) -> (ko raw, en)
    for e in entries:
        sk = (e["section"], e["key"])
        elabel = f"{label} [{e['section']}] {e['key']}"
        raw = check_value(elabel, e["ko"], src)
        if raw is None:
            continue
        if sk not in doc.st:
            src.err(elabel, "no matching `st` line in the original file")
            continue
        if sk in wanted and wanted[sk][0] != raw:
            src.err(elabel, "two different translations for the same section/key")
            continue
        wanted[sk] = (raw, e.get("en"))
    replaced = 0
    for sk, (raw, en) in sorted(wanted.items()):
        elabel = f"{label} [{sk[0]}] {sk[1]}"
        for loc in doc.st[sk]:
            cur = doc.value(loc)
            if en is not None and cur.decode("latin-1") != en:
                src.warn(elabel, f"original text is {cur.decode('latin-1')!r}, the entry's `en` is {en!r} (stale translation?)")
            check_markup(elabel, raw, cur, src)
            limit = re.search(rb"up to (\d+) characters", doc.tail(loc))       # e.g. Menus.fit ItemHelp0
            if limit and len(raw) > int(limit.group(1)):
                src.warn(elabel, f"{len(raw)} bytes, the file's comment says up to {limit.group(1).decode()} characters")
            n = doc.replace(loc, raw)
            if n > LINE_WARN:
                src.warn(elabel, f"line is {n} bytes (> {LINE_WARN})")
            replaced += 1
    if len(src.errors) > first_error:
        return None
    return doc.tobytes() if replaced else None


def apply_csv(label: str, orig: bytes, entries: list, src: Source):
    """Replace the name / abbr cells of compbas.csv rows ("component <id>" sections)."""
    lines = orig.splitlines(keepends=True)
    first_error = len(src.errors)
    rows: dict = {}
    longest = {1: 0, 2: 0}
    for i, ln in enumerate(lines):
        cells = ln.rstrip(b"\r\n").split(b",")
        first = cells[0].strip()
        if not first or first.startswith(b"//") or not first.isdigit() or len(cells) < 3:
            continue
        rows.setdefault(int(first), i)
        for c in (1, 2):
            longest[c] = max(longest[c], len(cells[c].strip()))
    COL = {"name": 1, "abbr": 2}
    wanted: dict = {}                                   # (row id, column) -> (raw, en)
    for e in entries:
        elabel = f"{label} [{e['section']}] {e['key']}"
        m = re.fullmatch(r"component\s+(\d+)", e["section"])
        if not m or e["key"] not in COL:
            src.err(elabel, "csv entries need section 'component <id>' and key 'name' or 'abbr'")
            continue
        rid = int(m.group(1))
        if rid not in rows:
            src.err(elabel, f"no row with id {rid} in the original file")
            continue
        raw = check_value(elabel, e["ko"], src)
        if raw is None:
            continue
        if b"," in raw:
            src.err(elabel, "value contains ',' (the cell would split)")
            continue
        wanted[(rid, COL[e["key"]])] = (raw, e.get("en"), elabel)
    if len(src.errors) > first_error:
        return None
    out_cells: dict = {}
    mirrored = 0
    for (rid, col), (raw, en, elabel) in sorted(wanted.items()):
        cells = out_cells.setdefault(rid, lines[rows[rid]].rstrip(b"\r\n").split(b","))
        cur = cells[col].strip()
        if en is not None and cur.decode("latin-1") != en:
            src.warn(elabel, f"original cell is {cur.decode('latin-1')!r}, the entry's `en` is {en!r} (stale translation?)")
        if len(raw) > longest[col]:
            src.warn(elabel, f"{len(raw)} bytes, longer than the longest original {('name', 'abbr')[col - 1]} cell ({longest[col]})")
        cells[col] = cells[col][:len(cells[col]) - len(cells[col].lstrip())] + raw + cells[col][len(cells[col].rstrip()):]
    # inventories list `abbr` only where it differs from `name`; where they were equal the abbreviation column
    # shows the full name, so it follows the translated name instead of staying English.
    for (rid, col), (raw, _en, _l) in sorted(wanted.items()):
        if col != 1 or (rid, 2) in wanted:
            continue
        cells = out_cells[rid]
        orig_cells = lines[rows[rid]].rstrip(b"\r\n").split(b",")
        if orig_cells[1].strip() == orig_cells[2].strip() and orig_cells[2].strip().lower() not in (b"undefined", b"na", b""):
            c = cells[2]
            cells[2] = c[:len(c) - len(c.lstrip())] + raw + c[len(c.rstrip()):]
            mirrored += 1
    if mirrored:
        src.note(f"{label}: {mirrored} abbr cells were identical to the English name and follow the translated name")
    for rid, cells in out_cells.items():
        ln = lines[rows[rid]]
        body = ln.rstrip(b"\r\n")
        lines[rows[rid]] = b",".join(cells) + ln[len(body):]
    return b"".join(lines) if out_cells else None


def run_fit(ctx: Context) -> Source:
    src = Source("fit")
    path = ctx.ko("fit_strings.json")
    if not path.is_file():
        src.skipped = "no localization/ko/fit_strings.json"
        return src
    try:
        entries = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        src.err("fit_strings.json", f"cannot read: {e}")
        return src
    if not isinstance(entries, list):
        src.err("fit_strings.json", "JSON root must be a list of {file, section, key, en, ko}")
        return src
    by_file: dict = defaultdict(list)
    translated = 0
    for n, e in enumerate(entries):
        if not (isinstance(e, dict) and all(isinstance(e.get(k), str) for k in ("file", "section", "key"))):
            src.err(f"entry {n}", "needs string fields file, section, key")
            continue
        ko = e.get("ko")
        if ko is None or ko == "":
            continue                                     # not translated yet
        if not isinstance(ko, str):
            src.err(f"entry {n}", "`ko` is not a string")
            continue
        m = re.fullmatch(r"(MISSION\.FST|MISC\.FST)[/\\]([^/\\]+)", e["file"], re.I)
        if not m:
            src.err(f"entry {n}", f"file {e['file']!r} must be MISSION.FST/<name> or MISC.FST/<name>")
            continue
        translated += 1
        by_file[(m.group(1).upper(), m.group(2).lower())].append(
            {"section": e["section"], "key": e["key"], "en": e.get("en", e.get("text")), "ko": ko, "name": m.group(2)})
    src.info = f"{translated}/{len(entries)} entries, {len(by_file)} files"
    missing_fst = set()
    for fst_name in sorted({k[0] for k in by_file}):
        try:
            ctx.fst(fst_name)
        except FileNotFoundError as e:
            src.err(fst_name, str(e))
            missing_fst.add(fst_name)
    for (fst_name, _low), ents in sorted(by_file.items()):
        if fst_name in missing_fst:
            continue
        name = ents[0]["name"]
        label = f"{fst_name}/{name}"
        try:
            orig, internal, note = ctx.original(fst_name, name)
        except (KeyError, FileNotFoundError) as e:
            src.err(label, str(e))
            continue
        if note:
            src.warn(label, note)
        if name.lower().endswith(".csv"):
            data = apply_csv(label, orig, ents, src)
        else:
            data = apply_fit(label, orig, ents, src)
        if data is not None:
            ctx.add_out(src, internal, data)
    return src


# ----------------------------------------------------------------------------------------------- pilots
def ci_path(base: Path, *parts: str) -> Path:
    """base/parts[0]/parts[1]... with case-insensitive matching of each existing component."""
    for part in parts:
        hit = next((c for c in base.iterdir() if c.name.lower() == part.lower()), None) if base.is_dir() else None
        base = hit if hit is not None else base / part
    return base


def load_pilots(ctx: Context, src: Source):
    """pilots.json -> ({english name: entry}, {lower name: english name}); entry = name / callsign / callsign_en /
    alt_callsigns ({english callsign: Korean}); other fields (source ...) are ignored."""
    path = ctx.ko("pilots.json")
    try:
        pilots = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        src.err("pilots.json", f"cannot read: {e}")
        return None
    if not isinstance(pilots, dict):
        src.err("pilots.json", "JSON root must be an object {english name: {name, callsign}}")
        return None
    table = {}
    for k, v in pilots.items():
        alt = v.get("alt_callsigns", {}) if isinstance(v, dict) else None
        if (not isinstance(v, dict) or not all(isinstance(v.get(f, ""), str) for f in ("name", "callsign", "callsign_en"))
                or not isinstance(alt, dict) or not all(isinstance(a, str) and isinstance(b, str) for a, b in alt.items())):
            src.err(f"pilots.json {k}", "needs an object with string fields name / callsign (+ optional callsign_en, "
                                        "alt_callsigns {english: Korean})")
            continue
        e = {f: nfc(v[f]) for f in ("name", "callsign") if v.get(f)}
        if v.get("callsign_en"):
            e["callsign_en"] = v["callsign_en"]
        if alt:
            e["alt"] = {a.lower(): nfc(b) for a, b in alt.items()}
        table[k] = e
    return table, {k.lower(): k for k in table}


def pick_callsign(tr: dict, en_callsign: str):
    """Korean callsign for the English callsign found in the file, or None if pilots.json has none for it."""
    if en_callsign.lower() in tr.get("alt", {}):
        return tr["alt"][en_callsign.lower()]
    if "callsign" in tr and tr.get("callsign_en", en_callsign).lower() == en_callsign.lower():
        return tr["callsign"]
    return None


def rewrite_warrior(doc: FitDoc, tr: dict, plabel: str, src: Source) -> bool | None:
    """Replace the General Name / Callsign values of one warrior profile in `doc`.  Returns True if the document was
    changed, None on error."""
    ok, changed = True, False
    nm = doc.st[("General", "Name")][0]
    cs = (doc.st.get(("General", "Callsign")) or [None])[0]
    jobs = []
    if "name" in tr:
        jobs.append(("name", nm, tr["name"], PILOT_NAME_WARN))
    else:
        src.warn(plabel, f"no name in pilots.json; kept {doc.value(nm).decode('latin-1')!r}")
    if cs is not None:
        en_cs = doc.value(cs).decode("latin-1")
        ko_cs = pick_callsign(tr, en_cs)
        if ko_cs is None:
            src.warn(plabel, f"no Korean callsign for {en_cs!r} in pilots.json (callsign_en "
                             f"{tr.get('callsign_en')!r}); kept English")
        else:
            jobs.append(("callsign", cs, ko_cs, PILOT_CALLSIGN_WARN))
    for field_, loc, text, warn_at in jobs:
        raw = check_value(f"{plabel} {field_}", text, src)
        if raw is None:
            ok = False
            continue
        if len(raw) > warn_at:
            src.warn(plabel, f"{field_} is {len(raw)} bytes (> {warn_at}, the longest English {field_})")
        doc.replace(loc, raw)
        changed = True
    return changed if ok else None


def run_pilots(ctx: Context, pkk_dir: Path | None = None, warrior_fits: bool = False) -> Source:
    src = Source("pilots")
    if not ctx.ko("pilots.json").is_file():
        src.skipped = "no localization/ko/pilots.json"
        return src
    loaded = load_pilots(ctx, src)
    if loaded is None:
        return src
    table, lower = loaded
    folder = pkk_dir or ci_path(ctx.game, "data", "savegame")
    names = {p.name.lower(): p for p in folder.iterdir()} if folder.is_dir() else {}
    used: set = set()
    src.info = f"{len(table)} pilots"
    for fname in ("START0.PKK", "XSTART0.PKK"):
        p = names.get(fname.lower())
        if p is None:
            src.warn(fname, f"not found in {folder}; skipped")
            continue
        data = convert_roster(p.name, p.read_bytes(), table, lower, used, src)
        if data is not None:
            ctx.add_out(src, f"data\\savegame\\{p.name}", data)
    if warrior_fits:
        run_warrior_fits(ctx, table, lower, used, src)
    unused = set(table) - used
    if unused:
        src.note(f"{len(unused)} of {len(table)} pilots.json entries matched no roster warrior"
                 + ("" if warrior_fits else " (pilots of the PMW*/war*.fit files come from fit_strings.json or --warrior-fits)"))
    return src


def find_pilot(en_name: str, table: dict, lower: dict):
    key = en_name if en_name in table else lower.get(en_name.lower())
    return key


def convert_roster(label: str, pkk: bytes, table: dict, lower: dict, used: set, src: Source):
    pf = mcg_pkk.PacketFile(pkk)
    if not pf.checksum_ok:
        src.err(label, "input roster fails its checksum")
        return None
    packets = [pf.read_packet(i) for i in range(pf.num_packets)]
    if b"Mad Cat" in packets[0]:
        src.note(f"{label}: the installed roster contains the Mad Cat A starting mech; the Korean copy keeps it")
    out, changed, untranslated = [], 0, []
    for i, p in enumerate(packets):
        doc = FitDoc(p)
        if ("General", "Name") not in doc.st or ("General", "Callsign") not in doc.st:
            out.append(p)                                # header, mech or gift packet
            continue
        en_name = doc.value(doc.st[("General", "Name")][0]).decode("latin-1")
        key = find_pilot(en_name, table, lower)
        if key is None:
            untranslated.append(en_name)
            out.append(p)
            continue
        used.add(key)
        res = rewrite_warrior(doc, table[key], f"{label} packet {i} ({en_name})", src)
        if res is None:
            return None
        out.append(doc.tobytes())
        changed += 1 if res else 0
    if untranslated:
        src.warn(label, f"{len(untranslated)} warriors without a translation kept English: " + ", ".join(untranslated))
    if not changed:
        src.note(f"{label}: no warrior packet matched pilots.json; not written")
        return None
    data = mcg_pkk.build_packet_file(out)
    chk = mcg_pkk.PacketFile(data)
    if not chk.checksum_ok or chk.num_packets != len(out) or any(chk.read_packet(i) != out[i] for i in range(len(out))):
        src.err(label, "rebuilt packet file does not read back identically")
        return None
    for i, (a, b) in enumerate(zip(packets, out)):
        if a.count(b"\r\n") != b.count(b"\r\n") or a.count(b"\n") != b.count(b"\n"):
            src.err(label, f"packet {i}: line endings changed")
            return None
    return data


def run_warrior_fits(ctx: Context, table: dict, lower: dict, used: set, src: Source) -> None:
    """--warrior-fits: Korean copies of the warrior profiles (PMW*.FIT, war*.fit ... in data\\missions\\warriors\\) whose
    [General] Name is in pilots.json; derived outputs, dropped again if fit_strings.json translates the same file."""
    try:
        _fst, idx = ctx.fst("MISSION.FST")
    except FileNotFoundError as e:
        src.err("MISSION.FST", str(e))
        return
    wanted = sorted({internal for hits in idx.values() for internal, _i, _r in hits
                     if internal.lower().startswith("data\\missions\\warriors\\") and internal.lower().endswith(".fit")},
                    key=str.lower)
    count = 0
    for internal in wanted:
        base = internal.rsplit("\\", 1)[-1]
        try:
            orig, internal, _note = ctx.original("MISSION.FST", base)
        except KeyError as e:
            src.err(base, str(e))
            continue
        doc = FitDoc(orig)
        if ("General", "Name") not in doc.st:
            continue
        en_name = doc.value(doc.st[("General", "Name")][0]).decode("latin-1")
        key = find_pilot(en_name, table, lower)
        if key is None:
            continue
        used.add(key)
        res = rewrite_warrior(doc, table[key], f"MISSION.FST/{base} ({en_name})", src)
        if res:
            ctx.add_out(src, internal, doc.tobytes(), derived=True)
            count += 1
    src.note(f"--warrior-fits: {count} warrior profile files matched pilots.json")


# ----------------------------------------------------------------------------------------------- driver
RUNNERS = {"strings": run_strings, "briefings": run_briefings, "fit": run_fit, "pilots": run_pilots}


def run(ctx: Context, only, check: bool, strict: bool = False, pkk_dir: Path | None = None,
        warrior_fits: bool = False):
    """Run the selected sources and write the outputs.  Returns the list of Source results."""
    results = []
    for name in SOURCES:
        if only and name not in only:
            continue
        try:
            src = run_pilots(ctx, pkk_dir, warrior_fits) if name == "pilots" else RUNNERS[name](ctx)
        except FileNotFoundError as e:
            src = Source(name)
            src.err(name, str(e))
        if strict and src.warnings:
            src.errors += [(l, "(warning, error under --strict) " + m) for l, m in src.warnings]
            src.warnings = []
            src.outputs = []
        results.append(src)
    # one writer per file: explicit fit_strings.json entries beat the files derived from pilots.json
    explicit = {o.rel.lower(): o for s in results if s.name == "fit" for o in s.outputs}
    for src in results:
        keep, skipped = [], 0
        for o in src.outputs:
            other = explicit.get(o.rel.lower())
            if o.derived and other is not None:
                skipped += 1
            elif src.name != "fit" and other is not None and other.data != o.data:
                src.err(o.rel, "written by two sources with different content")
            else:
                keep.append(o)
        if skipped:
            src.note(f"{skipped} warrior profile files derived from pilots.json were skipped because "
                     "fit_strings.json translates them explicitly")
        src.outputs = keep
    for src in results:
        for o in src.outputs:
            exists = o.path.is_file()
            same = exists and o.path.read_bytes() == o.data
            if same:
                o.status = "unchanged"
            elif check:
                o.status = "would write" if exists else "would create"
            else:
                o.path.parent.mkdir(parents=True, exist_ok=True)
                o.path.write_bytes(o.data)
                o.status = "written" if exists else "created"
    return results


def report(results, check: bool, verbose: bool, out=None) -> int:
    out = out or sys.stdout
    rows = [("source", "files", "bytes", "warn", "err", "result")]
    for s in results:
        if s.skipped:
            rows.append((s.name, "-", "-", "-", "-", f"skipped: {s.skipped}"))
            continue
        counts = Counter(o.status for o in s.outputs)
        detail = ", ".join(f"{n} {k}" for k, n in sorted(counts.items())) or "nothing to write"
        rows.append((s.name, str(len(s.outputs)), str(sum(len(o.data) for o in s.outputs)), str(len(s.warnings)),
                     str(len(s.errors)), detail + (f"  [{s.info}]" if s.info else "")))
    w = [max(len(r[i]) for r in rows) for i in range(5)]
    print(("CHECK (nothing written)" if check else "BUILD"), file=out)
    for r in rows:
        print("  ".join(c.ljust(w[i]) if i in (0, 5) else c.rjust(w[i]) for i, c in enumerate(r[:5])) + "  " + r[5], file=out)
    for s in results:
        if s.outputs and (verbose or len(s.outputs) <= 12):
            print(f"\n{s.name}:", file=out)
            for o in s.outputs:
                print(f"  {o.status:12} lang\\kor\\{o.rel}  ({len(o.data)} bytes)", file=out)
        for n in s.notes:
            print(f"note [{s.name}] {n}", file=out)
        per: dict = defaultdict(int)
        hidden = 0
        for kind, items in (("ERROR", s.errors), ("warning", s.warnings)):
            for label, msg in items:
                first = label.split(" ")[0]
                group = (kind, "ids" if first.isdigit() else first)     # per file; all string ids together
                per[group] += 1
                if not verbose and per[group] > (50 if group[1] == "ids" else 6):
                    hidden += 1
                    continue
                print(f"{kind} [{s.name}] {label}: {msg}", file=out)
        if hidden:
            print(f"  ... {hidden} more diagnostics for {s.name} (use -v)", file=out)
    nerr = sum(len(s.errors) for s in results)
    nwarn = sum(len(s.warnings) for s in results)
    print(f"\n{nerr} errors, {nwarn} warnings", file=out)
    return 1 if nerr else 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Build the Korean overlay (lang\\kor\\) of MechCommander Gold.")
    ap.add_argument("--repo", type=Path, default=REPO, help="repo root with localization/ and the extracted MISSION.FST/ MISC.FST/ folders")
    ap.add_argument("--game-dir", type=Path, help="MCX install dir (default <repo>/game-source/extracted/MCX)")
    ap.add_argument("--out", type=Path, help="overlay root (default <game-dir>/lang/kor)")
    ap.add_argument("--only", action="append", help="strings, briefings, fit or pilots (repeat or comma separate)")
    ap.add_argument("--check", action="store_true", help="validate everything, write nothing")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--roster-dir", type=Path, help="folder with the START0.PKK / XSTART0.PKK to translate "
                    "(default <game-dir>/DATA/SAVEGAME, i.e. whatever is installed)")
    ap.add_argument("--warrior-fits", action="store_true",
                    help="also write Korean copies of the warrior profiles (PMW*.FIT hireable pilots ...) whose Name is in "
                         "pilots.json; files translated by fit_strings.json are left to that source")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every output file and every diagnostic")
    a = ap.parse_args(argv)
    only = None
    if a.only:
        only = {x.strip() for item in a.only for x in item.split(",") if x.strip()}
        bad = only - set(SOURCES)
        if bad:
            ap.error(f"--only: unknown source(s) {sorted(bad)}; choose from {', '.join(SOURCES)}")
    repo = a.repo.resolve()
    game = (a.game_dir or repo / "game-source" / "extracted" / "MCX").resolve()
    out = (a.out or game / "lang" / "kor").resolve()
    ctx = Context(repo, game, out)
    results = run(ctx, only, a.check, a.strict, a.roster_dir, a.warrior_fits)
    return report(results, a.check, a.verbose)


if __name__ == "__main__":
    sys.exit(main())
