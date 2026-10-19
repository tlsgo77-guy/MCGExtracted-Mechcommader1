"""Extract the EXE string table of MCX.EXE and work out which screen uses which string id.

Output (see extract_text.py):
    localization/en/strings.json          one entry per string id
    localization/en/strings_summary.md    counts per scope + table of the pre-mission strings
    localization/en/dialogs.json          Win32 DIALOG resources (crash dialog, DirectPlay dialogs)

How the engine loads strings
    cLoadString(HINSTANCE, UINT id, char *buf, int size)   -- cdecl, @VA 0x75aa30
        calls LoadStringA(hInst, id + languageOffset, buf, size)
    `languageOffset` (VA 0x80a86c) is read from SYSTEM.CFG key `Language` (_systemInit), so
    the very same EXE can carry several languages in one string table (id + N*1000...).
    Every one of the 229 `call cLoadString` sites pushes (size, buf, id, hInst); the id is the
    second push counting backwards from the call.  Immediate ids are exact.  Register ids are
    "dynamic": they are `DescIndex + const` read from the object FIT files (mech names
    DescIndex+300, vehicle names DescIndex+700, building names ObjectType::descId...), and are
    attributed to the whole id range of that kind of name.

Needs `capstone` (pip install capstone, or set MCG_CAPSTONE_PATH to a folder containing it).
"""
from __future__ import annotations

import bisect
import json
import os
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

from loc_common import EXE, GAME, MISSION, OUT, REPO, SYMBOLS, md_cell, read_text, write_json, write_text

BASE = 0x600000
GAME_DATA = GAME / "DATA"
CLOADSTRING = 0x75AA30
TEXT_END = 0x179000            # file offset where code ends (.text raw size)

# --------------------------------------------------------------------------- PE resources


class PE:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        d = self.data
        e = struct.unpack_from("<I", d, 0x3C)[0]
        nsec = struct.unpack_from("<H", d, e + 6)[0]
        optsz = struct.unpack_from("<H", d, e + 20)[0]
        off = e + 24 + optsz
        self.secs = []
        for _ in range(nsec):
            name = d[off:off + 8].rstrip(b"\0").decode()
            vs, va, rs, rp = struct.unpack_from("<IIII", d, off + 8)
            self.secs.append((name, va, vs, rp, rs))
            off += 40

    def rva2off(self, rva):
        for _n, va, vs, rp, rs in self.secs:
            if va <= rva < va + max(vs, rs):
                return rva - va + rp
        raise ValueError(hex(rva))

    def resources(self):
        """yield (type_id, res_id, langid, file_offset, size)"""
        d = self.data
        rs_off = next(s[3] for s in self.secs if s[0] == ".rsrc")

        def entries(off):
            n_named, n_id = struct.unpack_from("<HH", d, off + 12)
            return [struct.unpack_from("<II", d, off + 16 + 8 * i) for i in range(n_named + n_id)]

        for tnm, tso in entries(rs_off):
            for inm, iso in entries(rs_off + (tso & 0x7FFFFFFF)):
                for lnm, lso in entries(rs_off + (iso & 0x7FFFFFFF)):
                    dro, sz, _cp, _ = struct.unpack_from("<IIII", d, rs_off + lso)
                    yield tnm, inm, lnm, self.rva2off(dro), sz


def read_string_table(pe: PE) -> dict[int, str]:
    out = {}
    d = pe.data
    for t, bid, _lang, fo, _sz in pe.resources():
        if t != 6:
            continue
        p = fo
        for k in range(16):
            n = struct.unpack_from("<H", d, p)[0]
            p += 2
            if n:
                out[(bid - 1) * 16 + k] = d[p:p + 2 * n].decode("utf-16le")
            p += 2 * n
    return out


DLG_CLASS = {0x80: "Button", 0x81: "Edit", 0x82: "Static", 0x83: "ListBox", 0x84: "ScrollBar", 0x85: "ComboBox"}


