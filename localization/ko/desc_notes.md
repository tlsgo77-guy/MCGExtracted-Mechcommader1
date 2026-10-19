# desc.fit translation notes (TR-D)

Output: `fit_strings_desc.json`, with all 217 `DescString` entries of `MISC.FST/desc.fit` (the ones `en/fit_strings.json` lists).

| group | sections | entries |
|---|---|---:|
| components (IS + Clan) | Desc13-161 | 61 (11 of them placeholders) |
| pilot bios | Desc301-350 | 49 |
| 'Mech variants A/W/J | Desc400-471 | 72 |
| ace 'Mechs | Desc472-483 | 10 |
| vehicles | Desc500-555 | 25 |

Style: descriptions use written declarative prose (~한다/~이다, STYLE 4.1). Bios keep the source's imperatives (`Don't let the name fool you` -> `이름에 속지 마라.`), and vehicle warnings keep theirs (`Beware!` -> `주의하라!`). Every `fixed_phrases` and `briefing_terms` sentence is reused word for word.

## Validation

Script: `scratchpad/kor/tr_d/validate_desc.py` (log in `validation_output.txt` next to it). Its negative self-test (`selftest_validator.py`) feeds it 똠, kana, `"`, `·`, `…`, jamo, an extra `%n`, `%` before Hangul, a changed number, a broken fixed phrase and an over-long entry, and it flags all 10.

* Every value is printable ASCII plus KS X 1001 Hangul syllables only. After EUC-KR encoding, each multibyte unit has a lead byte of 0xB0-0xC8 and none is an A4D4 jamo sequence.
* The `%` code sequence matches the English in every entry: 77 codes in total, 27 `%n` and 50 `%fc8`. The spaces around the codes and before the `LOAD VAL` label match too, and the `%fc8  N.N` tail is byte-identical.
* No `"`, CR, LF, TAB or `~` appears in any value. `%` is never followed directly by a multibyte byte.
* Every number in each entry (ranges, shots, load values, 8 points, 50m, 25-ton, AC/5, AC/20) appears in the Korean the same number of times.
* Result: **0 errors, 3 warnings**. The warnings are the `ACE` length exception below.
* Total size: en 29,045 bytes, ko 23,899 bytes (ratio 0.82). The highest ratio is Desc308 at 1.10, and every entry is far below 900 bytes.

### Longest 5 (Korean bytes)

| section | ko bytes | en bytes | ratio |
|---|---:|---:|---:|
| Desc15 (Sensor - Advanced) | 172 | 177 | 0.97 |
| Desc471 (Turkina J) | 167 | 178 | 0.94 |
| Desc37 (Beagle Probe) | 161 | 165 | 0.98 |
| Desc126 (Heavy Thunderbolt) | 161 | 179 | 0.90 |
| Desc17 (C Sensor - Adv) | 159 | 173 | 0.92 |

## Placeholder entries

* **Desc105, 106, 114, 115, 121, 122, 124, 131, 132, 134, 136** (`IF YOU SEE THIS DESCRIPTION PLEASE REPORT IT AS A BUG--- <name>`): these use `이 부품에 대한 설명이 아직 준비되지 않았습니다.` as the lead instructed. The English has no `%` codes here, so the Korean has none either. **Conflict:** `glossary.json` fixed_phrases and STYLE 4.4 still give `(설명 없음) 기관총` / `(설명 없음) <부품명>`. Please update both so `check_glossary.py` and later translators agree. This one sentence is in ~합니다 form (a system notice), while the rest of desc.fit is ~한다.
* **Desc500, 501** (`CUT FROM MULTIPLAYER. IF YOU SEE THIS, REPORT IT AS A BUG!`, APC and Armored Car): these use the glossary's fixed `(멀티플레이 전용 - 사용되지 않음)`. They are vehicles, so the "이 부품..." sentence would be wrong. If the lead prefers one neutral notice everywhere, `이 차량에 대한 설명이 아직 준비되지 않았습니다.` (47 bytes, within 1.3x) would fit.
* **Desc481-483** (`ACE`): these use `에이스` (glossary pilots `ACE`). That is 6 bytes against 3, so above 1.3x. No Korean word fits in 3.9 bytes, and the space is a description box, so this is a documented exception.

## Terminology I was unsure about (decisions taken, please confirm)

