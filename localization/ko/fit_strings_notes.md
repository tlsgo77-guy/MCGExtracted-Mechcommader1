# TR-F notes: FIT/CSV strings and pilot rosters

Outputs:
* `fit_strings.json`: 478 entries `{file, section, key, en, ko}`, the same file/section/key as `en/fit_strings.json`
* `pilots.json`: 41 pilots, `{name, callsign, callsign_en, source[, alt_callsigns]}`

Build and check scripts are in the session scratchpad (`kor/tr_f/build_tr_f.py`, `kor/tr_f/validate_tr_f.py`). The last validation run had 0 errors and 2 warnings. Both warnings are the dev callsigns listed under "Glossary additions needed" below.

## Counts per category

| category | entries | note |
|---|---:|---|
| mission objective name | 166 | original 102, expansion 46, solo 18. Multiplayer (94) and dev/test (11: E3_*, MISE303, testmis1) skipped |
| mech panel heading / location / damage state (MECHTEXT.FIT) | 49 | glossary `mech_locations` verbatim |
| mech repair diagram box label (MECHREP.FIT) | 8 | glossary `mech_locations` verbatim |
| component name (compbas.csv) | 129 | glossary `weapons_components` verbatim |
| component abbreviation (compbas.csv) | 100 | glossary `weapons_components` verbatim |
| pilot name (war*.fit) | 13 | glossary `pilots` |
| pilot callsign (war*.fit) | 13 | glossary `pilots`. 2 come from glossary notes (see below) |
| command-palette tooltip (Menus.fit) | 0 | skipped (in-mission) |
| **total** | **478** | 402 unique English texts |

The objectives cover 126 unique English texts. Identical English always gets identical Korean (checked). Different English with the same meaning also shares one Korean text, for example `Move All Units...` / `Get All Units...` and `Destroy All Enemy 'Mechs` / `...Mechs`.

`pilots.json` covers:
* 4 from START0 (Hawk, Lynx, Hunter, Beast) and 6 from XSTART0 (Siren, Rooster, Spice, Baron, Thunder, Goblin), read from the warrior packets
* the 11 war*.fit developer pilots
* the other 20 hireable player MechWarriors (see Scope 1)

## Labels I had to shorten

None. Every glossary value fits.

* **MECHREP boxes** are wider than the brief assumed. `TextW` in MECHREP.FIT is Head 79, CT 97, LT/RT 135, LA/RA 113, LL/RL 72 px. The widest Korean label is `오른쪽 몸통` (11 B, 44 px at 8 px, box 135 px). Each label is narrower than its English source.
* **MECHTEXT and MECHREP bytes and widths** (EUC-KR bytes; px = Korean 8 px WHITE.FNT, English px = MISC.FST/WHITE.FNT):

| label | ko | bytes | en px -> ko px |
|---|---|---:|---|
| Name / Tonnage | 이름 / 톤수 | 4 / 4 | 19 -> 16 / 30 -> 16 |
| Top Speed / Normal Speed / Jump Range | 최고 속도 / 일반 속도 / 점프 거리 | 9 each | 39 / 51 / 43 -> 36 |
| Armor / Heat Sinks / Location | 장갑 / 방열기 / 부위 | 4 / 6 / 4 | 24 -> 16 / 40 -> 24 / 31 -> 16 |
| Internal / Structure / Rear | 내부 / 구조 / 후면 | 4 each | 29 / 37 / 17 -> 16 |
| Weapon / Recycle / Status / Ammo | 무기 / 재장전 / 상태 / 탄약 | 4 / 6 / 4 / 4 | 26 -> 16 / 28 -> 24 / 25 -> 16 / 22 -> 16 |
| Fatigue / Morale / Wounds / Time | 피로 / 사기 / 부상 / 시간 | 4 each | 27 / 25 / 26 / 18 -> 16 |
| Effectiveness / Current Orders | 전투 효율 / 현재 명령 | 9 / 9 | 51 / 58 -> 36 |
| Head / Center Torso / Left Torso / Right Torso | 머리 / 중앙 몸통 / 왼쪽 몸통 / 오른쪽 몸통 | 4 / 9 / 9 / 11 | 17 -> 16 / 51 -> 36 / 43 -> 36 / 45 -> 44 |
| Left Arm / Right Arm / Left Leg / Right Leg | 왼팔 / 오른팔 / 왼다리 / 오른다리 | 4 / 6 / 6 / 8 | 37 -> 16 / 39 -> 24 / 34 -> 24 / 36 -> 32 |
| HEAD / CTORSO / LTORSO / RTORSO | (same Korean as above) | 4 / 9 / 9 / 11 | 21 -> 16 / **31 -> 36 / 31 -> 36 / 31 -> 44** |
| LARM / RARM / LLEG / RLEG | 왼팔 / 오른팔 / 왼다리 / 오른다리 | 4 / 6 / 6 / 8 | 22 -> 16 / **22 -> 24 / 20 -> 24 / 20 -> 32** |
| HD CT LT RT LA RA LL RL | unchanged (Latin) | 2 each | 10-11 |
| No Damage / Partial Damage / Destroyed / Disabled | 손상 없음 / 부분 손상 / 파괴됨 / 작동 불능 | 9 / 9 / 6 / 9 | 40 -> 36 / 57 -> 36 / 37 -> 24 / **30 -> 36** |

