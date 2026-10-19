# TR-B1 notes: original-campaign briefings brf0101-0306 (18 files)

Output: `localization/ko/briefings/brf0101.txt` ... `brf0306.txt`, UTF-8 without BOM, CRLF, trailing CRLF count mirrored from the English (brf0101/0105/0201/0304 end with one extra blank line, like the source). STYLE.md 4.3.4 wants EUC-KR in the game files, so the build step still has to convert these (all text is already verified to be EUC-KR clean, see below).

Validator: `check_briefings.py` in the TR-B1 scratchpad folder (`...\scratchpad\kor\tr_b1\`), with negative self-tests in `selftest.py` (17 cases, all pass). Final result: **18 files, 0 errors, 0 warnings**. Every `%` code sequence is identical to the English, with no inserted `%n%t9` pairs. All multibyte units are KS X 1001 Hangul cells (B0-C8). The widest hand-wrapped line is 162 px against the 167 px widest English line (measured with WHITE.FNT ASCII widths, 8 px per Hangul). The widest centred title is 140 px, and the longest physical line is 469 bytes (a brf0204 prose paragraph).

## Per file

| file | title | notes |
|---|---|---|
| brf0101 | `***노동 수용소 해방***` | Redone from the pre-glossary sample, keeping its structure. Terms: 수용소 HQ, 천연가스탑, 주둔지 건물 / 주둔 기지, 센서 프로브, 전술 경고, 전문 끝. ULLER warning reworded to fit 167 px (see "least sure" #1). |
| brf0102 | `***포로 조종사 구출***` | `"prison" barn` -> `"감옥"으로 쓰는 헛간`; `*must*` -> `*반드시*`. The source's last prose sentence has no period, so I added one. |
| brf0103 | `***레이븐 메크를 안전지대로 호위***` | `by 50% ` -> `50% 감소한다` (literal `% ` + space kept). The line was reflowed so `%t9` is never followed by a digit (`%t950` would be read as a 950 px indent). |
| brf0104 | `***클랜 본부 건물***` / `***파괴***` | Two centred lines, as in the STYLE.md example. The 12-line Activation Marker notice is reflowed into the same 12 lines. |
| brf0105 | `**적의 공격으로부터 농장 방어**` | Two asterisks, as in the source. Tactical -> 전술부; minelayer -> 지뢰 부설차. |
| brf0106 | `***카이오 산업 지구***` / `***해방***` | Title split like brf0104. `악명 높은 아코도 하루 대위` / `하루 대위`; LRM-equipped CATAPULT -> `LRM을 장착한 중량급 메크 캐터펄트`. |
| brf0201 | `***요원 구출***` | `쿠리타 DEST(특수부대) 요원`, `에어로스페이스 관측차`, `헌치백 IIC를`. |
| brf0202 | `***적 자산 파괴***` | `Battalion has decided` -> `대대 본부는`; supply caches -> `보급품 은닉처` (노획). |
| brf0203 | `***적 수송대 파괴***` | Wrote `적 수송대` for the convoy so it can't be confused with 대대 수송대 in the same sentence (see the collision below). |
| brf0204 | `***적 자산 파괴***` | `하이퍼펄스 발생기(HPG)`; `a Galaxy or two` -> `갤럭시 한두 개`; the source typo "there is not have much time" is rendered by meaning. Heavy Ultra Autocannon -> `중울트라 오토캐논`. |
| brf0205 | `***적 열차 파괴***` | diversionary action -> `양동 작전`. |
| brf0206 | `***기지 점령 및 방어***` | `OBJECTIVE TIME LIMIT- 06:00` -> `목표 제한 시간- 06:00`; turret control -> `포탑 통제소`. |
| brf0301 | `***적 지휘 부대 파괴***` | The header code `03PRDN02` is kept as it is (the source swaps the numbers of 0301 and 0302). `본즈맨 피오트레프 소령`; geothermal -> `지열 발전기`; "warm welcome" -> `뜨거운 환영` (ironic). |
| brf0302 | `***의료 수송대 호위***` | Header `03PRDN01` kept. `for additional Resource Points` -> `추가 자원 포인트를 획득하라`. |
| brf0303 | `***적 수송대 노획***` | Supply trucks -> 노획 (vehicles). |
| brf0304 | `***재교육 수용소 해방***` | `MISSION TIME LIMIT- 15:00` -> `임무 제한 시간- 15:00`; `마야 협곡`. |
| brf0305 | `***아군 기지 방어***` | `책임 장교`; Repair Bays -> `수리 시설 2곳`; `북쪽/남쪽 포탑 전원`. |
| brf0306 | `***애펀데일 해방***` | `행정 건물`, `센서 통제소`, `센서 단지`, `사무라이 산`. |

## Glossary additions needed (proposals only; glossary.json not edited)

No new proper nouns: every name in these 18 files is already in the glossary. These recurring common terms are not, and other translators will hit them too:

| en | proposed ko | where |
|---|---|---|
| DESTROY ENEMY ASSETS (title) | 적 자산 파괴 | brf0202, brf0204 |
| (enemy) patrol(s) / scouting patrols | 순찰대 / 정찰 순찰대 (정찰대 is taken by "Recon") | brf0104, brf0304 |
| command unit | 지휘 부대 | brf0301 |
| cargo transfer post | 화물 환적소 | brf0103 |
| sensor grid | 센서망 | brf0306 |
| staging center | 집결 거점 | brf0305 |
| Battalion tactical analysis | 대대 전술 분석 | brf0205 |
| intelligence analysts | 정보 분석관 | brf0204 |
| interstellar communique | 성간 통신문 | brf0204 |
| medical convoy | 의료 수송대 | brf0302 |
| spies | 첩보원 | brf0303 |
| Guard (objective "Camp Beta HQ and Guard") | 경비대 | brf0101 |

**Glossary collision:** `Battalion Transport` = 대대 수송대 and `convoy` = 수송대 clash when both appear in one sentence (brf0203). I wrote `적 수송대` for the convoy. The lead may want to change Battalion Transport to 대대 수송기 (the pre-glossary sample used this) or note the 적 workaround.

## Choices I was least sure about

1. brf0101: `Clan ULLER OmniMech reported in area.` -> `*클랜 울러 옴니메크도 이 지역에 출현했다.` The literal "...보고되었다" is 170 px, over the 167 px limit. I chose rewording over inserting a `%n%t9` wrap pair. Inserting the pair is the alternative if the lead prefers the exact wording.
2. brf0103 title `레이븐 메크를 안전지대로 호위` (140 px, the widest title). A shorter option is `레이븐 메크 호위`.
3. 배치 appears only for enemy forces "stationed/entrenched" (brf0106, brf0201, brf0205), never for the player's Deploy (출격). I'm flagging it so a grep for leftover 배치 doesn't raise a false alarm.
4. Second person: I avoided 귀관. Sentences are subjectless imperatives, or use `지휘관의 부대` (brf0305) and `지휘관이 선발한 타격 부대` (brf0206, "your select strike force").
5. brf0102 `burn through the forest` -> `숲을 뚫고 나아가`. In MCG trees really can be burned, so `숲을 불태우며 돌파해` is the literal alternative.
6. brf0301 `a minute or two` -> `1, 2분`. `~` is banned and `1-2분` looked like a range code.
7. brf0204 `Heavy Ultra Autocannons` (on Bondsman Hunchback IICs) -> `중울트라 오토캐논`, without the 클랜 prefix the compbas name 클랜 중울트라 오토캐논 carries.
8. brf0203 `jump over or across` -> `뛰어넘거나 건너뛸 수 있다`. The two verbs are close; a single verb would also do.
