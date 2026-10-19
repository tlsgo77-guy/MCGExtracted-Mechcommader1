"""Tests for tools/build_korean_overlay.py (fixtures live in a temp dir; no game files are read or written).

    python -I tools/test_build_korean_overlay.py
"""
import contextlib
import io
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import build_korean_overlay as bo  # noqa: E402
import build_strings_bin as bsb  # noqa: E402
import mcg_pkk  # noqa: E402

CRLF = b"\r\n"

BRF_EN = (b"%fm%fc1%c****CLASSIFIED****%n\r\n%fs%fc4%cFEDCOM:TEST%n\r\n%fc6Destroy the base.%n%n\r\n"
          b"%t9Second line%n\r\n%fc5%c----------%n\r\n")
FIT_EN = (b"FITini\r\n\r\n// st Name = \"commented out\"\r\n[Header]\r\nst FileType = \"Mission\"\r\n\r\n"
          b"[Objective0]\t\t// first\r\nst Name = \"Destroy the base\"   // shown in-mission\r\nst Other = \"keep me\"\r\n\r\n"
          b"[Objective1]\r\nst Name=\"Hold the line\"\r\nl Priority = 3\n\r\n[Pilot]\r\nst Name = \"Destroy the base\"\r\nFITend\r\n")
CSV_EN = (b"// header,,,\r\nMasterArmActuatorID = 4,,,\r\n0,undefined,undefined,0,0\r\n"
          b"1,Fusion Engine,Engine,Engine,6\r\n2,Cockpit,Cockpit,Cockpit,1\r\n3,Heat Sink, HtSnk ,HeatSink,1\r\n")
DESC_EN = (b"FITini\r\n[Desc13]\t\t//SENSOR\r\nst DescString = \"IS Sensors detect enemies.%nLOAD VAL:%fc8  0.0\" \r\n"
           b"[Desc14]\r\nst DescString = \"Second.%nLOAD VAL:%fc8  0.5\"\r\n")
PMW_EN = b"FITini\r\n\r\n// Name: x\r\n[General]\r\nst Name =\t\t\"%s\"\r\nst Callsign =\t\t\"%s\"\r\nl Rank = 1\r\nFITend\r\n"
WARRIOR_FITS = {"PMW10.FIT": PMW_EN % (b"Hawk", b"HAWK"), "WAR2.FIT": PMW_EN % (b"Glenn Doren", b"BITMAN"),
                "WAR2a.FIT": PMW_EN % (b"Glenn Doren", b"CENTURION"), "PCREW.FIT": PMW_EN % (b"Vehicle Crew", b"Vehicle Crew")}
MENUS_EN = b"FITini\r\n[Menu]\r\nst ItemHelp0\t= \"Baby!\"\t// this can be up to 63 characters\r\n"

WARRIOR = (b"FITini \r\n\r\n[General]\r\nst Name=\"%s\"\r\nst Callsign=\"%s\"\r\nl Rank = 0 \r\n\r\n"
           b"[Skills]\r\nc Piloting=35\r\nFITend \r\n")
WARRIOR_PADDED = (b"FITini\r\n\r\n//      MechWarrior:  86   Name: Siren  Callsign: SIREN\r\n\r\n[General]\r\n"
                  b"st Brain = \"pbrain\"\r\nst Name =                                     \"Siren\"\r\nl Rank = 0 \r\n"
                  b"st Callsign =                                \"SIREN\"\r\nul ID = 86 \r\nFITend\r\n")
PKK_PACKETS = [
    b"FITini \r\n\r\n[General]\r\nst PurchaseFile=\"p\"\r\nFITend \r\n",
    WARRIOR % (b"Hawk", b"HAWK"),
    WARRIOR_PADDED,
    WARRIOR % (b"Lynx", b"LYNX"),
    b"FITini\r\n[General]\r\nst Name = \"COM-J\"\r\nst MechType=\"Commando J\"\r\nFITend\r\n",
    b"FITini\r\n[Header]\r\nl NumGifts = 0\r\nFITend\r\n",
]


