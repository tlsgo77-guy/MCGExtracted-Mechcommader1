# art_labels.json: reconciliation with glossary.json (T4b step 1)

Authority: `localization/ko/glossary.json` (ui_terms, briefing_terms, game_terms, places_factions, ranks_titles, art_plates, plus `Recycle` from mech_locations) and `STYLE.md`. `art_labels.json` is no longer provisional (`"_provisional": false`). Change counts: **81 labels in 54 files** (31 distinct replacements). All changed files were re-rendered with `tools/relabel_tga.py`; no label overflows its bbox.

## 1. Replacements (grouped)

| old | new | English on the art | source term | files |
|---|---|---|---|---|
| 아니오 | 아니요 | NO | ui_terms: No | BG_NO.tga, BH_NO.tga, BN_NO.tga |
| 미션 저장 | 임무 저장 | SAVE MISSION | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') | 7 files (MM_SSG01.tga ... mm_xbn05.tga) |
| 미션 불러오기 | 임무 불러오기 | LOAD MISSION | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') | 7 files (MM_SSG02.tga ... mm_xbn04.tga) |
| 단독 미션 | 단독 임무 | SOLO MISSIONS | ui_terms: Solo Missions | mm_xbg02.tga, mm_xbh02.tga, mm_xbn02.tga |
| 작전 # | 작전 번호 | OPERATION # | ui_terms: Operation ('OPERATION #' -> '작전 번호') | MM_WN01.tga, MM_WN02.tga |
| 미션 # | 임무 번호 | MISSION # | ui_terms: Mission ('MISSION #' -> '임무 번호') | MM_WN01.tga, MM_WN02.tga |
| 메크 베이 | 메크 격납고 | 'MECH BAY | ui_terms: 'Mech Bay (user decision) | LSCBG03.tga, LSCBH03.tga, LSCBN03.tga |
| 재활용: | 재장전: | RECYCLE: | mech_locations: Recycle | LSCIIC.tga, LSPBIC00.tga |
| 등급: | 체급: | CLASS: | ui_terms: Class | LSCIIM.tga, LSPBIM00.tga |
| 계급: | 등급: | RANK: | ui_terms: Rank (pilot) ('RANK:' -> '등급:', not 계급) | LSBBKM00.tga, LSCIIP.tga, LSPBIP00.tga, LSRUPM00.tga, Lsrupm10.tga |
| 작전: 비치헤드 | 작전명: 비치헤드 | OPERATION: BEACHHEAD | ui_terms: Operation ('OPERATION: X' -> '작전명: X'); places_factions: BEACHHEAD | LSB_OP1.tga |
| 제1 데이비온 근위대 | 제1 다비온 근위대 | FIRST DAVION GUARDS | places_factions: First Davion Guards (Davion = 다비온) | LSB_OP1.tga, LSB_OP2.tga, LSB_OP3.tga, LSB_OP4.tga, LSB_OP5.tga |
| 작전: 스카이훅 | 작전명: 스카이훅 | OPERATION: SKYHOOK | ui_terms: Operation ('작전명:'); places_factions: SKYHOOK | LSB_OP2.tga |
| 작전: 뱅가드 | 작전명: 뱅가드 | OPERATION: VANGUARD | ui_terms: Operation ('작전명:'); places_factions: VANGUARD | LSB_OP3.tga |
| 작전: 린치핀 | 작전명: 린치핀 | OPERATION: LINCHPIN | ui_terms: Operation ('작전명:'); places_factions: LINCHPIN | LSB_OP4.tga |
| 작전: 컷스로트 | 작전명: 컷스로트 | OPERATION: CUTTHROAT | ui_terms: Operation ('작전명:'); places_factions: CUTTHROAT | LSB_OP5.tga |
| 미션 시작 | 임무 개시 | BEGIN MISSION | ui_terms: Begin Mission (user decision) | Lsbdf00.tga, Lsbdf00A.tga, Lsbdf01.tga |
| 부대 그룹 1 | 전투조 1 | FORCE GROUP 1 | ui_terms: Force Group (user decision) | LSBBK00.tga, LSBDF02.tga |
| 부대 그룹 2 | 전투조 2 | FORCE GROUP 2 | ui_terms: Force Group (user decision) | LSBBK00.tga, LSBDF03.tga |
| 부대 그룹 3 | 전투조 3 | FORCE GROUP 3 | ui_terms: Force Group (user decision) | LSBBK00.tga, LSBDF04.tga |
| 강하 중량 한도 | 투입 중량 제한 | DROP WEIGHT LIMIT | ui_terms: Drop Weight Limit | LSBBK00.tga, lsbdf07.tga |
| 현재 강하 중량 | 현재 투입 중량 | CURRENT DROP WEIGHT | ui_terms: Drop Weight Limit ('CURRENT DROP WEIGHT' -> '현재 투입 중량') | LSBBK00.tga, lsbdf07.tga |
| 캠페인 정보 | 캠페인 데이터 | CAMPAIGN DATA | ui_terms: Campaign Data | LSBBK00.tga |
| 콜사인: | 호출부호: | CALLSIGN: | ui_terms: Callsign ('CALLSIGN:' -> '호출부호:') | LSBBKM00.tga, LSRUPM00.tga, Lsrupm10.tga |
| 적재 무장 | 적재량 | PAYLOAD | ui_terms: Payload | LSBBKM00.tga, LSRUPM00.tga |
| 차량 적재 | 차량 적재량 | VEHICLE PAYLOAD | ui_terms: Payload ('VEHICLE PAYLOAD' -> '차량 적재량') | LSBBKV00.tga, LSRUPV00.tga |
| 미션 브리핑 | 임무 브리핑 | MISSION BRIEFING | ui_terms: Mission Briefing | LSBDW00.tga, LSBDW01.tga, LSBDW02.tga, LSBDW03.tga |
| 재고: | 보유: | AVAIL: | ui_terms: Avail (user decision) | LSPBIC00.tga, LSPBIM00.tga, LSPBIV00.tga |
| 가격: | 비용: | COST: | ui_terms: Cost (user decision) | LSPBIC00.tga, LSPBIM00.tga, LSPBIP00.tga, LSPBIV00.tga |
| 대대 보유 목록 | 대대 보급고 | BATTALION INVENTORY | ui_terms: Battalion Inventory (user decision) | LSPBK00.tga |
| 보유품 정보 | 보유 정보 | INVENTORY INFORMATION | ui_terms: Inventory Information | LSPBK00.tga, LSRBK00.tga |