def read_dialogs(pe: PE) -> list[dict]:
    d = pe.data
    out = []

    def wstr(p):
        s = p
        while struct.unpack_from("<H", d, p)[0]:
            p += 2
        return d[s:p].decode("utf-16le"), p + 2

    def ordstr(p):
        w = struct.unpack_from("<H", d, p)[0]
        if w == 0:
            return "", p + 2
        if w == 0xFFFF:
            return "#%d" % struct.unpack_from("<H", d, p + 2)[0], p + 4
        return wstr(p)

    for t, rid, _lang, fo, _sz in pe.resources():
        if t != 5:
            continue
        p = fo
        style, _ex, cdit = struct.unpack_from("<IIH", d, p)
        if style >> 16 == 0xFFFF:            # DLGTEMPLATEEX / garbage (resource 199)
            continue
        p += 18
        _menu, p = ordstr(p)
        _cls, p = ordstr(p)
        title, p = wstr(p)
        if style & 0x40:
            p += 2
            _face, p = wstr(p)
        items = []
        for _ in range(cdit):
            p = (p + 3) & ~3
            _st, _ex2, _x, _y, _cx, _cy, iid = struct.unpack_from("<IIhhhhH", d, p)
            p += 18
            cls, p = ordstr(p)
            txt, p = ordstr(p)
            extra = struct.unpack_from("<H", d, p)[0]
            p += 2 + extra
            if txt and not txt.startswith("#"):
                items.append({"control_id": iid if iid != 0xFFFF else None,
                              "class": DLG_CLASS.get(int(cls[1:]), cls) if cls.startswith("#") else cls,
                              "text": txt})
        out.append({"dialog_id": rid, "title": title, "items": items})
    return sorted(out, key=lambda x: x["dialog_id"])


# --------------------------------------------------------------------------- code analysis


def load_capstone():
    try:
        import capstone  # noqa: F401
    except ImportError:
        extra = os.environ.get("MCG_CAPSTONE_PATH")
        if extra:
            sys.path.insert(0, extra)
        try:
            import capstone  # noqa: F401,F811
        except ImportError:
            sys.exit("capstone is required: pip install capstone  (or set MCG_CAPSTONE_PATH)")
    import capstone
    return capstone


def demangle(sym: str) -> str:
    """Tiny MSVC name demangler: '?handleEvent@BriefingScreen@@UAE...' -> 'BriefingScreen::handleEvent'."""
    if not sym.startswith("?"):
        return sym.lstrip("_").split("@")[0]
    body = sym[1:]
    head = body.split("@@", 1)[0]
    parts = head.split("@")
    name, scope = parts[0], parts[1:]
    if name.startswith("?0"):
        name = scope[0] if scope else "ctor"
    return "::".join(list(reversed(scope)) + [name])