* **Risk:** the upper-case `BodyLocations` set is wider than its compact English, by up to 13 px for `RTORSO`. `Disabled` is 6 px wider. I could not find where these strings are drawn. If they turn out to sit in a narrow slot, a fallback is 중앙/왼몸통/오른몸통 or the Latin HD/CT/... abbreviations. That fallback would be a glossary change, so the lead decides.
* **compbas abbreviations:** every Korean abbreviation is at most the English bytes + 4. The tightest are +3: `U-Lt.AC Ammo` -> `경울트라AC 탄약` (12 -> 15 B), `Tbolt Ammo` -> `선더볼트 탄약` (10 -> 13), `Tbolt` -> `선더볼트` (5 -> 8). The widest in pixels is `Tbolt` -> `선더볼트` (21 -> 32 px). No glossary abbreviation had to be flagged as over budget.

## Longest values (EUC-KR bytes)

* Objectives: 35 B `야포와 모든 유닛을 지정 위치로 이동` (MIS0505; the English is 42 B). Only three objective texts are not shorter than their English: `Destroy Ace Madcat` (18 -> 18 B), `Kill Ace Cougar` (15 -> 16) and `Defend both farms` (17 -> 18).
* compbas: 25 B `클랜 스트릭 SRM/2 탄약 팩`
* MECHTEXT and MECHREP: 11 B `오른쪽 몸통`
* war*.fit and pilots.json: 15 B `에이미 바이오스`

## Scope decisions (please confirm)

1. **The hireable pilots are PMW00051-00080, not war*.fit.** `purchase*.fit` lists `pmw00051`...`pmw00080` as `[WarriorN] Profile`. The war*.fit files are developer test pilots: they are not referenced by any campaign or solo mission, and STYLE.md §5 lists them as out of scope. I translated war*.fit as the brief asked.
   * I added all 30 player MechWarriors to `pilots.json`, using the glossary values verbatim and recording the file in `source`.
   * I kept the PMW `Name`/`Callsign` entries out of `fit_strings.json`, as the brief asked ("skip PMW*").
   * Those names do appear on the pre-mission hire/roster screens. If PMW00051-80 (and their expansion copies PMW00086-109) should be patched as well, they can be generated from `pilots.json` by matching `Name`.
2. **Unreferenced mission FITs are included,** because they match `MIS*` and the inventory tags them `original`. `mechcmdr1.fit` only plays mis0101-0507, and mis0506 is not among them: operation 5 mission 6 is mis0507, which uses brf0506. The included but unreferenced files are:
   * MIS0101c/n/s
   * the 13 MIS0403c*/s*/mp variants
   * MIS0506 (`Placeholder` -> `임시 목표`, which is probably never shown, contrary to STYLE 3.3)
   * MIS0801 (a dev mission, according to the glossary)
3. **Developer callsigns per file:** Glenn Doren is BITMAN in war002 and CENTURION in war002a. Frank Savage is BUNG in WAR003 and COMMANDO in WAR003a. `fit_strings.json` has the right callsign for each file. In `pilots.json` the first callsign is `callsign` and the second is in `alt_callsigns`.

## Uncertain choices

* **Counts in brackets.** STYLE 3.3 says to keep `(2)` as is, so I wrote `부품 창고 (2) 점령`, `부품 보관고 (2) 점령` and `연구 단지 (2) 파괴`. The glossary rewrites `Protect All Base Turret Controls (3)` as `기지 포탑 통제탑 3곳 보호`. I used that verbatim, so the two styles are mixed. Suggestion: pick one, e.g. `부품 창고 2곳 점령`.
* `Destroy Major's Star` -> `소령의 스타 파괴` is literal. The briefing names the officer (Major Piotrev), so `피오트레프 소령의 스타 파괴` (26 B) would be clearer.
* `Kill Ace Cougar` -> `에이스 쿠거 격파`. "Kill" is not in the verb table. I used 격파, the results-screen word for Kills; 제거 is the alternative.
* **Forces:** `Enemy Forces` -> `적 병력`, but `Return/Get forces to extraction point` -> `부대를 철수 지점으로 귀환/이동`.
* `Defenders` -> `수비대`, `Guard` (MIS0101 `Camp Beta HQ and Guard`) -> `경비대`, `Three 'Mech Patrol` -> `메크 3기 순찰대`.
* `Activate abandoned Base` -> `버려진 기지 활성화` (following 활성화 표지). `Perimeter Turrets` -> `외곽 포탑`.
* `Move Artillery and all units into Position` -> `야포와 모든 유닛을 지정 위치로 이동`. The glossary says artillery pieces are 야포, and the briefing names a ridge-top position.
* `One Mobile Artillery Must Survive` -> `자주포 1대 이상 생존`. `Capture 7 of 7 Salvage Rigs` -> `회수 차량 7대 중 7대 노획` keeps the same pattern as the 4-of-7 and 6-of-7 objectives.
* **Particles in objective names.** Where a destination is needed, the name keeps a particle and still ends in a noun, e.g. `APC를 철수 지점까지 호위` and `모든 유닛을 철수 지점으로 이동`.
* **Source typos** are translated by meaning: `Destory` -> 파괴, `Defense Allied ...` -> 방어.

## Glossary additions needed (glossary.json not edited)

* `pilots`:
  * `CENTURION` -> `센추리온` (war002a callsign)
  * `COMMANDO` -> `코만도` (WAR003a callsign)
  * Both currently exist only inside the notes of Glenn Doren and Frank Savage, which is why the validator warns.
* `structures_objectives` or objective vocabulary:
  * `Defenders` 수비대, `Guard` 경비대, `Patrol` 순찰대
  * `Perimeter` 외곽, `Abandoned` 버려진
  * `Kill` 격파, `Activate` 활성화, `Complete (objectives)` 완수, `Survive` 생존, `Return` 귀환
  * `Freed Prisoners` 석방된 포로, `Enemy Forces` 적 병력
* An objective-name pattern for `X of Y` (`Y대 중 X대`) and for bracketed counts (see the first uncertain choice).
