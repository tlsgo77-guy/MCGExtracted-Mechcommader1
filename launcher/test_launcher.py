# -*- coding: utf-8 -*-
"""Unit tests for mcg_launcher (never starts the game).

Run from this folder:  python -m unittest -v test_launcher
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import unittest
import winreg
from pathlib import Path
from unittest import mock

import mcg_launcher as ml

CRLF = "\r\n"
SHIPPED_PREFS = CRLF.join([
    "FITini",
    "",
    "[MechCommander]",
    "b PaletteCycle=FALSE",
    "b DirectDraw=TRUE",
    "b Use90Pixel=TRUE",
    "b Force45Pixel=FALSE",
    "b Force16Mb=FALSE",
    "b Force32Mb=FALSE",
    "l Difficulty=1",
    "l Brightness=0",
    "l MusicVolume=64",
    "l RadioVolume=64",
    "l SFXVolume=96",
    "",
    "FITend",
]) + CRLF

DEFAULT_VALUES = ml.build_prefs_values(ml.SETTINGS_DEFAULTS, True, None)

STAGED_DDRAW_INI = (Path(__file__).resolve().parent.parent / "game-source" / "tools"
                    / "cnc-ddraw" / "ddraw.ini")
TEST_COMPAT_KEY = r"Software\MCGLauncherUnitTest\Layers"


def _force_rmtree(path):
    def onexc(func, p, _exc):
        os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
        func(p)
    shutil.rmtree(path, onexc=onexc)


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mcgl-test-"))
        self.addCleanup(_force_rmtree, self.tmp)


def _lines(raw: bytes) -> list[str]:
    return raw.decode("latin-1").split(CRLF)[:-1]


class PrefsTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.prefs = self.tmp / "prefs.cfg"
        self.prefs.write_bytes(SHIPPED_PREFS.encode("ascii"))

    def assert_wellformed(self, raw: bytes):
        self.assertTrue(raw.endswith(b"\r\n"), "must end with CRLF")
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"), "bare LF found")
        self.assertEqual(raw.count(b"\r"), raw.count(b"\r\n"), "bare CR found")
        lines = _lines(raw)
        self.assertEqual(lines[0].strip(), "FITini")
        self.assertEqual(lines[-1].strip(), "FITend")
        self.assertEqual(sum(1 for ln in lines if ln.strip() == "FITini"), 1)
        self.assertEqual(sum(1 for ln in lines if ln.strip() == "FITend"), 1)
        self.assertIn("[MechCommander]", lines)
        return lines

    def test_read_prefs_returns_lines(self):
        lines = ml.read_prefs(self.prefs)
        self.assertEqual(lines, SHIPPED_PREFS.split(CRLF)[:-1])
        self.assertEqual(ml.parse_prefs(lines)["SFXVolume"], "96")
        self.assertEqual(ml.read_prefs(self.tmp / "missing.cfg"), ml.SHIPPED_PREFS_LINES)

    def test_write_defaults_exact_output(self):
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        raw = self.prefs.read_bytes()
        self.assert_wellformed(raw)
        expected = CRLF.join([
            "FITini", "", "[MechCommander]",
            "b PaletteCycle=FALSE", "b DirectDraw=TRUE", "b Use90Pixel=TRUE",
            "b Force45Pixel=FALSE", "b Force16Mb=FALSE", "b Force32Mb=FALSE",
            "l Difficulty=1", "l Brightness=0", "l MusicVolume=64",
            "l RadioVolume=64", "l SFXVolume=96",
            "l Resolution=3", "l Language=0",
            "", "FITend"]) + CRLF
        self.assertEqual(raw.decode("ascii"), expected)

    def test_keys_replaced_not_duplicated(self):
        values = dict(DEFAULT_VALUES, Difficulty=3, MusicVolume=10, DirectDraw=False,
                      Use90Pixel=False, Force45Pixel=True, Resolution=1)
        ml.write_prefs(self.prefs, values)
        lines = self.assert_wellformed(self.prefs.read_bytes())
        for key in ml.PREFS_OWNED_KEYS:
            hits = [ln for ln in lines if ln.split("=")[0].split()[-1:] == [key]]
            self.assertEqual(len(hits), 1, f"{key}: {hits}")
        self.assertIn("l Difficulty=3", lines)
        self.assertIn("l MusicVolume=10", lines)
        self.assertIn("b DirectDraw=FALSE", lines)
        self.assertIn("b Use90Pixel=FALSE", lines)
        self.assertIn("b Force45Pixel=TRUE", lines)
        self.assertIn("l Resolution=1", lines)
        # replaced in place: Difficulty stays at its original line index
        self.assertEqual(lines.index("l Difficulty=3"), 9)

    def test_duplicate_owned_keys_collapsed(self):
        text = SHIPPED_PREFS.replace("l Difficulty=1\r\n", "l Difficulty=1\r\nl Difficulty=2\r\n")
        text = text.replace("l SFXVolume=96\r\n", "l SFXVolume=96\r\nl Resolution=0\r\nl resolution=2\r\n")
        self.prefs.write_bytes(text.encode("ascii"))
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        lines = self.assert_wellformed(self.prefs.read_bytes())
        self.assertEqual([ln for ln in lines if "Difficulty" in ln], ["l Difficulty=1"])
        self.assertEqual([ln for ln in lines if "esolution" in ln], ["l Resolution=3"])

    def test_unknown_lines_preserved(self):
        text = SHIPPED_PREFS.replace(
            "l SFXVolume=96\r\n",
            "l SFXVolume=96\r\nl CustomKey=5\r\n; a comment\r\nst Name=Foo Bar\r\n")
        text = text.replace("\r\nFITend", "\r\n[Other]\r\nl Difficulty=9\r\n\r\nFITend")
        self.prefs.write_bytes(text.encode("ascii"))
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        lines = self.assert_wellformed(self.prefs.read_bytes())
        for kept in ("b PaletteCycle=FALSE", "b Force16Mb=FALSE", "b Force32Mb=FALSE",
                     "l CustomKey=5", "; a comment", "st Name=Foo Bar", "[Other]",
                     "l Difficulty=9"):
            self.assertIn(kept, lines)
        # owned keys only touched inside [MechCommander]; new keys added there
        self.assertLess(lines.index("l Language=0"), lines.index("[Other]"))
        self.assertEqual(lines.index("st Name=Foo Bar") + 1, lines.index("l Resolution=3"))

    def test_readonly_set_after_write_and_cleared_for_rewrite(self):
        self.assertFalse(ml.is_readonly(self.prefs))
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        self.assertTrue(ml.is_readonly(self.prefs))
        with self.assertRaises(PermissionError):
            open(self.prefs, "ab").close()  # really read-only for other writers
        # rewrite with new values: must clear the attribute, write, set it again
        calls = []
        real = ml.set_readonly
        with mock.patch.object(ml, "set_readonly",
                               side_effect=lambda p, on: (calls.append(on), real(p, on))):
            ml.write_prefs(self.prefs, dict(DEFAULT_VALUES, Difficulty=2))
        self.assertEqual(calls, [False, True])
        self.assertIn("l Difficulty=2", _lines(self.prefs.read_bytes()))
        self.assertTrue(ml.is_readonly(self.prefs))

    def test_idempotent_second_write(self):
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        first = self.prefs.read_bytes()
        changed = ml.write_prefs(self.prefs, DEFAULT_VALUES)
        self.assertFalse(changed)
        self.assertEqual(self.prefs.read_bytes(), first)
        self.assertTrue(ml.is_readonly(self.prefs))
        # applying the transformation to its own output is a no-op as well
        self.assertEqual(ml.apply_prefs_values(_lines(first), DEFAULT_VALUES), _lines(first))

    def test_real_shipped_variant_trailing_spaces_no_blank(self):
        # The extracted game's PREFS.CFG has "FITini " / "FITend " and no blank line.
        text = SHIPPED_PREFS.replace("FITini\r\n", "FITini \r\n").replace(
            "\r\n\r\nFITend\r\n", "\r\nFITend \r\n")
        self.prefs.write_bytes(text.encode("ascii"))
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        lines = self.assert_wellformed(self.prefs.read_bytes())
        self.assertEqual(lines[0], "FITini ")
        self.assertEqual(lines[-1], "FITend ")
        self.assertEqual(lines[-3:-1], ["l Resolution=3", "l Language=0"])

    def test_missing_file_created_from_template(self):
        target = self.tmp / "new" / "prefs.cfg"
        target.parent.mkdir()
        ml.write_prefs(target, DEFAULT_VALUES)
        lines = self.assert_wellformed(target.read_bytes())
        self.assertIn("b PaletteCycle=FALSE", lines)
        self.assertIn("l Resolution=3", lines)

    def test_repairs_missing_markers_and_section(self):
        self.prefs.write_bytes(b"; junk\r\nl Something=1\r\n")
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        lines = self.assert_wellformed(self.prefs.read_bytes())
        self.assertIn("; junk", lines)
        self.assertIn("l Something=1", lines)
        sec = lines.index("[MechCommander]")
        self.assertEqual(lines[sec + 1], "l Resolution=3")

    def test_lf_input_normalized_to_crlf(self):
        self.prefs.write_bytes(SHIPPED_PREFS.replace(CRLF, "\n").encode("ascii"))
        ml.write_prefs(self.prefs, DEFAULT_VALUES)
        self.assert_wellformed(self.prefs.read_bytes())

    def test_language_and_sprite_mapping(self):
        s = dict(ml.SETTINGS_DEFAULTS, language="ko", sprite="45", display_mode="borderless")
        v = ml.build_prefs_values(s, True, 1000)
        self.assertEqual((v["Language"], v["Use90Pixel"], v["Force45Pixel"], v["DirectDraw"]),
                         (1000, False, True, True))
        self.assertEqual(ml.build_prefs_values(s, True, None)["Language"], 0)
        windowed_no_wrapper = ml.build_prefs_values(ml.SETTINGS_DEFAULTS, False, None)
        self.assertFalse(windowed_no_wrapper["DirectDraw"])
        self.assertEqual(list(v), list(ml.PREFS_OWNED_KEYS))

    def test_settings_from_prefs(self):
        lines = ml.read_prefs(self.prefs)
        s = ml.settings_from_prefs(lines, dict(ml.SETTINGS_DEFAULTS, music=1, sfx=1))
        self.assertEqual((s["music"], s["radio"], s["sfx"], s["sprite"], s["resolution"]),
                         (64, 64, 96, "90", 3))


DDRAW_FIXTURE = CRLF.join([
    "; cnc-ddraw - https://github.com/FunkyFr3sh/cnc-ddraw",
    "",
    "[ddraw]",
    "; ### Optional settings ###",
    "width=640",
    "height=480",
    "",
    "; Override the width/height settings",
    "fullscreen=false",
    "",
    "; Run in windowed mode rather than going fullscreen",
    "windowed=false",
    "maintas = false",
    "; windowed=commented-out-must-stay",
    "shader=Shaders\\interpolation\\catmull-rom-bilinear.glsl",
    "singlecpu=false",
    "",
    "",
    "; 7th Legion",
    "[legion]",
    "maxgameticks=25",
    "singlecpu=false",
    "windowed=false",
    "",
    "[Other]",
    "renderer=gdi",
]) + CRLF


COMMON_DDRAW = [f"{k}={v}" for k, v in ml.DDRAW_COMMON_SETTINGS]


class DdrawTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.ini = self.tmp / "ddraw.ini"

    def section(self, lines, name):
        start = lines.index(f"[{name}]")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("[")), len(lines))
        return lines[start + 1:end]

    def test_create_from_nothing_windowed(self):
        self.assertTrue(ml.update_ddraw_ini(self.ini, "windowed", False))
        self.assertEqual(self.ini.read_bytes().decode("ascii"), CRLF.join([
            "[ddraw]", "windowed=true", "fullscreen=false", "maintas=true", "boxing=false",
            "width=0", "height=0"] + COMMON_DDRAW) + CRLF)

    def test_create_from_nothing_other_modes(self):
        ml.update_ddraw_ini(self.ini, "borderless", False)
        self.assertEqual(_lines(self.ini.read_bytes()), [
            "[ddraw]", "windowed=true", "fullscreen=true", "maintas=true", "boxing=true"]
            + COMMON_DDRAW)
        self.ini.unlink()
        ml.update_ddraw_ini(self.ini, "fullscreen", True)
        self.assertEqual(_lines(self.ini.read_bytes()), [
            "[ddraw]", "windowed=false", "fullscreen=true", "maintas=true", "boxing=false"]
            + COMMON_DDRAW + ["singlecpu=true", "hook=4"])

    def test_advanced_keys_only_when_ticked(self):
        ml.update_ddraw_ini(self.ini, "windowed", False)
        text = self.ini.read_text()
        self.assertNotIn("singlecpu", text)
        self.assertNotIn("hook", text)
        ml.update_ddraw_ini(self.ini, "windowed", True)
        lines = _lines(self.ini.read_bytes())
        self.assertEqual(lines[-2:], ["singlecpu=true", "hook=4"])

    def test_update_existing_keeps_comments_and_other_sections(self):
        self.ini.write_bytes(DDRAW_FIXTURE.encode("ascii"))
        before = _lines(self.ini.read_bytes())
        ml.update_ddraw_ini(self.ini, "windowed", False)
        after = _lines(self.ini.read_bytes())
        raw = self.ini.read_bytes()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        # every comment line survives
        self.assertEqual([ln for ln in before if ln.startswith(";")],
                         [ln for ln in after if ln.startswith(";")])
        # other sections untouched
        self.assertEqual(self.section(before, "legion"), self.section(after, "legion"))
        self.assertEqual(self.section(before, "Other"), self.section(after, "Other"))
        ddraw = self.section(after, "ddraw")
        # replaced in place
        self.assertEqual(after[before.index("width=640")], "width=0")
        self.assertEqual(after[before.index("windowed=false")], "windowed=true")
        self.assertEqual(after[before.index("maintas = false")], "maintas=true")
        # untouched [ddraw] lines (advanced off -> singlecpu kept as is)
        self.assertIn("singlecpu=false", ddraw)
        self.assertIn("shader=Shaders\\interpolation\\catmull-rom-bilinear.glsl", ddraw)
        self.assertIn("; windowed=commented-out-must-stay", ddraw)
        # missing keys appended after the last setting of [ddraw], once each
        last = ddraw.index("singlecpu=false")
        appended = ["boxing=false"] + COMMON_DDRAW
        self.assertEqual(ddraw[last + 1:last + 1 + len(appended)], appended)
        for key in ("windowed", "fullscreen", "maintas", "boxing", "width", "height",
                    *[k for k, _ in ml.DDRAW_COMMON_SETTINGS]):
            self.assertEqual(sum(1 for ln in ddraw if ln.split("=")[0].strip() == key), 1, key)
        # the comment introducing [legion] stays right above it
        self.assertEqual(after[after.index("[legion]") - 1], "; 7th Legion")

    def test_advanced_replaces_existing_singlecpu(self):
        self.ini.write_bytes(DDRAW_FIXTURE.encode("ascii"))
        ml.update_ddraw_ini(self.ini, "borderless", True)
        after = _lines(self.ini.read_bytes())
        ddraw = self.section(after, "ddraw")
        self.assertIn("singlecpu=true", ddraw)
        self.assertNotIn("singlecpu=false", ddraw)
        self.assertIn("hook=4", ddraw)
        self.assertEqual(self.section(after, "legion"),
                         ["maxgameticks=25", "singlecpu=false", "windowed=false", ""])

    def test_idempotent_and_mode_switch(self):
        self.ini.write_bytes(DDRAW_FIXTURE.encode("ascii"))
        ml.update_ddraw_ini(self.ini, "windowed", False)
        first = self.ini.read_bytes()
        self.assertFalse(ml.update_ddraw_ini(self.ini, "windowed", False))
        self.assertEqual(self.ini.read_bytes(), first)
        ml.update_ddraw_ini(self.ini, "borderless", False)
        ml.update_ddraw_ini(self.ini, "fullscreen", False)
        ml.update_ddraw_ini(self.ini, "windowed", False)
        self.assertEqual(self.ini.read_bytes(), first)

    def test_lf_file_stays_lf_and_bom_kept(self):
        self.ini.write_bytes(b"\xef\xbb\xbf" + DDRAW_FIXTURE.replace(CRLF, "\n").encode("ascii"))
        ml.update_ddraw_ini(self.ini, "fullscreen", False)
        raw = self.ini.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf[") or raw.startswith(b"\xef\xbb\xbf;"))
        self.assertNotIn(b"\r", raw)
        self.assertIn(b"\nwindowed=false\n", raw)

    def test_file_without_ddraw_section(self):
        self.ini.write_bytes(b"[legion]\r\nwindowed=false\r\n")
        ml.update_ddraw_ini(self.ini, "borderless", False)
        self.assertEqual(_lines(self.ini.read_bytes()), [
            "[ddraw]", "windowed=true", "fullscreen=true", "maintas=true", "boxing=true"]
            + COMMON_DDRAW + ["", "[legion]", "windowed=false"])

    def test_bad_mode_rejected(self):
        with self.assertRaises(ValueError):
            ml.update_ddraw_ini(self.ini, "stretched", False)
        self.assertFalse(self.ini.exists())

    @unittest.skipUnless(STAGED_DDRAW_INI.is_file(), "staged cnc-ddraw ddraw.ini not present")
    def test_staged_cnc_ddraw_ini(self):
        shutil.copy2(STAGED_DDRAW_INI, self.ini)
        before = _lines(self.ini.read_bytes())
        ml.update_ddraw_ini(self.ini, "windowed", True)
        after = _lines(self.ini.read_bytes())
        self.assertEqual(len(before), len(after))  # all keys already present -> no appends
        changed = {before[i]: after[i] for i in range(len(before)) if before[i] != after[i]}
        # width/height/fullscreen/boxing/renderer/nonexclusive/singlecpu/hook already match
        expected_changes = {
            "windowed=false": "windowed=true", "maintas=false": "maintas=true",
            "maxfps=-1": "maxfps=60", "vsync=false": "vsync=true",
            "resolutions=0": "resolutions=2", "d3d9_filter=2": "d3d9_filter=1",
        }
        self.assertEqual(changed, expected_changes)
        start = before.index("[legion]")
        self.assertEqual(before[start:], after[start:])  # game sections untouched


AREA_1080P = (1920, 1040)   # 1920x1080 monitor minus a 40 px taskbar
AREA_4K = (3840, 2088)      # 3840x2160 monitor minus a 72 px taskbar
ALL_SCALES = [key for key, _ in ml.WINDOW_SCALES]


class WindowScaleTests(TempDirTestCase):
    """ddraw.ini width/height for the 창 배율 (window scale) option."""

    def setUp(self):
        super().setUp()
        self.ini = self.tmp / "ddraw.ini"

    def size_written(self, mode="windowed", resolution=3, scale="1", area=AREA_1080P):
        """(width, height) as written to a fresh ddraw.ini; None for a missing key."""
        if self.ini.exists():
            self.ini.unlink()
        with mock.patch.object(ml, "work_area", return_value=area):
            ml.update_ddraw_ini(self.ini, mode, False, resolution, scale)
        kv = dict(ln.split("=", 1) for ln in _lines(self.ini.read_bytes()) if "=" in ln)
        return kv.get("width"), kv.get("height")

    def test_choices_and_defaults(self):
        self.assertEqual(ALL_SCALES, ["1", "1.25", "1.5", "2", "fit"])
        self.assertEqual(ml.SETTINGS_DEFAULTS["window_scale"], "1")
        self.assertEqual(ml.GAME_RESOLUTIONS, {0: (640, 480), 1: (800, 600),
                                               2: (1024, 768), 3: (1280, 1024)})
        self.assertEqual(sorted(ml.GAME_RESOLUTIONS), [v for v, _ in ml.RESOLUTIONS])

    def test_scale_one_keeps_zero_and_skips_work_area(self):
        with mock.patch.object(ml, "work_area", side_effect=AssertionError("queried")):
            for res in ml.GAME_RESOLUTIONS:
                self.assertEqual(ml.ddraw_settings("windowed", False, res, "1"),
                                 ml.ddraw_settings("windowed", False))
        self.assertEqual(self.size_written(scale="1"), ("0", "0"))

    def test_fixed_scales_on_a_big_screen(self):
        expected = {   # resolution -> scale -> (width, height), big enough that nothing is clamped
            0: {"1.25": (800, 600), "1.5": (960, 720), "2": (1280, 960)},
            1: {"1.25": (1000, 750), "1.5": (1200, 900), "2": (1600, 1200)},
            2: {"1.25": (1280, 960), "1.5": (1536, 1152), "2": (2048, 1536)},
            3: {"1.25": (1600, 1280), "1.5": (1920, 1536), "2": (2560, 2048)},
        }
        for res, scales in expected.items():
            for scale, (w, h) in scales.items():
                with self.subTest(resolution=res, scale=scale):
                    self.assertEqual(self.size_written(resolution=res, scale=scale, area=AREA_4K),
                                     (str(w), str(h)))

    def test_fit_keeps_aspect_ratio(self):
        cases = [   # (area, resolution) -> size: largest of the game's aspect ratio in area-40
            (AREA_1080P, 2, (1333, 1000)), (AREA_1080P, 1, (1333, 1000)),
            (AREA_1080P, 0, (1333, 1000)), ((2560, 1400), 3, (1700, 1360)),
            (AREA_4K, 3, (2560, 2048)), (AREA_4K, 1, (2730, 2048)),
            ((3440, 1400), 3, (1700, 1360)),        # ultrawide: height-limited
            ((1400, 3000), 3, (1360, 1088)),        # portrait: width-limited
        ]
        for area, res, size in cases:
            with self.subTest(area=area, resolution=res):
                self.assertEqual(ml.window_size(res, "fit", area), size)
                self.assertEqual(self.size_written(resolution=res, scale="fit", area=area),
                                 tuple(map(str, size)))

    def test_fit_is_the_largest_size_inside_the_area(self):
        for res, (bw, bh) in ml.GAME_RESOLUTIONS.items():
            for aw, ah in ((1366, 768), (1600, 900), (1920, 1040), (2560, 1400), (3840, 2088),
                           (3440, 1400), (1400, 3000), (1320, 1064)):
                w, h = ml.window_size(res, "fit", (aw, ah)) or (0, 0)
                with self.subTest(resolution=res, area=(aw, ah)):
                    availw, availh = aw - ml.WINDOW_FRAME_MARGIN, ah - ml.WINDOW_FRAME_MARGIN
                    if availw < bw or availh < bh:
                        self.assertEqual((w, h), (0, 0))   # not even 1:1 fits
                        continue
                    self.assertLessEqual(w, availw)
                    self.assertLessEqual(h, availh)
                    self.assertTrue(w == availw or h == availh)
                    self.assertLess(abs(w * bh - h * bw), max(bw, bh))   # same aspect ratio
                    self.assertGreaterEqual(w, bw)
                    self.assertGreaterEqual(h, bh)

    def test_every_size_is_clamped_to_the_work_area(self):
        # 1280x1024 on a 1440p work area: 1.25x fits, 1.5x/2x are clamped to the fit size
        area = (2560, 1400)
        self.assertEqual(self.size_written(resolution=3, scale="1.25", area=area), ("1600", "1280"))
        for scale in ("1.5", "2", "fit"):
            self.assertEqual(self.size_written(resolution=3, scale=scale, area=area),
                             ("1700", "1360"), scale)
        # 800x600 on a 1080p work area: 1.25x and 1.5x stay exact, 2x is clamped to the fit size
        self.assertEqual(self.size_written(resolution=1, scale="1.25"), ("1000", "750"))
        self.assertEqual(self.size_written(resolution=1, scale="1.5"), ("1200", "900"))
        self.assertEqual(self.size_written(resolution=1, scale="2"), ("1333", "1000"))
        # never wider/taller than the work area minus the frame margin
        for area in ((1366, 768), (1920, 1040), (2560, 1400), AREA_4K):
            for res, scale in ((r, s) for r in ml.GAME_RESOLUTIONS for s in ALL_SCALES):
                size = ml.window_size(res, scale, area)
                if size is not None:
                    self.assertLessEqual(size[0], area[0] - ml.WINDOW_FRAME_MARGIN, (area, res, scale))
                    self.assertLessEqual(size[1], area[1] - ml.WINDOW_FRAME_MARGIN, (area, res, scale))

    def test_falls_back_to_one_to_one_when_even_that_does_not_fit(self):
        # (a 1080p work area is 1040 px high: 1024 + the 40 px margin does not fit)
        for area in ((1280, 1024), (1319, 1064), (1320, 1063), (1024, 768), AREA_1080P):
            for scale in ("1.25", "1.5", "2", "fit"):
                with self.subTest(area=area, scale=scale):
                    self.assertEqual(self.size_written(resolution=3, scale=scale, area=area),
                                     ("0", "0"))
        # exactly 1280x1024 + the 40 px margin: 1:1 fits, so everything collapses to it
        for scale in ("1.25", "2", "fit"):
            self.assertEqual(self.size_written(resolution=3, scale=scale, area=(1320, 1064)),
                             ("1280", "1024"))

    def test_unknown_work_area(self):
        self.assertIsNone(ml.window_size(3, "fit", None))              # -> width=0/height=0
        self.assertEqual(ml.window_size(3, "1.5", None), (1920, 1536))  # cannot clamp
        self.assertEqual(self.size_written(scale="fit", area=None), ("0", "0"))
        self.assertEqual(self.size_written(scale="1.5", area=None), ("1920", "1536"))

    def test_non_windowed_modes_ignore_the_scale(self):
        for mode in ("borderless", "fullscreen"):
            self.size_written(mode=mode, scale="1")
            baseline = self.ini.read_bytes()
            for scale in ALL_SCALES:
                with mock.patch.object(ml, "work_area", side_effect=AssertionError("queried")):
                    self.assertEqual(ml.ddraw_settings(mode, False, 3, scale),
                                     ml.ddraw_settings(mode, False))
                self.assertEqual(self.size_written(mode=mode, scale=scale), (None, None))
                self.assertEqual(self.ini.read_bytes(), baseline, (mode, scale))
                self.assertIsNone(ml.ddraw_window_size(mode, 3, scale))

    def test_switching_scale_replaces_in_place(self):
        self.ini.write_bytes(DDRAW_FIXTURE.encode("ascii"))
        with mock.patch.object(ml, "work_area", return_value=AREA_1080P):
            ml.update_ddraw_ini(self.ini, "windowed", False, 2, "fit")
            first = self.ini.read_bytes()
            self.assertFalse(ml.update_ddraw_ini(self.ini, "windowed", False, 2, "fit"))
            ml.update_ddraw_ini(self.ini, "windowed", False, 2, "1")
        after = _lines(self.ini.read_bytes())
        self.assertIn(b"width=1333\r\nheight=1000\r\n", first)
        self.assertEqual([ln for ln in after if ln.startswith(("width", "height"))],
                         ["width=0", "height=0"])                # no duplicate lines
        # the [ddraw] width/height lines keep their place from the fixture
        self.assertEqual(after.index("width=0"), _lines(DDRAW_FIXTURE.encode("ascii")).index("width=640"))

    def test_bad_values_rejected_without_writing(self):
        with self.assertRaises(ValueError):
            ml.update_ddraw_ini(self.ini, "windowed", False, 3, "3")
        with self.assertRaises(ValueError):
            ml.update_ddraw_ini(self.ini, "windowed", False, 9, "fit")
        self.assertFalse(self.ini.exists())

    def test_work_area_query(self):
        calls = []

        def fake(action, ui_param, rect_ref, win_ini):
            calls.append((action, ui_param, win_ini))
            rect = rect_ref._obj
            rect.left, rect.top, rect.right, rect.bottom = 0, 0, 1920, 1040
            return 1

        with mock.patch.object(ml.ctypes, "windll") as windll:
            windll.user32.SystemParametersInfoW.side_effect = fake
            self.assertEqual(ml.work_area(), (1920, 1040))
            self.assertEqual(calls, [(0x0030, 0, 0)])          # SPI_GETWORKAREA
            windll.user32.SystemParametersInfoW.side_effect = None
            windll.user32.SystemParametersInfoW.return_value = 0
            self.assertIsNone(ml.work_area())                   # API failure
            windll.user32.SystemParametersInfoW.side_effect = OSError
            self.assertIsNone(ml.work_area())
        size = ml.work_area()                                    # the real call: never raises
        self.assertTrue(size is None or (size[0] > 0 and size[1] > 0))

    def test_apply_settings_writes_scaled_window(self):
        game, src = _make_game(self.tmp), _make_wrapper(self.tmp)
        s = dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), wrapper_dir=str(src), window_scale="1.5")

        def sizes():
            return [ln for ln in _lines((game / "ddraw.ini").read_bytes())
                    if ln.startswith(("width", "height"))]

        with mock.patch.object(ml, "set_compat_layer"), \
                mock.patch.object(ml, "work_area", return_value=AREA_4K):
            notes = ml.apply_settings(s)
            self.assertEqual(sizes(), ["width=1920", "height=1536"])
            self.assertTrue(any("(창 1920×1536)" in n for n in notes), notes)
            notes = ml.apply_settings(dict(s, window_scale="1"))
            self.assertEqual(sizes(), ["width=0", "height=0"])
            self.assertFalse(any("(창" in n for n in notes), notes)
            notes = ml.apply_settings(dict(s, window_scale="fit", display_mode="borderless"))
            self.assertEqual(sizes(), ["width=0", "height=0"])       # borderless: not written
            self.assertFalse(any("(창" in n for n in notes), notes)
            notes = ml.apply_settings(dict(s, window_scale="fit"))
            self.assertEqual(sizes(), ["width=2560", "height=2048"])
            self.assertTrue(any("(창 2560×2048)" in n for n in notes), notes)


class CompatLayerTests(unittest.TestCase):
    def tearDown(self):
        for key in (TEST_COMPAT_KEY, r"Software\MCGLauncherUnitTest"):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key)
            except FileNotFoundError:
                pass

    def test_set_and_remove(self):
        exe = Path(tempfile.gettempdir()) / "mcgl-fake" / "MCX.EXE"
        ml.set_compat_layer(exe, False, TEST_COMPAT_KEY)  # absent key -> no error
        ml.set_compat_layer(exe, True, TEST_COMPAT_KEY)
        self.assertEqual(ml.get_compat_layer(exe, TEST_COMPAT_KEY), "~ HIGHDPIAWARE")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, TEST_COMPAT_KEY) as key:
            value, kind = winreg.QueryValueEx(key, str(exe))
        self.assertEqual((value, kind), ("~ HIGHDPIAWARE", winreg.REG_SZ))
        ml.set_compat_layer(exe, False, TEST_COMPAT_KEY)
        self.assertIsNone(ml.get_compat_layer(exe, TEST_COMPAT_KEY))
        ml.set_compat_layer(exe, False, TEST_COMPAT_KEY)  # already removed -> no error


def _make_game(root: Path) -> Path:
    game = root / "MCX"
    game.mkdir()
    (game / "MCX.EXE").write_bytes(b"MZ not a real game")
    (game / "PREFS.CFG").write_bytes(SHIPPED_PREFS.encode("ascii"))
    return game


def _make_wrapper(root: Path) -> Path:
    src = root / "cnc-ddraw"
    (src / "Shaders" / "crt").mkdir(parents=True)
    (src / "ddraw.dll").write_bytes(b"fake dll")
    (src / "Shaders" / "crt" / "a.glsl").write_text("x")
    return src


class WrapperAndApplyTests(TempDirTestCase):
    def test_install_wrapper_copies_missing_only(self):
        game, src = _make_game(self.tmp), _make_wrapper(self.tmp)
        self.assertEqual(ml.install_wrapper(src, game), ["ddraw.dll", "Shaders" + os.sep])
        self.assertTrue((game / "Shaders" / "crt" / "a.glsl").is_file())
        (game / "ddraw.dll").write_bytes(b"user dll")
        self.assertEqual(ml.install_wrapper(src, game), [])
        self.assertEqual((game / "ddraw.dll").read_bytes(), b"user dll")

    def test_install_wrapper_missing_source(self):
        game = _make_game(self.tmp)
        with self.assertRaises(ml.LauncherError):
            ml.install_wrapper(self.tmp / "nowhere", game)

    def test_apply_settings_full(self):
        game, src = _make_game(self.tmp), _make_wrapper(self.tmp)
        s = dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), wrapper_dir=str(src))
        with mock.patch.object(ml, "set_compat_layer") as compat:
            notes = ml.apply_settings(s)
        compat.assert_called_once_with(game / "MCX.EXE", True)
        self.assertTrue(notes)
        self.assertTrue((game / "ddraw.dll").is_file())
        self.assertIn("windowed=true", _lines((game / "ddraw.ini").read_bytes()))
        prefs = game / "PREFS.CFG"
        self.assertEqual(sorted(p.name for p in game.iterdir() if p.suffix.upper() == ".CFG"),
                         ["PREFS.CFG"])  # existing upper-case name kept, no second file
        lines = _lines(prefs.read_bytes())
        self.assertIn("b DirectDraw=TRUE", lines)
        self.assertIn("l Resolution=3", lines)
        self.assertTrue(ml.is_readonly(prefs))

    def test_apply_settings_no_wrapper_windowed_uses_gdi(self):
        game = _make_game(self.tmp)
        s = dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), use_wrapper=False, dpi_fix=False)
        with mock.patch.object(ml, "set_compat_layer") as compat:
            ml.apply_settings(s)
        compat.assert_called_once_with(game / "MCX.EXE", False)
        self.assertFalse((game / "ddraw.dll").exists())
        self.assertFalse((game / "ddraw.ini").exists())
        self.assertIn("b DirectDraw=FALSE", _lines((game / "PREFS.CFG").read_bytes()))

    def test_apply_settings_rejects_folder_without_exe(self):
        with self.assertRaises(ml.LauncherError):
            ml.apply_settings(dict(ml.SETTINGS_DEFAULTS, game_dir=str(self.tmp)))

    def test_korean_ready_file(self):
        game = _make_game(self.tmp)
        self.assertIsNone(ml.read_ko_language(game))
        self.assertIsNone(ml.read_ko_language(""))
        (game / "lang" / "kor").mkdir(parents=True)
        self.assertIsNone(ml.read_ko_language(game))          # directory alone is not enough
        (game / "lang" / "kor" / "strings.bin").write_bytes(b"KSTR")
        self.assertEqual(ml.read_ko_language(game), 1)
        s = dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), language="ko", use_wrapper=False)
        with mock.patch.object(ml, "set_compat_layer"):
            ml.apply_settings(s)
        self.assertIn("l Language=1", _lines((game / "PREFS.CFG").read_bytes()))
        (game / "lang" / "kor" / "strings.bin").unlink()
        with mock.patch.object(ml, "set_compat_layer"):
            ml.apply_settings(s)                               # overlay gone -> English again
        self.assertIn("l Language=0", _lines((game / "PREFS.CFG").read_bytes()))

    def test_gui_heap_raised_for_korean(self):
        game = _make_game(self.tmp)
        cfg = game / "SYSTEM.CFG"
        shipped = (b"FITini\r\n\r\n[systemHeap]\r\nul systemHeapSize=4095999\r\n"
                   b"ul guiHeapSize=4095999\r\nul soundHeapSize=1023999   \r\n\r\nFITend\r\n")
        cfg.write_bytes(shipped)
        self.assertTrue(ml.ensure_gui_heap(cfg))
        raised = cfg.read_bytes()
        self.assertEqual(raised, shipped.replace(b"ul guiHeapSize=4095999", b"ul guiHeapSize=16777215"))
        self.assertFalse(ml.ensure_gui_heap(cfg))              # idempotent
        cfg.write_bytes(shipped.replace(b"=4095999\r\nul sound", b"=99999999\r\nul sound"))
        self.assertFalse(ml.ensure_gui_heap(cfg))              # larger value is kept
        self.assertFalse(ml.ensure_gui_heap(game / "missing.cfg"))
        cfg.write_bytes(b"FITini\r\n[systemHeap]\r\nul systemHeapSize=1\r\nFITend\r\n")
        self.assertFalse(ml.ensure_gui_heap(cfg))              # no key -> untouched
        # apply_settings only touches SYSTEM.CFG when Korean is active
        cfg.write_bytes(shipped)
        (game / "lang" / "kor").mkdir(parents=True)
        (game / "lang" / "kor" / "strings.bin").write_bytes(b"KSTR")
        with mock.patch.object(ml, "set_compat_layer"):
            notes_en = ml.apply_settings(dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), use_wrapper=False))
            self.assertEqual(cfg.read_bytes(), shipped)
            notes_ko = ml.apply_settings(dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), use_wrapper=False,
                                              language="ko"))
        self.assertIn(b"ul guiHeapSize=16777215", cfg.read_bytes())
        self.assertFalse(any("guiHeapSize" in n for n in notes_en))
        self.assertTrue(any("guiHeapSize" in n for n in notes_ko))


class LaunchTests(TempDirTestCase):
    def test_launch_uses_exe_and_cwd_without_running(self):
        game = _make_game(self.tmp)
        with mock.patch.object(ml.subprocess, "Popen") as popen, \
                mock.patch.object(ml, "set_compat_layer") as compat:
            handle = ml.launch(game, dpi_fix=True)
        popen.assert_called_once_with([str(game / "MCX.EXE")], cwd=str(game))
        compat.assert_called_once_with(game / "MCX.EXE", True)
        self.assertIs(handle.process, popen.return_value)
        self.assertFalse(handle.err_before.exists)

    def test_launch_missing_exe(self):
        with mock.patch.object(ml.subprocess, "Popen") as popen, \
                mock.patch.object(ml, "set_compat_layer"):
            with self.assertRaises(ml.LauncherError):
                ml.launch(self.tmp)
        popen.assert_not_called()

    def test_crash_log_detection(self):
        game = _make_game(self.tmp)
        err = game / "DEFAULT.ERR"
        err.write_text("old crash\n")
        with mock.patch.object(ml.subprocess, "Popen"), mock.patch.object(ml, "set_compat_layer"):
            handle = ml.launch(game)
        self.assertIsNone(ml.crash_log_if_changed(handle))  # untouched during run
        err.write_text("".join(f"line {i}\n" for i in range(100)))
        os.utime(err, ns=(handle.err_before.mtime_ns + 10**9,) * 2)
        log = ml.crash_log_if_changed(handle)
        self.assertEqual(log.splitlines(), [f"line {i}" for i in range(40)])


class SettingsTests(TempDirTestCase):
    def test_roundtrip_and_validation(self):
        path = self.tmp / "MCGLauncher" / "settings.json"
        s = dict(ml.SETTINGS_DEFAULTS, music=200, display_mode="nonsense", resolution="2")
        ml.save_settings(s, path)
        loaded, existed = ml.load_settings(path)
        self.assertTrue(existed)
        self.assertEqual((loaded["music"], loaded["display_mode"], loaded["resolution"]),
                         (100, "windowed", 2))
        missing, existed = ml.load_settings(self.tmp / "nope.json")
        self.assertFalse(existed)
        self.assertEqual(missing["resolution"], 3)

    def test_window_scale_persisted_and_migrated(self):
        path = self.tmp / "MCGLauncher" / "settings.json"
        for scale in ALL_SCALES:
            ml.save_settings(dict(ml.SETTINGS_DEFAULTS, window_scale=scale), path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["window_scale"], scale)
            loaded, existed = ml.load_settings(path)
            self.assertTrue(existed)
            self.assertEqual(loaded["window_scale"], scale)
        # a settings.json written before the option existed -> 1:1
        old = {k: v for k, v in ml.SETTINGS_DEFAULTS.items() if k != "window_scale"}
        old.update(resolution=2, display_mode="borderless")
        path.write_text(json.dumps(old), encoding="utf-8")
        loaded, existed = ml.load_settings(path)
        self.assertTrue(existed)
        self.assertEqual((loaded["window_scale"], loaded["resolution"], loaded["display_mode"]),
                         ("1", 2, "borderless"))
        self.assertEqual(ml.normalize_settings({})["window_scale"], "1")
        for bad in ("3", "FIT", "", None, 5, ["fit"]):
            self.assertEqual(ml.normalize_settings({"window_scale": bad})["window_scale"], "1", bad)

    def test_settings_path_under_appdata(self):
        with mock.patch.dict(os.environ, {"APPDATA": str(self.tmp)}):
            self.assertEqual(ml.settings_path(), self.tmp / "MCGLauncher" / "settings.json")


class GuiTests(TempDirTestCase):
    def test_widgets_round_trip_settings(self):
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:  # pragma: no cover - no display
            self.skipTest(f"Tk unavailable: {exc}")
        root.withdraw()
        try:
            game = _make_game(self.tmp)
            s = dict(ml.SETTINGS_DEFAULTS, game_dir=str(game), resolution=1,
                     display_mode="fullscreen", sprite="45", difficulty=2, music=33,
                     advanced=True, dpi_fix=False, language="ko", window_scale="1.5")
            app = ml.LauncherApp(root, s, persist=False, interactive=False)
            root.update_idletasks()
            self.assertEqual(root.title(), "MechCommander Gold 런처")
            got = app.collect_settings()
            self.assertEqual(got["language"], "en")  # strings.bin missing -> disabled
            self.assertEqual(got["window_scale"], "1.5")
            self.assertEqual(got, ml.normalize_settings(dict(s, language="en")))
            self.assertIn("disabled", app.ko_radio.state())
            (game / "lang" / "kor").mkdir(parents=True)
            (game / "lang" / "kor" / "strings.bin").write_bytes(b"KSTR")
            app.refresh()
            self.assertNotIn("disabled", app.ko_radio.state())
            app.v_game_dir.set(str(self.tmp / "nope"))
            self.assertIn("disabled", app.btn_launch.state())
            self.assertIn("MCX.EXE", app.game_hint.cget("text"))
        finally:
            root.destroy()

    def test_window_scale_widget(self):
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:  # pragma: no cover - no display
            self.skipTest(f"Tk unavailable: {exc}")
        root.withdraw()
        try:
            game = _make_game(self.tmp)
            labels = [label for _, label in ml.WINDOW_SCALES]
            for key, label in ml.WINDOW_SCALES:
                app = ml.LauncherApp(root, dict(ml.SETTINGS_DEFAULTS, game_dir=str(game),
                                                window_scale=key),
                                     persist=False, interactive=False)
                self.assertEqual(app.v_window_scale.get(), label)
                self.assertEqual(app.collect_settings()["window_scale"], key)
                self.assertEqual(list(app.window_scale_box.cget("values")), labels)
                self.assertEqual(str(app.window_scale_box.cget("state")), "readonly")
                for other_key, other_label in ml.WINDOW_SCALES:
                    app.window_scale_box.set(other_label)
                    self.assertEqual(app.collect_settings()["window_scale"], other_key)
                app.v_window_scale.set("not a choice")
                self.assertEqual(app.collect_settings()["window_scale"], "1")
                app.notebook.destroy()
            # a settings dict from before the option existed opens as 1:1
            old = {k: v for k, v in ml.SETTINGS_DEFAULTS.items() if k != "window_scale"}
            app = ml.LauncherApp(root, dict(old, game_dir=str(game)), persist=False, interactive=False)
            self.assertEqual(app.v_window_scale.get(), "원본 1:1 (Original)")
            self.assertEqual(app.collect_settings()["window_scale"], "1")
        finally:
            root.destroy()


class WheelZoomTests(unittest.TestCase):
    def test_direction_and_scancode(self):
        up, down = 120 << 16, (-120 & 0xFFFF) << 16
        self.assertEqual(ml.wheel_direction(up), 1)
        self.assertEqual(ml.wheel_direction(down), -1)
        self.assertEqual(ml.wheel_direction(0), 0)
        self.assertEqual(ml.wheel_direction(up | 0x0001), 1)      # low word (buttons) ignored
        self.assertEqual(ml.wheel_scancode(1), ml.WHEEL_SCAN_ZOOM_IN)
        self.assertEqual(ml.wheel_scancode(-1), ml.WHEEL_SCAN_ZOOM_OUT)

    def test_input_struct_layout(self):
        import ctypes
        self.assertEqual(ctypes.sizeof(ml._INPUT), 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28)
        self.assertEqual(ctypes.sizeof(ml._MSLLHOOKSTRUCT), 32 if ctypes.sizeof(ctypes.c_void_p) == 8 else 24)

    def test_wheel_presses_zoom_keys_only_over_game(self):
        sent = []
        fg = {"pid": 4242}
        hook = ml.WheelZoomHook(4242, send=lambda scan, up: sent.append((scan, up)),
                                foreground_pid=lambda: fg["pid"])
        hook.HOLD_SECONDS = 0.01
        if not hook.start():
            hook.stop()
            self.skipTest(f"hook could not be installed: {hook.failed}")
        try:
            self.assertTrue(hook.active)
            self.assertTrue(hook.on_wheel(120 << 16))
            self.assertTrue(hook.on_wheel((-120 & 0xFFFF) << 16))
            fg["pid"] = 1                                       # another window in front
            self.assertFalse(hook.on_wheel(120 << 16))
            self.assertFalse(hook.on_wheel(0))
            deadline = __import__("time").time() + 2
            while len(sent) < 4 and __import__("time").time() < deadline:
                __import__("time").sleep(0.02)
        finally:
            hook.stop()
            hook.stop()                                         # idempotent
        self.assertEqual(sent, [(ml.WHEEL_SCAN_ZOOM_IN, False), (ml.WHEEL_SCAN_ZOOM_IN, True),
                                (ml.WHEEL_SCAN_ZOOM_OUT, False), (ml.WHEEL_SCAN_ZOOM_OUT, True)])
        self.assertFalse(hook.active)

    def test_setting_default_and_roundtrip(self):
        self.assertTrue(ml.SETTINGS_DEFAULTS["wheel_zoom"])
        old = {k: v for k, v in ml.SETTINGS_DEFAULTS.items() if k != "wheel_zoom"}
        self.assertTrue(ml.normalize_settings(old)["wheel_zoom"])
        self.assertFalse(ml.normalize_settings(dict(old, wheel_zoom=False))["wheel_zoom"])
        self.assertTrue(ml.normalize_settings(dict(old, wheel_zoom="no"))["wheel_zoom"])  # bad type -> default


if __name__ == "__main__":
    unittest.main(verbosity=2)