class CodeIndex:
    def __init__(self):
        cap = load_capstone()
        self.cs = cap.Cs(cap.CS_ARCH_X86, cap.CS_MODE_32)
        self.d = open(EXE, "rb").read()
        syms = json.load(open(SYMBOLS))
        self.byaddr = {}
        for k, v in syms.items():
            self.byaddr.setdefault(v, k)
        self.addrs = sorted(self.byaddr)

    def func_of(self, va):
        i = bisect.bisect_right(self.addrs, va) - 1
        return self.addrs[i], self.byaddr[self.addrs[i]]

    def callsites(self):
        d = self.d
        out = []
        for i in range(0x1000, TEXT_END):
            if d[i] == 0xE8:
                rel = struct.unpack_from("<i", d, i + 1)[0]
                if BASE + i + 5 + rel == CLOADSTRING:
                    out.append(BASE + i)
        return out

    def string_id_args(self, site):
        """All possible id arguments of the cLoadString call at `site`: a list of
        (kind, value, note) with kind 'imm' (value=int) or 'reg' (value=operand text) or 'unknown'.

        The call pushes (size, buf, id, hInst); the id is the 2nd push when walking backwards.
        Several `jmp`s can share one call (`push id1; jmp L / push id2; jmp L / L: call`), so the walk
        is a backward search over the function's jump targets, not just straight-line code."""
        fa, _ = self.func_of(site)
        ins = list(self.cs.disasm(self.d[fa - BASE:site - BASE + 5], fa))
        index = {x.address: n for n, x in enumerate(ins)}
        targets = defaultdict(list)                  # branch target address -> [instruction index of branch]
        for n, x in enumerate(ins):
            if x.mnemonic == "jmp" or x.mnemonic.startswith("j"):
                m = re.fullmatch(r"0x[0-9a-f]+", x.op_str)
                if m:
                    targets[int(x.op_str, 16)].append(n)
        # indirect `jmp [reg*4 + table]` (switch statements): add every table entry as a branch target
        fend = self.addrs[bisect.bisect_right(self.addrs, fa)] if bisect.bisect_right(self.addrs, fa) < len(self.addrs) else fa + 0x4000
        for n, x in enumerate(ins):
            if x.mnemonic == "jmp":
                m = re.search(r"\*4 \+ (0x[0-9a-f]+)\]", x.op_str)
                if m:
                    t = int(m.group(1), 16) - BASE
                    while 0 <= t < len(self.d) - 4:
                        v = struct.unpack_from("<I", self.d, t)[0]
                        if not (fa <= v < fend):
                            break
                        targets[v].append(n)
                        t += 4
        found, notes, seen = [], [], set()

        def back(i, need):
            while i >= 0:
                key = (i, need)
                if key in seen:
                    return
                seen.add(key)
                x = ins[i]
                if x.mnemonic == "push":
                    need -= 1
                    if need == 0:
                        found.append((x, i))
                        return
                elif x.mnemonic in ("call", "ret"):
                    notes.append(f"{x.mnemonic} at 0x{x.address:x} before id push")
                    return
                for j in targets.get(x.address, []):
                    back(j, need)
                i -= 1
                if i >= 0 and ins[i].mnemonic in ("jmp", "ret"):
                    return                           # no fall-through into x from the previous instruction

        for j in targets.get(site, []):               # jumps that land directly on the call
            back(j, 2)
        back(index[site] - 1, 2)
        out = []
        for x, i in found:
            op = x.op_str
            if re.fullmatch(r"0x[0-9a-f]+|\d+", op):
                out.append(("imm", int(op, 0), ""))
                continue
            addc = ""
            for y in reversed(ins[max(0, i - 12):i]):
                m = re.fullmatch(rf"{op}, (0x[0-9a-f]+)", y.op_str) if y.mnemonic == "add" else None
                if m:
                    addc = f"+{int(m.group(1), 16)}"
                    break
            out.append(("reg", op, addc))
        if not out:
            out.append(("unknown", None, "; ".join(notes) or "id push not found"))
        return out


# --------------------------------------------------------------------------- classification

# (regex on 'Class::method' / 'function', screen, scope)
RULES = [
    (r"^(BriefingScreen|MechBriefBlock)::", "Briefing", "pre-mission"),
    (r"^(PurchaseScreen|PurchaseDlg|MechPurchaseBlock|VehiclePurchaseBlock|CompPurchaseBlock|"
     r"PilotPurchaseBlock|PurMechList|PurVehicleList|PurPilotList)::|^check(Max|Num)Units$",
     "Purchase", "pre-mission"),
    (r"^(RepairScreen|MechRepairBlock|VehicleRepairBlock|RefitDialog)::", "Repair/Refit", "pre-mission"),
    (r"^(MechInventoryBlock|PilotInventoryBlock|VehicleInventoryBlock|CompInventoryBlock)::",
     "Inventory (mech bay / pilots / vehicles / components)", "pre-mission"),
    (r"^(LogMechList|LogVehicleList|Logistics)::(init|addMech|addVehicle|loadCampaign|prepareScenario)$",
     "Logistics", "pre-mission"),
    (r"^Logistics::handleLostPlayer$", "Multiplayer", "multiplayer"),
    (r"^MissionResultsScreen::", "MissionResults", "pre-mission"),
    (r"^(NewCampaign|NewMCXCampaign)$", "MainMenu/NewCampaign", "pre-mission"),
    (r"^(LoadScreen|SoloLoadScreen)$", "LoadScreen", "pre-mission"),
    (r"^(SaveScreen|SaveGame|SaveGameCallback|DeleteGame)$", "SaveScreen", "pre-mission"),
    (r"^ShowPreferences$", "Preferences", "pre-mission"),
    (r"^ReplayCinema$", "MainMenu/Cinema", "pre-mission"),
    (r"^(SessionScreen|MultiPlayer)::|^(ShowLANScreen|HostGame|JoinGame|JoinSerialSession|Dial|ConnectScreen|"
     r"CheckExit|DoExitToZone|DoExitToMplayer|ShowInternet|AllGoneCallback|ShowConnectStatus|"
     r"handleLocalPlayerRemoved)$|^Mission::init$", "Multiplayer", "multiplayer"),
    (r"^(aSystem::start|RealWinMain|handleEvent|CheckRegistryVersionNumber|WriteRegistryVersionNumber|"
     r"checkForCDInDrive|_systemInit|killTheGame)$", "System", "system"),
    (r"^(TacticalMap|InterfaceObject|ArtilleryButton|MechStatusWindow|Scenario)::", "In-mission HUD", "in-mission"),
    (r"^(Mover|Building|Gate|TreeBuilding|TrainCar|Turret|GroundVehicle|BattleMech)::init$|^execHbSetBuildingName$",
     "In-mission object names", "in-mission"),
]
RULES = [(re.compile(a), b, c) for a, b, c in RULES]

