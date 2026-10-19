# -*- coding: utf-8 -*-
"""MechCommander Gold / Desperate Measures (MCX.EXE) launcher for Windows 11.

Single-file tkinter GUI.  It edits the game's ``prefs.cfg`` (FITini format),
installs/configures the cnc-ddraw DirectDraw wrapper (``ddraw.dll`` +
``ddraw.ini``), sets the per-user AppCompat DPI layer and starts MCX.EXE.

Run ``python mcg_launcher.py --selftest`` to build the window without showing
it and exit (0 = OK).  See README.md for details.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import traceback
import winreg
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
APP_NAME = "MCGLauncher"
WINDOW_TITLE = "MechCommander Gold 런처"

GAME_EXE = "MCX.EXE"
PREFS_FILE = "prefs.cfg"
DDRAW_DLL = "ddraw.dll"
DDRAW_INI = "ddraw.ini"
SHADERS_DIR = "Shaders"
CNC_CONFIG_EXE = "cnc-ddraw config.exe"
ERR_FILE = "DEFAULT.ERR"
# Korean overlay: the patched MCX.EXE reads lang\kor\strings.bin and tries
# lang\kor\<path> before every data file whenever prefs `l Language` is non-zero.
KO_READY_FILE = os.path.join("lang", "kor", "strings.bin")
KO_DEFAULT_LANGUAGE = 1
# The 26 fonts loaded at startup grow from ~0.5 MB to ~6.3 MB with Hangul
# glyphs, so the GUI heap (SYSTEM.CFG [systemHeap] guiHeapSize, 4 MB as
# shipped) must be raised before the Korean fonts can load.
SYSTEM_CFG = "SYSTEM.CFG"
KO_GUI_HEAP_SIZE = 16777215
CRASH_LOG_LINES = 40

DEFAULT_GAME_DIR = r"D:\DEV\MCGExtracted-Mechcommader1\game-source\extracted\MCX"
DEFAULT_WRAPPER_DIR = r"D:\DEV\MCGExtracted-Mechcommader1\game-source\tools\cnc-ddraw"

COMPAT_KEY = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
COMPAT_HIGHDPI = "~ HIGHDPIAWARE"

CRLF = "\r\n"
# latin-1 maps every byte to one code point, so unknown bytes survive a
# read/modify/write round trip unchanged.
FILE_ENCODING = "latin-1"
UTF8_BOM = b"\xef\xbb\xbf"

# prefs.cfg ---------------------------------------------------------------
PREFS_HEADER = "FITini"
PREFS_FOOTER = "FITend"
PREFS_SECTION = "MechCommander"
SHIPPED_PREFS_LINES = [
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
]
# Keys owned by the launcher (written by build_prefs_values, in this order).
PREFS_OWNED_KEYS = (
    "Resolution", "Language", "DirectDraw", "Use90Pixel", "Force45Pixel",
    "Difficulty", "Brightness", "MusicVolume", "RadioVolume", "SFXVolume",
)

# ddraw.ini (cnc-ddraw) ---------------------------------------------------
DDRAW_SECTION = "ddraw"
# Keys verified on Windows 11 with MCX.EXE at 1280x1024 (2026-10-17):
# resolutions=2 exposes the full mode list so 1280x1024 is accepted,
# d3d9_filter=1 (bilinear) because bicubic/lanczos do not support 8-bit games,
# nonexclusive=true keeps GUI elements visible with the d3d9/opengl renderers.
DDRAW_COMMON_SETTINGS = (
    ("renderer", "auto"), ("resolutions", "2"), ("d3d9_filter", "1"),
    ("nonexclusive", "true"), ("vsync", "true"), ("maxfps", "60"),
)
DDRAW_MODE_SETTINGS = {
    "windowed": (
        ("windowed", "true"), ("fullscreen", "false"), ("maintas", "true"),
        ("boxing", "false"), ("width", "0"), ("height", "0"),
    ) + DDRAW_COMMON_SETTINGS,
    "borderless": (
        ("windowed", "true"), ("fullscreen", "true"), ("maintas", "true"),
        ("boxing", "true"),
    ) + DDRAW_COMMON_SETTINGS,
    # boxing=false is written so a previous borderless run (boxing=true) does
    # not leave integer-scaling switched on in exclusive mode.
    "fullscreen": (
        ("windowed", "false"), ("fullscreen", "true"), ("maintas", "true"),
        ("boxing", "false"),
    ) + DDRAW_COMMON_SETTINGS,
}
DDRAW_ADVANCED_SETTINGS = (("singlecpu", "true"), ("hook", "4"))

# Window scale (windowed mode only).  cnc-ddraw's ``width``/``height`` force the
# window size and it stretches the game picture to it (``maintas`` keeps the
# 5:4 / 4:3 aspect).  "1" keeps width=0/height=0 (window = game resolution);
# "fit" is the largest size that fits the primary monitor's work area.
GAME_RESOLUTIONS = {0: (640, 480), 1: (800, 600), 2: (1024, 768), 3: (1280, 1024)}
WINDOW_SCALE_FIT = "fit"
WINDOW_FRAME_MARGIN = 40        # px kept free for the window frame / title bar
SPI_GETWORKAREA = 0x0030

# GUI choices ---------------------------------------------------------------
RESOLUTIONS = ((0, "640×480"), (1, "800×600"), (2, "1024×768"), (3, "1280×1024"))
WINDOW_SCALES = (
    ("1", "원본 1:1 (Original)"),
    ("1.25", "1.25배 (1.25x)"),
    ("1.5", "1.5배 (1.5x)"),
    ("2", "2배 (2x)"),
    (WINDOW_SCALE_FIT, "화면에 맞춤 (Fit)"),
)
WINDOW_SCALE_HINT = ("창 모드에서만 적용됩니다. 테두리 없는 전체화면/전체화면(독점)은 "
                     "이미 화면에 맞춰 확대됩니다. (Windowed mode only.)")
DISPLAY_MODES = (
    ("windowed", "창 모드 (Windowed)"),
    ("borderless", "테두리 없는 전체화면 (Borderless)"),
    ("fullscreen", "전체화면(독점) (Exclusive fullscreen)"),
)
SPRITE_SETS = (("90", "90픽셀(기본) (90px, default)"), ("45", "45픽셀 (45px)"))
# MCX.EXE's preferences screen has exactly three buttons that store 0/1/2 in the
# Difficulty global (callbacks at 0x7061be/0x706218/0x706278). 0 applies the first
# [DifficultySettings] column of gamesys.fit (player skills/weapons 125 %, enemy
# 50 %, salvage 50 %), 1 applies no modifier, 2 applies the second column (enemy
# skills 125 %, enemy weapons 110 %, salvage 40 %). Any other value acts like 1.
DIFFICULTY_LABELS = ("0 쉬움 (Easy)", "1 보통 (Normal, 기본값)", "2 어려움 (Hard)")

# In-game hotkeys shown on the "게임 단축키" tab: (group, key, action, verification).
# Filled in from the Desperate Measures readme, MCX.EXE key handling and web sources;
# see HOTKEY_SOURCES below.  "검증" = how the entry was confirmed.
HOTKEY_INTRO = ("MechCommander Gold 미션 중 키보드 단축키입니다. \"+클릭\"은 키를 누른 채 대상을 왼쪽 클릭한다는 뜻입니다. "
                "검증 열: M=공식 매뉴얼, R=Desperate Measures Readme, C=MCX.EXE 코드(키 테이블), T=게임 내 툴팁 문자열, W=커뮤니티 자료")
HOTKEYS: list[tuple[str, str, str, str]] = [
    # 이동 / 기본 명령
    ("이동", "왼쪽 클릭", "이동 (걷기, Move half-power)", "M"),
    ("이동", "SPACE + 클릭", "전속력 이동 (달리기, Move Full Speed)", "M·C·T·W"),
    ("이동", "J + 클릭", "점프젯 사용 (Use Jumpjets, 점프 가능 메크만)", "M·C·T·W"),
    ("이동", "G + 클릭", "경계 / 호위 (Guard/Escort)", "M·C·T·W"),
    ("이동", "BACKSPACE", "모든 명령 취소, 사격 중지 (Hold fire / clear orders)", "R·M·C"),
    ("이동", "CTRL (누른 채)", "이동 경로 표시. 누르고 있는 동안 공격·점령 지정 불가", "R·M"),
    # 웨이포인트 (Desperate Measures)
    ("웨이포인트", "CTRL 또는 F9 + 클릭", "걷기 웨이포인트 추가 (최대 16개)", "R·M·C"),
    ("웨이포인트", "CTRL+SPACE 또는 F10 + 클릭", "달리기 웨이포인트 추가", "R·M·C"),
    ("웨이포인트", "CTRL+J 또는 F11 + 클릭", "점프 웨이포인트 추가", "R·M·C"),
    ("웨이포인트", "CTRL+F + 클릭", "지뢰 매설 웨이포인트 추가 (지뢰 부설 차량)", "R·M·C"),
    # 공격
    ("공격", "C + 클릭", "현재 위치에서 공격 (Attack-From Position)", "M·C·T·W"),
    ("공격", "S + 클릭", "근거리에서 공격 (Attack-Short Range)", "M·C·T·W"),
    ("공격", "M + 클릭", "중거리에서 공격 (Attack-Medium Range)", "M·C·T·W"),
    ("공격", "L + 클릭", "장거리에서 공격 (Attack-Long Range)", "M·C·T·W"),
    ("공격", "A + 클릭", "탄약 절약 사격: 에너지 무기만 사용 (조준선 주황색)", "R·M·C·W"),
    ("공격", "O + 클릭", "공격 (코드에만 있는 6번째 공격 모드, 기본 거리 추정)", "C (추정)"),
    # 부위 공격 (숫자 키패드)
    ("부위 공격", "키패드 8 + 클릭", "머리 공격 (Attack head)", "M·C·W"),
    ("부위 공격", "키패드 5 + 클릭", "중앙 몸통 공격 (Center torso)", "M·C·W"),
    ("부위 공격", "키패드 7 + 클릭", "왼쪽 몸통 공격 (Left torso)", "M·C"),
    ("부위 공격", "키패드 9 + 클릭", "오른쪽 몸통 공격 (Right torso)", "M·C"),
    ("부위 공격", "키패드 4 + 클릭", "왼팔 공격 (Left arm)", "M·C·W"),
    ("부위 공격", "키패드 6 + 클릭", "오른팔 공격 (Right arm)", "M·C·W"),
    ("부위 공격", "키패드 1 + 클릭", "왼다리 공격 (Left leg)", "M·C·W"),
    ("부위 공격", "키패드 3 + 클릭", "오른다리 공격 (Right leg)", "M·C·W"),
    # 특수 명령
    ("특수", "HOME + 유닛 클릭", "조종사 강제 사출 (Eject pilot)", "M·C"),
    ("특수", "PAGE DOWN", "선택 유닛 전원 끄기 (Power down)", "M·C·W"),
    ("특수", "PAGE UP", "선택 유닛 전원 켜기 (Power up)", "M·C"),
    ("특수", "F + 클릭", "지뢰 매설 (지뢰 부설 차량 선택 시)", "M·C"),
    ("특수", "I + 유닛 클릭", "유닛 정보 보기 (Get information)", "M·C·W"),
    ("특수", "(키 없음)", "점령·수리는 상황별 커서가 뜰 때 클릭", "M"),
    # 화력 지원 (상단 숫자키)
    ("화력 지원", "1 + 클릭", "소형 포격 (Small artillery strike) - 상단 숫자키", "R·M·C"),
    ("화력 지원", "2 + 클릭", "대형 포격 (Large artillery strike)", "R·M·C"),
    ("화력 지원", "3 + 클릭", "센서 탐침 투하 (Sensor probe)", "R·M·C"),
    ("화력 지원", "4 + 클릭", "카메라 드론 투하 (Camera drone)", "R·M·C"),
    # 선택 / 그룹
    ("선택", "E", "화면 안의 아군 유닛 모두 선택", "M"),
    ("선택", "오른쪽 클릭 (빈 곳)", "선택 해제", "M"),
    ("선택", "F1 ~ F4", "포스 그룹(랜스) 1~4 선택", "C·W"),
    ("선택", "CTRL+F1 ~ F4", "선택 유닛을 그룹 1~4로 재지정 (매뉴얼 표기)", "M"),
    # 화면 / 카메라
    ("화면", "+ / -  (키패드 포함)", "전장 화면 줌 인 / 줌 아웃", "M·C·W"),
    ("화면", "방향키 (키패드 포함)", "전장 화면 스크롤", "M·C"),
    ("화면", "CTRL + 방향키", "전술 지도(MFD 지도) 스크롤", "M"),
    ("화면", "CTRL + / CTRL -", "전술 지도 줌 인 / 줌 아웃", "M"),
    # 인터페이스
    ("인터페이스", "ALT", "MFD(다기능 디스플레이) 열기/닫기", "M·W"),
    ("인터페이스", "TAB", "MFD 명령 팔레트 열기/닫기", "M"),
    ("인터페이스", "ALT+B / ALT+D / ALT+M / ALT+S", "MFD 탭: 브리핑 / 정보 / 지도 / 노획(Salvage)", "M"),
    ("인터페이스", "ALT+C", "MFD 채팅 탭 (멀티플레이)", "M"),
    ("인터페이스", "ESC 또는 PAUSE", "일시정지 (미션 중 ESC = 일시정지 메뉴)", "M·C"),
    ("인터페이스", "ENTER", "채팅 입력 (멀티플레이)", "M"),
]
HOTKEY_SOURCES = ("출처: MechCommander Gold 공식 매뉴얼 pp.29-32 및 키보드 기능 차트(M), 게임 폴더 Readme.txt(R), "
                  "MCX.EXE InterfaceObject 키 테이블·handleEvent 디컴파일(C), EXE 문자열 테이블의 MFD 툴팁(T), "
                  "ModDB 가이드·Let's Play Archive·Neoseeker(W). 부위 공격 키가 숫자 키패드라는 점은 EXE 스캔코드로 확인했습니다.")

SETTINGS_DEFAULTS = {
    "game_dir": DEFAULT_GAME_DIR,
    "wrapper_dir": DEFAULT_WRAPPER_DIR,
    "resolution": 3,
    "display_mode": "windowed",
    "window_scale": "1",
    "language": "en",
    "sprite": "90",
    "difficulty": 1,
    "brightness": 0,
    "music": 64,
    "radio": 64,
    "sfx": 96,
    "use_wrapper": True,
    "dpi_fix": True,
    "advanced": False,
}
_INT_RANGES = {
    "resolution": (0, 3), "difficulty": (0, 2), "brightness": (0, 100),
    "music": (0, 100), "radio": (0, 100), "sfx": (0, 100),
}
_CHOICES = {
    "display_mode": tuple(m for m, _ in DISPLAY_MODES),
    "window_scale": tuple(k for k, _ in WINDOW_SCALES),
    "language": ("en", "ko"),
    "sprite": tuple(s for s, _ in SPRITE_SETS),
}

_SECTION_RE = re.compile(r"^\s*\[([^\]]*)\]\s*$")
_PREF_RE = re.compile(r"^\s*([A-Za-z]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")
_LINE_RE = re.compile(r"([^\r\n]*)(\r\n|\r|\n|\Z)")


class LauncherError(Exception):
    """A user-facing error (message is shown in the GUI)."""


# --------------------------------------------------------------------------
# Generic file helpers
# --------------------------------------------------------------------------
def _split_lines(text: str) -> list[tuple[str, str]]:
    """Split *text* into ``(content, eol)`` pairs, keeping each line's ending."""
    out: list[tuple[str, str]] = []
    pos, n = 0, len(text)
    while pos < n:
        m = _LINE_RE.match(text, pos)
        out.append((m.group(1), m.group(2)))
        pos = m.end()
    return out