def make_fst(path: Path, files: dict) -> None:
    """Uncompressed FST: u32 count + 262-byte entries {u32 offset, u32 packed, u32 real, char name[250]}."""
    names = list(files)
    head = struct.pack("<I", len(names))
    off = 4 + 262 * len(names)
    entries, body = b"", b""
    for n in names:
        d = files[n]
        entries += struct.pack("<III", off + len(body), len(d), len(d)) + n.encode("latin-1").ljust(250, b"\0")
        body += d
    path.write_bytes(head + entries + body)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.repo, self.game, self.out = root / "repo", root / "game", root / "game" / "lang" / "kor"
        for d in ("MISSION.FST", "MISC.FST", "localization/ko", "localization/en"):
            (self.repo / d).mkdir(parents=True)
        (self.game / "DATA" / "SAVEGAME").mkdir(parents=True)
        files = {"brf9999.txt": BRF_EN, "MIS9999.FIT": FIT_EN, "PMW9.FIT": FIT_EN}
        (self.repo / "MISSION.FST" / "brf9999.txt").write_bytes(BRF_EN)
        (self.repo / "MISSION.FST" / "MIS9999.FIT").write_bytes(FIT_EN)
        (self.repo / "MISSION.FST" / "PMW9.FIT").write_bytes(FIT_EN)
        for name, data in WARRIOR_FITS.items():
            (self.repo / "MISSION.FST" / name).write_bytes(data)
        for name, data in (("compbas.csv", CSV_EN), ("desc.fit", DESC_EN), ("Menus.fit", MENUS_EN)):
            (self.repo / "MISC.FST" / name).write_bytes(data)
        make_fst(self.game / "MISSION.FST", {
            "data\\missions\\brf9999.txt": BRF_EN, "data\\missions\\MIS9999.FIT": FIT_EN,
            "data\\missions\\warriors\\PMW9.FIT": FIT_EN, "data\\missions\\miscfunc.abi": b"x",
            **{"data\\missions\\warriors\\" + n: d for n, d in WARRIOR_FITS.items()}})
        make_fst(self.game / "MISC.FST", {
            "data\\fonts\\BLUE.FNT": b"font", "data\\objects\\desc.fit": DESC_EN,
            "data\\objects\\compbas.csv": CSV_EN, "data\\iface\\Menus.fit": MENUS_EN})
        for name in ("START0.PKK", "XSTART0.PKK"):
            (self.game / "DATA" / "SAVEGAME" / name).write_bytes(mcg_pkk.build_packet_file(PKK_PACKETS))

    def ko(self, rel: str, content, mode="w"):
        p = self.repo / "localization" / "ko" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        elif rel.endswith(".json"):
            p.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        else:
            p.write_text(content, encoding="utf-8", newline="")
        return p

    def build(self, only=None, check=False, **kw):
        ctx = bo.Context(self.repo, self.game, self.out)
        return bo.run(ctx, set(only) if only else None, check, **kw)

    def one(self, results, name):
        return next(r for r in results if r.name == name)

    def read(self, rel: str) -> bytes:
        return (self.out / rel.replace("\\", "/")).read_bytes()


class StringsTest(Base):
    def test_round_trip_through_dump(self):
        table = {"31": "현재 자원 포인트", "5": "목표 %i: %s -- ", "100": "안녕\n세상"}
        self.ko("strings.json", table)
        res = self.one(self.build(["strings"]), "strings")
        self.assertEqual(res.errors, [])
        path = self.out / "strings.bin"
        self.assertEqual(bsb.dump(path.read_bytes()), table)
        dumped = subprocess.run([sys.executable, "-I", str(TOOLS / "build_strings_bin.py"), "--dump", str(path)],
                                capture_output=True, check=True)
        self.assertEqual(json.loads(dumped.stdout.decode("utf-8")), table)

    def test_bad_syllable_is_an_error_and_nothing_is_written(self):
        self.ko("strings.json", {"1": "좋아", "2": "똠방각하"})
        res = self.one(self.build(["strings"]), "strings")
        self.assertTrue(any("2" == label and "KS X 1001" in msg for label, msg in res.errors), res.errors)
        self.assertFalse((self.out / "strings.bin").exists())

    def test_warnings_long_string_placeholders_unknown_id(self):
        (self.repo / "localization" / "en" / "strings.json").write_text(
            json.dumps([{"id": 5, "text": "Objective %i: %s"}, {"id": 6, "text": "Plain"}]), encoding="utf-8")
        self.ko("strings.json", {"5": "목표 %s: %i", "6": "가" * 130, "99": "없는 번호"})
        res = self.one(self.build(["strings"]), "strings")
        self.assertEqual(res.errors, [])
        msgs = " | ".join(f"{l}:{m}" for l, m in res.warnings)
        self.assertIn("placeholders differ", msgs)
        self.assertIn("260 bytes", msgs)
        self.assertIn("not in the English string table", msgs)

    def test_missing_source_is_skipped(self):
        res = self.one(self.build(["strings"]), "strings")
        self.assertTrue(res.skipped)
        self.assertEqual(res.errors, [])