# register-id (dynamic) callers -> (kind, list of ids it can produce).  See module docstring.
MECH_NAMES = list(range(700, 784))          # 'Atlas A' .. "Savage's Cougar"  (DescIndex 400..483 + 300)
VEHICLE_NAMES = list(range(1200, 1256))     # 'APC' .. 'Ammo Truck'            (DescIndex 500..555 + 700)
OBJECT_NAMES = (list(range(200, 639)) + [648] + list(range(857, 861)) + [872, 874, 875, 876, 877])
DYNAMIC = {
    "BattleMech::init": ("mech name", MECH_NAMES),
    "LogMechList::addMech": ("mech name", MECH_NAMES),
    "PurMechList::addMech": ("mech name", MECH_NAMES),
    "GroundVehicle::init": ("vehicle name", VEHICLE_NAMES),
    "LogVehicleList::addVehicle": ("vehicle name", VEHICLE_NAMES),
    "PurVehicleList::addVehicle": ("vehicle name", VEHICLE_NAMES),
    "Building::init": ("object name", OBJECT_NAMES),
    "Gate::init": ("object name", OBJECT_NAMES),
    "TreeBuilding::init": ("object name", OBJECT_NAMES),
    "TrainCar::init": ("object name", OBJECT_NAMES),
    "Turret::init": ("object name", OBJECT_NAMES),
    "execHbSetBuildingName": ("object name", OBJECT_NAMES),
}

def object_packets():
    """Text of the FIT packets of OBJECT2.PAK: the extracted folder data/objects/OBJECT2.PAK/*.txt in the repo,
    else the packet file of the local game install."""
    d = REPO / "data" / "objects" / "OBJECT2.PAK"
    if d.is_dir():
        for p in sorted(d.glob("*.txt")):
            yield read_text(p)
        return
    for pak in (d, GAME_DATA / "OBJECTS" / "OBJECT2.PAK"):
        if pak.is_file():
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import mcg_pkk
            pf = mcg_pkk.PacketFile(pak.read_bytes())
            for i in range(pf.num_packets):
                yield pf.read_packet(i).decode("cp1252", "replace")
            return


def resolve_dynamic_ids(table):
    """Which string ids can the register-id call sites really produce?  Read them from the data:
        mech names     : MISSION.FST profiles with FileType MechProfile           -> DescIndex + 300
        vehicle names  : profiles with FileType GroundVehicleProfile              -> DescIndex + 700
        object names   : OBJECT2.PAK building packets `l BuildingName = <id>` (direct string id)
                         and the train-car packets `l Name = <id>` (621..627)
    Falls back to the whole id range when a data source is missing."""
    mech, veh, obj = set(), set(), set()
    for p in MISSION.glob("*"):
        if p.suffix.lower() != ".fit":
            continue
        t = read_text(p)
        m = re.search(r'FileType\s*=\s*"(\w+)"', t)
        d = re.search(r"DescIndex\s*=\s*(\d+)", t)
        if not (m and d):
            continue
        if m.group(1) == "MechProfile":
            mech.add(int(d.group(1)) + 300)
        elif m.group(1) == "GroundVehicleProfile":
            veh.add(int(d.group(1)) + 700)
    for t in object_packets():
        for m in re.finditer(r"^\s*(?:l|ul)\s+BuildingName\s*=\s*(\d+)", t, re.M):
            obj.add(int(m.group(1)))
        if 'FileType' in t and '"TrainType"' in t:
            for m in re.finditer(r"^\s*(?:l|ul)\s+Name\s*=\s*(\d+)", t, re.M):
                obj.add(int(m.group(1)))
    ids = set(table)
    return {
        "mech name": (mech & ids) or set(MECH_NAMES),
        "vehicle name": (veh & ids) or set(VEHICLE_NAMES),
        "object name": (obj & ids) or set(OBJECT_NAMES),
    }


