# Proper nouns in the pre-mission texts and their glossary coverage

Scope: the 48 in-scope briefings of `MISSION.FST` (32 original `brf*.txt` incl. the unreferenced `brf0304c/s`, 13 expansion `xbrf*.txt` incl. the unreferenced `xbrf0304`, 3 solo `xsbrf*.txt`), plus the other pre-mission sources (desc.fit pilot bios and descriptions, EXE strings, name plates, operation cards). Multiplayer briefings are out of scope.

Method: every capitalised word and word sequence of the 48 files was extracted with a script (564 distinct capitalised words, 630 sequences), sorted by hand into proper nouns vs. ordinary headline words (DESTROY, CAPTURE, TACTICAL ...), and each proper noun below was re-searched in the 48 files with a regular expression; the 'files' column is the result of that search. Generic structure names (Turret Control Tower, Sensor Control, Repair Bay ...) are not proper nouns; they are in the glossary category `structures_objectives`.

**Result: 145 of 145 briefing proper nouns covered, 31 of 31 other-source names covered (100%).**

## 1. Briefings (48 files)

| proper noun | type | files | where (first 6) | glossary category | ko | covered |
|---|---|---:|---|---|---|---|
| Mystique | person (pilot) | 1 | brf0103 | pilots | 미스틱 | yes |
| Firestorm | person (pilot) | 1 | brf0401 | pilots | 파이어스톰 | yes |
| Akodo Haru (Captain Akodo Haru / Captain Haru) | person | 1 | brf0106 | places_factions | 아코도 하루 | yes |
| Piotrev (Bondsman Major Piotrev) | person | 1 | brf0301 | places_factions | 피오트레프 | yes |
| Reese (Colonel Reese) | person | 1 | brf0401 | places_factions | 리스 | yes |
| Nairn (Captain / Cpt. Nairn) | person | 3 | brf0501, brf0502, xsbrf0404 | places_factions | 네언 | yes |
| Katherine Furey | person | 1 | xbrf0103 | places_factions | 캐서린 퓨리 | yes |
| Marcus Osis | person | 1 | xbrf0202 | places_factions | 마커스 오시스 | yes |
| Rathbun | person | 1 | xbrf0204 | places_factions | 래스번 | yes |
| Dulaney | person | 1 | xbrf0204 | places_factions | 덜레이니 | yes |
| Kulin | person | 1 | xbrf0204 | places_factions | 쿨린 | yes |
| Marcus Kotare | person | 1 | xbrf0305 | places_factions | 마커스 코타레 | yes |
| Burnell Wirth | person | 1 | xbrf0305 | places_factions | 버넬 워스 | yes |
| Glenn | person (dev joke) | 1 | brf0304c | places_factions | 글렌 | yes |
| Port Arthur | planet | 3 | brf0105, brf0204, xsbrf0404 | places_factions | 포트 아서 | yes |
| Cermak | planet | 1 | xbrf0301 | places_factions | 세르막 | yes |
| Kathil | planet | 2 | xbrf0301, xbrf0302 | places_factions | 캐실 | yes |
| Clairesfield | place | 1 | brf0104 | places_factions | 클레어스필드 | yes |
| Vanderhome | place | 1 | brf0105 | places_factions | 밴더홈 | yes |
| Kaio (Kaio Industrial Zone) | place | 1 | brf0106 | places_factions | 카이오 산업 지구 | yes |
| Froese River | place | 1 | brf0201 | places_factions | 프로즈 강 | yes |
| Ai-Ki River | place | 1 | brf0202 | places_factions | 아이키 강 | yes |
| Bakerville | place | 1 | brf0203 | places_factions | 베이커빌 | yes |
| Yokohama | place | 1 | brf0204 | places_factions | 요코하마 | yes |
| Serpent Bay | place | 1 | brf0206 | places_factions | 서펀트 만 | yes |
| Affendale | place | 3 | brf0303, brf0305, brf0306 | places_factions | 애펀데일 | yes |
| Kenuk River | place | 1 | brf0303 | places_factions | 케눅 강 | yes |
| Mayan Canyons | place | 3 | brf0304, brf0304c, brf0304s | places_factions | 마야 협곡 | yes |
| Mount Samurai | place | 1 | brf0306 | places_factions | 사무라이 산 | yes |
| Field Hospital Delta | place | 1 | brf0302 | places_factions | 델타 야전 병원 | yes |
| Kylemartin (depot) | place | 1 | brf0402 | places_factions | 카일마틴 | yes |
| Cambridge | place | 1 | brf0403 | places_factions | 케임브리지 | yes |
| Chresbute | place | 1 | brf0502 | places_factions | 크레스뷰트 | yes |
| Bellum | place | 1 | brf0503 | places_factions | 벨룸 | yes |
| Weisman Fuel Depot and Processing Station | place | 1 | brf0504 | places_factions | 와이즈먼 연료 저장소 및 처리 시설 | yes |
| Lambert Valley | place | 1 | brf0505 | places_factions | 램버트 계곡 | yes |
| Miasota Basin | place | 1 | brf0505 | places_factions | 미아소타 분지 | yes |
| Starbase | place (Clan base) | 6 | brf0501, brf0502, brf0503, brf0504, brf0505, brf0506 | places_factions | 스타베이스 | yes |
| Base Nomad | place | 2 | xbrf0102, xbrf0103 | places_factions | 노마드 기지 | yes |
| Baitan sector | place | 2 | xbrf0103, xbrf0104 | places_factions | 바이탄 구역 | yes |
| Base Ogre | place | 2 | xbrf0104, xbrf0201 | places_factions | 오거 기지 | yes |
| Azimuth sector | place | 2 | xbrf0201, xbrf0203 | places_factions | 애지머스 구역 | yes |
| Jade sector | place | 1 | xbrf0202 | places_factions | 제이드 구역 | yes |
| Base Kraken | place | 1 | xbrf0301 | places_factions | 크라켄 기지 | yes |
| Rehold Mountains | place | 1 | xsbrf0402 | places_factions | 리홀드 산맥 | yes |
| Land Bridge | place (terrain) | 1 | xbrf0302 | places_factions | 지협 | yes |
| Alpha | designator | 4 | brf0101, brf0406, brf0503, xbrf0305 | places_factions | 알파 | yes |
| Beta | designator | 4 | brf0101, brf0406, brf0503, xbrf0305 | places_factions | 베타 | yes |
| Gamma | designator | 3 | brf0406, brf0503, xbrf0305 | places_factions | 감마 | yes |
| Delta | designator | 2 | brf0302, xbrf0305 | places_factions | 델타 | yes |
| Smoke Jaguar(s) | faction | 15 | brf0101, brf0103, brf0105, brf0106, brf0202, brf0204 (+9) | places_factions | 스모크 재규어 | yes |
| Jaguar(s) (short form) | faction | 16 | brf0105, brf0202, brf0203, brf0204, brf0301, brf0302 (+10) | places_factions | 재규어 | yes |
| Smoke Jaguar Command Force | unit | 1 | xbrf0303 | places_factions | 스모크 재규어 지휘군 | yes |
| Jaguar Main Command | unit | 1 | xbrf0305 | places_factions | 재규어 주 사령부 | yes |
| Jaguar Complex | place | 1 | xbrf0305 | places_factions | 재규어 단지 | yes |
| Clan(s) | faction | 30 | brf0101, brf0102, brf0104, brf0201, brf0203, brf0206 (+24) | places_factions | 클랜 | yes |
| Clanners | faction slang | 2 | xbrf0201, xsbrf0402 | pilots | 클래너 | yes |
| ClanWarriors | faction | 1 | brf0502 | places_factions | 클랜워리어 | yes |
| Bondsman / Bondsmen | faction | 8 | brf0101, brf0102, brf0103, brf0106, brf0204, brf0301 (+2) | places_factions | 본즈맨 | yes |
| Inner Sphere | faction | 7 | brf0304, brf0304s, brf0502, xbrf0301, xbrf0302, xsbrf0401 (+1) | places_factions | 이너 스피어 | yes |
| IS | faction (acronym) | 1 | xsbrf0404 | places_factions | IS | yes |
| Kurita | faction | 1 | brf0201 | places_factions | 쿠리타 | yes |
| DEST | unit (acronym) | 2 | brf0201, brf0202 | places_factions | DEST | yes |
| Zulu Company | unit | 2 | brf0101, brf0504 | places_factions | 줄루 중대 | yes |
| X-Ray Company | unit | 1 | brf0501 | places_factions | 엑스레이 중대 | yes |
| Galaxy | unit size (Clan) | 1 | brf0204 | places_factions | 갤럭시 | yes |
| Binary | unit size (Clan) | 2 | brf0501, brf0502 | ranks_titles | 바이너리 | yes |
| Star (Clan unit) | unit size (Clan) | 2 | brf0503, xbrf0201 | ranks_titles | 스타 | yes |
| Lance | unit size | 3 | brf0505, xsbrf0402, xsbrf0404 | ranks_titles | 랜스 | yes |
| Company | unit size | 5 | brf0101, brf0501, brf0504, brf0506, xsbrf0402 | ranks_titles | 중대 | yes |
| Battalion | unit / HQ | 11 | brf0101, brf0102, brf0105, brf0201, brf0202, brf0203 (+5) | ranks_titles | 대대 | yes |
| Battalion Transport | organisation | 6 | brf0101, brf0102, brf0105, brf0201, brf0203, brf0401 | ranks_titles | 대대 수송대 | yes |
| Battalion Intelligence / Intelligence | organisation | 18 | brf0104, brf0202, brf0203, brf0205, brf0301, brf0306 (+12) | ranks_titles | 정보부 | yes |
| Tactical (staff) | organisation | 4 | brf0105, brf0403, xbrf0103, xbrf0104 | ranks_titles | 전술부 | yes |
| Strategic (staff) | organisation | 4 | xbrf0201, xbrf0203, xbrf0302, xbrf0305 | ranks_titles | 전략부 | yes |
| Recon | organisation | 10 | xbrf0102, xbrf0103, xbrf0104, xbrf0201, xbrf0202, xbrf0203 (+4) | ranks_titles | 정찰대 | yes |
| Command | organisation | 1 | xsbrf0402 | ranks_titles | 사령부 | yes |
| Special Forces | organisation | 1 | brf0201 | ranks_titles | 특수부대 | yes |
| Partisans | organisation | 1 | brf0401 | ranks_titles | 유격대 | yes |
| Jade Falcon(s) | faction | 1 | xsbrf0401 | places_factions | 제이드 팰컨 | yes |
| Wolf-Clan-In-Exile | faction | 1 | xsbrf0401 | places_factions | 망명 울프 클랜 | yes |
| Star League / Starleague | faction (historic) | 8 | xbrf0104, xbrf0201, xbrf0204, xbrf0301, xbrf0303, xbrf0304 (+2) | places_factions | 스타 리그 | yes |
| FEDCOM | dispatch prefix | 46 | brf0101, brf0102, brf0103, brf0104, brf0105, brf0106 (+40) | places_factions | FEDCOM | yes |
| STARCOM | dispatch prefix | 2 | xsbrf0401, xsbrf0404 | places_factions | STARCOM | yes |
| BEACHHEAD | operation | 6 | brf0101, brf0102, brf0103, brf0104, brf0105, brf0106 | places_factions | 비치헤드 | yes |
| SKYHOOK | operation | 6 | brf0201, brf0202, brf0203, brf0204, brf0205, brf0206 | places_factions | 스카이훅 | yes |
| VANGUARD | operation | 6 | brf0301, brf0302, brf0303, brf0304, brf0305, brf0306 | places_factions | 뱅가드 | yes |
| LINCHPIN | operation | 6 | brf0401, brf0402, brf0403, brf0404, brf0405, brf0406 | places_factions | 린치핀 | yes |
| CUTTHROAT | operation | 6 | brf0501, brf0502, brf0503, brf0504, brf0505, brf0506 | places_factions | 컷스로트 | yes |
| HYDRA | operation | 4 | xbrf0101, xbrf0102, xbrf0103, xbrf0104 | places_factions | 하이드라 | yes |
| GORGON | operation | 4 | xbrf0201, xbrf0202, xbrf0203, xbrf0204 | places_factions | 고르곤 | yes |
| MINOTAUR | operation | 4 | xbrf0301, xbrf0302, xbrf0303, xbrf0305 | places_factions | 미노타우로스 | yes |
| SOLO | operation code | 3 | xsbrf0401, xsbrf0402, xsbrf0404 | places_factions | 솔로 | yes |
| HUNTER | operation code (dev) | 2 | brf0304c, brf0304s | places_factions | 헌터 | yes |
| PORT ARTHUR REDUX | mission title | 1 | xsbrf0404 | places_factions | 포트 아서 리덕스 | yes |
| Commander | title | 5 | brf0401, brf0501, xsbrf0401, xsbrf0402, xsbrf0404 | ranks_titles | 지휘관 | yes |
| Captain | rank | 4 | brf0106, brf0501, brf0502, xbrf0103 | ranks_titles | 대위 | yes |
| Cpt. | rank | 1 | xsbrf0404 | ranks_titles | 대위 | yes |
| Major | rank | 1 | brf0301 | ranks_titles | 소령 | yes |
| Colonel | rank | 1 | brf0401 | ranks_titles | 대령 | yes |
| Star Captain | rank (Clan) | 2 | xbrf0202, xbrf0204 | ranks_titles | 스타 캡틴 | yes |
| Star Colonel | rank (Clan) | 1 | xbrf0305 | ranks_titles | 스타 커널 | yes |
| Clan Captain | rank (Clan) | 1 | xbrf0103 | ranks_titles | 스타 캡틴 | yes |
| MechWarrior(s) | title | 2 | brf0102, brf0502 | ranks_titles | 메크워리어 | yes |
| Ace(s) | title | 3 | xbrf0103, xbrf0304, xsbrf0401 | ranks_titles | 에이스 | yes |
| Uller | mech | 2 | brf0101, xsbrf0401 | mech_chassis | 울러 | yes |
| Raven | mech | 1 | brf0103 | mech_chassis | 레이븐 | yes |
| Catapult | mech | 1 | brf0106 | mech_chassis | 캐터펄트 | yes |
| Hunchback IIC | mech | 2 | brf0201, brf0204 | mech_chassis | 헌치백 IIC | yes |
| Vulture | mech | 1 | brf0302 | mech_chassis | 벌처 | yes |
| Masakari | mech | 5 | brf0401, brf0503, xbrf0202, xbrf0204, xsbrf0401 | mech_chassis | 마사카리 | yes |
| Atlas | mech | 2 | brf0501, xsbrf0404 | mech_chassis | 아틀라스 | yes |
| Thor | mech | 1 | brf0506 | mech_chassis | 토르 | yes |
| Mad Cat / Madcat | mech | 3 | xbrf0102, xbrf0201, xsbrf0401 | mech_chassis | 매드캣 | yes |
| Shadow Cat / Shadowcat | mech | 2 | xbrf0103, xsbrf0401 | mech_chassis | 섀도캣 | yes |
| Loki | mech | 2 | xbrf0104, xbrf0201 | mech_chassis | 로키 | yes |
| Nova Cat | mech | 2 | xbrf0202, xbrf0302 | mech_chassis | 노바캣 | yes |
| Turkina | mech | 3 | xbrf0301, xbrf0304, xbrf0305 | mech_chassis | 터키나 | yes |
| Cougar | mech | 1 | xsbrf0401 | mech_chassis | 쿠거 | yes |
| OmniMech | mech type | 16 | brf0101, brf0302, brf0401, brf0501, brf0502, brf0503 (+10) | weapons_components | 옴니메크 | yes |
| BattleMech | mech type | 1 | xbrf0104 | game_terms | 배틀메크 | yes |
| 'Mech | mech type | 22 | brf0101, brf0102, brf0103, brf0105, brf0106, brf0203 (+16) | game_terms | 메크 | yes |
| Elemental | unit type | 1 | xbrf0302 | vehicles | 엘리멘탈 | yes |
| APC | vehicle | 3 | brf0102, brf0401, xbrf0204 | vehicles | APC | yes |
| Aerospace Spotter | vehicle | 2 | brf0201, brf0401 | vehicles | 에어로스페이스 관측차 | yes |
| Manticore | vehicle | 1 | xbrf0102 | vehicles | 맨티코어 | yes |
| Hover Limo / Limo | vehicle | 1 | xbrf0204 | vehicles | 호버 리무진 | yes |
| Salvage Rig | vehicle | 1 | xbrf0202 | vehicles | 회수 차량 | yes |
| Mobile Artillery | vehicle | 1 | xsbrf0402 | vehicles | 자주포 | yes |
| Ambulance | vehicle | 2 | brf0302, xsbrf0404 | vehicles | 구급차 | yes |
| Ordnance Truck | vehicle | 1 | brf0402 | vehicles | 군수품 트럭 | yes |
| Supply Truck | vehicle | 1 | brf0303 | vehicles | 보급 트럭 | yes |
| Minelayer | vehicle | 4 | brf0105, brf0305, xbrf0103, xsbrf0404 | vehicles | 지뢰 부설차 | yes |
| Mobile HQ | vehicle | 1 | xbrf0104 | vehicles | 이동 HQ | yes |
| ECM (Suite) | equipment | 1 | brf0103 | weapons_components | ECM | yes |
| LRM | weapon | 4 | brf0106, xbrf0102, xbrf0204, xsbrf0401 | weapons_components | LRM | yes |
| PPC / ER PPC | weapon | 2 | xbrf0102, xbrf0204 | weapons_components | PPC | yes |
| Gauss Rifle | weapon | 1 | xbrf0104 | weapons_components | 가우스 라이플 | yes |
| Ultra Autocannon | weapon | 1 | brf0204 | weapons_components | 울트라 오토캐논 | yes |
| Long Tom | weapon | 2 | xsbrf0401, xsbrf0402 | weapons_components | 롱 톰 | yes |
| HPG / Hyperpulse | tech | 2 | brf0204, xbrf0301 | game_terms | HPG | yes |
| MOG / Mobile Orbital Gun | tech | 3 | brf0406, brf0506, xbrf0203 | game_terms | 이동식 궤도포 | yes |
| Orbital Gun | tech | 5 | brf0401, brf0402, brf0406, brf0506, xbrf0203 | game_terms | 궤도포 | yes |
| Dropship | tech | 4 | brf0406, xbrf0203, xbrf0303, xbrf0304 | game_terms | 드롭십 | yes |
| Deja Vu | loanword | 1 | xsbrf0404 | places_factions | 데자뷔 | yes |

