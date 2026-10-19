# Korean briefings at 10 px (TR-10PX)

Body text of the 45 briefings in `localization/ko/briefings/` (brf0101-0506, xbrf0101-0305, xsbrf0401-0404) was switched from the 8 px to the 10 px Korean font.
Files stay UTF-8, CRLF, no BOM, same trailing CRLF count as before. English originals (`MISSION.FST\`), `glossary.json` and `STYLE.md` were not touched; nothing was committed; the game was not started.

Validator: `check_briefings_10px.py` (copy of the TR-B3 `check_briefings.py`, in the TR-B3 scratch folder `kor/tr_b3/`). Result: **45 files, 0 errors, 0 warnings** at the assumed 168 px panel width. Overlay: `python -I tools/build_korean_overlay.py --only briefings` -> 45 written, 0 errors, 76 warnings (45 "`%` codes differ from the English original" = the size codes, expected; 31 "line is N bytes (> 253)" that were already there at 8 px, same files and same count).

The 8 px versions of the 45 files (before this change) are kept outside the repo in the session scratchpad folder `kor/briefings_backup_8px/` (`localization/` is not tracked by git, so there is no other copy).

## What was done

1. **`%fs` -> `%fm`: 73 substitutions** (45 of them are the second header line `%fs%fc4%cFEDCOM:...`). That header `%fs` is what sets the size of everything below it (separator, title, objectives, fire support, briefing text) until the next size code, so it has to change for the body to become 10 px. Titles that already used `%fm` (`****기밀****`, `**전술 경고**`, `제한 시간: ...`) were left alone (there is no `%fl` in the Korean files; nothing was promoted to 12 px).
2. **Colour 8 (the `   (부 목표)` markers in xbrf0102/0103/0104/0201/0202/0204, 14 lines): guard codes.** The source never has a `%fs` after `%fc8`, so rule 1 alone would leave the size state at `%fm` when `%fc8` is selected, and colour 8 has only the 8 px Korean font (`%fm` after `%fc8` selects a font without Hangul). Each marker is therefore written `%fc8%fs   (부 목표)%n` and the next line starts `%fm%fc2...` (or `%fm%fc6화력 지원:` after the last marker): **14 x `%fs` after `%fc8`, 14 x `%fm` before the `%fcN` that leaves colour 8**. These 28 codes are the only added size codes. Colour 9 is not used.
3. **Re-wrapped hand-wrapped lines: 50 items** (28 objective lines `%fc2N-...` / `N-...`, 22 tactical-notice or tactical-warning bullets). Each flagged item (objective line or `*` bullet plus its `%n%t9` continuation lines) was joined and re-wrapped at spaces to fit 168 px (a `%t9` line has 168-18 px): objectives greedily (the predicate such as `파괴하라` stays on the last line, as in the 8 px text), bullets in the fewest lines with the most even line lengths. 113 physical lines became 152 (net +39 `%n%t9` pairs; no pair was removed). Items that still fit at 10 px were not touched. No `%t12` fire-support line needed re-wrapping (the widest, `포격: 소형 4  대형 2`, is 129 px including the double indent).
4. **Hard `%n` inside prose: 12.** Where the wrap landed right after a colour code (the validator's mid-word / empty-buffer break: a particle such as 가, 에, 두 pushed alone to the next line), one space in that paragraph was replaced by `%n` (nearest earlier space that removes the warning and creates none). Wording is unchanged; list below.
5. **Title shortened: 1** (brf0103, see the table). All other `%c` lines are <= 164 px at 10 px (second longest: brf0105 `**적의 공격으로부터 농장 방어**`, 162 px; the longest `FEDCOM:...` header is 149 px).
6. **Nothing could not be fitted.**

Pitfalls handled by the re-wrapper: never break after a literal `%` (`50%` + `%n` would read as `%%` + `n`), never start a `%t9` continuation with a digit (`%t91...`).

## Checks in `check_briefings_10px.py` beyond the original

* the code sequence is compared with the English original **after** applying the planned mapping (`%fs` -> `%fm` except in colours 8/9); tolerated differences, reported as notes: inserted/removed `%n%t9` / `%n%t12` pairs, a lone `%n` inserted inside a paragraph, and the `%fs`/`%fm` guard codes around colour 8;
* rendering check: every glyph of colours 8/9 is drawn with the small font, no glyph of any other colour is drawn with the small font, every glyph exists in its font;
* the visible text (all `%` codes, spaces and line ends removed) must equal the 8 px files (only the brf0103 title is allowed to differ); header lines 1-4 and the last line must equal the 8 px files after the size mapping; trailing CR/LF count must equal;
* hand-wrapped lines (objective, `%t9`/`%t12`, first line of a bullet followed by a `%t9` continuation) must not wrap automatically; a `%t` line that wraps automatically is only tolerated as an indented prose paragraph (logical line >= 1.5 panel widths and not a bullet continuation: 1 case, brf0401);
* all original checks: KS X 1001 syllables, `%` before Hangul, `%c` <= 80 bytes, CRLF only + trailing CRLF, 256-byte runs, mid-word and colour-change breaks, centred line width.

Negative tests (`negtest_10px.py`, 15 mutations: 8 px text left over, missing guard code, too long objective/continuation line, changed wording, missing trailing CRLF, bare LF, wrong size after `%fc8`, removed colour code, too wide title, colour-change break, non-KS X 1001 syllable, `%t9`+digit, `%%n`) are all detected.

Caveat: the layouts are tuned for exactly 168 px, like the 8 px files were (at 167 px one prose paragraph in xbrf0203 and at 170 px one in xbrf0302 gets a mid-word / particle-at-line-start break; the 8 px files showed the same sensitivity). The vertical size of the briefing panel at 10 px (about 25 % taller lines, 39 extra objective/bullet lines in total) was not checked in the game.

## Per file

`%fs->%fm` = substitutions (of which the header line); guard = number of `(부 목표)` guard pairs (each is one `%fs` + one `%fm`); items = re-wrapped objective (o) / tactical bullet (t) items; lines = physical lines of those items before -> after; hard = hard `%n` in prose.

| file | `%fs->%fm` | guard | items (o/t) | lines | hard | notes |
|---|---:|---:|---:|---|---:|---|
| brf0101 | 2 (1) | 0 | 1 (1/0) | 2 -> 2 | 0 |  |
| brf0102 | 3 (1) | 0 | 4 (2/2) | 13 -> 14 | 0 |  |
| brf0103 | 3 (1) | 0 | 4 (1/3) | 9 -> 12 | 0 | Title shortened: `***레이븐 메크를 안전지대로 호위***` (184 px) -> `***레이븐 메크 안전지대 호위***` (164 px; only the particles 를/로 dropped). The `50%` in the last tactical line is kept together with its `감소한다` (never break after a literal `%`). |
| brf0104 | 2 (1) | 0 | 3 (0/3) | 20 -> 22 | 0 |  |
| brf0105 | 2 (1) | 0 | 3 (0/3) | 8 -> 9 | 0 |  |
| brf0106 | 2 (1) | 0 | 1 (0/1) | 5 -> 6 | 0 |  |
| brf0201 | 2 (1) | 0 | 1 (0/1) | 4 -> 5 | 0 |  |
| brf0202 | 2 (1) | 0 | 2 (1/1) | 3 -> 5 | 0 |  |
| brf0203 | 2 (1) | 0 | 2 (0/2) | 6 -> 8 | 0 |  |
| brf0204 | 2 (1) | 0 | 1 (0/1) | 2 -> 3 | 0 |  |
| brf0205 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0206 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0301 | 2 (1) | 0 | 2 (1/1) | 4 -> 6 | 0 |  |
| brf0302 | 2 (1) | 0 | 1 (0/1) | 4 -> 4 | 0 |  |
| brf0303 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0304 | 1 (1) | 0 | 1 (1/0) | 1 -> 2 | 0 |  |
| brf0305 | 2 (1) | 0 | 2 (0/2) | 7 -> 8 | 0 | A continuation line must not start with a digit: `%t9` + `1대` would read as `%t91` (tab of 91 px), so `최소 1대` is kept on one line. |
| brf0306 | 2 (1) | 0 | 2 (1/1) | 4 -> 5 | 0 |  |
| brf0401 | 1 (1) | 0 | 0 | - | 0 | The indented prose paragraph (`%fc4%t9지휘관, 이번 건에서 ...`) wraps automatically after its first line; this is the tolerated generic `tab line wraps automatically` note (no mid-word split). It was already present at 8 px. |
| brf0402 | 2 (1) | 0 | 2 (2/0) | 3 -> 5 | 0 |  |
| brf0403 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0404 | 2 (1) | 0 | 0 | - | 0 |  |
| brf0405 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0406 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0501 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0502 | 2 (1) | 0 | 0 | - | 0 |  |
| brf0503 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0504 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0505 | 1 (1) | 0 | 0 | - | 0 |  |
| brf0506 | 1 (1) | 0 | 2 (2/0) | 2 -> 4 | 0 |  |
| xbrf0101 | 1 (1) | 0 | 1 (1/0) | 1 -> 2 | 0 |  |
| xbrf0102 | 4 (1) | 2 | 0 | - | 1 | Two `(부 목표)` lines: `%fc8%fs   (부 목표)` + `%fm` before the next `%fcN` (see item 2 above). Hard `%n` before: `센서` / `통제소가 온전한` (the colour-2 phrase `센서 통제소` is followed by the particle 가 right at the panel edge). |
| xbrf0103 | 1 (1) | 2 | 1 (1/0) | 1 -> 2 | 1 | As xbrf0102 (2 x). Objective 1 and 3 keep the source hand wrap (`%fc2%t9방어 부대를 파괴하라`), they still fit. Hard `%n` before: `클랜 부품 보관고` / `두 곳 주변의`. |
| xbrf0104 | 1 (1) | 1 | 0 | - | 2 | One `(부 목표)` guard pair. Hard `%n` before: `이동 HQ` / `차량을 노획할`; `수리` / `시설 두 곳을`. |
| xbrf0201 | 2 (1) | 5 | 1 (1/0) | 1 -> 2 | 0 | Five `(부 목표)` guard pairs; the `%fc5%fm%c----------` separator after the time limit is `%fm` too (was `%fs`). |
| xbrf0202 | 1 (1) | 2 | 2 (2/0) | 2 -> 4 | 2 | Two `(부 목표)` guard pairs. Hard `%n` before: `스타 캡틴` / `마커스 오시스가`; `노바캣` / `옴니메크가 수송대를`. |
| xbrf0203 | 2 (1) | 0 | 5 (5/0) | 5 -> 10 | 0 |  |
| xbrf0204 | 1 (1) | 2 | 1 (1/0) | 1 -> 2 | 3 | Two `(부 목표)` guard pairs. Hard `%n` before: `기지 동쪽의` / `클랜 HQ에`; `스타 리그 지휘` / `본부에`; `강습급 옴니메크` / `마사카리가`. |
| xbrf0301 | 1 (1) | 0 | 0 | - | 1 | Hard `%n` before: `강습급 옴니메크` / `터키나가`. |
| xbrf0302 | 1 (1) | 0 | 0 | - | 0 |  |
| xbrf0303 | 2 (1) | 0 | 0 | - | 0 |  |
| xbrf0305 | 2 (1) | 0 | 4 (4/0) | 4 -> 8 | 1 | Hard `%n` before: `스타 커널` / `마커스 코타레가`. |
| xsbrf0401 | 1 (1) | 0 | 0 | - | 0 |  |
| xsbrf0402 | 3 (1) | 0 | 0 | - | 1 | Hard `%n` before: `못한다.` / `제자리에 멈춰`. |
| xsbrf0404 | 1 (1) | 0 | 1 (1/0) | 1 -> 2 | 0 |  |
| **total (45)** | **73 (45)** | **14** | **50 (28/22)** | **113 -> 152** | **12** | 1 title shortened |