class BriefingTest(Base):
    KO = ("%fm%fc1%c****기밀****%n\n%fs%fc4%cFEDCOM:TEST%n\n%fc6기지를 파괴하십시오.%n%n\n"
          "%t9두 번째 줄%n\n%fc5%c----------%n")           # LF only, no trailing newline

    def test_crlf_and_trailing_crlf(self):
        self.ko("briefings/brf9999.txt", self.KO)
        res = self.one(self.build(["briefings"]), "briefings")
        self.assertEqual((res.errors, res.warnings), ([], []))
        data = self.read("data/missions/brf9999.txt")
        self.assertTrue(data.endswith(CRLF))
        self.assertEqual(data.count(b"\n"), data.count(CRLF))
        self.assertEqual(data.count(CRLF), 5)
        self.assertEqual(data.decode("euc_kr"), self.KO.replace("\n", "\r\n") + "\r\n")
        i = 0
        while i < len(data):                                # every Hangul is a 2-byte KS X 1001 cell
            if data[i] < 0x80:
                i += 1
                continue
            self.assertTrue(0xB0 <= data[i] <= 0xC8 and 0xA1 <= data[i + 1] <= 0xFE, data[i:i + 2].hex())
            i += 2

    def test_crlf_source_and_bom(self):
        self.ko("briefings/brf9999.txt", b"\xef\xbb\xbf" + self.KO.replace("\n", "\r\n").encode("utf-8") + b"\r\n\r\n")
        res = self.one(self.build(["briefings"]), "briefings")
        self.assertEqual(res.errors, [])
        self.assertTrue(any("BOM" in m for _l, m in res.warnings))
        data = self.read("data/missions/brf9999.txt")
        self.assertEqual(data.count(b"\n"), data.count(CRLF))
        self.assertTrue(data.endswith(CRLF + CRLF))         # a trailing blank line is kept, not collapsed

    def test_code_count_mismatch_warns_but_writes(self):
        self.ko("briefings/brf9999.txt", self.KO.replace("%n%n", "%n").replace("%t9", "%t12"))
        res = self.one(self.build(["briefings"]), "briefings")
        self.assertEqual(res.errors, [])
        text = " ".join(m for _l, m in res.warnings)
        self.assertIn("%n 6->5", text)                      # one %n fewer
        self.assertNotIn("%t", text)                        # %tN is compared by kind, not by value
        self.assertTrue((self.out / "data/missions/brf9999.txt").exists())

    def test_centre_overflow_fails(self):
        ok = "%c" + "가" * 40 + "%n"                         # exactly 80 bytes: allowed
        bad = "%c" + "가" * 41 + "%n"                        # 82 bytes
        self.ko("briefings/brf9999.txt", self.KO + "\n" + ok + "\n" + bad)
        res = self.one(self.build(["briefings"]), "briefings")
        self.assertEqual(len(res.errors), 1, res.errors)
        self.assertIn("82 bytes", res.errors[0][1])
        self.assertIn("line 7", res.errors[0][1])
        self.assertFalse((self.out / "data/missions/brf9999.txt").exists())
        self.assertEqual(res.outputs, [])

    def test_centre_segment_ignores_line_breaks_and_stops_at_next_code(self):
        data = ("%c" + "가" * 30 + "\r\n" + "가" * 10 + "%n" + "가" * 60).encode("euc_kr")
        self.assertEqual([n for _o, n, _s in bo.centre_overflows(data)], [])     # 80 bytes, then %n ends it
        self.assertEqual([n for _o, n, _s in bo.centre_overflows(b"%%c" + b"x" * 90)], [])   # '%%' then literal c
        self.assertEqual([n for _o, n, _s in bo.centre_overflows(b"%C" + b"x" * 90)], [90])

    def test_bad_syllable_and_non_utf8(self):
        self.ko("briefings/brf9999.txt", "%c햏%n\n")
        self.ko("briefings/MIS9999.FIT.txt", b"\xff\xfe")
        res = self.one(self.build(["briefings"]), "briefings")
        labels = " | ".join(f"{l}:{m}" for l, m in res.errors)
        self.assertIn("brf9999.txt line 1", labels)
        self.assertIn("KS X 1001", labels)
        self.assertIn("no English original", labels)

    def test_long_line_warns(self):
        self.ko("briefings/brf9999.txt", self.KO + "\n" + "가" * 127 + "%n")      # 254 bytes + "%n"
        res = self.one(self.build(["briefings"]), "briefings")
        self.assertEqual(res.errors, [])
        self.assertTrue(any("> 253" in m for _l, m in res.warnings), res.warnings)

    def test_scan_codes(self):
        toks = [t for t, _s, _e in bo.scan_codes(b"%FM%fc1%C a %t12 %T9 %%n %fl %fs %x % %fc")]
        self.assertEqual(toks, ["%fm", "%fc1", "%c", "%t", "%t", "%%", "%fl", "%fs", "%x", "% ", "%f?"])