## 2. Other pre-mission sources

| name | type | source | glossary category | ko | covered |
|---|---|---|---|---|---|
| Davion / Davion Guards / First Davion Guards | faction / unit | desc310, 312, 318, 320, 321, 327, 330; art LSB_OP1-5, MCXCard1-3 | places_factions | 다비온 | yes |
| First Davion Guards | unit | operation cards LSB_OP*/MCXCard* | places_factions | 제1 다비온 근위대 | yes |
| Kurita | faction | desc312, desc325 ('Kurita-phile') | places_factions | 쿠리타 | yes |
| Steiner | faction | desc314, desc348 | places_factions | 스타이너 | yes |
| Lyran Commonwealth | faction | desc304 | places_factions | 라이란 연방 | yes |
| Draconic (sic) Combine | faction | desc346 ('Draonic Combine') | places_factions | 드라코니스 연맹 | yes |
| Bandit Kingdoms | region | desc301 | places_factions | 밴딧 킹덤 | yes |
| Periphery | region | desc332 | places_factions | 페리페리 | yes |
| Wolf Dragoons | unit | desc338 | places_factions | 울프 용기병대 | yes |
| Smoke Jaguar(s) / Jaguars | faction | desc310, 317, 323, 327, 344, 346, 349 | places_factions | 스모크 재규어 | yes |
| Inner Sphere / IS | faction | desc13-161 ('IS'), desc328, desc451 | places_factions | 이너 스피어 | yes |
| Star League | faction (historic) | desc98 ('Star League era relic'), desc472, desc554 | places_factions | 스타 리그 | yes |
| Katherine Furey | person | desc472; mech 772 | places_factions | 캐서린 퓨리 | yes |
| Marcus Osis | person | desc473; mech 773 | places_factions | 마커스 오시스 | yes |
| Burnell Wirth | person | desc474; mech 774 | places_factions | 버넬 워스 | yes |
| Kotare | person | mech 775 | places_factions | 마커스 코타레 | yes |
| Kim Ward | person | desc476; mech 776 | places_factions | 킴 워드 | yes |
| Jefferson Stiles | person | desc477; mech 777 | places_factions | 제퍼슨 스타일스 | yes |
| Garrison Bowen | person | desc478; mech 778 | places_factions | 개리슨 보웬 | yes |
| Felicia Lopez | person | desc479; mech 779 | places_factions | 펠리시아 로페즈 | yes |
| Kim / Lee / Til / Savage | person (solo aces) | mechs 780-783 | places_factions | 킴 | yes |
| Trickshot | nickname | desc347 | places_factions | 트릭샷 | yes |
| Alpha Strike | jargon | desc306 | weapons_components | 알파 스트라이크 | yes |
| MechCommander | title | strings 870, 1256; art mm_bkgd | places_factions | 메크커맨더 | yes |
| Desperate Measures | title | art mm_bkgd (logo) | places_factions | 데스퍼릿 메저스 | yes |
| OP299-FARMER-00 | code | operation cards | places_factions | OP299-FARMER-00 | yes |
| Port Arthur / Cermak (identifiers) | identifier | strings 890, 891, 902, 903 - NOT translated | places_factions | 포트 아서 | yes |
| 30 player pilots (Beast ... Vixen) | people | rosters START0/XSTART0, purchase files, desc301-350, plates LSPFLP00-29 | pilots | 비스트 | yes |
| dev/test pilots (war*.fit, PMW00002-13, PMW00150) | people | never referenced by campaign/solo missions | pilots | 팀 라이언 | yes |
| Bravo / Charlie | designator | objective names MIS0801 (dev mission) | places_factions | 브라보 | yes |
| Ace Madcat / Ace Ullers / Ace Masakari / Ace Cougar / Ace Shadowcats | objective names | AceHunt.FIT, MCXS0401.FIT | ranks_titles | 에이스 | yes |