| English | Korean used | where / why |
|---|---|---|
| Inner Sphere version / IS version / Clan version | 이너 스피어판 / IS판 / 클랜판 | Clan components 110-155, 424-426. Not in the glossary |
| IS Sensors (basic), IS Basic Sensors | IS 센서, IS 기본형 센서 | 13, 16. Grade words follow the compbas names (기본형/중급형/고급형, Clan 표준형/확장형) |
| active enemy units | 가동 중인 적 유닛 | the opposite of "powered down" (전원이 차단된) |
| extended-range (prose) | 확장 사거리 / 확장 사거리형 | per the glossary `ER` note |
| recycle rate / recycle time | 재장전 속도 / 재장전 시간 | glossary Recycle = 재장전 |
| slug / shotgun-like round / fragmenting round | 탄체 / 산탄총 같은 탄, 산탄 / 분열탄 | gauss, LB-X |
| high-explosive shells / salvo | 고폭탄 / 일제 사격 | 101, 102 |
| particle bolts / energy bolt | 입자탄 / 에너지탄 | 145, 146 |
| cannot arm itself at targets within 50m | 50m 이내의 목표에는 신관이 작동하지 않는다 | 126 |
| 8 points of damage | 8포인트의 피해 | 160 |
| 'Mech mounted artillery piece | 메크 탑재형 야포 | 161 (glossary: artillery pieces = 야포) |
| second-line fire support 'Mech | 후방 화력 지원 메크 | 406-408. 2선 would add a digit that is not in the source |
| heavy scout | 중량급 정찰기 | glossary. Reads oddly for the Cougar (a light 'Mech described as a "heavy scout"), but I followed the glossary |
| workhorse design | 든든한 기체 | 451-453 |
| missile boat | 미사일 차량 | 506, 515 |
| heavy-strike tank (Rommel) | 강타 전차 | 511 |
| strafing runs | 훑고 지나가며 공격 | 504 |
| aerospace corps / aerospace jockeying | 항공우주군 / 항공우주기를 몰던 | 322, 350 |
| Davion military / Inner Sphere forces | 다비온군 / 이너 스피어군 | 320, 321, 328 |
| picket duty | 초계 임무 | 340 |
| veteran (prose, not the rank) | 베테랑 | 327, 340 (allowed by the glossary note). `green MechWarrior` (339) is 신참 메크워리어 |
| Elite warriors (Masakari) | 정예 전사 | 436-438 |
| Vulture class heavy OmniMech | 중량급 옴니메크 벌처 | 472-479: avoids the stacked "벌처급 중량급" |
| Countess / Baron | 누나 / 남동생 | 310 and 318: 318 says "her younger brother Baron" |
| Fiend is anything but | 핀드는 전혀 악마 같은 사람이 아니다 | spells out the pun, because 핀드 means nothing to a Korean reader |
| Also known as the AC/20 | 일명 AC/20인 | avoids a particle whose form depends on how "20" is read (이십/트웬티). AC/5 reads with a vowel ending either way, so 라고도 is used there |
| Command it like the Refit Truck | 조작법은 정비 트럭과 같다 | 555 |

Source typos are translated by their meaning (STYLE 4.3 rule 11). Examples: `know and feared` (442-444), `insure` (321), `intention or pursuing` (336), `aeropspace` (350), `Draonic Combine` (346, glossary 드라코니스 연맹), and `short-range combat` with its noun missing (504, rendered as 전투 차량). `Alacorn MKIV` (554) keeps the source mark, per the glossary. The small differences between variants are mirrored: 447 drops "Clan" and 450 drops "mostly". The leading space of 465 and 506 is kept, and so are the two trailing spaces of 348.

## Glossary additions needed (glossary.json was not edited)

1. **Pilot callsigns missing from `pilots`**, used in desc332-342 (bios beyond the 30 plate pilots). Proposed forms: Boomer 부머, Detox 디톡스, Ghost 고스트, Needle 니들, Pyro 파이로, Sponge 스펀지, Squid 스퀴드, Toad 토드, Vandal 밴덜, Wasp 와스프. Two more are not named in any translated text: Jinx 징크스 (desc335) and Apollo 아폴로 (desc331). Note that 토드 (Toad) sounds the same as the dev pilot 토드 라본테 (Todd); they are different people.
2. `fixed_phrases`: replace the placeholder ko `(설명 없음) 기관총` with `이 부품에 대한 설명이 아직 준비되지 않았습니다.` (lead decision), and update STYLE 4.4 to match.
3. Optional prose terms worth fixing for other translators: 이너 스피어판 / IS판 / 클랜판, 가동 중인 (active), 탄체 (slug), 분열탄, 고폭탄, 일제 사격 (salvo), 재장전 속도 (recycle rate), 신관 (arming), 후방 (second-line), 항공우주군 (aerospace corps), 다비온군, 초계 임무 (picket duty).

## Sections not covered (not in en/fit_strings.json)

`Desc331`, `Desc475` and `Desc480` exist in desc.fit, but their quoting is broken there: 331 and 475 have a raw line break inside the string, and 480 has no opening quote. The extractor therefore skipped them. If the lead wants them handled, these are ready-made drafts (checked as valid KS X 1001, 117 / 94 / 6 bytes):

* Desc331 (Apollo): `아폴로는 완벽한 메크워리어가 되려고 애쓴다. 그는 다른 어떤 조종사보다 재훈련과 조종석 영상 검토에 많은 시간을 쏟는다.`
* Desc475 (Marcus Kotare's Turkina): `스타 커널 마커스 코타레는 점프젯, 레일건, 롱 톰 포를 장착한 강습급 옴니메크 터키나를 지휘한다.`
* Desc480 (Kim's Masakari): `에이스`
