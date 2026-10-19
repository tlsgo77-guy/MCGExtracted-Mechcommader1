# TR-B3 notes: Desperate Measures briefings (xbrf0101-0305)

12 files in `localization/ko/briefings/` (UTF-8, CRLF, no BOM, trailing CRLF). `xbrf0304.txt` was skipped because no mission uses it. Validator: `check_briefings.py` in the TR-B3 scratch folder (`kor/tr_b3/`). Result: 0 errors and 0 warnings. The `%` code sequence is identical to the English in every file; no hand-wrap pairs were added.

Note: STYLE.md 4.3.4 says briefings are stored as EUC-KR. As instructed, these files are UTF-8, so the build step must convert them (the validator already checks that every character encodes to a KS X 1001 syllable).

## Per file

| file | title | notes |
|---|---|---|
| xbrf0101 | `***착륙 지대 확보***` | `Component Warehouses (2)` becomes "부품 창고 2곳을 점령하라" (the count is written into the sentence). The source double space in `Extraction  Point` is dropped. |
| xbrf0102 | `***노마드 기지 보호***` | The title uses Protect = 보호; the objectives use Defend = 방어. Two mid-sentence `%n` (after `Local Turret Power`, after `Mad Cat`) were moved to the next sentence boundary. Code order is unchanged. `Local Turret Power Generators` is rendered as "발전기, 즉 현지 포탑 전원 시설". |
| xbrf0103 | `***바이탄 구역 확보***` | Objectives 1/3 keep the source hand wrap (`%fc2%t9방어 부대를 파괴하라`). `Clan Captain` becomes 스타 캡틴 (glossary). The source's stray blank physical line is kept. |
| xbrf0104 | `***오거 기지 제거***` | The `%n` after `Mobile HQ` was moved to the end of that sentence. `Loki Class heavy OmniMech` becomes "중량급 옴니메크 로키" (avoids "로키급 중량급"). |
| xbrf0201 | `***기회 표적***` | Fixed two-digit pitfall: `%fc225 minutes` becomes `%fc225분`. Highlights were reordered inside the sentence (same code sequence). Two hint `%n` moved to sentence ends. The last tactical line ends `%n%n%n` (one extra blank line before END DISPATCH). The alternative was a forced break mid-sentence. |
| xbrf0202 | `***군수품 수송대 노획***` | Objectives: "회수 차량 7대 중 4대를 노획하라" and so on. The `%n` before `Salvage Rigs` and after `Nova Cat` now fall at sentence ends. |
| xbrf0203 | `***궤도포 제거***` | The source says "all six" MOG sites but lists 5 objectives; translated faithfully as 여섯 곳 (decide whether to correct it). `ARTILLERY: 2 Small 1 Large` has a single space in the source; kept as `포격: 소형 2 대형 1`. Objective particles: 1을 / 2를 / 3을 / 4를 / 5를. |
| xbrf0204 | `***적 지휘관 생포***` | Capture used for people becomes 생포 (title, body). `Star League Command building` (tactical notice) is unified to 스타 리그 지휘 본부 (Command Center). Objective 4 `Capture APC` is kept as is, although the text talks about Kulin's Hover Limo. |
| xbrf0301 | `***크라켄 기지 점령***` | `Command Center on Kathil` becomes 캐실의 사령부 (glossary). The `%n` after `HPG Stations` now falls at the sentence end. |
| xbrf0302 | `***증원군 제거***` | The source's 4 hint `%n` were turned into a paragraph break plus 2 sentence-end breaks. `suprise` is translated by meaning. `Patrol of 'Mechs` becomes 메크 순찰대; objective 4 is "메크 3기 순찰대를 제거하라". |
| xbrf0303 | `***단지 완전 파괴***` | Obliterate = 완전 파괴 (glossary). `***25 MINUTE TIME LIMIT***` becomes `***제한 시간 25분***`. `a medium walls` (source typo) becomes 중간 높이의 방벽. |
| xbrf0305 | `***엔진 드릴 파괴***` | The `%n` after `Star Colonel` was moved to the end of the first sentence. Objective 1: "숨겨진 보관고 드릴 알파를 파괴하라". |

## Glossary additions needed

No new proper nouns: every name, place, mech, vehicle and structure in these 12 files is already in `glossary.json`. The common military terms below were not in the glossary. They are used consistently across the 12 files, and the lead may want to fix them:

| en | ko used | where |
|---|---|---|
| strikeforce | 타격대 | xbrf0202, 0203, 0303 |
| target(s) of opportunity | 기회 표적 | xbrf0201 title/body |
| Defenders (objective) | 방어 부대 | xbrf0103, 0302 |
| enemy column(s) | (적) 종대 | xbrf0102 |
| reinforcements / reserve units | 증원군 / 예비 부대 | xbrf0302, 0303 |
| engineering team | 공병대 | xbrf0102 |
| Return Forces to ... | 병력을 ...으로 귀환시켜라 | xbrf0204 obj 2 |
| Capture (a person) | 생포 | xbrf0204, 0301 |
| Move All Units to Extraction Point | 모든 유닛을 철수 지점으로 이동하라 | xbrf0101/0103/0201 |

## Least sure about

1. 기회 표적 vs 임기 표적 (臨機標的, the formal ROK military term) for "targets of opportunity". I chose the transparent form.
2. `Capture Component Warehouses (2)` became "2곳을 점령하라" instead of keeping a literal `(2)`. The in-mission objective names (STYLE 3.3) will keep `(2)`.
3. xbrf0201: the extra blank line before `<<<<전문 끝` (from keeping all three `%n` without breaking a sentence).
4. xbrf0203: "six" sites vs the 5 MOG objectives (kept as in the source).
5. Wording that was adjusted only to avoid line-break bugs (see below), e.g. "정찰대가 클랜의 섀도캣 여러 기를 포착했다", "끝으로 지협 입구를 지키는 노바캣을".

## Engine findings (for the lead)

* **Briefing port width is almost certainly 168 px.** I replayed SMUTI::process/checkWrap on the 48 in-scope English briefings with the real fonts. At exactly W = 168, the English has zero mid-word breaks and zero empty-buffer breaks. Every other width from 164 to 175 has at least one (167: 2 mid-word breaks; 169: 1 empty-buffer break). The developers' mid-sentence `%n` fixes are also best explained at 168-170 (9 of 11 needed at 168). The validator simulates W = 168 by default (`--sweep A B` to try others).
* **checkWrap empty-buffer bug: text can disappear.** When the first character after a `%fc` colour change overflows the line, the pending buffer is empty. The original body at 0x729479 (and the Korean `cw_nospace`, which takes the old path for count < 2) copies `buf[-1]` (byte +0x1f, the zero high byte of the colour index at +0x1c) into `buf[0]`. The rest of that segment then prints as an empty string until the next wrap or flush: the words vanish and leave a gap. It affects any language. At W = 168 the English never triggers it. My first Korean draft triggered it 6 times. All are now rephrased away, but other translators' files could hit it. Suggested patch: for count == 0 in `cw_nospace`, start the new line and leave the buffer unchanged.
* `%tN` is added to both pen x (+0x14) and pending width (+0xc) (0x72927b). Under the strict reading, a `%t9` line has only about W - 18 px for text. The validator uses that strict model.