class FitTest(Base):
    def entry(self, **kw):
        e = {"file": "MISSION.FST/MIS9999.FIT", "section": "Objective0", "key": "Name",
             "en": "Destroy the base", "ko": "기지를 파괴하라"}
        e.update(kw)
        return e

    def test_replace_keeps_everything_else_identical(self):
        self.ko("fit_strings.json", [self.entry(), self.entry(section="Objective1", en="Hold the line", ko="방어선을 사수하라"),
                                     self.entry(key="Name", ko="", section="Pilot")])         # empty ko = untranslated
        res = self.one(self.build(["fit"]), "fit")
        self.assertEqual((res.errors, res.warnings), ([], []))
        self.assertEqual([o.rel for o in res.outputs], ["data\\missions\\MIS9999.FIT"])
        data = self.read("data/missions/MIS9999.FIT")
        expect = (FIT_EN.replace(b"\"Destroy the base\"   //", "\"기지를 파괴하라\"   //".encode("euc_kr"))
                  .replace(b"st Name=\"Hold the line\"", b"st Name=\"" + "방어선을 사수하라".encode("euc_kr") + b"\""))
        # the [Pilot] section value (same English text) must not have been touched
        self.assertTrue(expect.count(b"Destroy the base") == 1)
        self.assertEqual(data, expect)
        self.assertEqual(data.count(b"\r\n"), FIT_EN.count(b"\r\n"))        # CRLF kept, the bare LF line too
        self.assertEqual(data.count(b"\n"), FIT_EN.count(b"\n"))
        self.assertIn(b"// st Name = \"commented out\"", data)

    def test_warrior_path_comes_from_the_fst_entry(self):
        self.ko("fit_strings.json", [self.entry(file="MISSION.FST/PMW9.FIT", ko="호크")])
        res = self.one(self.build(["fit"]), "fit")
        self.assertEqual(res.errors, [])
        self.assertTrue((self.out / "data/missions/warriors/PMW9.FIT").exists())

    def test_misc_paths_and_markup_check(self):
        self.ko("fit_strings.json", [
            {"file": "MISC.FST/desc.fit", "section": "Desc13", "key": "DescString", "en": "x",
             "ko": "IS 센서는 적을 탐지합니다.%n적재값:%fc8  0.0"},
            {"file": "MISC.FST/desc.fit", "section": "Desc14", "key": "DescString", "ko": "둘째.%n%n적재값:%fc8  0.5"},
            {"file": "MISC.FST/Menus.fit", "section": "Menu", "key": "ItemHelp0", "ko": "가" * 40}])
        res = self.one(self.build(["fit"]), "fit")
        self.assertEqual(res.errors, [])
        self.assertEqual(sorted(o.rel for o in res.outputs), ["data\\iface\\Menus.fit", "data\\objects\\desc.fit"])
        msgs = " | ".join(f"{l}:{m}" for l, m in res.warnings)
        self.assertIn("%n 1->2", msgs)                                  # Desc14 has one %n more
        self.assertIn("original text is", msgs)                         # Desc13: stale `en`
        self.assertIn("up to 63 characters", msgs)                      # Menus.fit comment: 80 bytes > 63
        desc = self.read("data/objects/desc.fit")
        self.assertIn("IS 센서는 적을 탐지합니다.%n적재값:%fc8  0.0".encode("euc_kr") + b"\" \r\n", desc)

    def test_errors(self):
        self.ko("fit_strings.json", [
            self.entry(section="Objective9"),                         # no such section
            self.entry(key="Missing"),                                # no such key
            self.entry(ko='say "hi"'),                                # quote would end the value
            self.entry(ko="똠"),                                       # not a KS X 1001 syllable
            self.entry(file="MISSION.FST/NOPE.FIT"),                  # unknown file
            self.entry(file="OTHER/x.fit"),                           # bad folder
        ])
        res = self.one(self.build(["fit"]), "fit")
        text = " | ".join(f"{l}:{m}" for l, m in res.errors)
        for needle in ("no matching `st` line", "breaks the quoted FIT value", "KS X 1001", "not in MISSION.FST", "must be MISSION.FST"):
            self.assertIn(needle, text)
        self.assertEqual(res.outputs, [])

    def test_conflicting_translations(self):
        self.ko("fit_strings.json", [self.entry(ko="가"), self.entry(ko="나")])
        res = self.one(self.build(["fit"]), "fit")
        self.assertTrue(any("two different translations" in m for _l, m in res.errors))

    def csv_entry(self, rid, key, ko, en=None):
        return {"file": "MISC.FST/compbas.csv", "section": f"component {rid}", "key": key, "en": en, "ko": ko}

    def test_csv_rows(self):
        self.ko("fit_strings.json", [
            self.csv_entry(1, "name", "핵융합 엔진", "Fusion Engine"), self.csv_entry(1, "abbr", "엔진", "Engine"),
            self.csv_entry(2, "name", "조종석", "Cockpit"),            # abbr == name in the original: follows the name
            self.csv_entry(3, "abbr", "방열기")])                       # padded cell " HtSnk " keeps its padding
        res = self.one(self.build(["fit"]), "fit")
        self.assertEqual(res.errors, [])
        self.assertEqual(res.outputs[0].rel, "data\\objects\\compbas.csv")
        lines = self.read("data/objects/compbas.csv").split(CRLF)
        orig = CSV_EN.split(CRLF)
        self.assertEqual(lines[0], orig[0])
        self.assertEqual(lines[1], orig[1])
        self.assertEqual(lines[2], orig[2])
        self.assertEqual(lines[3], "1,핵융합 엔진,엔진,Engine,6".encode("euc_kr"))
        self.assertEqual(lines[4], "2,조종석,조종석,Cockpit,1".encode("euc_kr"))
        self.assertEqual(lines[5], b"3,Heat Sink, " + "방열기".encode("euc_kr") + b" ,HeatSink,1")
        self.assertEqual(len(lines), len(orig))
        self.assertTrue(any("follow the translated name" in n for n in res.notes))

    def test_csv_errors(self):
        self.ko("fit_strings.json", [self.csv_entry(1, "name", "가,나"), self.csv_entry(77, "name", "가"),
                                     self.csv_entry(2, "type", "가")])
        res = self.one(self.build(["fit"]), "fit")
        text = " | ".join(m for _l, m in res.errors)
        self.assertIn("would split", text)
        self.assertIn("no row with id 77", text)
        self.assertIn("key 'name' or 'abbr'", text)
        self.assertEqual(res.outputs, [])