# strings that are identifiers / templates / debug text rather than player-facing prose
# generic logistics code that only runs for multiplayer sessions
SCOPE_OVERRIDE = {887: "multiplayer", 889: "multiplayer"}      # "%s's game" (default session name), "%s has entered the mission."

KIND_OVERRIDE = {
    640: ("identifier", "version component (window title / registry), not shown to players"),
    641: ("identifier", "version component (window title / registry), not shown to players"),
    642: ("identifier", "build number, written to registry / window title"),
    643: ("format", "window-title template; 'Release' / 'Debug' build tag"),
    644: ("format", "window-title template; 'Release' / 'Debug' build tag"),
    96: ("debug", "developer-only watermark"),
    97: ("debug", "developer-only watermark"),
    862: ("debug", "'Demo' build marker"),
    890: ("identifier", "movie/briefing file-name template (Port Arthur, after); do not translate"),
    891: ("identifier", "movie/briefing file-name template (Port Arthur, before); do not translate"),
    902: ("identifier", "movie/briefing file-name template (Cermak, after); do not translate"),
    903: ("identifier", "movie/briefing file-name template (Cermak, before); do not translate"),
    892: ("identifier", "save-game file-name template; do not translate"),
    900: ("identifier", "language name written to the registry (language marker)"),
    901: ("ui-text", "single-letter label drawn instead of the quantity when a purchase item is unlimited "
                     "(MechPurchaseBlock/VehiclePurchaseBlock/CompPurchaseBlock::drawBackground use it as a printf format)"),
}

FMT_RE = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?[hlL]?[diuxXfFeEgGcsp]|%%")


def func_rule(fn: str):
    for rx, screen, scope in RULES:
        if rx.search(fn):
            return screen, scope
    return "(unclassified)", "unknown"


SCOPE_PRIORITY = ["pre-mission", "multiplayer", "system", "in-mission", "unknown"]


def build():
    pe = PE(EXE)
    table = read_string_table(pe)
    dialogs = read_dialogs(pe)
    ci = CodeIndex()
    sites = ci.callsites()

    dyn_ids = resolve_dynamic_ids(table)
    callers = defaultdict(list)     # id -> [{function, site, screen, scope, dynamic}]
    problems = []
    for site in sites:
        fa, sym = ci.func_of(site)
        fn = demangle(sym)
        screen, scope = func_rule(fn)
        rec = {"function": fn, "call_site": f"0x{site:x}", "screen": screen, "scope": scope}
        for kind, val, note in ci.string_id_args(site):
            if kind == "imm":
                callers[val].append(rec)
            elif kind == "reg" and fn in DYNAMIC:
                what, _ids = DYNAMIC[fn]
                r = dict(rec, dynamic=what)
                for i in sorted(dyn_ids[what]):
                    callers[i].append(r)
            else:
                problems.append((fn, f"0x{site:x}", kind, val, note))

    entries = []
    for sid in sorted(table):
        text = table[sid]
        cl = callers.get(sid, [])
        fns = sorted({c["function"] for c in cl})
        screens = sorted({c["screen"] for c in cl})
        scopes = {c["scope"] for c in cl}
        scope = next((s for s in SCOPE_PRIORITY if s in scopes), "unknown")
        if sid in SCOPE_OVERRIDE and scope != "unknown":
            scope = SCOPE_OVERRIDE[sid]
        kind, note = KIND_OVERRIDE.get(sid, ("ui-text", ""))
        if kind == "ui-text" and FMT_RE.search(text):
            kind = "format"
        e = {"id": sid, "text": text, "callers": fns, "screens": screens, "scope": scope}
        if len(scopes) > 1:
            e["also_scopes"] = sorted(scopes - {scope})
        if any(c.get("dynamic") for c in cl):
            e["dynamic"] = sorted({c["dynamic"] for c in cl if c.get("dynamic")})[0]
        e["call_sites"] = [c["call_site"] for c in cl if not c.get("dynamic")]
        e["kind"] = kind
        ph = FMT_RE.findall(text)
        if ph:
            e["placeholders"] = ph
        if note:
            e["note"] = note
        entries.append(e)
    tag_unreferenced(entries)
    build.literals = hardcoded_literals(ci)
    return entries, dialogs, problems, len(sites)


