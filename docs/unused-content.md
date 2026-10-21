# MechCommander Gold / Desperate Measures 미사용·삭제·플레이스홀더 콘텐츠 조사

작성일 2026-10-22. 대상은 `MISSION.FST`, `MISC.FST`, `TERRAIN.FST`, `SHAPES.FST` 추출본과 `game-source/extracted/MCX`의 `DATA`(OBJECT2.PAK, 세이브 템플릿, 영상, 사운드), `MCX.EXE` 문자열이다. 모두 읽기 전용으로 조사했고 게임 파일은 수정하지 않았다(게임 실행 없음, 커밋 없음). 같은 사실의 구조화 데이터는 `docs/unused-content.json`에 있다.

조사 방법: FIT 파서로 모든 미션·프로필·구매 목록을 읽고, 교차 참조(캠페인 파일 -> 미션 -> 파트/워리어/브레인 -> 프로필 -> OBJECT2 객체 타입)를 계산했다. ABL은 파일명 토큰이 다른 FIT/ABL/ABI/ABX 텍스트에 나오는지로 참조를 판정했다. 모든 판정은 "추출본 데이터에서 참조가 없다"는 뜻이며, EXE가 이름을 런타임에 조립해 읽는 경우는 [확인 못 한 것](#11-확인-못-한-것)에 따로 적었다.

**난이도 표기**: `데이터만` = FIT/CSV/TXT 편집으로 끝남, `세이브 수정` = 진행 중 캠페인 세이브(PKK/SAV)도 손봐야 함, `EXE 패치 필요` = 코드 변경 필요. `(+자산 제작)`은 지형·초상화·영상 등 새로 만들어야 할 자원이 있다는 뜻이다.

## 1. 요약 (되살릴 가치 / 난이도 순)

| 순위 | 항목 | 근거 | 되살리는 방법 | 난이도 | 가치 |
|---|---|---|---|---|---|
| 1 | 클랜 메크를 캠페인에서 구매 가능하게 | 클랜 기본 프로필 33개(11섀시 x A/W/J)는 멀티/솔로 목록(`netpur/ispur/clanpur`, ACEHUNT·PAREDUX·THEGUNS.SOL)에만 있고 `purchase00~29`, `xpurchase00~11`에는 한 번도 안 나옴. 멀티/솔로 목록이 이미 클랜 메크를 담고 있어 구매 화면이 클랜 항목을 처리할 수 있어 보임(캠페인 경로는 미검증) | `purchaseNN.fit`/`xpurchaseNN.fit`에 `[MechN] TypeAFile/WFile/JFile` 블록 추가 + `[Header] NumMechs` 증가 | 데이터만(새 게임 권장) | 높음 |
| 2 | MIS0506 'Blood Makes the Grass Grow' (작전 5의 마지막 미션 초안) | 파일 전부 존재: FIT, 지형 `m0506`, 스크립트 `MIS0506.ABL`(클랜 병력 전멸 시 목표 성공까지 구현), 브레인 8종, `brf0506.txt`. 목표명만 'Placeholder'. 어떤 캠페인 파일에도 없음 | `mechcmdr1.fit`에 Scenario30="mis0506" 등록 + OpInfo + LastScenario=30 + `purchase30.fit`(purchase.fit Mission30이 이미 가리키는데 파일이 없음) 작성 | 데이터만 | 높음 |
| 3 | "LastScenario 뒤" 슬롯 활용 (E3_0101A 'Show & Tell' 등) | `mechcmdr1.fit`은 71개 시나리오를 나열하지만 `LastScenario=29`(mis0507)에서 끊음. 30번 이후는 e3_0101a, e3_0203, mise303, testmis1, MCX*, MCXS04xx. 이 중 E3_0101A('Show & Tell')는 지형·스크립트가 모두 있어 재생 가능 | LastScenario 상향 + OpInfo/purchase30 작성 + E3_0101A의 빈 `BriefingFile` 채움 | 데이터만 | 중간 |
| 4 | 열두 명이 쓰이지 않은 파일럿 약력 Desc331~342 (Apollo, Boomer, Detox, Ghost, Jinx, Needle, Pyro, Sponge, Squid, Toad, Vandal, Wasp) | `desc.fit`에 약력(Apollo는 본문 비어 있음)이 있으나 PMW 프로필·초상화·영상·음성이 전혀 없음. 파일럿 자산은 정확히 30명분(PILOT00~29, 음성 PILOTA~Z+AA~AD) | PMW00036~00047류 프로필 12개 신규(DescIndex 331~342) + 구매 목록 `[WarriorN]` 추가. 초상화·영상은 기존 것 재사용 또는 신규 | 데이터만(+자산 제작) | 중간 |
| 5 | 캠페인에서 영입 불가능한 파일럿 3명: Mystique(57), Falcon(71), Firestorm(79) | `purchase00~29` 전체에서 Status가 항상 4(UNSEEN)이고 시작 로스터에도 없음. 미션 FIT에서는 플레이어 소대 자리표시 워리어로 7~20개 미션이 참조함 | `purchaseNN.fit`에서 해당 `[WarriorN] Status`를 0으로 | 데이터만 | 중간(영입 풀 확대) |
| 6 | 캠페인에서 못 사는 차량 12종 + 확장 신차량 4종 | Rommel, Harasser, Bulldog, SRM/LRM Carrier, Shrek, Saracen, Striker, J.Edgar, VonLuckner, Condor, Savannah은 멀티/솔로 목록에만 있고 캠페인 목록(Swiftwind, Pegasus, Sweeper, Mine Layer, Refit, +확장 Centipede·Ammo Truck)에는 없음. Regulator/Manticore/Pilum/Alacorn은 확장 캠페인에도 없음 | `[VehicleN] Filename`(예 `20100`) 추가 + `NumVehicles` 증가 | 데이터만 | 중간 |
| 7 | 이름 붙은 에이스 메크 프로필 14종을 구매·로스터에 추가 | Furey's Vulture(PM204101/204350), Osis' Masakari, Wirth's/Kotare's Turkina, Ward's Madcat, Stiles/Bowen/Lopez' Uller, Kim's Masakari, Lee's/Til's Shadowcat, Savage's Cougar 등. 구매 목록엔 전혀 없고 AceHunt·MCX 일부 미션에만 적으로 배치. PM204101과 PM206401은 어디서도 안 쓰임 | 구매 목록에 파일 지정 추가(이름·설명 문자열 772~783/Desc472~483 이미 있음) | 데이터만 | 중간 |
| 8 | MX0304 컷 버전 ('Destroy Engine Drills', 에이스 터키나 2기) | `xbrf0304.txt`(placeholder 지휘관 `FEDCOM:<placeholder>`), `mx0304*.ABL` 스크립트 16개가 어디서도 참조되지 않음. 지형 `MX0304`는 없음 -> 최종판 MCX0304는 `MX0305` 지형·`mx0305*` 스크립트 사용 | 지형 MX0304를 제작하거나 MX0305에 좌표 재배치. 스크립트 16개는 보존돼 있음 | 데이터만(+지형 제작) | 낮음~중간 |
| 9 | 미사용 무기: Sniper Cannon(161), Rail Gun(98)/Heavy Thunderbolt(126)/Long Tom(160) | Sniper Cannon은 실제 설명문과 탄약(228)이 있으나 구매 목록·프로필 어디에도 없음. Rail Gun·Heavy Thunderbolt는 멀티/솔로 목록에만 있고, 에이스 프로필만 장착 | 구매 목록 `[ComponantN] ComponantID` 추가, 프로필 `[Item:N] MasterID` 편집 | 데이터만 | 낮음 |
| 10 | 표시 이름 버그 수정: Light Transport가 'Armored Car'로, Refit Truck이 'Refit Rig' 아님 등 | 문자열 1228 'Lt. Transport', 1248 'Refit Rig'에 대응하는 프로필 DescIndex(528, 548)가 없음. PV22700은 DescIndex 501('Armored Car'), PV30400/30500은 서로 이름이 뒤바뀜 | `PV22700` DescIndex=528, `PV32300` DescIndex=548로 수정하고 desc.fit에 Desc528/548 추가 | 데이터만 | 낮음 |
| 11 | MIS0801 'Power Plant Attack' (1997 시제품, 작전 8-1) | FIT/스크립트/브레인은 있으나 지형 `0801`이 없고 ABL의 목표 판정은 템플릿(주석 처리) 상태. 브리핑도 없음 | 지형 신규 제작 + 판정 구현 | 데이터만(+지형 제작) | 낮음 |
| 12 | 멀티플레이 모드 변형 브리핑 22개(hh/k/mb/rs/c/m)와 대응 FIT 부재 | 브리핑에 'Hounds and Hares', 'Most Bases', 'Robin Hood and the Sheriff' 등 게임 모드가 쓰여 있으나 이를 가리키는 FIT가 없음(모드별 FIT가 MP07xx 번호로 분리되면서 남은 것으로 추정) | 해당 모드용 FIT를 만들어 `ISBriefingFile/ClanBriefingFile`에 연결 | 데이터만(+ABL 작성) | 낮음 |
| 13 | 미션 후 메크별 보고 화면(문자열 1~28) | 'Report for Mech %i of Lance %i', 'shots hit', 'Salvage List', 'Ejected, and was captured by the Clan' 등 28개 문자열이 EXE에 있으나 호출처가 없음 | UI 코드 복원 필요 | EXE 패치 필요 | 낮음(난이도 매우 높음) |

그 밖의 발견: ① `mechcmdr1.fit`은 Op3의 두 미션을 순서대로 `mis0302 -> mis0301`로, Op5를 `0501, 0502, 0504, 0505, 0503, 0507`로 재배열했는데 `purchase.fit` 주석은 옛 순서(0503이 26번)로 남아 있다. ② `soloispurchase.fit`은 `purchase.fit`와 바이트 단위로 동일하고 어디서도 참조되지 않는다. ③ 크레딧 영상 `credits`는 `mechcmdr1.fit`이 두 번 요청하지만 `CREDITS.SMK`는 추출본에 없다. ④ EXE에는 치트 심볼(`Cheat_BunnyStrike`, `CantHitMe`, `DeadEye`, `Duh`, `GetSalvage`, `HealAll`, `Reveal`, `framegraph`)이 있고 `\hidden.txt`의 고정 문자열로 게이트된다 (`HIDDEN.TXT` 참고, 기능 복원 대상은 아님).

## 2. 미션

### 2.1 캠페인 연결 구조

- 미션 FIT 108개 중 캠페인·솔로 파일에서 실제로 재생되는 것은 45개(원본 30, 확장 12, 솔로 3). 나머지 63개는 도달 불가다: 개발/E3/시제품 26개, 멀티 맵 37개.
- `mechcmdr1.fit`: `numScenarios=71`, `LastScenario=29`. 0~29가 원본 30개 미션, 30~70은 개발 슬롯(e3_0101a, e3_0203, mise303, testmis1, MCX0101~0304 12개, MCXS0401~0426). 이 중 FIT 파일이 없는 이름이 23개(MCXS0403, MCXS0404~0426 중 0409 제외)이다. 원래 솔로 미션을 26개까지 계획했으나 3개(AceHunt, TheGuns, PARedux)만 만들어진 흔적이다.
- `[OpInfo]`는 Scenario0~29에만 Operation/Mission이 있다. 30번 이후 시나리오를 켜려면 이 줄도 추가해야 한다(자동 저장 이름 `PortArthurBefore_Op%i_Mis%i`, 작전 영상 선택에 쓰임으로 추정).
- GameSegment 체인(0~71)은 시나리오 0~33을 순서대로 잇고 34번에서 종료(16)한다. 35~71은 24~26 구간으로 되돌아가는 개발용 잔재다.
- `purchase.fit`은 `Mission0~31`을 가지며 `Mission30 -> purchase30`(파일 없음), `Mission31 -> NetPur`이다. 즉 원본 캠페인은 31번째 미션(Op5)을 위한 구매 슬롯을 이미 예약했다.
- 솔로 캠페인 3개(`campaignAceHunt/PARedux/TheGuns.fit`)는 `AceHunt.FIT`/`PARedux.FIT`/`TheGuns.FIT`를 직접 가리킨다. `MCXS0401.FIT`/`MCXS0402.FIT`는 그 원본(1998-11/12판)이다: 목표 Points=1, MaxTonnage 210/150이었다가 1999-02에 20000~35000점, 245/200톤으로 조정, TheGuns는 워리어 프로필도 PMW00116 -> PMW00308로 교체됨.

### 2.2 도달 불가한 단독 미션 (멀티 제외)

| 파일 | 정체 | 작전-미션 | 목표 | 브리핑 | 지형 | 스크립트 | 파트 | 판정 | 난이도 |
|---|---|---|---|---|---|---|---|---|---|
| E3_0101.FIT | E3 1997 데모 'Rescue Mechs' | 123-1 | Destroy Red Claws at Base; Get to Extraction Point; Recover Supplies from Bunker | 없음 X | Map0101 X | E3_0101 O | 28 | 재생 불가(지형·프로필 없음) | 데이터만(+지형 제작) |
| E3_0101A.FIT | E3 1997 데모 'Show & Tell' | 99-9 | Destroy Planetary Oribtal Guns; Destroy Government Building | 없음 X | Map0101A O | E3_0101A O | 35 | 거의 재생 가능 | 데이터만 |
| E3_0203.FIT | E3 1997 데모 'Convoy Shuffle' | 123-2 | Capture 4 of 7 Supply Trucks; Capture All Supply Trucks | 없음 X | 0203 X | E3_0203 O | 32 | 재생 불가(지형·프로필 없음) | 데이터만(+지형 제작) |
| EDITSCEN.FIT | 미션 에디터 기본 템플릿 |  |  | 없음 X | default X | editscen O | 0 | 템플릿 | 해당 없음 |
| MCXS0401.FIT | 솔로 'Destroy All Aces' 구판(1998-11) | 4-1 | Destroy Ace Madcat; Take Out three Ace Ullers; Eliminate Ace Masakari; Kill Ace Cougar; Destroy two Ace Shadowcats | xsbrf0401.TXT O | MXS001 O | MCXS0401 O | 10 | AceHunt.FIT로 대체된 구판 | 데이터만 |
| MCXS0402.FIT | 솔로 'Sound the Guns' 구판(1998-12) | 4-2 | Destroy Vehicles at Base; One Mobile Artillery Must Survive | xsbrf0402.txt O | MXS0402 O | MCXS0402 O | 47 | TheGuns.FIT로 대체된 구판 | 데이터만 |
| MIS0101c.fit | MIS0101 'Rough Landing' 초기판(1997-11) | 1-1 | Destroy North Natural Gas Towers; Destroy East Natural Gas Towers | brf0101.txt O | M0101 O | MIS0101n O | 4 | 테스트 배치(재생 가능하나 의미 없음) | 데이터만 |
| MIS0101n.fit | MIS0101 초기판(적 차량 위주) | 1-1 | Destroy North Natural Gas Towers; Destroy East Natural Gas Towers | brf0101.txt O | M0101 O | MIS0101n O | 6 | 테스트 배치 | 데이터만 |
| MIS0101s.fit | MIS0101 초기판(IS vs IS?) | 1-1 | Destroy North Natural Gas Towers; Destroy East Natural Gas Towers | brf0101.txt O | M0101 O | MIS0101n O | 4 | 테스트 배치 | 데이터만 |
| MIS0506.FIT | 캠페인 초안(마지막 작전 5-6) | 5-6 | Placeholder | brf0506.txt O | m0506 O | MIS0506 O | 40 | 재생 가능(그대로) | 데이터만 |
| MIS0801.FIT | 1997년 시제품(작전 8-1 'Power Plant Attack') | 8-1 | Destroy Power Complex Alpha; Destroy Power Complex Bravo; Destroy Power Complex Charlie | 없음 X | 0801 X | MIS0801 O | 80 | 재생 불가(지형 없음) | 데이터만(+지형 제작) |
| MISE303.FIT | E3 'HPG Attack'(1997-06) | 123-3 | Prevent X-Mit: Destroy Main Power; Prevent X-Mitt: Destroy Dishes; Keep Secondary Power Intact | 없음 X | E3_3 X | MISE303 O | 62 | 재생 불가(지형·프로필 없음) | 데이터만(+지형 제작) |
| testmis1.FIT | ABL 라이브러리 테스트(작전 9-3) | 9-3 | Kill |   X | testmis1 X | testmis1 O | 34 | 개발용(재생 불가) | 해당 없음 |

(O/X = 파일 존재 여부.) 보충: MIS0506의 objective 이름 'Placeholder'는 한국어화에서도 번역 대상으로 남아 있다(`localization/ko/fit_strings_notes.md`).

- **MIS0506.FIT**: ABL이 완성되어 있음(클랜 병력 전멸 시 목표 성공). brf0506을 MIS0507과 공유. 동명 멀티 맵 MP0712(Blood Makes the Grass Grow) 존재. 필요한 것: purchase30.fit(purchase.fit Mission30이 가리키지만 파일 없음), 목표 표시명(현재 'Placeholder'), OpInfo 줄.
- **MIS0801.FIT**: 목표 3개(발전소 Alpha/Bravo/Charlie 파괴), 파트 80개(플레이어 12), cgs0801a/b/c 브레인은 존재. 필요한 것: TERRAIN.FST/0801.*(map,obj,elv,dat,bdg,gmm,lst,pre,fit), 브리핑(BriefingFile 없음), 목표 달성 판정(스크립트 템플릿 상태).
- **E3_0101A.FIT**: 지형 Map0101A·ABL 전부 존재. 플레이어 선배치 소대가 Masakari J/Mad Cat J(클랜 메크) 포함. 목표: 궤도포·정부 건물 파괴. 필요한 것: purchase30.fit, 브리핑 txt(BriefingFile가 빈 문자열), OpInfo(Operation/Mission) 줄.

### 2.3 MIS0403 변형 13종과 MIS0101c/n/s

`MIS0403c.fit, MIS0403c1_3p.fit, MIS0403c1_5p.fit, MIS0403c2_3p.fit, MIS0403c2_5p.fit, MIS0403c3_5p.fit, MIS0403c4_5p.fit, MIS0403c_2p.fit, MIS0403mp.fit, MIS0403s.fit, MIS0403s_2p.fit, MIS0403s_3p.fit, MIS0403s_5p.fit` (모두 지형 `m0403`, 스크립트 `MIS0403n.abl`). 정식 `MIS0403.fit`(46파트, 브레인 13종)과 달리 파트 19개·목표 2개('Activate abandoned Base' / 'Destroy all Enemy units')이고, `[Multiplayer]` 블록에 서버 여부·플레이어 이름('Denny' 등)·HomeTeam(0=IS, 1=Clan)이 들어 있다. 2/3/5인용 클랜(`c`)·IS(`s`) 한 쌍씩, `MIS0403mp.fit`(6 드롭존)은 이후 MP 맵의 전신이다. 개발자 네트워크 테스트용으로 보이며 복원 가치는 낮다. `MIS0101c/n/s.fit`도 같은 계열(4~6파트, 2개 목표)로 1997-11판 'Rough Landing' 시제품이다(`MIS0101n.abl`).

`Nplayer*.fit`(2/3/5/6player1~6, 16개)는 `[Multiplayer] SessionName="RYAN'S GAME"` 류의 개발자 LAN 테스트 설정이며 EXE도 참조하지 않는다.

### 2.4 멀티플레이 맵

멀티 FIT 37개(MP07xx, 이름 붙은 맵, MXM0502)는 캠페인에서는 도달 불가이며 [Campaign] 블록에 `ISBriefingFile`/`ClanBriefingFile`을 가진다. 멀티 목록에 어떻게 노출되는지(폴더 스캔 `%s*.fit` 추정)는 EXE 확인 전이라 확정하지 않았다. 아래는 브리핑·지형·스크립트가 모두 있는지의 점검이다.

| FIT | 지형 | 첫 목표 | 목표 수 | 드롭존 | IS/Clan 브리핑 | 지형/ABL | 상태 |
|---|---|---|---|---|---|---|---|
| Achilles.FIT | Achilles | Destroy Headquarters | 4 | 6 | O/O | O/O | 완비 |
| Bakwoods.FIT | Bakwoods | Capture Enemy HQ | 2 | 6 | O/O | O/O | 완비 |
| CaptIsld.FIT | CaptIsld | Capture Buildings | 2 | 6 | O/O | O/O | 완비 |
| DValley.FIT | DValley | Capture Enemy HQ | 4 | 6 | O/O | O/O | 완비 |
| HvrDmmt.FIT | HvrDmmt | Capture Buildings | 2 | 6 | O/O | O/O | 완비 |
| KingIsle.FIT | KingIsle | Capture and Hold HQ | 4 | 6 | O/O | O/O | 완비 |
| MP0304.fit | m0304 | Capture ReEducation Camp HQ | 4 | 6 | O/O | O/O | 완비 |
| MP0701.FIT | MP0701 | Capture Enemy Base HQ | 4 | 6 | O/O | O/O | 완비 |
| MP0702.FIT | MP0702 | Control 5 bases | 2 | 6 | O/O | O/O | 완비 |
| MP0703.FIT | MP0703 | Fight to the Death | 2 | 6 | O/O | O/O | 완비 |
| MP0705.FIT | MP0705 | Protect Base Headquarters | 2 | 6 | O/O | O/O | 완비 |
| MP0706.FIT | MP0706 | Defend 4 Generators | 2 | 6 | O/O | O/O | 완비 |
| MP0707.FIT | MP0707 | Capture and Hold HQ on Hill | 2 | 6 | O/O | O/O | 완비 |
| MP0708.FIT | MP0708 | Destroy 4 Orbital Guns or kill all enemies | 4 | 6 | O/O | O/O | 완비 |
| MP0709.FIT | MP0709 | Capture & Hold Command Building | 2 | 6 | O/O | O/O | 완비 |
| MP0712.FIT | MP0712 | Destroy all Enemy Forces | 2 | 6 | O/O | O/O | 완비 |
| MP0714.FIT | MP0701 | Capture Enemy Base HQ | 4 | 6 | O/O | O/O | 완비 |
| MP0715.FIT | MP0702 | Control 5 bases | 2 | 6 | O/O | O/O | 완비 |
| MP0716.FIT | MP0706 | Defend 4 Generators | 2 | 6 | O/O | O/O | 완비 |
| MP0718.FIT | MP0706 | Defend 4 Generators | 2 | 6 | O/O | O/O | 완비 |
| MP0719.FIT | MP0719 | Defend 2 Industrial Complexes | 2 | 6 | O/O | O/O | 완비 |
| MP0720.FIT | MP0720 | Destroy enemy industrial complexes | 4 | 6 | O/O | O/O | 완비 |
| MP0721.FIT | MP0721 | Defend 2 Artillery Crates | 2 | 6 | O/O | O/O | 완비 |
| MP0722.FIT | MP0722 | Capture and hold at least two HQs | 2 | 6 | O/O | O/O | 완비 |
| MP0723.FIT | MP0701 | Destroy all Enemy Forces | 2 | 6 | O/O | O/O | 완비 |
| MP0725.FIT | MP0720 | Destroy enemy industrial complexes | 4 | 6 | O/O | O/O | 완비 |
| MP0726.FIT | MP0709 | Capture & Hold Command Building | 2 | 6 | O/O | O/O | 완비 |
| MP0727.FIT | MP0719 | Defend 2 Industrial Complexes | 2 | 6 | O/O | O/O | 완비 |
| MP0728.FIT | MP0722 | Capture and hold at least two HQs | 2 | 6 | O/O | O/O | 완비 |
| MP0729.FIT | swamp | Destroy all enemy forces | 2 | 6 | O/O | O/O | 완비 |
| MP0730.FIT | swamp | Destroy All Enemy Forces | 2 | 6 | O/O | O/O | 완비 |
| MP0731.FIT | bakwoods | Destroy all enemies | 2 | 6 | O/O | O/O | 완비 |
| MXM0502.FIT | Random | Capture and Hold HQ Alpha | 4 | 6 | O/O | O/O | 완비 |
| MouseTrp.FIT | MouseTrp | Capture Buildings | 2 | 6 | O/O | O/O | 완비 |
| Urbana.FIT | Urbana | Destroy All Enemy Forces | 2 | 6 | O/O | O/O | 완비 |
| WetNWild.FIT | WetNWild | Destroy All Enemy Forces | 2 | 6 | O/O | O/O | 완비 |
| caldera.FIT | caldera | Destroy Enemies | 2 | 6 | O/O | O/O | 완비 |

특이 사항: ① 지형 `mp0704`(오브젝트 세트만 다른 `mp0707`의 이전판)는 대응 FIT가 없다. `MP0707.FIT`가 `brf0704`('King of the Hill')를 쓰므로 번호 변경 후 남은 구판이다. ② `MP0304.fit`은 `MIS0304`의 멀티판(39파트·6드롭존)이며 `brf0304.txt`를 양 진영이 재사용한다. ③ `MP0701/0714/0723`은 지형 `MP0701`을 공유한다.

### 2.5 이름만 있고 파일이 없는 솔로 슬롯

`mechcmdr1.fit`의 Scenario48~70: MCXS0403, MCXS0404, MCXS0405, MCXS0406, MCXS0407, MCXS0408, MCXS0410, MCXS0411, MCXS0412, MCXS0413, MCXS0414, MCXS0415, MCXS0416, MCXS0417, MCXS0418, MCXS0419, MCXS0420, MCXS0421, MCXS0422, MCXS0423, MCXS0424, MCXS0425, MCXS0426. 지형(`MXS001`, `MXS0402`, `MCXS0404`)은 확장 솔로 3개분만 존재한다.

## 3. 메크

프로필 89개(`PM*.FIT`). 표시 이름은 문자열 id = DescIndex + 300(예: Commando A, DescIndex 409 -> 709). 모든 프로필의 `Chassis`는 OBJECT2.PAK의 `MechType` 객체에 존재하므로 섀시 자체는 크래시 위험이 없다. 분류: 캠페인 구매 가능 39, 멀티/솔로 목록에만 33, 구매 불가·미션 스크립트 배치만 15, 완전 미사용 2.

**핵심**

- 클랜 메크 33개 프로필(Uller, Cougar, Hunchback IIc, Vulture, Loki, Thor, Mad Cat, Masakari, Shadow Cat, Nova Cat, Turkina 각 A/W/J)은 캠페인·확장 구매 목록에 한 번도 없다. 멀티/솔로 목록에는 `-1`(무제한)로 있다.
- 완전 미사용: **PM204101**(Furey's Vulture A, DescIndex 472를 PM204350과 공유하는 중복), **PM206401**(Thor W 중복). 구매 가능하지만 어떤 미션에도 배치되지 않음: Atlas J, Stiletto W, Bushwacker J, Mauler W, Turkina J.
- 이름 붙은 에이스 프로필 14개(Furey 2, Osis, Wirth, Kotare 2, Ward, Stiles, Bowen, Lopez, Kim, Lee, Til, Savage)와 일반 이름 중복 변형 2개(PM108101 Awesome A, PM109150 Atlas A)는 구매 목록에 없다. 에이스의 표시 이름(문자열 772~783)과 설명(Desc472~483)은 완성돼 있다.
- 데이터 불일치: `PM110x`의 MechType은 'Fire Falcon'인데 표시 이름은 'Stiletto'(문자열 754~756). `PM207350`은 Mad Cat J인데 DescIndex 475('Kotare's Turkina'). `PM209150`/`PM209450`은 MechType 'Shadow Cat J'지만 파일 번호 계열은 A/W.
- OBJECT2 MechType 28개 중 프로필이 없는 것: 타입 **45**(Commando 복제, BASE ID 2), **55 Puma**(외형은 Cougar와 같은 0x0100000A이나 `pu.hsp`가 SHAPES.FST에 없음 -> 그대로 켜면 오류 위험), **64**(Firestarter 복제), **65**(Centurion 3050). `h2.hsp`도 쓰는 객체가 없다.

| 프로필 | 표시명 (문자열 id) | 톤(C=클랜) | 원본 캠페인 최초 구매 | 확장 최초 구매 | 멀티/솔로 목록 | 배치 미션 수(도달/불가) | 판정 |
|---|---|---|---|---|---|---|---|
| PM100100 | Commando A (709) | 25 | MIS0102 | MCX0101 | O | 8/4 | 캠페인 구매 가능 |
| PM100300 | Commando J (711) | 25 | MIS0105 | MCX0101 | O | 8/1 | 캠페인 구매 가능 |
| PM100400 | Commando W (710) | 25 | MIS0103 | MCX0101 | O | 3/2 | 캠페인 구매 가능 |
| PM101100 | Firestarter A (715) | 30 | MIS0104 | MCX0101 | O | 5/0 | 캠페인 구매 가능 |
| PM101300 | Firestarter J (717) | 30 | MIS0201 | MCX0101 | O | 7/0 | 캠페인 구매 가능 |
| PM101400 | Firestarter W (716) | 30 | MIS0102 | MCX0101 | O | 8/1 | 캠페인 구매 가능 |
| PM102100 | Raven A (739) | 35 | MIS0105 | MCX0101 | O | 5/3 | 캠페인 구매 가능 |
| PM102300 | Raven J (741) | 35 | MIS0201 | MCX0102 | O | 15/1 | 캠페인 구매 가능 |
| PM102400 | Raven W (740) | 35 | MIS0206 | MCX0104 | O | 7/1 | 캠페인 구매 가능 |
| PM103100 | Hollander II A (718) | 45 | MIS0302 | MCX0101 | O | 3/3 | 캠페인 구매 가능 |
| PM103300 | Hollander II J (720) | 45 | MIS0204 | MCX0102 | O | 1/0 | 캠페인 구매 가능 |
| PM103400 | Hollander II W (719) | 45 | MIS0202 | MCX0201 | O | 4/1 | 캠페인 구매 가능 |
| PM104100 | Hunchback A (721) | 50 | MIS0104 | MCX0102 | O | 4/2 | 캠페인 구매 가능 |
| PM104300 | Hunchback J (723) | 50 | MIS0203 | MCX0103 | O | 4/4 | 캠페인 구매 가능 |
| PM104400 | Hunchback W (722) | 50 | MIS0206 | MCX0101 | O | 5/1 | 캠페인 구매 가능 |
| PM105100 | Centurion A (751) | 55 | MIS0103 | MCX0101 | O | 9/4 | 캠페인 구매 가능 |
| PM105300 | Centurion J (753) | 55 | MIS0301 | MCX0202 | O | 5/1 | 캠페인 구매 가능 |
| PM105400 | Centurion W (752) | 55 | MIS0106 | MCX0103 | O | 13/2 | 캠페인 구매 가능 |
| PM106100 | Catapult A (706) | 65 | MIS0201 | MCX0102 | O | 10/1 | 캠페인 구매 가능 |
| PM106300 | Catapult J (708) | 65 | MIS0405 | MCX0201 | O | 1/1 | 캠페인 구매 가능 |
| PM106400 | Catapult W (707) | 65 | MIS0201 | MCX0104 | O | 12/1 | 캠페인 구매 가능 |
| PM107100 | JagerMech A (727) | 70 | MIS0205 | MCX0104 | O | 6/0 | 캠페인 구매 가능 |
| PM107300 | JagerMech J (729) | 70 | MIS0402 | MCX0203 | O | 2/14 | 캠페인 구매 가능 |
| PM107400 | JagerMech W (728) | 70 | MIS0306 | MCX0102 | O | 6/2 | 캠페인 구매 가능 |
| PM108100 | Awesome A (703) | 80 | MIS0304 | MCX0103 | O | 3/0 | 캠페인 구매 가능 |
| PM108101 | Awesome A (703) | 80 | - | - | - | 1/0 | 구매 불가·미션 배치 전용(적) |
| PM108300 | Awesome J (705) | 80 | MIS0406 | MCX0302 | O | 2/1 | 캠페인 구매 가능 |
| PM108400 | Awesome W (704) | 80 | MIS0305 | MCX0202 | O | 1/16 | 캠페인 구매 가능 |
| PM109100 | Atlas A (700) | 100 | MIS0202 | MCX0204 | O | 5/2 | 캠페인 구매 가능 |
| PM109150 | Atlas A (700) | 100 | - | - | - | 1/0 | 구매 불가·미션 배치 전용(적) |
| PM109300 | Atlas J (702) | 100 | MIS0302 | MCX0304 | O | - | 캠페인 구매 가능, 미션 미배치 |
| PM109400 | Atlas W (701) | 100 | MIS0202 | MCX0201 | O | 2/3 | 캠페인 구매 가능 |
| PM110100 | Stiletto A (754) | 35 | - | MCX0201 | O | 1/0 | 캠페인 구매 가능 |
| PM110300 | Stiletto J (756) | 35 | - | MCX0103 | O | 3/1 | 캠페인 구매 가능 |
| PM110400 | Stiletto W (755) | 35 | - | MCX0102 | O | - | 캠페인 구매 가능, 미션 미배치 |
| PM111100 | Bushwacker A (757) | 55 | - | MCX0102 | O | 3/0 | 캠페인 구매 가능 |
| PM111300 | Bushwacker J (759) | 55 | - | MCX0201 | O | - | 캠페인 구매 가능, 미션 미배치 |
| PM111400 | Bushwacker W (758) | 55 | - | MCX0103 | O | 6/1 | 캠페인 구매 가능 |
| PM112100 | Mauler A (760) | 90 | - | MCX0202 | O | 2/0 | 캠페인 구매 가능 |
| PM112300 | Mauler J (762) | 90 | - | MCX0301 | O | 1/1 | 캠페인 구매 가능 |
| PM112400 | Mauler W (761) | 90 | - | MCX0104 | O | - | 캠페인 구매 가능, 미션 미배치 |
| PM200100 | Uller A (745) | 30C | - | - | O | 8/3 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM200150 | Stiles' Uller (777) | 30C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM200160 | Bowen's Uller (778) | 30C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM200170 | Lopez's Uller (779) | 30C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM200300 | Uller J (747) | 30C | - | - | O | 7/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM200400 | Uller W (746) | 30C | - | - | O | 12/3 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM201100 | Cougar A (712) | 35C | - | - | O | 13/4 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM201300 | Cougar J (714) | 35C | - | - | O | 12/13 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM201350 | Savage's Cougar (783) | 35C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM201400 | Cougar W (713) | 35C | - | - | O | 11/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM203100 | Hunchback IIc A (724) | 50C | - | - | O | 10/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM203300 | Hunchback IIc J (726) | 50C | - | - | O | 7/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM203400 | Hunchback IIc W (725) | 50C | - | - | O | 10/2 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM204100 | Vulture A (748) | 60C | - | - | O | 10/14 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM204101 | Furey's Vulture (772) | 60C | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PM204300 | Vulture J (750) | 60C | - | - | O | 6/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM204350 | Furey's Vulture (772) | 60C | - | - | - | 1/0 | 구매 불가·미션 배치 전용(적) |
| PM204400 | Vulture W (749) | 60C | - | - | O | 6/2 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM205100 | Loki A (730) | 65C | - | - | O | 5/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM205300 | Loki J (732) | 65C | - | - | O | 1/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM205400 | Loki W (731) | 65C | - | - | O | 4/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM206100 | Thor A (742) | 70C | - | - | O | 4/4 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM206300 | Thor J (744) | 70C | - | - | O | 5/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM206400 | Thor W (743) | 70C | - | - | O | 6/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM206401 | Thor W (743) | 70C | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PM207100 | Mad Cat A (733) | 75C | - | - | O | 13/4 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM207300 | Mad Cat J (735) | 75C | - | - | O | 14/16 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM207350 | Kotare's Turkina (775) | 75C | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PM207360 | Ward's Madcat (776) | 75C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM207400 | Mad Cat W (734) | 75C | - | - | O | 10/2 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM208100 | Masakari A (736) | 85C | - | - | O | 5/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM208150 | Osis' Masakari (773) | 85C | - | - | - | 1/0 | 구매 불가·미션 배치 전용(적) |
| PM208300 | Masakari J (738) | 85C | - | - | O | 3/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM208350 | Kim's Masakari (780) | 85C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM208400 | Masakari W (737) | 85C | - | - | O | 4/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM209100 | Shadow Cat A (763) | 45C | - | - | O | 8/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM209150 | Lee's Shadowcat (781) | 45C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM209300 | Shadow Cat J (765) | 45C | - | - | O | 7/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM209400 | Shadow Cat W (764) | 45C | - | - | O | 7/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM209450 | Til's Shadowcat (782) | 45C | - | - | - | 1/1 | 구매 불가·미션 배치 전용(적) |
| PM210100 | Nova Cat A (766) | 70C | - | - | O | 4/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM210300 | Nova Cat J (768) | 70C | - | - | O | 4/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM210400 | Nova Cat W (767) | 70C | - | - | O | 3/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM211100 | Turkina A (769) | 95C | - | - | O | 1/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM211300 | Turkina J (771) | 95C | - | - | O | - | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM211350 | Kotare's Turkina (775) | 95C | - | - | - | 1/0 | 구매 불가·미션 배치 전용(적) |
| PM211400 | Turkina W (770) | 95C | - | - | O | 1/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PM211450 | Wirth's Turkina (774) | 95C | - | - | - | 1/0 | 구매 불가·미션 배치 전용(적) |

메모: "배치 미션 수"는 `[Parts] ObjectProfile` 기준이다. 적 전용 판정(`적` 팀 = `Alignment -1` 또는 `TeamID 1`)은 JSON의 `enemy_in`에 있다. 클랜 메크를 적에게서 얻는 인양(salvage) 경로가 있는지는 확인하지 못했다.

## 4. 차량

프로필 61개(`PV*`/`PE*`/`Pem*`; 문자열 id = DescIndex + 700, 범위 1200~1255). 분류: 캠페인 구매 가능 7, 선물로만 1, 멀티/솔로에만 17, 미션 배치만 24, 완전 미사용 12.

**핵심**

- 캠페인(원본·확장 합쳐)에서 구매할 수 있는 차량은 Swiftwind, Pegasus, Mine Sweeper, Mine Layer, Refit Truck(PV32300), 확장의 Centipede·Ammo Truck 7종뿐이다. 나머지 전투 차량 17종은 멀티/솔로 목록에만 있다.
- `PV20600` APC는 `desc.fit` Desc500에 "CUT FROM MULTIPLAYER"라고 쓰여 있지만 원본 캠페인 `purchase01~29`에 필수 선물(`Required = T`)로 계속 지급된다. 옛 `netpur.fit`에는 APC와 Light Transport가 있으나 후속 `ispur/clanpur`에서 삭제됐다. Desc501(Armored Car)도 같은 "CUT FROM MULTIPLAYER" 메시지이며 PV22700/22701이 같은 DescIndex 501을 공유한다.
- 문자열 1228 'Lt. Transport', 1248 'Refit Rig'는 어떤 프로필 DescIndex도 가리키지 않는다. PV22700('Light Transport')은 501('Armored Car')로 표시되고, `PV32200`('Refit Truck', 객체 478 'Field Refit Truck')은 DescIndex가 없고 아무 데서도 쓰이지 않는다. 구매 목록의 Refit Truck(PV32300)은 객체 479 'Refit Rig'를 쓴다. 즉 두 프로필의 이름·설명 연결이 뒤섞여 있다.
- PV30400(Semi Tractor)과 PV30500(Flatbed)은 표시 이름이 서로 바뀌어 있다(문자열 1229 'Flatbed' / 1230 'Semi-Tractor').
- 프로필 없이 객체만 있는 `GroundVehicleType`: **407 Crane, 413 Hopper, 418 mradar, 421 relay** (OBJECT2.PAK에는 있으나 PV 프로필·미션 배치 없음). 완전 미사용 프로필: Artillery Loader(PV21200), Towed Turret(PV21500), Armed Flatbed(PV30501), Farm Truck(PV30600)/Armed(PV30601), Car(PV30700, PV31000), Sports Car(PV30800), Hover Limo(PV31100), PV32200, Elemental 1(PE000001), Hicks(PEM00001).
- 트레일러·열차(`trainone~trainsix`, `engine`)는 MIS0205/MIS0401이 쓰므로 미사용이 아니다.

| 프로필 | 이름 / 표시명 (문자열 id) | 톤 | 원본 구매 | 확장 구매 | 멀티/솔로 | 배치(도달/불가) | 판정 |
|---|---|---|---|---|---|---|---|
| PE000001 | Elemental 1 / - (-) | 25 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PE000003 | Elemental 3 / - (-) | 5 | - | - | - | 7/6 | 구매 불가·미션 배치 전용 |
| PEM00001 | Hicks / - (-) | 25 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV20000 | Swiftwind / Swiftwind (1217) | 5 | MIS0101 | MCX0101 | O | 4/2 | 캠페인 구매 가능 |
| PV20100 | Rommel / Rommel (1211) | 65 | - | - | O | 20/4 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV20200 | Mobile HQ / Mobile HQ (1219) | 25 | - | - | - | 9/2 | 구매 불가·미션 배치 전용 |
| PV20300 | Fuel Truck / Fuel Truck (1220) | 55 | - | - | - | 11/0 | 구매 불가·미션 배치 전용 |
| PV20400 | Elem. Carrier / Elem. Carrier (1221) | 65 | - | - | - | 0/2 | 구매 불가·미션 배치 전용 |
| PV20500 | Harasser / Harasser (1204) | 25 | - | - | O | 11/4 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV20600 | APC / APC (1200) | 10 | 선물 | - | O | 4/0 | 캠페인에서는 선물(필수 지급)로만 제공 |
| PV20650 | APC / APC (1200) | 10 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV20800 | Bulldog / Bulldog (1202) | 60 | - | - | O | 21/18 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV20900 | SRM Carrier / SRM Carrier (1215) | 60 | - | - | O | 8/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV21000 | LRM Carrier / LRM Carrier (1206) | 60 | - | - | O | 19/3 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV21100 | Mobile Artillery / Mbl Artlry (1222) | 95 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV21150 | Mobile Artillery / Mbl Artlry (1222) | 95 | - | - | - | 2/1 | 구매 불가·미션 배치 전용 |
| PV21200 | Artillery Loader / Artillery Loader (1223) | 50 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV21300 | Shrek / Shrek (1214) | 80 | - | - | O | 4/3 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV21400 | Saracen / Saracen (1212) | 35 | - | - | O | 15/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV21500 | Towed Turret / Towed Turret (1224) | 35 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV21600 | AeroSpace Spotter / AeroSpace Spotter (1225) | 45 | - | - | - | 11/3 | 구매 불가·미션 배치 전용 |
| PV21700 | Striker / Striker (1216) | 35 | - | - | O | 17/4 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV21800 | Pegasus / Pegasus (1209) | 15 | MIS0102 | MCX0101 | O | 2/1 | 캠페인 구매 가능 |
| PV21900 | J. Edgar / J. Edgar (1205) | 25 | - | - | O | 8/2 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV22000 | VonLuckner / VonLuckner (1218) | 75 | - | - | O | 11/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV22100 | Condor / Condor (1203) | 50 | - | - | O | 12/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV22200 | Ordnance Truck / Ordnance Truck (1226) | 20 | - | - | - | 7/0 | 구매 불가·미션 배치 전용 |
| PV22400 | Salvage Rig / Salvage Rig (1227) | 50 | - | - | - | 6/1 | 구매 불가·미션 배치 전용 |
| PV22700 | Light Transport / Armored Car (1201) | 7.5 | - | - | O | 3/0 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV22701 | Armored Car / Armored Car (1201) | 7.5 | - | - | - | 4/2 | 구매 불가·미션 배치 전용 |
| PV22800 | Mine Sweeper / Sweeper (1208) | 40 | MIS0105 | MCX0101 | O | - | 캠페인 구매 가능 |
| PV22900 | Mine Layer / Mine Layer (1207) | 40 | MIS0105 | MCX0103 | O | 8/1 | 캠페인 구매 가능 |
| PV30400 | Semi Tractor / Flatbed (1229) | 40 | - | - | - | 6/0 | 구매 불가·미션 배치 전용 |
| PV30500 | Flatbed / Semi-Tractor (1230) | 40 | - | - | - | 5/1 | 구매 불가·미션 배치 전용 |
| PV30501 | Armed Flatbed / Armed Flatbed (1231) | 40 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV30600 | Farm Truck / Farm Truck (1232) | 5 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV30601 | Armed Farm Truck / Armed Farm Truck (1233) | 5 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV30700 | Car / Car (1234) | 5 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV30800 | Sports Car / Sports Car (1235) | 5 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV30900 | Sports Car / Sports Car (1236) | 5 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV31000 | Car / Car (1237) | 5 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV31100 | Hover Limo / Hover Limo (1238) | 5 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV31200 | Limo / Limo (1239) | 5 | - | - | - | 0/1 | 구매 불가·미션 배치 전용 |
| PV31300 | Sports Car / Sports Car (1240) | 5 | - | - | - | 0/1 | 구매 불가·미션 배치 전용 |
| PV31400 | Car / Car (1241) | 5 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV31500 | Car / Car (1242) | 5 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV31600 | Sports Car / Sports Car (1243) | 25 | - | - | - | 0/1 | 구매 불가·미션 배치 전용 |
| PV31700 | Car / Car (1244) | 5 | - | - | - | 2/0 | 구매 불가·미션 배치 전용 |
| PV31800 | Car / Car (1245) | 5 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV31900 | Savannah Master / Savannah (1213) | 5 | - | - | O | 4/2 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV32000 | Sports Car / Sports Car (1246) | 5 | - | - | - | 1/0 | 구매 불가·미션 배치 전용 |
| PV32100 | Salvage Truck / Salvage Truck (1247) | 40 | - | - | - | 3/0 | 구매 불가·미션 배치 전용 |
| PV32200 | Refit Truck / - (-) | 10 | - | - | - | - | 완전 미사용(구매·배치 없음) |
| PV32300 | Refit Truck / Refit Truck (1210) | 35 | MIS0106 | MCX0101 | O | 1/1 | 캠페인 구매 가능 |
| PV32400 | Ambulance / Ambulance (1249) | 10 | - | - | - | 3/0 | 구매 불가·미션 배치 전용 |
| PV33300 | Centipede / Centipede (1250) | 15 | - | MCX0101 | O | - | 캠페인 구매 가능 |
| PV33400 | Regulator / Regulator (1251) | 45 | - | - | O | 8/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV33500 | Manticore / Manticore (1252) | 60 | - | - | O | 7/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV33600 | Pilum / Pilum (1253) | 70 | - | - | O | 6/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV33700 | Alacorn / Alacorn (1254) | 95 | - | - | O | 6/1 | 캠페인 구매 불가(멀티/솔로 목록에만 있음) |
| PV33800 | Ammo Truck / Ammo Truck (1255) | 10 | - | MCX0101 | O | 2/0 | 캠페인 구매 가능 |

## 5. 부품 (compbas.csv)

무기·탄약·센서 계열 항목 중 **구매 목록에도 없고 어떤 프로필에도 장착되지 않은 것**은 24개다. 그중 설명문이 `IF YOU SEE THIS DESCRIPTION PLEASE REPORT IT AS A BUG`인 플레이스홀더 항목은 11개다. 질문하신 Machine Gun(105)과 Anti-Missile System(106)은 구매 목록(캠페인·확장·솔로·멀티 모두)에 한 번도 없고 프로필에도 장착되지 않아 **실제로 구매할 수 없다**.

| id | 이름 | 타입 | 진영 | 설명 상태 | 사용 현황 |
|---|---|---|---|---|---|
| 105 | Machine Gun | BallisticWeapon | IS | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 106 | Anti-Missile System | removed | IS | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 114 | C Machine Gun | BallisticWeapon | Clan | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 115 | C Anti-Missile System | removed | Clan | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 121 | LR Missile/15 | MissileWeapon | IS | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 122 | LR Missile/20 | MissileWeapon | IS | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 124 | SR Missile/6 | MissileWeapon | IS | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 131 | C LR Missile/15 | MissileWeapon | Clan | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 132 | C LR Missile/20 | MissileWeapon | Clan | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 134 | C SR Missile/6 | MissileWeapon | Clan | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 136 | C ST-SR Missile/6 | MissileWeapon | Clan | 플레이스홀더 | 구매 목록·장착 모두 없음 |
| 161 | Sniper Cannon | MissileWeapon | IS | 설명 있음 | 구매 목록·장착 모두 없음 |
| 205 | M Gun Ammo | Ammo | IS | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 206 | Anti-Missile Ammo | Ammo | IS | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 214 | C M Gun Ammo | Ammo | Clan | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 215 | C Anti-Missile Ammo | Ammo | Clan | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 221 | LRM/15 Pack | Ammo | IS | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 222 | LRM/20 Pack | Ammo | IS | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 224 | SRM/6 Pack | Ammo | IS | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 228 | Sniper Cannon Ammo | Ammo | IS | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 231 | C LRM/15 Pack | Ammo | Clan | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 232 | C LRM/20 Pack | Ammo | Clan | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 234 | C SRM/6 Pack | Ammo | Clan | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |
| 236 | C ST-SRM/2 Pack | Ammo | Clan | (탄약/설명 없음) | 구매 목록·장착 모두 없음 |

**구매 범위별 정리**

- 캠페인(원본·확장)에서 한 번도 안 나오는 구매 항목: 16 C Sensor - Basic, 17 C Sensor - Adv, 42 C ECM Suite, 43 C Active Probe, 98 Rail Gun, 110 C Lt. Ultra Autocannon, 111 C  Ultra Autocannon, 112 C Hvy Ultra Autocannon, 113 C Gauss Rifle, 116 C Light LBX, 117 C LBX Autocannon, 118 C Heavy LBX Autocannon, 126 Heavy Thunderbolt, 130 C LR Missile Rack, 133 C SR Missile Pack, 135 C ST-SR Missile Pack, 150 C Large ER Laser, 151 C Large PS Laser, 152 C ER Laser, 153 C Pulse  Laser, 154 C ER PPC, 155 C Heavy Flamer. 클랜 부품 전체가 여기에 속하며, 클랜 메크를 구매 가능하게 하려면 함께 열어야 한다.
- 확장 캠페인에서만 나오는 항목: 99 Light Gauss Rifle, 107 Light LBX Autocannon, 108 LBX Autocannon, 109 Heavy LBX Autocannon, 139 Large X Pulse Laser, 160 Long Tom.
- 장착은 되지만 구매는 불가: Small Laser(156, 엘리멘탈·차량 전용), 모든 탄약 항목(탄약은 무기 장착 시 함께 붙는 구조로 추정, 구매 목록에 없음).
- 구조 항목(엔진 2·3, 방열기 7~9, Gyro I 23, 파워앰프 24, 페로 25~28, 엔도 29~30, CASE 31~32)은 프로필에 `[Item]`으로 들어가지 않고 `[Engine]/[HeatSinks]/[Armor]` 필드로 표현되므로 "미사용"으로 보지 않았다.
- Sniper Cannon(161)은 구매 목록·프로필 대신 `XSTART0.PKK` 첫 패킷의 컴포넌트 재고(수량 0)에만 이름이 보인다.

## 6. 파일럿

`PMW*.FIT` 324개 중 어떤 미션 워리어·구매 목록·시작 로스터에도 안 나오는 것이 208개다. 대부분은 AI 숙련도 등급별 범용 파일럿(Clan/Allied Green~Elite 등)이다.

| 그룹 | 개수 | 참조됨 | 미참조 | 미참조 예 |
|---|---|---|---|---|
| AI 등급별 범용(110-206) | 73 | 9 | 64 | Clanner, Clanner, Clanner, Clanner, Clanner, Clanner ... |
| AI 등급별 범용(300-459) | 160 | 40 | 120 | Clan, Clan, Clan, Clan, Clan, Clan ... |
| 개발 테스트(14-20,35) | 8 | 0 | 8 | Regular 1, Regular 2, Regular 3, Green 1, Green 2, Green 3 ... |
| 개발자 이름 파일럿(4-13) | 10 | 0 | 10 | WICCED, REBEL, SABER, DRAGON, DREAMER, BLACKJACK ... |
| 기타(1-3 등) | 3 | 3 | 0 |  |
| 미션용 AI 범용(22-34,100) | 14 | 14 | 0 |  |
| 민간 차량(1000) | 1 | 0 | 1 | Civilian Vehicle |
| 차량 승무원(81-85) | 5 | 0 | 5 | CREW, Crew, Crew, Crew, Crew |
| 캠페인 고용 풀(51-80) | 30 | 30 | 0 |  |
| 확장 고용 풀(86-97,102-109) | 20 | 20 | 0 |  |

**영입 풀**

- 원본 캠페인 영입 풀은 PMW00051~00080(30명). `purchase*.fit`의 `[WarriorN] Status` 4는 UNSEEN, 0은 AVAILABLE이다. 시작 로스터(`START0.PKK`)는 Hawk·Lynx·Hunter·Beast 4명이다. **어떤 목록에서도 Status 0이 아닌 파일럿**: MYSTIQUE(PMW00057, AI 출연 19개 미션이 워리어 슬롯으로 참조), HUNTER(PMW00065, AI 출연 19개 미션이 워리어 슬롯으로 참조), LYNX(PMW00066, AI 출연 15개 미션이 워리어 슬롯으로 참조), FALCON(PMW00071, AI 출연 7개 미션이 워리어 슬롯으로 참조), FIRESTORM(PMW00079, AI 출연 20개 미션이 워리어 슬롯으로 참조). 이 중 Hunter·Lynx는 시작 로스터라 정상이고, 나머지 Mystique·Falcon·Firestorm은 영입할 수 없다.
- 확장 영입 풀은 PMW00086~00097, 00102~00109(20명, 대부분 원본 이름의 재스탯 복제본). 00098~00101 번호는 비어 있다(00100은 Elemental 파일럿). 모두 Status 0이 되는 시점이 있다.
- 개발자 이름을 딴 파일럿(PMW00004~00013: David Abzug 'WICCED', Scott Janssen 'REBEL', Tom Dowd 'SABER', Rob Nicholls 'DRAGON', Robyn Tisch 'DREAMER', Tonya Labonte 'BLACKJACK', Jamie Marshall 'CORSAIR', Charles Oines 'PUNISHER', Academy Instructor 'PRINCIPAL', John Giovannoni 'SICILIAN')는 어디서도 안 쓰인다. PMW00030 'Do not use'는 MISE303에서만, PMW00035 'fsdf'는 어디서도 안 쓰인다.

**`war*.fit` 개발 파일럿**: `war001~war011`(+`war002a`, `WAR003a`; 13개 파일, 11명). 모두 어떤 FIT·ABL·EXE에서도 참조되지 않는다. 구 스키마(`Profile=`, `TargetingShort/Medium/Long`)라 현재 `PMW`(Gunnery) 형식과 호환되지 않는다.

| 파일 | 이름 | 콜사인 | ID | 영상 | 그림 | Targeting S/M/L |
|---|---|---|---|---|---|---|
| war001.fit | Amy Bios | SUCKUP | 1000 | plt1g001 | pilot6.gif | 75/50/50 |
| war002.fit | Glenn Doren | BITMAN | 1010 | plt1n001 | pilot3.gif | 100/100/100 |
| war002a.fit | Glenn Doren | CENTURION | 1010 | plt1n001 | pilot3.gif | 100/100/100 |
| WAR003.FIT | Frank Savage | BUNG | 1020 | plt1r001 | pilot4.gif | 50/50/50 |
| WAR003a.fit | Frank Savage | COMMANDO | 1020 | plt1r001 | pilot4.gif | 50/50/50 |
| WAR004.FIT | Jon Marcus | Lord Bunny | 1030 | - | pilot1.gif | 50/50/50 |
| WAR005.FIT | Scott Janssens | LUCIFER | 1040 | - | - | 50/50/50 |
| War006.fit | Kermit | KERMY | 1050 | - | - | 50/50/50 |
| War007.fit | Fozzie | FOZ | 1060 | - | - | 50/50/50 |
| War008.fit | Piggy | PIG | 1070 | - | - | 90/90/90 |
| war009.fit | Todd Labonte | ANIMBOY | 1000 | plt1g001 | pilot7.gif | 100/100/100 |
| war010.fit | Jamie Marshall | BITBOY | 1000 | plt1g001 | pilot8.gif | 100/100/100 |
| war011.fit | Charles Oines | COLORBOY | 1000 | plt1g001 | pilot1.gif | 90/100/100 |

**캠페인 영입 풀 상태**

| 프로필 | 콜사인 | 구매 목록 Status 집합 | 미션 워리어 슬롯 참조 수(대부분 플레이어 소대 자리표시) | 비고 |
|---|---|---|---|---|
| PMW00051 | BEAST | 0,4 | 20 |  |
| PMW00052 | HAWK | 0,4 | 20 |  |
| PMW00053 | SIREN | 0,4 | 19 |  |
| PMW00054 | ROOSTER | 0,4 | 20 |  |
| PMW00055 | ISIS | 0,4 | 23 |  |
| PMW00056 | GUNMAN | 0,4 | 23 |  |
| PMW00057 | MYSTIQUE | 4 | 19 | 영입 불가 |
| PMW00058 | SKATER | 0,4 | 18 |  |
| PMW00059 | SPICE | 0,4 | 10 |  |
| PMW00060 | BARON | 0,4 | 9 |  |
| PMW00061 | FIEND | 0,4 | 13 |  |
| PMW00062 | RONIN | 0,4 | 6 |  |
| PMW00063 | GATOR | 0,4 | 11 |  |
| PMW00064 | REBEL | 0,4 | 11 |  |
| PMW00065 | HUNTER | 4 | 19 | 영입 불가 |
| PMW00066 | LYNX | 4 | 15 | 영입 불가 |
| PMW00067 | HITMAN | 0,4 | 23 |  |
| PMW00068 | COUNTESS | 0,4 | 14 |  |
| PMW00069 | SCARAB | 0,4 | 16 |  |
| PMW00070 | OUTLAW | 0,4 | 8 |  |
| PMW00071 | FALCON | 4 | 7 | 영입 불가 |
| PMW00072 | BURNOUT | 0,4 | 12 |  |
| PMW00073 | GOBLIN | 0,4 | 15 |  |
| PMW00074 | MANTIS | 0,4 | 20 |  |
| PMW00075 | DRAGON | 0,4 | 21 |  |
| PMW00076 | BLAZE | 0,4 | 14 |  |
| PMW00077 | THUNDER | 0,4 | 14 |  |
| PMW00078 | PAINGOD | 0,4 | 13 |  |
| PMW00079 | FIRESTORM | 4 | 20 | 영입 불가 |
| PMW00080 | VIXEN | 0,4 | 15 |  |

**미사용 파일럿 약력 (desc.fit Desc331~342)**

| Desc | 이름 | 본문 |
|---|---|---|
| 331 | Apollo | (본문 비어 있음) |
| 332 | Boomer | Raised on an isolated Periphery world, Boomer's dialect is more than difficult to understa... |
| 333 | Detox | You won't find this MechWarrior in the barracks- Detox's `Mech is his home. Unfortunately,... |
| 334 | Ghost | Quiet and aloof without tons of hardened metal around her, Ghost comes alive on the battle... |
| 335 | Jinx | Her nickname comes not from the effect she has on teammates, but on the bad luck that seem... |
| 336 | Needle | A military brat, Needle knows nothing but military life. But, unlike her siblings, she has... |
| 337 | Pyro | Pyro earned his name for reasons you can well imagine. His obsession, however, aptly conce... |
| 338 | Sponge | Sponge owns nothing that he did not beg, borrow, or steal from someone. Even his callsign,... |
| 339 | Squid | Squid's callsign is a holdover from his days as a green MechWarrior. A rookie no longer, S... |
| 340 | Toad | The veteran Toad is even grumpier out of the cockpit than in. To that end, his superiors t... |
| 341 | Vandal | To many, it seems amazing that Vandal has lived as long as he has. If there is a risk to b... |
| 342 | Wasp | Wasp loves recon work, the lighter and faster the `Mech the better. Fortunately, few can p... |

약력이 있는 영입 파일럿은 301~330(PMW51~80)과 343~350(확장 PMW102~109)이며, 331~342만 주인이 없다. `localization/ko/desc_notes.md`가 Jinx(335)와 Apollo(331)를 "어떤 번역문에도 이름이 안 나온다"고 한 것과 일치한다.

## 7. 브리핑·문자열

### 7.1 참조되지 않는 브리핑 22개

| 파일 | 내용 | 대응하는 사용 중 파일 |
|---|---|---|
| brf0304c.txt | 개발자 장난 'GLENN ROCKS THE HOUSE'. 클랜 전사 구출 버전 | brf0304.txt(IS 전사 구출, 'LIBERATE RE-EDUCATION CAMP') |
| brf0304s.txt | MIS0304 구판. 목표 항목·시간제한·화력 지원 줄 없이 간단한 문단 구성 | brf0304.txt |
| Cbrf0701hh.txt | HOUNDS AND HARES(클랜 측): 생존 목표 | Cbrf0701.txt(CAPTURE ENEMY BASE) |
| ISbrf0701hh.txt | HOUNDS AND HARES(IS 측): 적 추적 섬멸 | ISbrf0701.txt |
| Cbrf0701k.txt | CANYON COMBAT: 적 섬멸 목표 버전 | Cbrf0701.txt와 69% 동일 |
| Cbrf0702.txt | MANY BASES: 모든 적 유닛 파괴(클랜) | Cbrf0702b5.txt(실사용) |
| ISbrf0702.txt | MANY BASES: 모든 적 유닛 파괴(IS).  | ISbrf0702b5.txt |
| Cbrf0702mb.txt | MANY BASES MB: 가장 많은 기지를 점령한 쪽이 승리(시간제) | Cbrf0702b5.txt |
| ISbrf0702mb.txt | MANY BASES MB(IS 측) | ISbrf0702b5.txt |
| Cbrf0704k.txt | OVER THE TOP: 모든 적 섬멸(클랜) | Cbrf0704.txt(King of the Hill) |
| ISbrf0704k.txt | OVER THE TOP: 모든 적 섬멸(IS) | ISbrf0704.txt |
| Cbrf0705c.txt | BIG BASE TANGO C: 기지 HQ 점령(클랜) | Cbrf0705.txt와 96% 동일 |
| Cbrf0705m.txt | BIG BASE TANGO M: 모든 HQ 파괴(클랜) | Cbrf0705.txt와 99% 동일 |
| ISbrf0705m.txt | BIG BASE TANGO M(IS): HQ 1동 방어 | ISbrf0705.txt와 거의 동일 |
| Cbrf0705rs.txt | ROBIN HOOD AND THE SHERIFF(클랜): 생존 또는 기지 HQ 파괴 | Cbrf0705.txt |
| Cbrf0705rsc.txt | ROBIN HOOD AND THE SHERIFF(클랜): 생존 또는 기지 HQ 점령 | Cbrf0705.txt |
| ISbrf0705rs.txt | ROBIN HOOD AND THE SHERIFF(IS): 기지 방어 + 적 섬멸 | ISbrf0705.txt |
| Cbrf0706.txt | POWER SURGE: 모든 발전기 파괴(클랜) | Cbrf0706g46.txt(실사용) |
| ISbrf0706.txt | POWER SURGE: 발전기 최소 1기 방어(IS) | ISbrf0706g46.txt |
| Cbrf0706k.txt | POWER SURGE SHOWDOWN: 발전기 무시하고 적 섬멸 | Cbrf0706g46.txt와 66% 동일 |
| ISbrf0706k.txt | POWER SURGE SHOWDOWN(IS) | ISbrf0706g46.txt와 70% 동일 |
| xbrf0304.txt | 확장 MCX0304 컷 버전 'DESTROY ENGINE DRILLS'. 지휘관 `FEDCOM:<placeholder>`, 목표 2개(드릴·연구시설 파괴), 화력 지원 포격 3/센서 2, '개조된 에이스 터키나 2기' 경고 | xbrf0305.txt(MCX0304 실사용: 드릴 4그룹, Marcus Kotare·Burnell Wirth) |

접미사 규칙으로 보이는 것: `hh`=Hounds and Hares, `k`=Kill(전멸) 변형, `mb`=Most Bases, `rs/rsc`=Robin Hood and the Sheriff(점령/파괴), `c/m`=Capture/Destroy 변형. 저장소의 멀티 시작 파일(`SAVEGAME/MANYBASE.MPK`, `MANYLOCK`, `POWRSURG/POWRSRG2/POWRLOCK`, `CPTRBASE/CPTRLOCK`, `KINGHILL/KINGLOCK` 등)이 이 모드들과 이름이 겹친다. 게임 모드가 접미사 파일을 직접 고르는지는 확인하지 못했다.

### 7.2 문자열 표의 미참조 블록 (`localization/en/strings.json`, `referenced:false` 355개)

| id | 내용 | 의미/시사하는 기능 | 복원 난이도 |
|---|---|---|---|
| 1~28 | 미션 후 메크별 보고(목표 완료/실패, Lance Organization, 'Report for Mech %i of Lance %i', 탄착률, 살비지 목록, 탈출·포획 상태) | 미션 결과 화면의 메크별 보고 기능(컷) | EXE 패치 필요 |
| 37, 88~94 | 'Review campaign briefing.', 'Current Operation/Campaign/Mission Briefing', 'Current BattleMech/Pilot/Component/Vehicle Inventory' | 로지스틱스 화면 머리글(구 UI) | EXE 패치 필요 |
| 96, 97 | 'This version for FIT Use ONLY', 'Pre-Release build Do Not Distribute' | 개발 워터마크 | 해당 없음 |
| 119 | 'Standard' | 목표 유형 단어 (neighbours 120~128은 사용 중) | EXE 패치 필요 |
| 155, 163~165 | '%s Powered Down', 'Building', 'Turret', 'Gate' | 객체 상태/분류어 | EXE 패치 필요 |
| 168~170, 174, 885 | 멀티 세션 문구('Maximum number of players...', 'WAITING FOR HOST...') | 멀티 로비 (일부 경로 미사용) | EXE 패치 필요 |
| 180, 181 | 'Clan', 'Inner Sphere' | 진영명 | EXE 패치 필요 |
| 207~872 중 다수 | 건물 이름(Barn, Command Station, House, Factory, Silo, Billboard, Kurita-Style House, Quonset Hut, Tent, 터렛 전원 등) 약 300개 | 이름 id는 EXE가 번호로 계산해 읽는 방식이라 '미참조' 표시가 반드시 미사용을 뜻하지는 않음(추정) | 확인 필요 |
| 862, 904, 905 | 'Demo', 'Please insert the original MechCommander compact disc.', 'Movie not found' | 데모/CD 체크 오류문 | 해당 없음 |
| 1228, 1248 | 'Lt. Transport', 'Refit Rig' | 대응 프로필 DescIndex 없음(섹션 4) | 데이터만 |

### 7.3 대화상자·하드코딩 문자열

`dialogs.json`의 6개 중 쓸모 있는 단서는 둘이다: ID 105(Exit/Continue/**Debug**/Save/**Email**/**Capture Screen**/**Save Log Files**; 크래시 리포트 대화상자)와 ID 203('Messages Sent/Received', 네트워크 디버그 카운터). `hardcoded_strings.json`에는 복원할 가치가 있는 항목이 없다(플레이어 메시지 8, 개발자 assert 6).

## 8. 지형·스프라이트·사운드·영상

### 8.1 지형 (TERRAIN.FST)

- 지형 세트(`.map/.obj/.elv/.dat/.bdg/.gmm/.lst/.pre/.tga/.fit`)는 모든 미션 FIT가 참조하는 이름과 일치한다. 예외: **mp0704**(대응 FIT 없음, mp0707 구판).
- 반대로 FIT가 지형을 참조하지만 지형이 없는 것: Map0101(E3_0101), 0203(E3_0203), E3_3(MISE303), 0801(MIS0801), testmis1, default(EDITSCEN). 즉 6개 미션이 지형 부재로 재생 불가.
- `TERRAIN.FST`에 섞여 있는 비지형 파일: `MIS0403.ABL`(8209 B, 'Erol Otus 1997-10' 구판. 미션 폴더 것은 18611 B), `mp0701log*.tga`, 각종 `.log`. `m0506`과 `m0506m`은 둘 다 존재(MIS0506·MIS0507 각각).

### 8.2 객체·스프라이트 (OBJECT2.PAK, SHAPES.FST, SPRITES)

- OBJECT2.PAK 1190개 패킷 중 MechType 28, GroundVehicleType 57, ElementalType 2(RoboGlen·Hicks), TrainType 7. 프로필이 없는 MechType 45/55/64/65와 GroundVehicleType 407/413/418/421은 섹션 3·4에 있다. ElementalType 653 Hicks는 `Pem00001`만 가리키고 이 프로필은 어디서도 쓰이지 않는다.
- SHAPES.FST 123개 파일 중 어떤 객체·FIT에도 이름이 안 나오는 것: `airstrik.shp`(`airstrk.shp`를 쓰는 듯), `connect.shp`, `dust30-.shp`, `forestx.shp`, `h2.hsp`+세트, `pause.shp`, `reglaser.shp`, `shadow.shp`, `test.shp`, `tmplaser.shp`, `waypoints.shp`(일부는 EXE 문자열에는 있음 -> 코드가 직접 로드할 가능성). 위 중 `test.shp`, `forestx.shp`, `reglaser.shp`, `tmplaser.shp`, `dust30-.shp`는 이름상 개발 잔재다.
- 로지스틱스 아이콘 계열(`LSPFLMA/J/W`, `LSPFDMA/J/W`, `LSCFLMA/J/W` 등)은 각각 24개씩이라 섀시 24종(IS 13 + 클랜 11)과 일치한다. 프로필이 없는 MechType(45/55/64/65)용 별도 아이콘은 확인하지 못했다.
- 차량 아이콘 계열(`LSPFLV`, `LSCFLV`, `LSPFDV`, `VMASK`)은 각각 35개이고 PV 프로필은 59개다. 즉 구매 목록에 새 차량을 넣으면 아이콘이 없을 수 있다(확인 필요).

### 8.3 영상

- `DATA/MOVIES`: `OPENING`, `CLOSING`, `LOGOS1`, `OPVID1~5`(원본 작전 영상, `purchase.fit`), `MCXVID1~3`(확장 작전 영상, `xpur.fit`), `MCXVID4`(확장 엔딩; `Xmechcmdr1.fit movie3`), `PILOT00~29`×{A,C,D} 90개. 모두 참조된다.
- 부재: `credits`(`mechcmdr1.fit movie2/movie4`) -> `CREDITS.SMK` 없음. `PMW0000x` 일부가 가리키는 `plt1g001/plt1n001/plt1r001/plt1t001`(개발용 파일럿 영상)도 없음.
- `PortArthurBefore/After_Op%i_Mis%i`(문자열 891/890)와 `CermakBefore/After_Op%i_Mis%i`(903/902)는 영상이 아니라 **자동 저장 파일명 서식**이다(원본 캠페인 'Port Arthur', 확장 'Cermak'). `DATA/SAVEGAME/*.sav` 중 이 이름의 파일은 사용자의 플레이 저장이고 출하 콘텐츠가 아니다.

### 8.4 사운드

- `MUSIC00~47.WAV` 중 40개(결번 있음). 미션 FIT의 `scenarioTuneNum` 값은 0(98개 FIT), 2·3·4·5뿐이고 1과 6 이상은 쓰이지 않는다. 곡 번호와 WAV 번호 대응 규칙은 확인하지 못했다.
- `PILOTA~Z`+`PILOTAA~AD`(30개 음성 PAK)는 모두 어떤 PMW가 참조한다. `opilota`, `opilotf`를 요구하는 `PMW00001/00150/01000`은 대응 PAK가 없다. `BETTY.PAK`, `NOISE.PAK`, `SOUND.PAK`은 FIT에는 안 나오지만 코어 자원으로 추정.

## 9. ABL 스크립트

`.abl` 774개 중 178개는 다른 FIT/ABL/ABI 어디에도 이름이 나오지 않고, 67개는 도달 불가한 미션에서만 참조된다. `.abi` 541개 중 참조 없는 것은 7개(`3_4MX(AC,CR,IN,LP,ST,VR).ABI` 6개와 `Orders.ABI`; 후자는 `orders.abx` 라이브러리로 대체)이다.

| 계열 | 개수 | 예 |
|---|---|---|
| dred* (UNIVERSAL WARRIOR BRAIN, 1998-11) | 11 | dredambush01.abl, dredAttack01.abl, dredCircle01.abl, dredDestroy01.abl, dredEscort01.abl ... |
| m0104 계열 (미션 전용 브레인) | 1 | m0104_Nil.ABL |
| m0106 계열 (미션 전용 브레인) | 3 | m0106ul1.ABL, m0106ulc.ABL, m0106ult.ABL |
| m0201 계열 (미션 전용 브레인) | 3 | m0201_Guard3.3.ABL, m0201_Hunter.ABL, m0201_Still.ABL |
| m0202 계열 (미션 전용 브레인) | 4 | m0202bb2.ABL, M0202BD.ABL, M0202E.ABL, m0202fctry.ABL |
| m0203 계열 (미션 전용 브레인) | 4 | m0203ec.ABL, m0203kmk.ABL, m0203mi3.ABL, m0203t2.ABL |
| m0205 계열 (미션 전용 브레인) | 2 | m0205air.ABL, m0205ul.ABL |
| m0301 계열 (미션 전용 브레인) | 1 | m0301amb.abl |
| m0302 계열 (미션 전용 브레인) | 1 | m0302Block.ABL |
| m0303 계열 (미션 전용 브레인) | 1 | m0303guard3.ABL |
| m0305 계열 (미션 전용 브레인) | 2 | m0305elem.ABL, m0305Test.ABL |
| m0306 계열 (미션 전용 브레인) | 1 | M0306madcat.ABL |
| m0403 계열 (미션 전용 브레인) | 17 | m0403_base3.1.ABL, m0403_jump1.ABL, m0403_snip1.ABL, m0403bp.ABL, m0403delay-1.ABL ... |
| m0405 계열 (미션 전용 브레인) | 1 | m0405scoutd.ABL |
| m0406 계열 (미션 전용 브레인) | 25 | m0406_1Archer4.ABL, m0406_1Clog.ABL, m0406_2Archer1.ABL, m0406_Ammo1.ABL, m0406_Atlas.ABL ... |
| m0501 계열 (미션 전용 브레인) | 1 | m0501cgrs.ABL |
| m0502 계열 (미션 전용 브레인) | 17 | m0502_test.ABL, m0502A1.ABL, m0502A2.ABL, m0502A2Rommel.ABL, m0502A4.ABL ... |
| m0503 계열 (미션 전용 브레인) | 8 | m0503_Booster2.1.ABL, m0503_defender1.1.ABL, m0503_defender1.2.ABL, m0503_defender1.3.ABL, m0503_defender1.5.ABL ... |
| m0504 계열 (미션 전용 브레인) | 4 | m0504d2final.ABL, m0504guard.ABL, m0504test.ABL, m0504testd1.ABL |
| m0505 계열 (미션 전용 브레인) | 3 | m0505a.ABL, m0505HillNE1.ABL, m0505Uber.ABL |
| m0507 계열 (미션 전용 브레인) | 4 | m0507patrolc.ABL, m0507patrold.ABL, m0507patrole.ABL, m0507patrolf.ABL |
| mx0103 계열 (미션 전용 브레인) | 1 | mx0103ambush2.ABL |
| mx0104 계열 (미션 전용 브레인) | 2 | mx0104civvy2.ABL, mx0104patrolA1.ABL |
| mx0201 계열 (미션 전용 브레인) | 1 | mx0201WHV.ABL |
| mx0301 계열 (미션 전용 브레인) | 3 | mx0301convoy4.ABL, mx0301null.ABL, mx0301vult.ABL |
| mx0303 계열 (미션 전용 브레인) | 3 | mx0303ace.ABL, mx0303pwrguard.ABL, mx0303vaultpatrol.ABL |
| mx0304 계열 (미션 전용 브레인) | 16 | mx0304_1BackDodoPatrol.ABL, mx0304_1DodoPatrol.ABL, mx0304_1JabberPatrol.ABL, mx0304_2BackDodoPatrol.ABL, mx0304_2DodoPatrol.ABL ... |
| mx0402 계열 (미션 전용 브레인) | 1 | mx0402miner.ABL |
| 범용 클랜/AI 브레인 (c*, chk*, cgd*, trt*, ClanMiss1Part*) | 37 | cat0000.abl, Catk05011.abl, Catk05012.abl, cbrain01.abl, cbrain101.abl ... |

해석: ① `mx0304*`(16개)는 섹션 2·10의 컷 MCX0304 버전의 스크립트다(Dodo/Jabber 순찰, Alacorn Research, Drill Alarm/Protect). 최종판은 `mx0305*`를 쓴다. ② `mx0303ace.ABL`, `mx0301vult.ABL`은 에이스 전용 브레인으로 보이나 MCX0303·MCX0301 FIT가 참조하지 않는다. ③ `m0403delay-1~6`/`delayed1~5` 등 MIS0403·0406·0502의 변형 브레인은 최종 FIT가 쓰지 않는 이전 설계다. ④ `dred*01.abl`(11개, 1998-11 david abzug)은 데이터 입력 도구가 생성한 범용 워리어 브레인 한 벌로 어떤 미션도 쓰지 않는다. ⑤ `ClanMiss1Part4~7`, `Cbrain101~106`, `cbrain01`, `ebrain01`은 `ClanBrain003`/엘리멘탈 브레인 같은 1997년식 `MI_MODE` 구조로 새 `c*`/`m*` 브레인으로 대체된 구판이다.

도달 불가 미션 전용 스크립트(멀티 제외): abrain01.abl <- E3_0101A.FIT, cgs0000.abl <- E3_0101A.FIT, MIS0801.FIT, cgs0101.abl <- MIS0801.FIT, cgs0101a.abl <- E3_0101.FIT, E3_0101A.FIT, MISE303.FIT, cgs0101b.abl <- E3_0101.FIT, E3_0101A.FIT, cgs0101c.abl <- E3_0101.FIT, E3_0101A.FIT, CGS0203a.abl <- E3_0203.FIT, CGS0801A.abl <- MIS0801.FIT, MISE303.FIT, cgs0801b.abl <- MIS0801.FIT, CGS0801c.abl <- MIS0801.FIT, cgsE303a.abl <- MISE303.FIT, cgsE303b.abl <- MISE303.FIT, cpl0101b.abl <- E3_0101.FIT, E3_0101A.FIT, cpl0101e3a.abl <- E3_0101.FIT, E3_0101A.FIT, CPL0203A.abl <- E3_0203.FIT, CPL0203B.abl <- E3_0203.FIT, CPL0203C.abl <- E3_0203.FIT, CPL0203D.abl <- E3_0203.FIT, CPL0203E.abl <- E3_0203.FIT, CPL0203F.abl <- E3_0203.FIT, E3_0101.abl <- E3_0101.FIT, E3_0101a.abl <- E3_0101A.FIT, mechcmdr1.fit, E3_0203.ABL <- E3_0203.FIT, mechcmdr1.fit, editscen.abl <- EDITSCEN.FIT, joy9.ABL <- testmis1.FIT, m0506Enter.ABL <- MIS0506.FIT, m0506nw.ABL <- MIS0506.FIT, m0506nw2.ABL <- MIS0506.FIT, m0506PatrolA.ABL <- MIS0506.FIT, m0506PatrolB.ABL <- MIS0506.FIT, m0506patrolc.ABL <- MIS0506.FIT, m0506patrold.ABL <- MIS0506.FIT, m0506patrole.ABL <- MIS0506.FIT, MISE303.ABL <- MISE303.FIT, mechcmdr1.fit, sbrain01.abl <- MIS0801.FIT, testmis1.ABL <- mechcmdr1.fit, testmis1.FIT

## 10. 컷 미션 두 건의 증거 요약

**MCX0304 초안 ('Destroy Engine Drills')**: `xbrf0304.txt`(지휘관 `<placeholder>`; 목표 '엔진 드릴 파괴, 연구시설 파괴'; 에이스 터키나 2기 경고), `mx0304*.ABL` 16개, 터키나 에이스 프로필 `PM211350`(Kotare)·`PM211450`(Wirth)가 최종판 MCX0304에 그대로 남아 있다. 지형 `MX0304`는 없고 최종판은 `MX0305`를 쓴다. 헤더의 미션명은 'Him Give me Smaller Banana'(개발자 농담)이다.

**MIS0506 ↔ MIS0507**: MIS0506(1998-04-08, 'Blood Makes the Grass Grow', 목표 'Placeholder', 파트 40개, 드롭존 3)와 MIS0507(1998-06-03, 헤더 'Mid 0506', 목표 4개: 터릿 포획/무력화 + 궤도포 3곳 파괴, 파트 49개)이 같은 `brf0506.txt`를 공유한다. 캠페인은 MIS0507만 쓴다. 따라서 MIS0506은 최종 마지막 미션의 이전 설계로 보이며, 둘 중 어느 쪽이 작전 5의 '6번째'인지는 `mechcmdr1.fit`(Op5 Mission6=mis0507)이 결정했다.

## 11. 확인 못 한 것

- `LastScenario`의 정확한 의미(마지막 인덱스인지, 종료 처리 조건인지). 값 29가 mis0507과 일치해서 "마지막 인덱스"로 가정했다. 바꿔서 실제로 이어지는지는 게임 실행이 필요해 확인하지 않았다.
- 구매 목록이 클랜 메크·새 차량·새 파일럿을 수용하는지(UI 슬롯 수, 아이콘 부재 시 동작). 멀티·솔로 목록은 클랜 메크를 표시하므로 되는 쪽이 유력하나 캠페인 경로는 미검증.
- 진행 중인 세이브의 영향: 구매 목록은 미션 전환 시 `purchaseNN.fit`에서 다시 읽는 것으로 추정하나 PKK 세이브가 재고를 보존하는지는 미확인.
- 멀티 맵 선택 UI가 어떤 FIT를 노출하는지, 그리고 게임 모드(hh/k/mb/rs 등)가 접미사 브리핑을 동적으로 고르는지. EXE의 `%s*.fit` 열거와 `.MPK` 로딩 경로를 디스어셈블해야 확정 가능.
- ABL '미참조' 판정은 이름 토큰 검색 결과다. EXE가 `sprintf`로 브레인 이름을 조립하는 경우는 놓칠 수 있다. 특히 `m0403delay-N`처럼 번호가 붙은 스크립트.
- 문자열 207~872 구간의 건물 이름 id: `referenced:false`가 많으나 객체 번호에서 계산하는 방식이라 미사용 여부를 가르지 못했다.
- `Menus.fit`, `mechint.fit`, `engine.fit`, `EDITSCEN.FIT`는 EXE에서 이름이 직접 보이지 않지만(`%s%s.fit` 서식 로드 가능) 사용 여부를 확정하지 못했다. `Menus.fit`의 `GEC_*` 명령 항목 중 최종 UI에 없는 것이 있는지도 미확인.
- 음악 번호(`scenarioTuneNum` 0~5)와 `MUSIC00~47.WAV`의 대응, 미사용 곡 목록.
- ART.FST 전체(1651개) 중 사용되지 않는 이미지. 아트는 이름이 아니라 인덱스로 로드되어 이름 검색으로는 미사용을 판정할 수 없었다.
- TERRAIN의 `.obj`에 배치된 건물·나무 객체 중 한 번도 쓰이지 않은 OBJECT2 타입(건물·나무 약 1000종).
- MIS0506/E3_0101A를 실제로 로드했을 때의 동작(프로필 부재 경고, 브리핑 누락, AI 전술 등). 게임 실행 금지 조건이라 정적 분석까지만 했다.
- 헌정 Easter egg 요소: `brf0304c.txt`의 'GLENN ROCKS THE HOUSE', 개발자 이름 파일럿(PMW00004~13)은 출하 의도가 없는 개발 흔적으로 분류했다.

## 부록: 산출물 관련

- 스크립트는 세션 스크래치패드 `unused/`에 있고 저장소에는 넣지 않았다. 구조화 데이터는 `docs/unused-content.json`(항목별 `category, file, name, used_by, missing, restore_how, effort`)이다.
- 사용한 기존 인벤토리: `localization/en/strings.json`, `briefings.json`, `dialogs.json`, `hardcoded_strings.json`, `localization/ko/fit_strings_notes.md`, `desc_notes.md`.
