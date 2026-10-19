# TR-B2 briefing notes (brf0401-0406, brf0501-0506, xsbrf0401/0402/0404)

15 files in `localization/ko/briefings/` (UTF-8, no BOM, CRLF; trailing CRLF count mirrors the English file).
STYLE.md 4.3-4 says the game file itself is EUC-KR, so the build step has to convert them.
Validator: `scratchpad/kor/tr_b2/check_briefings.py`. All 15 files pass with 0 errors and 0 warnings.
The `%` code sequence of every file matches the English in count and order, with no wrap pairs added.
The widest single-row line is 155 px (limit 167), and no `%t` line has more than 20 Hangul.

## Per file

| file | title | notes |
|---|---|---|
| brf0401 | `***마사카리 노획***` / `****궤도포 파괴***` | Kept the source's unbalanced asterisks (4/3). Colonel Reese's letter is in 해라체 with a little voice. `발신: 리스 대령`. The END line has 5 `<`. Guns are counted with 문 (두 문). |
| brf0402 | `***클랜 보급 차단***` | END line is `>>>전문 끝%n%n` (the source uses `>>>` and a trailing `%n%n`). The 4-line TACTICAL NOTICE is rewrapped in the same 4 lines. |
| brf0403 | `***클랜 야전 기지 점령***` | `Towers (3)` became `3곳` (glossary example "기지 포탑 통제탑 3곳 보호"). `insure` is a source typo, translated as meant. |
| brf0404 | `***산업 시설 점령***` | The 7-line TACTICAL NOTICE keeps 7 lines; "Be advised" became a closing `...에 유의하라.` |
| brf0405 | `***적 부대 요격***` | "Orbital Reconnaissance" became 궤도 정찰대. |
| brf0406 | `***스모크 재규어***` / `***궤도포 파괴***` | Korean word order is spread over the two centred lines (STYLE 4.3-6 pattern). |
| brf0501 | `***아군 지휘관 구출***` | `정예 바이너리(2개 스타)` as in the glossary. "Allied Captain" is 아군 대위. |
| brf0502 | `***클랜 세력 섬멸***` | `(8)` became `8기`. `moral blow` (typo) is 사기. "Smoke Jaguar commanders" became 지휘부, so 지휘관 stays reserved for the player. |
| brf0503 | `***보조 전력 시설 파괴***` | Header code `05PRDN05` kept although the file is 0503. END line `<<<< 전문 끝` keeps the space. |
| brf0504 | `***연료 저장소***` / `***점령 및 방어***` | Glossary title split over the two lines. The source's `- ` dash, `...` and the stray space after the last `%n%n` are kept. |
| brf0505 | `***아군 야포 배치***` | "a lance of mobile artillery" became 자주포 1개 랜스 (glossary). Later "artillery pieces" became 야포 (glossary game_terms). See the uncertain choices. |
| brf0506 | `***스타베이스 점령***` | The body says six guns but the objectives list three. Kept as in the source (여섯 문). NW/NE became 북서쪽/북동쪽. |
| xsbrf0401 | `***모든 에이스 파괴***` | Clan voice. `임무 난이도: 어려움`. "Madcat J" became 매드캣 J. Long Toms became 롱 톰. Single spaces replace the source's double spaces after periods. |
| xsbrf0402 | `***주둔군 파괴***` | Header `FEDCOM:SOLO/04PRDN02` kept (not STARCOM). The red `%fc1` clause and the white `%fc6` highlight keep their spans. The source has a mid-sentence `%n` after "current position". The Korean breaks at the clause boundary instead (`...%fc6제자리%fc2에 멈춰 서서 사격해야%n자주포의 위력을...`). |
| xsbrf0404 | `***포트 아서 리덕스***` | Clan voice (`흐음, 데자뷔로군.`, `알겠나, 지휘관?`). "IS dogs" became IS 개들. Source typos `of of` and `holes up` are translated as meant. "Take out" in the body became 제거하라. |

## Glossary additions needed

No new proper nouns. Every name was already in glossary.json: Kylemartin, Cambridge, Bellum, Chresbute, Weisman, Lambert Valley, Miasota Basin, Rehold Mountains, X-Ray Company, Firestorm, Wolf-Clan-In-Exile, Jade Falcon, Long Tom, Thor and the rest.

These common terms came up and are worth fixing for the other teams, especially the objective-name team:

| en | proposed ko | where |
|---|---|---|
| perimeter turrets | 외곽 포탑 | brf0506 objective 1 (the in-mission objective name needs the same word) |
| outer turret defense ring | 외곽 포탑 방어망 | brf0506 |
| Secondary Power (title) | 보조 전력 (시설) | brf0503 |
| power station | 발전소 (different from Power Complex 발전 단지 and generator 발전기) | brf0503 |
| sensor grid | 센서망 (TR-B1 uses it too) | brf0503 |
| Orbital Reconnaissance | 궤도 정찰대 | brf0405 |
| stealth drop / airdrop / drop point | 은밀 강하 / 공중 투하 / 투하 지점 | brf0401 |
| cargo plane / cargo (ships) | 화물기 / 화물선 | brf0401, brf0406 |
| relief force | 구원 부대 | brf0501 |
| fixed artillery emplacements | 고정 포대 | xsbrf0402 |
| Scouts | 정찰병 | xsbrf0402 |
| quadrant | 사분면 | xsbrf0401, xsbrf0404 |
| facility (title) | 시설 | brf0404 |
| counter for guns | 문 (궤도포 두 문/여섯 문, 롱 톰 포 1문) | STYLE 2.7 has no counter for guns |

## Choices I was least sure about

1. **야포 vs 자주포 in brf0505.** The glossary gives 'artillery pieces' -> 야포, so the title and objective say 야포. These units are the 자주포 (Mobile Artillery) the player sees on the plates, so a player may think they are different units. The alternative is 자주포 throughout (`***아군 자주포 배치***`, `2-자주포를 포함한 모든 부대를`).
2. **perimeter -> 외곽.** The alternative 경계 포탑 would match Perimeter Alarm = 경계 경보기, but 경계 also means "alert", so I chose 외곽.
3. **Counter 문 for orbital guns.** The alternatives are 기 or 곳.
4. **brf0503 title.** `보조 전력 시설 파괴` adds 시설. The literal `보조 전력 파괴` reads oddly.
5. **xsbrf0402 objective 2.** "One Mobile Artillery Must Survive" became the imperative `자주포를 1대 이상 생존시켜라` (STYLE 4.1). It could also be `적어도 자주포 1대는 지켜 내라`.
6. **Clan-voice register (xsbrf0401/0404).** It is mostly 해라체, with 하게체 `알겠나` and `-로군` for flavour, which STYLE 4.1 allows. Check that this is not too much.
7. **brf0401 asterisks.** `****궤도포 파괴***` keeps the source's 4/3 imbalance. It could be normalised to `***`.
8. **"Destroy All Enemy Forces" (brf0404, brf0504).** I used `모든 적 부대를 파괴하라`, following the glossary verb, instead of 섬멸.
9. **Addressing the player.** I used 지휘관 or a 아군/지휘관의 rewording and never 귀관. "Reese's" 우리 is kept in his letter.