## 2. Per file

| file | old | new | source term |
|---|---|---|---|
| BG_NO.tga | 아니오 | 아니요 | ui_terms: No |
| BH_NO.tga | 아니오 | 아니요 | ui_terms: No |
| BN_NO.tga | 아니오 | 아니요 | ui_terms: No |
| LSB_OP1.tga | 작전: 비치헤드 | 작전명: 비치헤드 | ui_terms: Operation ('OPERATION: X' -> '작전명: X'); places_factions: BEACHHEAD |
| LSB_OP1.tga | 제1 데이비온 근위대 | 제1 다비온 근위대 | places_factions: First Davion Guards (Davion = 다비온) |
| LSB_OP2.tga | 작전: 스카이훅 | 작전명: 스카이훅 | ui_terms: Operation ('작전명:'); places_factions: SKYHOOK |
| LSB_OP2.tga | 제1 데이비온 근위대 | 제1 다비온 근위대 | places_factions: First Davion Guards (Davion = 다비온) |
| LSB_OP3.tga | 작전: 뱅가드 | 작전명: 뱅가드 | ui_terms: Operation ('작전명:'); places_factions: VANGUARD |
| LSB_OP3.tga | 제1 데이비온 근위대 | 제1 다비온 근위대 | places_factions: First Davion Guards (Davion = 다비온) |
| LSB_OP4.tga | 작전: 린치핀 | 작전명: 린치핀 | ui_terms: Operation ('작전명:'); places_factions: LINCHPIN |
| LSB_OP4.tga | 제1 데이비온 근위대 | 제1 다비온 근위대 | places_factions: First Davion Guards (Davion = 다비온) |
| LSB_OP5.tga | 작전: 컷스로트 | 작전명: 컷스로트 | ui_terms: Operation ('작전명:'); places_factions: CUTTHROAT |
| LSB_OP5.tga | 제1 데이비온 근위대 | 제1 다비온 근위대 | places_factions: First Davion Guards (Davion = 다비온) |
| LSBBK00.tga | 강하 중량 한도 | 투입 중량 제한 | ui_terms: Drop Weight Limit |
| LSBBK00.tga | 부대 그룹 1 | 전투조 1 | ui_terms: Force Group (user decision) |
| LSBBK00.tga | 부대 그룹 2 | 전투조 2 | ui_terms: Force Group (user decision) |
| LSBBK00.tga | 부대 그룹 3 | 전투조 3 | ui_terms: Force Group (user decision) |
| LSBBK00.tga | 캠페인 정보 | 캠페인 데이터 | ui_terms: Campaign Data |
| LSBBK00.tga | 현재 강하 중량 | 현재 투입 중량 | ui_terms: Drop Weight Limit ('CURRENT DROP WEIGHT' -> '현재 투입 중량') |
| LSBBKM00.tga | 계급: | 등급: | ui_terms: Rank (pilot) ('RANK:' -> '등급:', not 계급) |
| LSBBKM00.tga | 적재 무장 | 적재량 | ui_terms: Payload |
| LSBBKM00.tga | 콜사인: | 호출부호: | ui_terms: Callsign ('CALLSIGN:' -> '호출부호:') |
| LSBBKV00.tga | 차량 적재 | 차량 적재량 | ui_terms: Payload ('VEHICLE PAYLOAD' -> '차량 적재량') |
| Lsbdf00.tga | 미션 시작 | 임무 개시 | ui_terms: Begin Mission (user decision) |
| Lsbdf00A.tga | 미션 시작 | 임무 개시 | ui_terms: Begin Mission (user decision) |
| Lsbdf01.tga | 미션 시작 | 임무 개시 | ui_terms: Begin Mission (user decision) |
| LSBDF02.tga | 부대 그룹 1 | 전투조 1 | ui_terms: Force Group (user decision) |
| LSBDF03.tga | 부대 그룹 2 | 전투조 2 | ui_terms: Force Group (user decision) |
| LSBDF04.tga | 부대 그룹 3 | 전투조 3 | ui_terms: Force Group (user decision) |
| lsbdf07.tga | 강하 중량 한도 | 투입 중량 제한 | ui_terms: Drop Weight Limit |
| lsbdf07.tga | 현재 강하 중량 | 현재 투입 중량 | ui_terms: Drop Weight Limit ('CURRENT DROP WEIGHT' -> '현재 투입 중량') |
| LSBDW00.tga | 미션 브리핑 | 임무 브리핑 | ui_terms: Mission Briefing |
| LSBDW01.tga | 미션 브리핑 | 임무 브리핑 | ui_terms: Mission Briefing |
| LSBDW02.tga | 미션 브리핑 | 임무 브리핑 | ui_terms: Mission Briefing |
| LSBDW03.tga | 미션 브리핑 | 임무 브리핑 | ui_terms: Mission Briefing |
| LSCBG03.tga | 메크 베이 | 메크 격납고 | ui_terms: 'Mech Bay (user decision) |
| LSCBH03.tga | 메크 베이 | 메크 격납고 | ui_terms: 'Mech Bay (user decision) |
| LSCBN03.tga | 메크 베이 | 메크 격납고 | ui_terms: 'Mech Bay (user decision) |
| LSCIIC.tga | 재활용: | 재장전: | mech_locations: Recycle |
| LSCIIM.tga | 등급: | 체급: | ui_terms: Class |
| LSCIIP.tga | 계급: | 등급: | ui_terms: Rank (pilot) ('RANK:' -> '등급:', not 계급) |
| LSPBIC00.tga | 가격: | 비용: | ui_terms: Cost (user decision) |
| LSPBIC00.tga | 재고: | 보유: | ui_terms: Avail (user decision) |
| LSPBIC00.tga | 재활용: | 재장전: | mech_locations: Recycle |
| LSPBIM00.tga | 가격: | 비용: | ui_terms: Cost (user decision) |
| LSPBIM00.tga | 등급: | 체급: | ui_terms: Class |
| LSPBIM00.tga | 재고: | 보유: | ui_terms: Avail (user decision) |
| LSPBIP00.tga | 가격: | 비용: | ui_terms: Cost (user decision) |
| LSPBIP00.tga | 계급: | 등급: | ui_terms: Rank (pilot) ('RANK:' -> '등급:', not 계급) |
| LSPBIV00.tga | 가격: | 비용: | ui_terms: Cost (user decision) |
| LSPBIV00.tga | 재고: | 보유: | ui_terms: Avail (user decision) |
| LSPBK00.tga | 대대 보유 목록 | 대대 보급고 | ui_terms: Battalion Inventory (user decision) |
| LSPBK00.tga | 보유품 정보 | 보유 정보 | ui_terms: Inventory Information |
| LSRBK00.tga | 보유품 정보 | 보유 정보 | ui_terms: Inventory Information |
| LSRUPM00.tga | 계급: | 등급: | ui_terms: Rank (pilot) ('RANK:' -> '등급:', not 계급) |
| LSRUPM00.tga | 적재 무장 | 적재량 | ui_terms: Payload |
| LSRUPM00.tga | 콜사인: | 호출부호: | ui_terms: Callsign ('CALLSIGN:' -> '호출부호:') |
| Lsrupm10.tga | 계급: | 등급: | ui_terms: Rank (pilot) ('RANK:' -> '등급:', not 계급) |
| Lsrupm10.tga | 콜사인: | 호출부호: | ui_terms: Callsign ('CALLSIGN:' -> '호출부호:') |
| LSRUPV00.tga | 차량 적재 | 차량 적재량 | ui_terms: Payload ('VEHICLE PAYLOAD' -> '차량 적재량') |
| MM_SSG01.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |
| MM_SSG02.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| MM_SSH01.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |
| MM_SSH02.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| MM_SSN01.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |
| MM_SSN02.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| MM_WN01.tga | 미션 # | 임무 번호 | ui_terms: Mission ('MISSION #' -> '임무 번호') |
| MM_WN01.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| MM_WN01.tga | 작전 # | 작전 번호 | ui_terms: Operation ('OPERATION #' -> '작전 번호') |
| MM_WN02.tga | 미션 # | 임무 번호 | ui_terms: Mission ('MISSION #' -> '임무 번호') |
| MM_WN02.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |
| MM_WN02.tga | 작전 # | 작전 번호 | ui_terms: Operation ('OPERATION #' -> '작전 번호') |
| mm_xbg02.tga | 단독 미션 | 단독 임무 | ui_terms: Solo Missions |
| mm_xbg04.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| mm_xbg05.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |
| mm_xbh02.tga | 단독 미션 | 단독 임무 | ui_terms: Solo Missions |
| mm_xbh04.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| mm_xbh05.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |
| mm_xbn02.tga | 단독 미션 | 단독 임무 | ui_terms: Solo Missions |
| mm_xbn04.tga | 미션 불러오기 | 임무 불러오기 | ui_terms: Mission (임무), Load ('LOAD MISSION' -> '임무 불러오기') |
| mm_xbn05.tga | 미션 저장 | 임무 저장 | ui_terms: Mission (임무), Save ('SAVE MISSION' -> '임무 저장') |