class PilotsTest(Base):
    def test_roster_rewrite(self):
        self.ko("pilots.json", {"Hawk": {"name": "호크", "callsign": "매"}, "Siren": {"name": "사이렌", "callsign": "사이렌"},
                                "Ghost": {"name": "유령", "callsign": "유령"}})
        res = self.one(self.build(["pilots"]), "pilots")
        self.assertEqual(res.errors, [])
        self.assertEqual(sorted(o.rel for o in res.outputs), ["data\\savegame\\START0.PKK", "data\\savegame\\XSTART0.PKK"])
        warn = " | ".join(f"{l}:{m}" for l, m in res.warnings)
        self.assertIn("Lynx", warn)                                         # untranslated warrior stays English
        self.assertTrue(any("1 of 3 pilots.json entries matched no" in n for n in res.notes), res.notes)   # Ghost
        for name in ("START0.PKK", "XSTART0.PKK"):
            pf = mcg_pkk.PacketFile(self.read("data/savegame/" + name))
            self.assertTrue(pf.checksum_ok)
            self.assertEqual(pf.num_packets, len(PKK_PACKETS))
            got = [pf.read_packet(i) for i in range(pf.num_packets)]
            self.assertEqual(got[0], PKK_PACKETS[0])
            self.assertEqual(got[3:], PKK_PACKETS[3:])                      # untranslated / mech / gifts: untouched
            self.assertEqual(got[1], PKK_PACKETS[1].replace(b'"Hawk"', b'"' + "호크".encode("euc_kr") + b'"')
                             .replace(b'"HAWK"', b'"' + "매".encode("euc_kr") + b'"'))
            self.assertEqual(got[2], PKK_PACKETS[2].replace(b'"Siren"', b'"' + "사이렌".encode("euc_kr") + b'"')
                             .replace(b'"SIREN"', b'"' + "사이렌".encode("euc_kr") + b'"'))
            for p in got:
                self.assertTrue(p.endswith(CRLF))
                self.assertEqual(p.count(b"\n"), p.count(CRLF))
            self.assertEqual({mcg_pkk.PacketFile(self.read("data/savegame/" + name)).packet_info(i)[0] for i in range(6)}, {0})   # RAW

    def test_deterministic_and_unchanged_on_rerun(self):
        self.ko("pilots.json", {"Hawk": {"name": "호크", "callsign": "호크"}})
        self.build(["pilots"])
        first = self.read("data/savegame/START0.PKK")
        res = self.one(self.build(["pilots"]), "pilots")
        self.assertEqual({o.status for o in res.outputs}, {"unchanged"})
        self.assertEqual(self.read("data/savegame/START0.PKK"), first)

    def test_warrior_fits_are_opt_in(self):
        self.ko("pilots.json", {"Hawk": {"name": "호크", "callsign": "호크", "callsign_en": "HAWK", "source": "x"}})
        res = self.one(self.build(["pilots"]), "pilots")
        self.assertFalse(any("warriors" in o.rel for o in res.outputs))
        res = self.one(self.build(["pilots"], warrior_fits=True), "pilots")
        self.assertEqual(res.errors, [])
        self.assertEqual([o.rel for o in res.outputs if "warriors" in o.rel], ["data\\missions\\warriors\\PMW10.FIT"])
        self.assertEqual(self.read("data/missions/warriors/PMW10.FIT"),
                         WARRIOR_FITS["PMW10.FIT"].replace(b'"Hawk"', b'"' + "호크".encode("euc_kr") + b'"')
                         .replace(b'"HAWK"', b'"' + "호크".encode("euc_kr") + b'"'))

    def test_alt_callsigns_and_mismatches(self):
        self.ko("pilots.json", {"Glenn Doren": {"name": "글렌 도런", "callsign": "비트맨", "callsign_en": "BITMAN",
                                                "alt_callsigns": {"CENTURION": "센추리온"}},
                                "Hawk": {"name": "호크", "callsign": "호크", "callsign_en": "FALCON"}})
        res = self.one(self.build(["pilots"], warrior_fits=True), "pilots")
        self.assertEqual(res.errors, [])
        a = self.read("data/missions/warriors/WAR2.FIT")
        b = self.read("data/missions/warriors/WAR2a.FIT")
        self.assertIn('"비트맨"'.encode("euc_kr"), a)
        self.assertIn('"센추리온"'.encode("euc_kr"), b)
        self.assertIn('"글렌 도런"'.encode("euc_kr"), b)
        hawk = self.read("data/missions/warriors/PMW10.FIT")                 # callsign_en says FALCON: callsign kept
        self.assertIn(b'"HAWK"', hawk)
        self.assertIn('"호크"'.encode("euc_kr"), hawk)
        self.assertTrue(any("kept English" in m and "HAWK" in m for _l, m in res.warnings), res.warnings)
        self.assertFalse((self.out / "data/missions/warriors/PCREW.FIT").exists())

    def test_explicit_fit_entry_beats_pilots_json(self):
        self.ko("pilots.json", {"Hawk": {"name": "호크", "callsign": "호크"}})
        self.ko("fit_strings.json", [{"file": "MISSION.FST/PMW10.FIT", "section": "General", "key": "Name", "ko": "매"}])
        results = self.build(["fit", "pilots"], warrior_fits=True)
        pilots = self.one(results, "pilots")
        self.assertEqual([o.rel for o in pilots.outputs if "warriors" in o.rel], [])
        self.assertTrue(any("translates them explicitly" in n for n in pilots.notes), pilots.notes)
        data = self.read("data/missions/warriors/PMW10.FIT")
        self.assertIn('"매"'.encode("euc_kr"), data)
        self.assertIn(b'"HAWK"', data)                                       # only the explicit entry applied

    def test_bad_pilot_text(self):
        self.ko("pilots.json", {"Hawk": {"name": "똠", "callsign": "호크"}})
        res = self.one(self.build(["pilots"]), "pilots")
        self.assertTrue(res.errors)
        self.assertEqual(res.outputs, [])