# Ids that no `cLoadString` call site names (not even through jump tables / shared tails).  They are
# probably dead strings left in the resource script (or reached from code that was compiled out), so
# `scope` stays "unknown"; `guess_scope` records what the text itself and its neighbours suggest.
UNREFERENCED_GUESS = [
    (range(1, 29), "pre-mission", "mission-report / results text (objective status, lance organisation, salvage list); "
                                  "no call site in this EXE - likely dead report code"),
    ((37,), "pre-mission", "briefing-screen help text (neighbours 29-42 are Briefing/Purchase/Repair help)"),
    (range(88, 95), "pre-mission", "logistics screen header texts ('Current ... Briefing/Inventory'); probably baked into the art instead"),
    ((96, 97), "system", "developer watermark"),
    ((119,), "in-mission", "objective-type word (neighbours 120-128 are used by TacticalMap::init)"),
    ((155, 163, 164, 165), "in-mission", "object status / object class word"),
    ((168, 169, 170, 174, 885), "multiplayer", "multiplayer session text"),
    ((180, 181), "unknown", "faction names 'Clan' / 'Inner Sphere' (neighbours are multiplayer/team strings)"),
    ((862, 904, 905), "system", "demo / CD-check / movie error text"),
]


def tag_unreferenced(entries):
    for e in entries:
        if e["callers"]:
            continue
        e["referenced"] = False
        e["scope"] = "unknown"
        if e["id"] in OBJECT_NAMES:
            e["scope"] = "in-mission"
            e["guess_note"] = ("object-name id (building / turret / gate / train car names are loaded through the "
                               "object profiles); no profile in OBJECT2.PAK uses this id - spare or leftover entry")
            continue
        if e["id"] in VEHICLE_NAMES or e["id"] in MECH_NAMES:
            e["guess_scope"] = "pre-mission"
            e["guess_note"] = "mech/vehicle name id that no MISSION.FST profile uses (DescIndex)"
            continue
        for ids, gscope, why in UNREFERENCED_GUESS:
            if e["id"] in ids:
                e["guess_scope"] = gscope
                e["guess_note"] = why
                break


# --------------------------------------------------------------------------- hard-coded literals

LITERAL_SKIP = re.compile(
    r"[\\/]|\.(tga|fit|bmp|pal|txt|csv|dat|wav|fnt|ini|cfg|abl|abi|pak|fst|shp|exe|dll|log|gif|smk|tbl|bin|res)\b|"
    r"Could|Unable|rror|ailed|Not enough|NULL|Illegal|Assert|ASSERT|[Hh]eap|Cannot|Can't|couldn|not find|No RAM|Fatal|"
    r"emory|[Bb]ad |nknown|unexpected|FIT|ABL|\bkey\b|mismatch|exceeded|overflow|orrupt|debug|Debug")


LITERAL_NOT_TEXT = {"Elemental Carriers", "Smoke Manager", "Game System File", "Invalid player number",
                    "Connection protocol specified is invalid.", "User Break"}   # FIT section names / developer asserts