def _section_name(line: str) -> str | None:
    m = _SECTION_RE.match(line)
    return m.group(1).strip() if m else None


def _find_section(lines: list[str], name: str) -> int | None:
    wanted = name.lower()
    for i, line in enumerate(lines):
        sec = _section_name(line)
        if sec is not None and sec.lower() == wanted:
            return i
    return None


def is_readonly(path) -> bool:
    st = os.stat(path)
    attrs = getattr(st, "st_file_attributes", None)
    if attrs is not None:
        return bool(attrs & stat.FILE_ATTRIBUTE_READONLY)
    return not st.st_mode & stat.S_IWRITE


def set_readonly(path, on: bool) -> None:
    """Set or clear the Windows read-only attribute."""
    os.chmod(path, stat.S_IREAD if on else stat.S_IREAD | stat.S_IWRITE)


def _write_bytes(path: Path, data: bytes, readonly: bool | None) -> bool:
    """Write *data* to *path*, clearing the read-only attribute first.

    ``readonly`` True/False sets the attribute afterwards, ``None`` restores
    the previous state.  The file is rewritten in place (keeps the existing
    file name's case).  Returns True when the content changed.
    """
    existed = path.exists()
    was_ro = existed and is_readonly(path)
    final_ro = was_ro if readonly is None else readonly
    changed = not existed or path.read_bytes() != data
    if changed:
        if was_ro:
            set_readonly(path, False)
        try:
            with open(path, "wb") as fh:
                fh.write(data)
        finally:
            if final_ro and path.exists():
                set_readonly(path, True)
    elif was_ro != final_ro:
        set_readonly(path, final_ro)
    return changed