## 3. Notes for translators

* `brf0304c.txt`, `brf0304s.txt` and `xbrf0304.txt` are not referenced by any mission FIT (dead files; `brf0304c` even has the dev header `****GLENN ROCKS THE HOUSE****` and `xbrf0304` the code `FEDCOM:<placeholder>/03PRDN04`). Translate them last, or not at all.
* Same place, two spellings: `Madcat`/`Mad Cat`, `Shadowcat`/`Shadow Cat`, `Starleague`/`Star League`, `Omnimech`/`OmniMech`, `ReEducation`/`Re-Education`/`Re-education` - one Korean form each (glossary).
* Furey is called `Clan Captain` in xbrf0103 but `Star Captain` in desc472: use 스타 캡틴.
* `Jade sector` (xbrf0202, a map sector on Cermak) is unrelated to the Jade Falcon clan of xsbrf0401: 제이드 구역 vs 제이드 팰컨.
* Operation numbering in the headers is not always in order (brf0301 is `03PRDN02`, brf0302 is `03PRDN01`, brf0504 is `05PRDN03`): copy the code line verbatim, never 'fix' it.
* xsbrf0401 and xsbrf0404 are written from the Clan side (`STARCOM`): there 'IS dogs', 'the "Star League" troops' and 'Cpt. Nairn' are the enemy.
