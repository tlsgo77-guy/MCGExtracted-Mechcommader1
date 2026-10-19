# strings.json (ko) translator notes: TR-S, pre-mission EXE strings

Scope: 248 ids. That is the 245 `scope == "pre-mission"` entries minus the 5 identifiers (890, 891, 892, 902, 903, left out so they fall back to the EXE text), plus the in-mission copies 130-137. 1256 is already pre-mission. Ids 1228 and 1248 (unreferenced vehicles, scope in-mission) are not included.

Validation: `tools/build_strings_bin.py` builds 248 strings (6188 bytes) with no warnings. The extra check passes with 0 errors: byte limits (79-82/100-102/130-133 ≤ 14, 110 ≤ 29, names ≤ 39, others ≤ 253), identical printf sequences, `\n` count, edge spaces, end punctuation, KS X 1001 syllables only.

## Shared-meaning / ambiguous ids

| id | en | ko | why |
|---|---|---|---|
| 79 / 81 | Light / Heavy | 경량 / 중량 | Glossary. One string serves both the weight class and the damage/armor scale (초경량 < 경량 < 보통 < 중량 < 초중량). 130/132 are the same. |
| 80 | Medium | 중간 | Glossary. One string serves weight, weapon range (also in-mission TacticalMap::drawWeapons) and the speed scale (매우 빠름 / 빠름 / 중간 / 느림 / 매우 느림). 131 is the same. |
| 85 / 109 | Short / Long | 단거리 / 장거리 | Range scale, also in-mission. 86 is 초단거리. |
| 101 | Moderate | 보통 | Glossary. The PREFS difficulty REGULAR is also 보통 (art), but the two never share a screen. |
| 108 | N/A | 없음 | Glossary (field value, e.g. jump range of a mech without jump jets). If it ever reads oddly, 해당 없음 (8 bytes) is the fallback. |
| 897 | `<empty>` | `<비어 있음>` | Glossary (empty save slot). Angle brackets kept. |
| 901 | U | U | Kept as Latin "U" (glossary + STYLE 5). The note in en/strings.json says it is a printf format drawn in place of the quantity for unlimited purchase items. strings_summary.md also says 900/901 are written to the registry. Keeping "U" is safe either way. If the in-game check confirms "unlimited", candidates are 무한 (4 bytes) or 무제한 (6 bytes), but the slot is one character wide in English. |
| 647 | MechWarrior | 메크워리어 | Glossary. Pilot-inventory column label (40 px at 8 px). |
| 182 / 183 | Friendly / Enemy | 아군 / 적군 | Glossary (results-screen column labels). 적군, not 적, so the pair reads as matching labels. |
| 110 | Tons | 톤 | Glossary (2 bytes of 29). |
| 893 | `Inventory: ` | `보유: ` | Glossary. Trailing space kept. |

## Choices worth a second look

- **32**: STYLE 3.1 gives "대기 구역에서 유닛을 이곳으로 끌어다 놓습니다." but the glossary (higher priority) fixes Ready Area as 출격 대기 구역 for ids 32/49/67/71/645. So I wrote "출격 대기 구역에서 ...". The STYLE example probably predates that decision and may need updating.
- **52 / 54 / 63 / 98** use 제거, as the glossary note lists these ids. In 54 (removing a pilot from a mech) and 52 (taking a vehicle back out of the ready area), 배정 해제 / 제외 would read more naturally. I followed the glossary. 95 uses 제외 per glossary.
- **36 / 30 / 46**: when the player moves a unit, the verb takes the causative form: 출격시킵니다, 전출시킵니다. 33 and 34 use the glossary phrase 임무에 투입.
- **55 / 56 / 62** are noun phrases with a final period (exact glossary text; the source also ends with '.').
- **84** ends with ':' like the source ("다음 부품은 교체할 수 없습니다:").
- **882** is the exact STYLE text. 883 and 884 follow the same pattern (`%d대`, so no particle comes right after a placeholder). The source's double spaces after a period are not reproduced.
- **1256** uses ~해 주십시오 (STYLE 3.1): "메크커맨더 확장팩 CD를 CD-ROM 드라이브에 넣어 주십시오."
- **Mech names 700-771** are glossary chassis + space + A/W/J (e.g. 헌치백 IIC J). 772-783 are the glossary ace names (X의 Y). Vehicles 1200-1255 are glossary `vehicles`, used verbatim.

## Width (8 px Korean WHITE.FNT vs English WHITE.FNT)

Nothing exceeds a byte limit. The widest help-line tooltips are 49 (260 px vs 211 px English), 67 (222 px), 32 (202 px) and 64 (202 px). Short tooltips such as 48 and 38 run 1.4-1.5x the English, but stay under 150 px. I could not confirm the width of the help-line box. If 49 gets clipped there, a shorter version is "출격 대기 구역으로 끌어다 놓아 조종사 배정/수리/재무장을 합니다." That shortening is not applied because STYLE prefers commas. Widest names: 에어로스페이스 관측차 84 px, 오시스의 마사카리 68 px.

## Could not fit

None.

## Glossary additions needed

These are general words with no glossary entry. My proposed ko is what I used:

| en | proposed ko | used in |
|---|---|---|
| Expansion (MechCommander Expansion) | 확장팩 | 1256 (the glossary only has it inside the Campaign note) |
| forces | 부대 | 30 |
| video | 영상 | 38 (consistent with Opening Cinema = 오프닝 영상) |
| replace (components) | 교체 | 57, 84 |
| systems | 시스템 | 58 |
| pilot's picture | 조종사 사진 | 53, 54 |
| item (purchase) | 품목 | 77 (taken from the STYLE example) |
| scroll | 스크롤 | 47 |
| insufficient room | 공간이 부족 | 99 |
| maximum | 최대 / 최대치 | 882-884 |