def hardcoded_literals(ci: CodeIndex, scopes=("pre-mission", "multiplayer", "system")):
    """English prose that is compiled into the code (not in the string table), found as immediate string
    pointers inside functions of the given scopes.  Heuristic: contains a space, mostly letters, no debug words."""
    d = ci.d
    found = defaultdict(set)
    for a in (x for x in ci.addrs if 0x601000 <= x < 0x77A000):
        i = bisect.bisect_right(ci.addrs, a)
        end = ci.addrs[i] if i < len(ci.addrs) else a + 0x1000
        fn = demangle(ci.byaddr[a])
        screen, scope = func_rule(fn)
        if scope not in scopes:
            continue
        for ins in ci.cs.disasm(d[a - BASE:end - BASE], a):
            if ins.mnemonic not in ("push", "mov", "lea"):
                continue
            for m in re.finditer(r"0x[0-9a-f]{6,8}\b", ins.op_str):
                v = int(m.group(), 16)
                o = v - BASE
                if not (0x17A000 <= o < 0x1AA000):
                    continue
                e = d.find(b"\0", o)
                if e < 0 or not (6 <= e - o <= 200):
                    continue
                raw = d[o:e]
                if not all(32 <= c < 127 or c in (9, 10) for c in raw):
                    continue
                txt = raw.decode()
                if (" " not in txt or LITERAL_SKIP.search(txt) or len(re.findall(r"[A-Za-z]{3,}", txt)) < 2
                        or not re.match(r"[A-Z%(\"']", txt) or txt in LITERAL_NOT_TEXT):
                    continue
                found[txt].add((fn, screen, scope, f"0x{v:x}"))
    out = []
    for txt, refs in sorted(found.items(), key=lambda kv: kv[0].lower()):
        out.append({"text": txt, "address": sorted({r[3] for r in refs})[0],
                    "kind": "developer assert" if re.search(r"[Ff]ile|AddMech", txt) else "player-facing message",
                    "callers": sorted({r[0] for r in refs}),
                    "screens": sorted({r[1] for r in refs}),
                    "scope": next(sc for sc in SCOPE_PRIORITY if sc in {r[2] for r in refs})})
    return out