# --------------------------------------------------------------------------
# prefs.cfg
# --------------------------------------------------------------------------
def read_prefs(path) -> list[str]:
    """Return the lines of prefs.cfg (without line endings).

    A missing file yields the content the game ships with.
    """
    p = Path(path)
    if not p.is_file():
        return list(SHIPPED_PREFS_LINES)
    text = p.read_bytes().decode(FILE_ENCODING)
    return [content for content, _ in _split_lines(text)]


def parse_prefs(lines: list[str]) -> dict[str, str]:
    """Return ``{key: raw value}`` for the ``[MechCommander]`` section."""
    start = _find_section(lines, PREFS_SECTION)
    if start is None:
        return {}
    values: dict[str, str] = {}
    for line in lines[start + 1:]:
        if _section_name(line) is not None or line.strip() == PREFS_FOOTER:
            break
        m = _PREF_RE.match(line)
        if m and m.group(2) not in values:
            values[m.group(2)] = m.group(3).strip()
    return values


def format_pref(key: str, value) -> str:
    """Format one FITini line: ``b Key=TRUE`` for bools, ``l Key=N`` for ints."""
    if isinstance(value, bool):
        return f"b {key}={'TRUE' if value else 'FALSE'}"
    if isinstance(value, int):
        return f"l {key}={value}"
    raise TypeError(f"unsupported prefs value for {key}: {value!r}")


def apply_prefs_values(lines: list[str], values: dict) -> list[str]:
    """Return *lines* with *values* set in ``[MechCommander]``.

    Existing key lines are replaced in place (later duplicates removed),
    missing keys are appended at the end of the section, every other line is
    kept.  ``FITini`` is forced to be the first line and ``FITend`` the last.
    """
    out = list(lines)

    if not out or out[0].strip() != PREFS_HEADER:
        out = [PREFS_HEADER] + [ln for ln in out if ln.strip() != PREFS_HEADER]

    while len(out) > 1 and not out[-1].strip():
        out.pop()
    if out[-1].strip() != PREFS_FOOTER:
        out = [out[0]] + [ln for ln in out[1:] if ln.strip() != PREFS_FOOTER]
        while len(out) > 1 and not out[-1].strip():
            out.pop()
        out.append(PREFS_FOOTER)

    start = _find_section(out, PREFS_SECTION)
    if start is None:
        footer = len(out) - 1
        block = [f"[{PREFS_SECTION}]"]
        if out[footer - 1].strip():
            block.insert(0, "")
        out[footer:footer] = block
        start = footer + len(block) - 1

    end = len(out) - 1  # the FITend line
    for i in range(start + 1, len(out)):
        if _section_name(out[i]) is not None or out[i].strip() == PREFS_FOOTER:
            end = i
            break

    by_lower = {k.lower(): k for k in values}
    seen: set[str] = set()
    i = start + 1
    while i < end:
        m = _PREF_RE.match(out[i])
        key = by_lower.get(m.group(2).lower()) if m else None
        if key is None:
            i += 1
            continue
        if key in seen:          # duplicate line for an owned key -> drop
            del out[i]
            end -= 1
            continue
        out[i] = format_pref(key, values[key])
        seen.add(key)
        i += 1

    insert_at = end
    while insert_at > start + 1 and not out[insert_at - 1].strip():
        insert_at -= 1
    out[insert_at:insert_at] = [format_pref(k, v) for k, v in values.items() if k not in seen]
    return out


def write_prefs(path, values: dict) -> bool:
    """Update prefs.cfg with *values* (``{key: bool|int}``), CRLF, read-only.

    The read-only attribute is cleared before writing and set again after,
    so the game cannot rewrite the file (and drop unknown keys) on exit.
    Returns True when the content changed.
    """
    p = Path(path)
    new_lines = apply_prefs_values(read_prefs(p), values)
    data = (CRLF.join(new_lines) + CRLF).encode(FILE_ENCODING)
    return _write_bytes(p, data, readonly=True)


def build_prefs_values(settings: dict, wrapper_active: bool,
                       ko_language: int | None) -> dict:
    """Map launcher settings to the prefs.cfg keys the launcher owns."""
    s = normalize_settings(settings)
    sprite90 = s["sprite"] == "90"
    language = ko_language if (s["language"] == "ko" and ko_language is not None) else 0
    # With cnc-ddraw the game must use its DirectDraw path (the wrapper does
    # the windowing).  Without a wrapper, "windowed" falls back to the game's
    # own GDI window (DirectDraw=FALSE).
    direct_draw = wrapper_active or s["display_mode"] != "windowed"
    return {
        "Resolution": s["resolution"],
        "Language": language,
        "DirectDraw": direct_draw,
        "Use90Pixel": sprite90,
        "Force45Pixel": not sprite90,
        "Difficulty": s["difficulty"],
        "Brightness": s["brightness"],
        "MusicVolume": s["music"],
        "RadioVolume": s["radio"],
        "SFXVolume": s["sfx"],
    }


def settings_from_prefs(lines: list[str], settings: dict) -> dict:
    """Copy game options found in prefs.cfg into *settings* (first run)."""
    s = dict(settings)
    raw = parse_prefs(lines)

    def as_int(key):
        try:
            return int(raw[key])
        except (KeyError, ValueError):
            return None

    for pref_key, setting_key in (("Resolution", "resolution"), ("Difficulty", "difficulty"),
                                  ("Brightness", "brightness"), ("MusicVolume", "music"),
                                  ("RadioVolume", "radio"), ("SFXVolume", "sfx")):
        v = as_int(pref_key)
        if v is not None:
            s[setting_key] = v
    if raw.get("Force45Pixel", "").upper() == "TRUE":
        s["sprite"] = "45"
    elif raw.get("Use90Pixel", "").upper() == "TRUE":
        s["sprite"] = "90"
    return normalize_settings(s)


# --------------------------------------------------------------------------
# ddraw.ini (cnc-ddraw)
# --------------------------------------------------------------------------
class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def work_area() -> tuple[int, int] | None:
    """Width/height of the primary monitor's work area (screen minus taskbar).

    Physical pixels, because the launcher is DPI-aware.  ``None`` when the
    query fails.  Tests patch this function.
    """
    try:
        rect = _RECT()
        if not ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
            return None
    except (AttributeError, OSError):
        return None
    width, height = rect.right - rect.left, rect.bottom - rect.top
    return (width, height) if width > 0 and height > 0 else None


