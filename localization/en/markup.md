# Text markup (`%` codes) used in briefings and descriptions

Decoded from `SMUTI::process` in MCX.EXE (VA 0x728ed0).  SMUTI renders the briefing `.txt` files (`Logistics::getCurrentMission` -> `SMUTI::init`), the component descriptions of `MISC.FST/desc.fit` (`DescString`), the drag-icon popup of the repair screen and the chat windows.

Counts below are over the 129 `.txt` files in `MISSION.FST` (column *briefings*) and over the 217 `DescString` values of `MISC.FST/desc.fit` (column *desc.fit*).  Codes are case-insensitive (`%FC1` = `%fc1`); counts fold the two spellings together only where noted.

## Codes

| code | meaning | briefings (uses) | briefings (files) | desc.fit (uses) | reading |
|---|---|---:|---:|---:|---|
| `%n` | newline | 2269 | 129 | 27 | flush the pending text and start a new line (x=0, y += font height + 1). Plain CR/LF in the file are ignored. |
| `%c` | centre | 740 | 129 | 0 | centre the text that follows, up to the next `%` code (at most 80 characters are measured). |
| `%fs` | font size 0 | 191 | 127 | 0 | small font of the current colour (`<name>.fnt`, e.g. `white.fnt`). |
| `%fm` | font size 1 | 188 | 129 | 0 | medium font (`<name>10.fnt`). |
| `%fl` | font size 2 | 2 | 2 | 0 | large font (`<name>12.fnt`). |
| `%tN` | horizontal gap | 287 | 60 | 0 | `%t` + decimal digits N: advance the pen by N pixels (hanging indents, column alignment). No glyph is drawn. |
| `%%` | literal % | 0 | 0 | 0 | a single percent sign. |
| `%fc1` | colour 1 (red) | 163 | 129 | 0 | `%fc` + one digit selects the colour row of the font table: red.fnt |
| `%fc2` | colour 2 (yellow) | 392 | 129 | 0 | `%fc` + one digit selects the colour row of the font table: yellow.fnt |
| `%fc4` | colour 4 (blue) | 330 | 129 | 0 | `%fc` + one digit selects the colour row of the font table: blue.fnt |
| `%fc5` | colour 5 (grey) | 295 | 127 | 0 | `%fc` + one digit selects the colour row of the font table: gryfnt.fnt |
| `%fc6` | colour 6 (white) | 408 | 129 | 0 | `%fc` + one digit selects the colour row of the font table: white.fnt |
| `%fc8` | colour 8 (yellow drop-shadow) | 14 | 6 | 50 | `%fc` + one digit selects the colour row of the font table: yelldrp.fnt |
| `% ` | not a SMUTI code | 1 | 1 | 0 | emitted literally ('%' + the character) |

### `%tN` values seen

briefings: `%t9` x108, `%t12` x179

desc.fit: none

## Colour / size table (`fonts[colour][size]`, filled in `aSystem::start`)

| `%fcN` | colour | `%fs` | `%fm` | `%fl` |
|---:|---|---|---|---|
| 0 | black | blkfnt.fnt | blkfnt10.fnt | blkfnt12.fnt |
| 1 | red | red.fnt | red10.fnt | red12.fnt |
| 2 | yellow | yellow.fnt | yellow10.fnt | yellow12.fnt |
| 3 | green | green.fnt | green10.fnt | green12.fnt |
| 4 | blue | blue.fnt | blue10.fnt | blue12.fnt |
| 5 | grey | gryfnt.fnt | gryfnt10.fnt | gryfnt12.fnt |
| 6 | white | white.fnt | white10.fnt | white12.fnt |
| 7 | dim | dim.fnt | dim10.fnt | dim12.fnt |
| 8 | yellow drop-shadow | yelldrp.fnt | (dim10.fnt?) | (not set) |
| 9 | blue drop-shadow | bluedrp.fnt | (dim10.fnt?) | (not set) |

Font files are in `MISC.FST` (`*.FNT`, bitmaps in `ART.FST/data/art/logart/*.tga`).  Colours 8 and 9 only define the base size; `%fm/%fl` after them select the entries that `aSystem::start` leaves partly unset (the disassembly assigns `dim10.fnt` to slots 25 and 28), so avoid size changes after `%fc8/%fc9`.

## Behaviour that matters for translation

* **Line breaks** in the file are meaningless: CR, LF and TAB (anything below 0x20) are skipped. Only `%n` ends a line. A blank line is `%n%n`.
* **Word wrap** is automatic at the last space (0x20) before the pen passes the port width; there is no hyphenation. Text without spaces wraps only at the very last character that fits.
* **Last two bytes dropped**: `SMUTI::init` reads the whole file and writes a NUL at `length-2`.  Every file therefore needs at least two trailing bytes (the usual CR LF) after the last visible character, otherwise the last characters are cut.
* **Pending text buffer** is 256 bytes (`SMUTI+0x20..+0x120`); wrapping flushes it, but a single unbroken run longer than that between two codes overflows.
* **`%c` measures at most 80 characters** (stack buffer of 0x50 bytes) and centres a single line.
* **Per-byte rendering**: every byte is looked up in the current `aFont` with `aFont::width(byte)`; there is no multi-byte (DBCS) handling in SMUTI itself.
* **Apostrophes**: the text uses a back-tick for some apostrophes (`` `Mechs``) and a straight quote for others (`'Mechs`).  Both glyphs exist in the fonts; keep whichever the original used when copying names such as `'Mech`.
* **`%d`-style printf codes are not interpreted** here (`%s`, `%i` ... belong to the EXE string table, see `strings.json`); a bare `%` followed by an unknown letter prints the percent sign and the letter.
