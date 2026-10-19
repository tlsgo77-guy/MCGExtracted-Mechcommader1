# MCG bitmap fonts (.FNT) and the Korean build

## FNT format (little-endian)

| Offset | Type | Meaning |
|---|---|---|
| 0 | u32 | version = 11825 (ASCII "1.") |
| 4 | u32 | glyph count |
| 8 | u32 | height in pixels (shared by all glyphs) |
| 12 | u32 | unknown, preserved verbatim (10 in the 280-glyph fonts, 254 in the 140-glyph ones) |
| 16 | u32[count] | absolute glyph offsets from the file start |
| ... | `{u32 width; u8 pixels[width*height]}` | glyph, row-major |

Pixel `0xFF` is transparent; any other value is a palette index (the glyph colour).
Several offsets may point at the same record (the Korean fonts share one blank glyph).
Glyph index = byte value of the character. `tools/mcg_fnt.py` reads and writes this
(all 30 original files round-trip byte-identically).

```
python tools/mcg_fnt.py info <font.FNT>
python tools/mcg_fnt.py preview <font.FNT> <out.png> ["text"] [--scale 4]   # white on black, shadow grey
```

`text` may be Korean; it is encoded as EUC-KR and mapped with the layout below.

## Korean layout (count = 256 + 94*94 = 9092)

* Index 0..255: the original glyphs, unchanged (padded with width-0 glyphs when the
  original has only 140, dropped past 255 when it has 280).
* EUC-KR pair (lead L, trail T), both in 0xA1..0xFE:
  `index = 256 + (L - 0xA1) * 94 + (T - 0xA1)`; e.g. U+D55C (EUC-KR C7D1) = 3876.
* Filled: the 2350 KS X 1001 syllables (rows 0xB0..0xC8) and the symbol rows 0xA1..0xA3
  (242 glyphs at 8 px, 258 at 10/12 px). Every other cell points at one shared blank
  glyph whose width is the Hangul advance, so unsupported characters show as a gap.

## What the build does

`tools/build_korean_fonts.py` converts the 23 text fonts (BLKFNT, BLUE, GREEN, GRYFNT,
RED, WHITE, YELLOW in 8/10/12 px, plus BLUEDRP and YELLDRP) and ignores DIM*/L*.

| Font height | Galmuri face | Pillow size | Hangul ink | Advance | Hangul rows |
|---|---|---|---|---|---|
| 8 | Galmuri7 | 8 | 7x7 | 8 | 0-6 |
| 10 | Galmuri9 | 10 | 9x9 | 10 | 0-8 |
| 12 | Galmuri11 | 12 | 11x11 | 12 | 0-10 |

* The TTFs have a design size equal to the Hangul advance (em + 1 px spacing), so
  Pillow must be asked for 8/10/12, not 7/9/11 (7/9/11 renders a rescaled, wrong grid).
  Rendering is 1-bit; the ink of every glyph is compared with Galmuri's own `.bdf`
  bitmaps (exact author pixels) and the build fails on any difference (`--no-verify`
  skips this and needs no BDFs).
* Vertical placement: bottom row of the Hangul box = Latin cap baseline + 1, clamped
  into the cell (all fonts end up with the Hangul box starting at row 0).
* Main colour = most frequent value over 'A'..'Z'. The *DRP shadow (index 16) is main
  shifted by (0,+1) and (+1,+1); Hangul gets the same shadow drawn first.
* Symbols that overhang the cell (accent marks above the em box, the fullwidth
  low line, the inverted marks) are shifted into it when they fit entirely; the rest
  are clipped: U+212B (Angstrom) at 8/10 px, and in the 8 px DRP fonts a few shadow pixels
  of U+2103, U+2109, U+2592, U+FF3F, U+FFE3.
* Galmuri7 (8 px fonts) has no glyph for 16 symbols: A2A7-A2AB, A2AD, A2B0, A2B1,
  A2CD-A2D1, A2E1, A2E3, A2E4 (caron/breve/accents, contour integral, hot springs,
  telephone signs, pointing hands, SQUARE CO/AM/PM). Those cells stay blank.
  Galmuri9/11 cover all of rows A1-A3.

## Rebuild

```
pip install pillow
python tools/build_korean_fonts.py ^
  --src MISC.FST ^
  --galmuri game-source/tools/galmuri ^
  --out game-source/extracted/MCX/lang/kor/data/fonts
```

(`--src` is the directory with the original `*.FNT`, i.e. the repo's extracted `MISC.FST/`.) It also writes
the contact sheet `lang/kor/fonts_preview.png` (rendered with `mcg_fnt`, not PIL text).

## Galmuri

Galmuri (갈무리) by quiple (Lee Minseo), version 2.40.4 (release 2026-07-12), SIL Open Font
License 1.1: https://github.com/quiple/galmuri . Files used live in `game-source/tools/galmuri/`
(`Galmuri7/9/11.ttf`, `.bdf`, `LICENSE.txt`, `VERSION.txt`); that directory is gitignored.
The generated `.FNT` files are derivative works of Galmuri: keep the OFL text and the
copyright line (Copyright (c) 2019-2025 Lee Minseo) with any redistribution, and do not
sell them by themselves.