def window_size(resolution: int, scale: str,
                area: tuple[int, int] | None) -> tuple[int, int] | None:
    """Window size for cnc-ddraw ``width``/``height``, or ``None`` to keep 0/0 (1:1).

    The game resolution times *scale*, rounded.  ``"fit"`` is the largest size
    of the game's aspect ratio that fits *area* (work area minus
    ``WINDOW_FRAME_MARGIN``); every other scale is clamped to that size, and
    when even 1:1 does not fit the result is ``None``.  Without a work area
    ``"fit"`` gives ``None`` and the other scales are not clamped.
    """
    try:
        base_w, base_h = GAME_RESOLUTIONS[resolution]
    except KeyError:
        raise ValueError(f"unknown resolution: {resolution!r}") from None
    if scale not in _CHOICES["window_scale"]:
        raise ValueError(f"unknown window scale: {scale!r}")
    if scale == "1":
        return None
    want = None
    if scale != WINDOW_SCALE_FIT:
        factor = Fraction(scale)
        want = (round(base_w * factor), round(base_h * factor))
    if area is None:
        return want
    avail_w, avail_h = area[0] - WINDOW_FRAME_MARGIN, area[1] - WINDOW_FRAME_MARGIN
    if avail_w < base_w or avail_h < base_h:
        return None
    if avail_w * base_h <= avail_h * base_w:           # width-limited
        fit = (avail_w, avail_w * base_h // base_w)
    else:                                              # height-limited
        fit = (avail_h * base_w // base_h, avail_h)
    if want is None or want[0] > fit[0] or want[1] > fit[1]:
        return fit
    return want


def ddraw_window_size(mode: str, resolution: int = SETTINGS_DEFAULTS["resolution"],
                      window_scale: str = SETTINGS_DEFAULTS["window_scale"]
                      ) -> tuple[int, int] | None:
    """``(width, height)`` written to ddraw.ini, ``None`` when both stay 0.

    Only the windowed mode uses the scale; the other modes always fill the screen.
    """
    if mode != "windowed" or window_scale == "1":
        return None
    return window_size(resolution, window_scale, work_area())


def ddraw_settings(mode: str, advanced: bool = False,
                   resolution: int = SETTINGS_DEFAULTS["resolution"],
                   window_scale: str = SETTINGS_DEFAULTS["window_scale"]
                   ) -> list[tuple[str, str]]:
    """Return the ``[ddraw]`` key/value pairs for a display mode."""
    try:
        pairs = list(DDRAW_MODE_SETTINGS[mode])
    except KeyError:
        raise ValueError(f"unknown display mode: {mode!r}") from None
    size = ddraw_window_size(mode, resolution, window_scale)
    if size:
        override = {"width": str(size[0]), "height": str(size[1])}
        pairs = [(k, override.get(k, v)) for k, v in pairs]
    if advanced:
        pairs.extend(DDRAW_ADVANCED_SETTINGS)
    return pairs


def _apply_ddraw(entries: list[tuple[str, str]], pairs, eol: str) -> list[list[str]]:
    out = [[content, ending] for content, ending in entries]
    start = None
    for i, (content, _) in enumerate(out):
        sec = _section_name(content)
        if sec is not None and sec.lower() == DDRAW_SECTION:
            start = i
            break

    if start is None:
        block = [[f"[{DDRAW_SECTION}]", eol]] + [[f"{k}={v}", eol] for k, v in pairs]
        if out:
            block.append(["", eol])
        return block + out

    end = len(out)
    for i in range(start + 1, len(out)):
        if _section_name(out[i][0]) is not None:
            end = i
            break

    wanted = {k.lower(): (k, v) for k, v in pairs}
    seen: set[str] = set()
    last_setting = start
    for i in range(start + 1, end):
        stripped = out[i][0].strip()
        if not stripped or stripped[0] in ";#":
            continue
        last_setting = i
        if "=" in stripped:
            name = stripped.split("=", 1)[0].strip().lower()
            if name in wanted:
                k, v = wanted[name]
                out[i][0] = f"{k}={v}"
                seen.add(name)

    missing = [[f"{k}={v}", eol] for k, v in pairs if k.lower() not in seen]
    if missing:
        # Append after the last setting of the section, i.e. before the
        # comments that introduce the next section.
        if not out[last_setting][1]:
            out[last_setting][1] = eol
        out[last_setting + 1:last_setting + 1] = missing
    return out


def update_ddraw_ini(path, mode: str, advanced: bool = False,
                     resolution: int = SETTINGS_DEFAULTS["resolution"],
                     window_scale: str = SETTINGS_DEFAULTS["window_scale"]) -> bool:
    """Write the display-mode keys into the ``[ddraw]`` section of ddraw.ini.

    Other sections, comments and unrelated keys are kept, existing key lines
    are replaced in place and missing keys are appended at the end of the
    section.  ``singlecpu``/``hook`` are only written when *advanced*.
    In windowed mode ``width``/``height`` follow *window_scale* (see
    ``window_size``); the other modes do not write them (``fullscreen=true``
    makes cnc-ddraw ignore them).  A missing file is created with just a
    ``[ddraw]`` section.  Returns True when the content changed.
    """
    p = Path(path)
    pairs = ddraw_settings(mode, advanced, resolution, window_scale)
    bom = b""
    entries: list[tuple[str, str]] = []
    if p.is_file():
        raw = p.read_bytes()
        if raw.startswith(UTF8_BOM):
            bom, raw = UTF8_BOM, raw[len(UTF8_BOM):]
        entries = _split_lines(raw.decode(FILE_ENCODING))
    eol = next((ending for _, ending in entries if ending), CRLF)
    out = _apply_ddraw(entries, pairs, eol)
    data = bom + "".join(content + ending for content, ending in out).encode(FILE_ENCODING)
    return _write_bytes(p, data, readonly=None)


def install_wrapper(src_dir, game_dir) -> list[str]:
    """Copy ddraw.dll (+ Shaders folder) into the game folder if missing.

    Returns the names that were copied.  Raises LauncherError if ddraw.dll is
    needed but not present in *src_dir*.
    """
    src, dst = Path(src_dir), Path(game_dir)
    copied = []
    if not (dst / DDRAW_DLL).is_file():
        dll = src / DDRAW_DLL
        if not dll.is_file():
            raise LauncherError(f"cnc-ddraw 래퍼 원본 폴더에 {DDRAW_DLL}이(가) 없습니다: {src}")
        shutil.copy2(dll, dst / DDRAW_DLL)
        copied.append(DDRAW_DLL)
    shaders = src / SHADERS_DIR
    if shaders.is_dir() and not (dst / SHADERS_DIR).exists():
        shutil.copytree(shaders, dst / SHADERS_DIR)
        copied.append(SHADERS_DIR + os.sep)
    return copied


# --------------------------------------------------------------------------
# Registry (AppCompat layer)
# --------------------------------------------------------------------------
def _compat_value_name(exe) -> str:
    return os.path.normpath(os.path.abspath(os.fspath(exe)))


def set_compat_layer(exe, on: bool, key_path: str = COMPAT_KEY) -> None:
    """Set ``~ HIGHDPIAWARE`` for *exe* in HKCU AppCompat Layers, or remove it."""
    name = _compat_value_name(exe)
    if on:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0,
                                winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, COMPAT_HIGHDPI)
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def get_compat_layer(exe, key_path: str = COMPAT_KEY) -> str | None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, _compat_value_name(exe))
            return value
    except FileNotFoundError:
        return None