def write_outputs(entries, dialogs, problems, nsites):
    write_json(OUT / "strings.json", entries, indent=1)
    write_json(OUT / "dialogs.json", dialogs, indent=1)
    write_json(OUT / "hardcoded_strings.json", build.literals, indent=1)
    cnt = Counter(e["scope"] for e in entries)
    kinds = Counter((e["scope"], e["kind"]) for e in entries)
    lines = ["# MCX.EXE string table (STRINGTABLE resource, LANGID 1033)", "",
             f"{len(entries)} strings, ids {entries[0]['id']}..{entries[-1]['id']}; "
             f"{nsites} `cLoadString` call sites analysed (VA 0x75aa30).", "",
             "## Counts per scope", "", "| scope | strings | of which format templates | identifiers/debug |", "|---|---:|---:|---:|"]
    for s in SCOPE_PRIORITY:
        if cnt[s]:
            lines.append(f"| {s} | {cnt[s]} | {kinds[(s, 'format')]} | {kinds[(s, 'identifier')] + kinds[(s, 'debug')]} |")
    lines.append(f"| **total** | **{len(entries)}** | | |")
    pre = [e for e in entries if e["scope"] == "pre-mission"]
    names = [e for e in pre if e.get("dynamic") in ("mech name", "vehicle name")]
    results_only = [e for e in pre if e["screens"] == ["MissionResults"]]
    ident = [e for e in pre if e["kind"] in ("identifier", "debug")]
    lines += ["",
              f"Of the {len(pre)} pre-mission strings: {len(names)} are mech/vehicle names (ids 700-783, 1200-1255, loaded through "
              f"`DescIndex`), {len(results_only)} are only used by the mission-results screen, {len(ident)} are identifiers "
              f"(file-name templates, registry values) that must not be translated, leaving about "
              f"{len(pre) - len(names) - len(results_only) - len(ident)} ordinary UI strings.", "",
              "## How the engine uses the table", "",
              "* `cLoadString(hInst, id, buf, size)` (VA 0x75aa30) calls `LoadStringA(hInst, id + languageOffset, ...)`.  "
              "`languageOffset` (VA 0x80a86c) is read from `SYSTEM.CFG` key `Language` in `_systemInit`, so one EXE can hold several "
              "languages in a single STRINGTABLE (second language at e.g. id+1000).  Strings 900 (`English`) and 901 are written to the "
              "registry by `WriteRegistryVersionNumber`.",
              "* Only 229 call sites exist; the id is the second `push` before the call.  Several sites share one call through jumps "
              "(`push id1 / jmp L / push id2 / jmp L / L: call`), so a call site can name up to ~12 ids (`call_sites` lists them).",
              "* Register ids (`dynamic`) come from data: mech names `DescIndex + 300`, vehicle names `DescIndex + 700` (MISSION.FST "
              "profiles `PM*.FIT` / `PV*.FIT` / `PE*.FIT`), object names directly from `BuildingName = <id>` in OBJECT2.PAK building "
              "packets and `Name = <id>` in train packets.",
              "* printf templates are filled with `sprintf` (`%s Lance %i`, `Objective %i: %s -- `, `%.0f Ton %s 'Mech`...); the placeholder order "
              "is fixed by the code, so a translation may not reorder `%s`/`%i`.  `placeholders` in strings.json lists them.",
              "* `\\n` inside a string is a real newline (97, 153, 154, 1257).", ""]
    lines += ["## Pre-mission strings", "",
              "Scope `pre-mission` = every screen reachable before a mission starts (main menu, new/load/save, "
              "preferences, logistics: inventory, pilots, purchase, repair/refit, briefing) plus the post-mission "
              "results screen (`MissionResults`, optional).  `kind`: ui-text / format (printf template) / identifier.  "
              "Mech and vehicle names are collapsed into one row each.", "",
              "| id | text | screens | kind |", "|---:|---|---|---|"]
    mech_rows = [e for e in entries if e["scope"] == "pre-mission" and e.get("dynamic") == "mech name"]
    veh_rows = [e for e in entries if e["scope"] == "pre-mission" and e.get("dynamic") == "vehicle name"]
    shown = set()
    for e in entries:
        if e["scope"] != "pre-mission":
            continue
        if e.get("dynamic") == "mech name":
            if "mech" not in shown:
                shown.add("mech")
                lines.append(f"| {mech_rows[0]['id']}-{mech_rows[-1]['id']} | {len(mech_rows)} mech names, e.g. "
                             f"{md_cell(mech_rows[0]['text'])}, {md_cell(mech_rows[1]['text'])}, {md_cell(mech_rows[2]['text'])} "
                             f"(chassis + A/W/J variant letter) | {md_cell(', '.join(mech_rows[0]['screens']))} | ui-text |")
            continue
        if e.get("dynamic") == "vehicle name":
            if "veh" not in shown:
                shown.add("veh")
                lines.append(f"| {veh_rows[0]['id']}-{veh_rows[-1]['id']} | {len(veh_rows)} vehicle names, e.g. "
                             f"{md_cell(veh_rows[0]['text'])}, {md_cell(veh_rows[1]['text'])}, {md_cell(veh_rows[2]['text'])} "
                             f"| {md_cell(', '.join(veh_rows[0]['screens']))} | ui-text |")
            continue
        lines.append(f"| {e['id']} | {md_cell(e['text'])} | {md_cell(', '.join(e['screens']))} | {e['kind']} |")
    lines += ["", "## Ids that no code path references", ""]
    unref = [e for e in entries if e.get("referenced") is False]
    lines.append(f"{len(unref)} strings have no `cLoadString` call site and no object/profile data pointing at them "
                 f"(`referenced: false` in strings.json); {sum(1 for e in unref if e['scope'] == 'unknown')} of them stay "
                 "`scope: unknown` (with a `guess_scope` where the neighbours or the text suggest one), the rest are spare "
                 "object-name ids (`in-mission`).  Ids: " + ", ".join(_ranges([e['id'] for e in unref])) + ".")
    if problems:
        lines += ["", "## Call sites the id tracer could not resolve", ""]
        lines += [f"- {fn} @ {site}: {kind} {val} {note}" for fn, site, kind, val, note in problems]
    write_text(OUT / "strings_summary.md", "\n".join(lines) + "\n")


def _ranges(ids):
    out = []
    ids = sorted(ids)
    i = 0
    while i < len(ids):
        j = i
        while j + 1 < len(ids) and ids[j + 1] == ids[j] + 1:
            j += 1
        out.append(f"{ids[i]}" if i == j else f"{ids[i]}-{ids[j]}")
        i = j + 1
    return out


def run():
    entries, dialogs, problems, nsites = build()
    write_outputs(entries, dialogs, problems, nsites)
    print(f"strings: {len(entries)}; call sites {nsites}; unresolved {len(problems)}")
    print(Counter(e["scope"] for e in entries))
    return entries


if __name__ == "__main__":
    from loc_common import utf8_stdout
    utf8_stdout()
    run()