## 3. Checked against the glossary, unchanged

These provisional labels already equal the glossary `ko`: 게임 목록, 게임으로 돌아가기, 계속, 구매, 구조:, 내부 구조, 멀티플레이, 메인 메뉴, 메크, 메크워리어, 메크워리어 고용, 메크워리어 재배치, 배틀메크 구매, 배틀메크 판매, 부품, 부품 구매, 부품 판매, 불러오기, 브리핑/출격, 사거리:, 사격, 삭제, 새 캠페인, 센서, 속도:, 엔진, 예, 오리지널 영상, 오리지널 캠페인, 오프닝 영상, 자원 포인트, 작전 브리핑, 장갑, 장갑:, 저장, 전체 수리, 전체 재장비, 점프, 점프:, 조종, 종료, 종류:, 중량:, 차량, 차량 구매, 차량 종류:, 차량 판매, 최고 속도:, 출격 대기 구역, 취소, 톤, 피해:, 현재 보유 목록, 확인, 확장팩 캠페인, 환경 설정.

## 4. Not in the glossary: provisional text kept

No decision conflicts with these; the lead may want glossary entries so the Korean is authoritative:

- `계획 시작` = BEGIN PLANNING
- `나가기` = LEAVE
- `멀티플레이 종료` = EXIT MULTIPLAYER
- `멀티플레이 채팅` = MULTIPLAYER CHAT (vertical tabs LSBDW02/03/08)
- `전 부대 통신` = ALL STATIONS COMMUNICATION (operation cards LSB_OP1-5)
- `접근: 제한` = ACCESS: RESTRICTED (operation cards)
- `참가` = JOIN GAME
- `통신 종료` = END TRANSMISSION (LSB_OP6)
- `호스트` = HOST GAME