# --------------------------------------------------------------------------
# Language, crash log, launch
# --------------------------------------------------------------------------
def read_ko_language(game_dir) -> int | None:
    """Language value for Korean, or None when ``lang\\kor\\strings.bin`` is absent."""
    if not game_dir:
        return None
    return KO_DEFAULT_LANGUAGE if (Path(game_dir) / KO_READY_FILE).is_file() else None


_GUI_HEAP_RE = re.compile(rb"^(\s*ul\s+guiHeapSize\s*=\s*)(\d+)(\s*)$", re.IGNORECASE)


def ensure_gui_heap(path, minimum: int = KO_GUI_HEAP_SIZE) -> bool:
    """Raise ``ul guiHeapSize`` in SYSTEM.CFG to at least *minimum*.

    Only that one value is touched; every other byte (CRLF, comments, the
    file's attributes) is kept.  Returns True when the file was changed.
    A missing file or key is left alone (the game then uses its own default).
    """
    p = Path(path)
    if not p.is_file():
        return False
    raw = p.read_bytes()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    out, hit = [], False
    for line in raw.split(nl):
        m = _GUI_HEAP_RE.match(line)
        if m and not hit:
            hit = True
            if int(m.group(2)) < minimum:
                line = m.group(1) + str(minimum).encode("ascii") + m.group(3)
        out.append(line)
    data = nl.join(out)
    return _write_bytes(p, data, readonly=None) if hit else False


@dataclass(frozen=True)
class FileStamp:
    exists: bool
    mtime_ns: int = 0
    size: int = 0


def file_stamp(path) -> FileStamp:
    try:
        st = os.stat(path)
    except OSError:
        return FileStamp(False)
    return FileStamp(True, st.st_mtime_ns, st.st_size)


def read_head(path, max_lines: int = CRASH_LOG_LINES) -> str:
    """First *max_lines* lines of a text file (ANSI code page, lossy)."""
    with open(path, "rb") as fh:
        raw = fh.read(256 * 1024)
    try:
        text = raw.decode("mbcs", errors="replace")
    except LookupError:
        text = raw.decode(FILE_ENCODING)
    lines = re.split(r"\r\n|\r|\n", text)[:max_lines]
    return "\n".join(lines).rstrip("\n")


@dataclass
class LaunchHandle:
    process: subprocess.Popen
    err_path: Path
    err_before: FileStamp


def launch(game_dir, dpi_fix: bool = True) -> LaunchHandle:
    """Set the DPI compat layer and start MCX.EXE with the game folder as cwd."""
    game = Path(game_dir)
    exe = game / GAME_EXE
    if not exe.is_file():
        raise LauncherError(f"{GAME_EXE}을(를) 찾을 수 없습니다: {game}")
    set_compat_layer(exe, dpi_fix)
    err_path = game / ERR_FILE
    before = file_stamp(err_path)
    proc = subprocess.Popen([str(exe)], cwd=str(game))
    return LaunchHandle(proc, err_path, before)


def crash_log_if_changed(handle: LaunchHandle) -> str | None:
    """Head of DEFAULT.ERR if it was created/modified since launch, else None."""
    after = file_stamp(handle.err_path)
    if after.exists and after != handle.err_before:
        try:
            return read_head(handle.err_path)
        except OSError as exc:
            return f"({ERR_FILE} 읽기 실패: {exc})"
    return None


# --------------------------------------------------------------------------
# Launcher settings (%APPDATA%\MCGLauncher\settings.json)
# --------------------------------------------------------------------------
def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def settings_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / APP_NAME / "settings.json"


def default_settings() -> dict:
    s = dict(SETTINGS_DEFAULTS)
    # Launcher exe dropped into the game folder -> use that folder.
    if (app_dir() / GAME_EXE).is_file():
        s["game_dir"] = str(app_dir())
    for cand in (Path(DEFAULT_WRAPPER_DIR), app_dir() / "cnc-ddraw"):
        if (cand / DDRAW_DLL).is_file():
            s["wrapper_dir"] = str(cand)
            break
    return s


def normalize_settings(settings: dict) -> dict:
    """Validate types/ranges, falling back to defaults for bad values."""
    out = {}
    for key, default in SETTINGS_DEFAULTS.items():
        value = settings.get(key, default)
        if isinstance(default, bool):
            value = value if isinstance(value, bool) else default
        elif isinstance(default, int):
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = default
            lo, hi = _INT_RANGES[key]
            value = min(max(value, lo), hi)
        elif key in _CHOICES:
            value = value if value in _CHOICES[key] else default
        else:
            value = str(value).strip() if isinstance(value, str) else default
        out[key] = value
    return out


def load_settings(path=None) -> tuple[dict, bool]:
    """Return ``(settings, existed)``; corrupt/missing files give defaults."""
    p = Path(path) if path else settings_path()
    base = default_settings()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("settings.json is not an object")
    except FileNotFoundError:
        return normalize_settings(base), False
    except (OSError, ValueError):
        return normalize_settings(base), True
    base.update(data)
    return normalize_settings(base), True


def save_settings(settings: dict, path=None) -> Path:
    p = Path(path) if path else settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(normalize_settings(settings), ensure_ascii=False, indent=2),
                   encoding="utf-8")
    os.replace(tmp, p)
    return p