class DriverTest(Base):
    def test_check_writes_nothing_and_full_run_is_deterministic(self):
        self.ko("strings.json", {"1": "확인"})
        self.ko("briefings/brf9999.txt", BriefingTest.KO)
        self.ko("fit_strings.json", [{"file": "MISC.FST/desc.fit", "section": "Desc13", "key": "DescString",
                                      "ko": "가.%nLOAD VAL:%fc8  0.0"}])
        self.ko("pilots.json", {"Hawk": {"name": "호크", "callsign": "호크"}})
        results = self.build(check=True)
        self.assertFalse(self.out.exists())
        self.assertEqual({o.status for r in results for o in r.outputs}, {"would create"})
        self.build()
        snap = {p.relative_to(self.out).as_posix(): p.read_bytes() for p in sorted(self.out.rglob("*")) if p.is_file()}
        self.assertEqual(sorted(snap), ["data/missions/brf9999.txt", "data/objects/desc.fit", "data/savegame/START0.PKK",
                                        "data/savegame/XSTART0.PKK", "strings.bin"])
        results = self.build()
        self.assertEqual({o.status for r in results for o in r.outputs}, {"unchanged"})
        again = {p.relative_to(self.out).as_posix(): p.read_bytes() for p in sorted(self.out.rglob("*")) if p.is_file()}
        self.assertEqual(snap, again)

    def test_never_writes_art_or_fonts(self):
        ctx = bo.Context(self.repo, self.game, self.out)
        for bad in ("data\\art\\x.tga", "DATA\\Fonts\\BLUE.FNT", "data/fonts/a.fnt", "data\\..\\x", "C:\\x"):
            with self.assertRaises(ValueError):
                ctx.overlay_path(bad)
        self.assertEqual(ctx.overlay_path("data\\art2\\x.tga"), self.out / "data" / "art2" / "x.tga")

    def test_cli_exit_codes_and_only(self):
        self.ko("strings.json", {"1": "확인"})
        self.ko("briefings/brf9999.txt", "%c" + "가" * 50 + "%n\n")       # %c overflow: hard failure
        argv = ["--repo", str(self.repo), "--game-dir", str(self.game)]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(bo.main(argv + ["--only", "strings", "--check"]), 0)
            self.assertEqual(bo.main(argv + ["--only", "strings,briefings", "--check"]), 1)
        self.assertFalse(self.out.exists())
        self.assertIn("exceeds the 80-byte limit", buf.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(bo.main(argv + ["--only", "strings"]), 0)
        self.assertTrue((self.out / "strings.bin").exists())
        self.assertFalse((self.out / "data").exists())

    def test_strict_turns_warnings_into_errors(self):
        self.ko("briefings/brf9999.txt", BriefingTest.KO.replace("%n%n", "%n"))
        with contextlib.redirect_stdout(io.StringIO()):
            argv = ["--repo", str(self.repo), "--game-dir", str(self.game), "--only", "briefings"]
            self.assertEqual(bo.main(argv + ["--check"]), 0)
            self.assertEqual(bo.main(argv + ["--check", "--strict"]), 1)

    def test_missing_fst_is_one_clear_error(self):
        (self.game / "MISSION.FST").unlink()
        self.ko("briefings/brf9999.txt", BriefingTest.KO)
        res = self.one(self.build(["briefings"]), "briefings")
        self.assertEqual(len(res.errors), 1)
        self.assertIn("MISSION.FST", res.errors[0][1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