def apply_settings(settings: dict) -> list[str]:
    """Apply everything to the game folder (no launch).  Returns status notes."""
    s = normalize_settings(settings)
    game = Path(s["game_dir"])
    exe = game / GAME_EXE
    if not s["game_dir"] or not exe.is_file():
        raise LauncherError(f"{GAME_EXE}을(를) 찾을 수 없습니다: {game}")
    notes = []
    if s["use_wrapper"]:
        copied = install_wrapper(s["wrapper_dir"], game)
        if copied:
            notes.append("cnc-ddraw 설치: " + ", ".join(copied))
    wrapper_active = (game / DDRAW_DLL).is_file()
    if wrapper_active:
        update_ddraw_ini(game / DDRAW_INI, s["display_mode"], s["advanced"],
                         s["resolution"], s["window_scale"])
        size = ddraw_window_size(s["display_mode"], s["resolution"], s["window_scale"])
        notes.append(f"{DDRAW_INI} 갱신" + (f" (창 {size[0]}×{size[1]})" if size else ""))
        if not s["use_wrapper"]:
            notes.append(f"주의: 게임 폴더에 {DDRAW_DLL}이 있어 래퍼가 계속 적용됩니다")
    elif s["display_mode"] != "windowed":
        notes.append("주의: 래퍼 없이 독점 DirectDraw(8bpp)로 실행됩니다")
    ko = read_ko_language(game) if s["language"] == "ko" else None
    write_prefs(game / PREFS_FILE, build_prefs_values(s, wrapper_active, ko))
    notes.append(f"{PREFS_FILE} 저장(읽기 전용)")
    if ko is not None and ensure_gui_heap(game / SYSTEM_CFG):
        notes.append(f"{SYSTEM_CFG} guiHeapSize를 {KO_GUI_HEAP_SIZE}로 올림 (한글 글꼴용)")
    set_compat_layer(exe, s["dpi_fix"])
    notes.append("DPI 보정 " + ("켬" if s["dpi_fix"] else "끔"))
    return notes


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
def enable_dpi_awareness() -> None:
    """Make the process system-DPI aware (must run before creating Tk)."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def _format_exit_code(code: int) -> str:
    if 0 <= code <= 255:
        return str(code)
    return f"{code} (0x{code & 0xFFFFFFFF:08X})"


class LauncherApp:
    """The launcher window."""

    POLL_MS = 1000
    OK_COLOR = "#1b7f1b"
    ERR_COLOR = "#c0001a"

    def __init__(self, root: tk.Tk, settings: dict, *, persist: bool = True,
                 interactive: bool = True, settings_file=None):
        self.root = root
        self.persist = persist
        self.interactive = interactive
        self.settings_file = settings_file
        self.handle: LaunchHandle | None = None
        s = normalize_settings(settings)

        root.title(WINDOW_TITLE)
        self._init_fonts()
        self.scale = max(1.0, root.winfo_fpixels("1i") / 96.0)

        self.v_game_dir = tk.StringVar(value=s["game_dir"])
        self.v_wrapper_dir = tk.StringVar(value=s["wrapper_dir"])
        self.v_resolution = tk.IntVar(value=s["resolution"])
        self.v_mode = tk.StringVar(value=s["display_mode"])
        self.v_window_scale = tk.StringVar(value=dict(WINDOW_SCALES)[s["window_scale"]])
        self.v_language = tk.StringVar(value=s["language"])
        self.v_sprite = tk.StringVar(value=s["sprite"])
        self.v_difficulty = tk.StringVar(value=DIFFICULTY_LABELS[s["difficulty"]])
        self.v_brightness = tk.IntVar(value=s["brightness"])
        self.v_music = tk.IntVar(value=s["music"])
        self.v_radio = tk.IntVar(value=s["radio"])
        self.v_sfx = tk.IntVar(value=s["sfx"])
        self.v_use_wrapper = tk.BooleanVar(value=s["use_wrapper"])
        self.v_dpi_fix = tk.BooleanVar(value=s["dpi_fix"])
        self.v_advanced = tk.BooleanVar(value=s["advanced"])
        self.v_status = tk.StringVar(value="준비됨 (Ready)")
        self.scales: dict[str, ttk.Scale] = {}

        self._build()
        self.v_game_dir.trace_add("write", lambda *_: self.refresh())
        self.v_wrapper_dir.trace_add("write", lambda *_: self.refresh())
        self.refresh()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.update_idletasks()
        root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())

    # ---------------------------------------------------------------- setup
    def _init_fonts(self) -> None:
        families = set(tkfont.families(self.root))
        family = next((f for f in ("Malgun Gothic", "맑은 고딕") if f in families), None)
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont",
                     "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"):
            try:
                f = tkfont.nametofont(name, root=self.root)
            except tk.TclError:
                continue
            if family:
                f.configure(family=family)
            if name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
                f.configure(size=10)
        try:
            tkfont.nametofont("TkFixedFont", root=self.root).configure(family="Consolas", size=9)
        except tk.TclError:
            pass

    def _p(self, n: float) -> int:
        return int(round(n * self.scale))

    def _build_hotkeys(self, parent: ttk.Frame) -> None:
        """Read-only table of in-game hotkeys (see HOTKEYS / HOTKEY_SOURCES)."""
        P = self._p
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text=HOTKEY_INTRO, justify="left", wraplength=P(620)).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, P(6)))
        cols = ("group", "key", "action", "conf")
        style = ttk.Style(self.root)
        style.configure("Hotkeys.Treeview", rowheight=P(22))
        style.configure("Hotkeys.Treeview.Heading", padding=(P(2), P(3)))
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=26, selectmode="browse",
                            style="Hotkeys.Treeview")
        for cid, title, width, anchor in (("group", "구분", P(84), "w"), ("key", "키", P(196), "w"),
                                          ("action", "동작", P(360), "w"), ("conf", "검증", P(64), "center")):
            tree.heading(cid, text=title)
            tree.column(cid, width=width, minwidth=width, anchor=anchor, stretch=(cid == "action"))
        ys = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ys.set)
        tree.grid(row=1, column=0, sticky="nsew")
        ys.grid(row=1, column=1, sticky="ns")
        for g, key, action, conf in HOTKEYS:
            tree.insert("", "end", values=(g, key, action, conf))
        self.hotkey_tree = tree
        ttk.Label(parent, text=HOTKEY_SOURCES, justify="left", wraplength=P(620),
                  foreground="#555555").grid(row=2, column=0, columnspan=2, sticky="w", pady=(P(6), 0))

    def _build(self) -> None:
        P = self._p
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        outer = ttk.Frame(self.notebook, padding=P(10))
        self.notebook.add(outer, text="  실행 설정  ")
        keys_tab = ttk.Frame(self.notebook, padding=P(10))
        self.notebook.add(keys_tab, text="  게임 단축키  ")
        self._build_hotkeys(keys_tab)
        outer.columnconfigure(0, weight=1, uniform="col")
        outer.columnconfigure(1, weight=1, uniform="col")
        gap = (0, P(6))

        # Game folder
        gf = ttk.LabelFrame(outer, text="게임 폴더 (Game folder)", padding=P(6))
        gf.grid(row=0, column=0, columnspan=2, sticky="ew", pady=gap)
        gf.columnconfigure(0, weight=1)
        ttk.Entry(gf, textvariable=self.v_game_dir, width=60).grid(row=0, column=0, sticky="ew")
        ttk.Button(gf, text="찾기", command=self.browse_game_dir).grid(row=0, column=1, padx=(P(6), 0))
        self.game_hint = ttk.Label(gf, text="")
        self.game_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(P(3), 0))

        # Wrapper source folder
        wf = ttk.LabelFrame(outer, text="cnc-ddraw 래퍼 원본 폴더 (Wrapper source)", padding=P(6))
        wf.grid(row=1, column=0, columnspan=2, sticky="ew", pady=gap)
        wf.columnconfigure(0, weight=1)
        ttk.Entry(wf, textvariable=self.v_wrapper_dir, width=60).grid(row=0, column=0, sticky="ew")
        ttk.Button(wf, text="찾기", command=self.browse_wrapper_dir).grid(row=0, column=1, padx=(P(6), 0))
        self.wrapper_hint = ttk.Label(wf, text="")
        self.wrapper_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(P(3), 0))

        # Resolution / display mode
        rf = ttk.LabelFrame(outer, text="해상도 (Resolution)", padding=P(6))
        rf.grid(row=2, column=0, sticky="nsew", pady=gap, padx=(0, P(3)))
        for i, (value, label) in enumerate(RESOLUTIONS):
            ttk.Radiobutton(rf, text=label, value=value, variable=self.v_resolution).grid(
                row=i, column=0, columnspan=2, sticky="w")
        ttk.Label(rf, text="창 배율 (Window scale)").grid(
            row=len(RESOLUTIONS), column=0, sticky="w", padx=(0, P(8)), pady=(P(6), 0))
        self.window_scale_box = ttk.Combobox(rf, textvariable=self.v_window_scale, state="readonly",
                                             values=[label for _, label in WINDOW_SCALES], width=20)
        self.window_scale_box.grid(row=len(RESOLUTIONS), column=1, sticky="w", pady=(P(6), 0))
        ttk.Label(rf, text=WINDOW_SCALE_HINT, justify="left", wraplength=P(300),
                  foreground="#555555").grid(row=len(RESOLUTIONS) + 1, column=0, columnspan=2,
                                             sticky="w", pady=(P(3), 0))
        mf = ttk.LabelFrame(outer, text="화면 모드 (Display mode)", padding=P(6))
        mf.grid(row=2, column=1, sticky="nsew", pady=gap, padx=(P(3), 0))
        for i, (value, label) in enumerate(DISPLAY_MODES):
            ttk.Radiobutton(mf, text=label, value=value, variable=self.v_mode).grid(
                row=i, column=0, sticky="w")

        # Language / sprite set
        lf = ttk.LabelFrame(outer, text="언어 (Language)", padding=P(6))
        lf.grid(row=3, column=0, sticky="nsew", pady=gap, padx=(0, P(3)))
        ttk.Radiobutton(lf, text="English", value="en", variable=self.v_language).grid(
            row=0, column=0, sticky="w")
        self.ko_radio = ttk.Radiobutton(lf, text="한국어 (준비 중)", value="ko",
                                        variable=self.v_language, state="disabled")
        self.ko_radio.grid(row=1, column=0, sticky="w")
        sf = ttk.LabelFrame(outer, text="스프라이트 (Sprite set)", padding=P(6))
        sf.grid(row=3, column=1, sticky="nsew", pady=gap, padx=(P(3), 0))
        for i, (value, label) in enumerate(SPRITE_SETS):
            ttk.Radiobutton(sf, text=label, value=value, variable=self.v_sprite).grid(
                row=i, column=0, sticky="w")

        # Game options
        of = ttk.LabelFrame(outer, text="게임 옵션 (Game options)", padding=P(6))
        of.grid(row=4, column=0, columnspan=2, sticky="ew", pady=gap)
        of.columnconfigure(1, weight=1)
        ttk.Label(of, text="난이도 (Difficulty)").grid(row=0, column=0, sticky="w", padx=(0, P(8)))
        self.difficulty_box = ttk.Combobox(of, textvariable=self.v_difficulty, state="readonly",
                                           values=DIFFICULTY_LABELS, width=22)
        self.difficulty_box.grid(row=0, column=1, sticky="w", pady=(0, P(4)))
        for row, (key, label, var) in enumerate((
                ("brightness", "밝기 (Brightness)", self.v_brightness),
                ("music", "음악 (Music)", self.v_music),
                ("radio", "무전 (Radio)", self.v_radio),
                ("sfx", "효과음 (SFX)", self.v_sfx)), start=1):
            self._slider(of, row, key, label, var)

        # Compatibility
        cf = ttk.LabelFrame(outer, text="호환성 (Compatibility)", padding=P(6))
        cf.grid(row=5, column=0, columnspan=2, sticky="ew", pady=gap)
        ttk.Checkbutton(cf, text="DirectDraw 래퍼 사용(cnc-ddraw)",
                        variable=self.v_use_wrapper, command=self.refresh).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(cf, text="DPI 보정(HIGHDPIAWARE)",
                        variable=self.v_dpi_fix).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(cf, text="고급 cnc-ddraw 옵션 (singlecpu=true, hook=4)",
                        variable=self.v_advanced).grid(row=2, column=0, sticky="w")

        # Buttons
        bf = ttk.Frame(outer)
        bf.grid(row=6, column=0, columnspan=2, sticky="ew", pady=gap)
        for c in range(4):
            bf.columnconfigure(c, weight=1, uniform="btn")
        self.btn_launch = ttk.Button(bf, text="게임 실행", command=self.on_launch)
        self.btn_save = ttk.Button(bf, text="설정만 저장", command=self.on_save)
        self.btn_open = ttk.Button(bf, text="게임 폴더 열기", command=self.open_game_dir)
        self.btn_cnc = ttk.Button(bf, text="cnc-ddraw 설정 도구 열기", command=self.open_cnc_config)
        for c, btn in enumerate((self.btn_launch, self.btn_save, self.btn_open, self.btn_cnc)):
            btn.grid(row=0, column=c, sticky="ew", padx=(0 if c == 0 else P(3), 0), ipady=P(2))

        # Crash log
        xf = ttk.LabelFrame(outer, text="크래시 로그 (DEFAULT.ERR)", padding=P(6))
        xf.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=gap)
        outer.rowconfigure(7, weight=1)
        xf.columnconfigure(0, weight=1)
        xf.rowconfigure(0, weight=1)
        self.crash_text = tk.Text(xf, height=8, wrap="none", font="TkFixedFont",
                                  state="disabled", relief="flat", borderwidth=0)
        ys = ttk.Scrollbar(xf, orient="vertical", command=self.crash_text.yview)
        xs = ttk.Scrollbar(xf, orient="horizontal", command=self.crash_text.xview)
        self.crash_text.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.crash_text.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self.set_crash_log("")

        # Status line
        ttk.Label(outer, textvariable=self.v_status, relief="sunken", anchor="w",
                  padding=(P(4), P(2))).grid(row=8, column=0, columnspan=2, sticky="ew")

    def _slider(self, parent, row: int, key: str, label: str, var: tk.IntVar) -> None:
        P = self._p
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, P(8)))
        scale = ttk.Scale(parent, from_=0, to=100, orient="horizontal",
                          command=lambda v, var=var: var.set(int(round(float(v)))))
        scale.set(var.get())
        scale.grid(row=row, column=1, sticky="ew", pady=P(1))
        ttk.Label(parent, textvariable=var, width=4, anchor="e").grid(row=row, column=2, sticky="e")
        self.scales[key] = scale

    # --------------------------------------------------------------- state
    def collect_settings(self) -> dict:
        try:
            difficulty = DIFFICULTY_LABELS.index(self.v_difficulty.get())
        except ValueError:
            difficulty = SETTINGS_DEFAULTS["difficulty"]
        window_scale = next((key for key, label in WINDOW_SCALES
                             if label == self.v_window_scale.get()),
                            SETTINGS_DEFAULTS["window_scale"])
        return normalize_settings({
            "game_dir": self.v_game_dir.get(),
            "wrapper_dir": self.v_wrapper_dir.get(),
            "resolution": self.v_resolution.get(),
            "display_mode": self.v_mode.get(),
            "window_scale": window_scale,
            "language": self.v_language.get(),
            "sprite": self.v_sprite.get(),
            "difficulty": difficulty,
            "brightness": self.v_brightness.get(),
            "music": self.v_music.get(),
            "radio": self.v_radio.get(),
            "sfx": self.v_sfx.get(),
            "use_wrapper": self.v_use_wrapper.get(),
            "dpi_fix": self.v_dpi_fix.get(),
            "advanced": self.v_advanced.get(),
        })

    def refresh(self) -> None:
        """Re-validate folders and update hints / Korean option."""
        game = self.v_game_dir.get().strip()
        game_ok = bool(game) and (Path(game) / GAME_EXE).is_file()
        if game_ok:
            installed = (Path(game) / DDRAW_DLL).is_file()
            self.game_hint.configure(
                foreground=self.OK_COLOR,
                text=f"{GAME_EXE} 확인됨 · cnc-ddraw " + ("설치됨" if installed else "미설치 (실행 시 복사)"))
        else:
            self.game_hint.configure(
                foreground=self.ERR_COLOR,
                text=f"{GAME_EXE}이(가) 없습니다. 올바른 게임 폴더를 선택하세요. (MCX.EXE not found)")

        wrapper = self.v_wrapper_dir.get().strip()
        if wrapper and (Path(wrapper) / DDRAW_DLL).is_file():
            self.wrapper_hint.configure(foreground=self.OK_COLOR, text=f"{DDRAW_DLL} 확인됨")
        elif game_ok and (Path(game) / DDRAW_DLL).is_file():
            self.wrapper_hint.configure(foreground=self.OK_COLOR,
                                        text=f"게임 폴더에 {DDRAW_DLL}이 이미 설치되어 있습니다")
        elif self.v_use_wrapper.get():
            self.wrapper_hint.configure(foreground=self.ERR_COLOR,
                                        text=f"이 폴더에 {DDRAW_DLL}이 없습니다 (ddraw.dll not found)")
        else:
            self.wrapper_hint.configure(foreground="", text="래퍼 사용 안 함")

        ko = read_ko_language(game) if game_ok else None
        if ko is None:
            self.ko_radio.configure(text="한국어 (준비 중)", state="disabled")
            if self.v_language.get() == "ko":
                self.v_language.set("en")
        else:
            self.ko_radio.configure(text="한국어", state="normal")

        for btn in (self.btn_save, self.btn_open, self.btn_cnc):
            btn.state(["!disabled"] if game_ok else ["disabled"])
        running = self.handle is not None and self.handle.process.poll() is None
        self.btn_launch.state(["!disabled"] if game_ok and not running else ["disabled"])

    def set_status(self, text: str) -> None:
        self.v_status.set(text)

    def set_crash_log(self, text: str) -> None:
        self.crash_text.configure(state="normal")
        self.crash_text.delete("1.0", "end")
        self.crash_text.insert("1.0", text or "(없음 — 게임이 DEFAULT.ERR을 남기면 여기에 표시됩니다)")
        self.crash_text.configure(state="disabled")

    def _error(self, title: str, message: str) -> None:
        self.set_status(f"오류: {message}")
        if self.interactive:
            messagebox.showerror(title, message, parent=self.root)

    def _save_launcher_settings(self, settings: dict) -> None:
        if not self.persist:
            return
        try:
            save_settings(settings, self.settings_file)
        except OSError as exc:
            self.set_status(f"런처 설정 저장 실패: {exc}")

    # -------------------------------------------------------------- actions
    def _apply(self) -> tuple[dict, list[str]] | None:
        s = self.collect_settings()
        try:
            notes = apply_settings(s)
        except (LauncherError, OSError) as exc:
            self._error("설정 적용 실패", str(exc))
            return None
        self._save_launcher_settings(s)
        self.refresh()
        return s, notes

    def on_save(self) -> None:
        result = self._apply()
        if result:
            self.set_status("설정 저장 완료: " + " · ".join(result[1]))

    def on_launch(self) -> None:
        if self.handle is not None and self.handle.process.poll() is None:
            self.set_status("게임이 이미 실행 중입니다.")
            return
        result = self._apply()
        if not result:
            return
        s, _ = result
        try:
            self.handle = launch(s["game_dir"], s["dpi_fix"])
        except (LauncherError, OSError) as exc:
            self._error("게임 실행 실패", str(exc))
            return
        self.set_crash_log("")
        self.refresh()
        self.set_status(f"게임 실행 중... (PID {self.handle.process.pid})")
        self.root.after(self.POLL_MS, self._poll)

    def _poll(self) -> None:
        handle = self.handle
        if handle is None:
            return
        code = handle.process.poll()
        if code is None:
            self.root.after(self.POLL_MS, self._poll)
            return
        self.handle = None
        self.refresh()
        log = crash_log_if_changed(handle)
        if log is not None:
            self.set_crash_log(log)
            self.set_status(f"게임 종료 (코드 {_format_exit_code(code)}) — "
                            f"{ERR_FILE}이 갱신되었습니다. 크래시 로그를 확인하세요.")
        else:
            self.set_status(f"게임 종료 (코드 {_format_exit_code(code)})")

    def browse_game_dir(self) -> None:
        d = filedialog.askdirectory(parent=self.root, mustexist=True,
                                    title="MCX.EXE가 있는 게임 폴더 선택",
                                    initialdir=self.v_game_dir.get() or None)
        if d:
            self.v_game_dir.set(os.path.normpath(d))

    def browse_wrapper_dir(self) -> None:
        d = filedialog.askdirectory(parent=self.root, mustexist=True,
                                    title="ddraw.dll이 있는 cnc-ddraw 폴더 선택",
                                    initialdir=self.v_wrapper_dir.get() or None)
        if d:
            self.v_wrapper_dir.set(os.path.normpath(d))

    def open_game_dir(self) -> None:
        d = self.v_game_dir.get().strip()
        if d and os.path.isdir(d):
            os.startfile(d)
        else:
            self._error("폴더 열기 실패", f"폴더가 없습니다: {d}")

    def open_cnc_config(self) -> None:
        game = Path(self.v_game_dir.get().strip())
        tool = game / CNC_CONFIG_EXE
        if not tool.is_file():
            src = Path(self.v_wrapper_dir.get().strip()) / CNC_CONFIG_EXE
            if not (src.is_file() and (game / GAME_EXE).is_file()):
                self._error("설정 도구 없음", f"게임 폴더에 '{CNC_CONFIG_EXE}'이(가) 없습니다.")
                return
            if not (self.interactive and messagebox.askyesno(
                    "cnc-ddraw 설정 도구",
                    f"게임 폴더에 '{CNC_CONFIG_EXE}'이(가) 없습니다.\n"
                    f"래퍼 원본 폴더에서 복사할까요?\n\n{src}", parent=self.root)):
                return
            try:
                shutil.copy2(src, tool)
            except OSError as exc:
                self._error("복사 실패", str(exc))
                return
        try:
            subprocess.Popen([str(tool)], cwd=str(game))
        except OSError as exc:
            self._error("설정 도구 실행 실패", str(exc))
            return
        self.set_status(f"'{CNC_CONFIG_EXE}' 실행됨 — 런처가 관리하는 [ddraw] 키는 다음 저장/실행 시 덮어씁니다.")

    def on_close(self) -> None:
        self._save_launcher_settings(self.collect_settings())
        self.root.destroy()


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------
def _emit(text: str) -> None:
    stream = sys.stdout
    if stream is not None:
        try:
            stream.write(text + "\n")
            stream.flush()
        except (OSError, ValueError):
            pass
    try:  # --noconsole builds have no stdout; keep a log for verification
        Path(tempfile.gettempdir(), f"{APP_NAME}-selftest.log").write_text(text + "\n", encoding="utf-8")
    except OSError:
        pass


def _count_widgets(widget) -> int:
    return 1 + sum(_count_widgets(child) for child in widget.winfo_children())


def run_selftest() -> int:
    """Build the window (hidden), exercise the pipeline on temp files, exit."""
    report = []
    code = 0
    try:
        enable_dpi_awareness()
        root = tk.Tk()
        root.withdraw()
        try:
            settings, existed = load_settings()
            app = LauncherApp(root, settings, persist=False, interactive=False)
            root.update_idletasks()
            collected = app.collect_settings()
            if root.title() != WINDOW_TITLE:
                raise AssertionError(f"unexpected title {root.title()!r}")
            expected = normalize_settings(settings)
            expected["language"] = collected["language"]  # ko falls back to en if not ready
            if collected != expected:
                raise AssertionError(f"widgets do not round-trip settings: {collected} != {expected}")
            with tempfile.TemporaryDirectory(prefix="mcgl-selftest-") as td:
                prefs = Path(td, PREFS_FILE)
                write_prefs(prefs, build_prefs_values(collected, True, None))
                write_prefs(prefs, build_prefs_values(collected, True, None))
                update_ddraw_ini(Path(td, DDRAW_INI), collected["display_mode"], collected["advanced"],
                                 collected["resolution"], collected["window_scale"])
                # real work-area query + a "fit" size (the frozen exe must be able to call it)
                area = work_area()
                fit = window_size(collected["resolution"], WINDOW_SCALE_FIT, area)
                if not is_readonly(prefs):
                    raise AssertionError("prefs.cfg not read-only after write")
                set_readonly(prefs, False)
            report.append(f"settings.json exists={existed} path={settings_path()}")
            report.append(f"game_dir={collected['game_dir']} valid={(Path(collected['game_dir']) / GAME_EXE).is_file()}")
            report.append(f"window_scale={collected['window_scale']} work_area={area} fit_size={fit}")
            report.append(f"widgets={_count_widgets(root)} reqsize={root.winfo_reqwidth()}x{root.winfo_reqheight()} "
                          f"tk_scaling={float(root.tk.call('tk', 'scaling')):.3f}")
        finally:
            root.destroy()
        report.append("SELFTEST OK")
    except Exception:  # noqa: BLE001 - report anything
        code = 1
        report.append(traceback.format_exc().rstrip())
        report.append("SELFTEST FAILED")
    _emit("\n".join(report))
    return code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=WINDOW_TITLE)
    parser.add_argument("--selftest", action="store_true",
                        help="build the GUI without showing it and exit (0 = OK)")
    parser.add_argument("--tab", choices=("settings", "keys"), default="settings",
                        help="tab to show at startup (keys = 게임 단축키)")
    args, _ = parser.parse_known_args(argv)
    if args.selftest:
        return run_selftest()

    enable_dpi_awareness()
    settings, existed = load_settings()
    if not existed:
        settings = settings_from_prefs(read_prefs(Path(settings["game_dir"]) / PREFS_FILE), settings)
    root = tk.Tk()
    app = LauncherApp(root, settings)
    if args.tab == "keys":
        app.notebook.select(1)
    if not existed:
        app.set_status("첫 실행: 게임의 prefs.cfg에서 옵션을 불러왔습니다. 확인 후 '게임 실행'을 누르세요.")
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
