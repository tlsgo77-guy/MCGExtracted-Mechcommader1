# MechCommander Gold 런처 (MCGLauncher)

1999년작 **MechCommander Gold / Desperate Measures**(`MCX.EXE`)를 Windows 11에서
편하게 실행하기 위한 작은 런처입니다. Python 3.13 + tkinter 단일 파일
(`mcg_launcher.py`)이며 PyInstaller로 `MCGLauncher.exe` 하나로 묶을 수 있습니다.

- 게임 옵션(`prefs.cfg`) 편집
- cnc-ddraw 래퍼(`ddraw.dll` + `ddraw.ini`)로 창 모드 / 테두리 없는 전체화면 / 독점 전체화면 선택
- 고해상도(150% 등) 모니터용 DPI 보정(`HIGHDPIAWARE` 호환성 레이어)
- 게임 종료 후 `DEFAULT.ERR`가 새로 기록되면 크래시 로그 표시

## 폴더 구성

| 파일 | 설명 |
|---|---|
| `mcg_launcher.py` | 런처 본체 (GUI + 설정 로직) |
| `test_launcher.py` | 단위 테스트 (unittest, 게임을 실행하지 않음) |
| `build.ps1` | PyInstaller 빌드 스크립트 → `dist\MCGLauncher.exe` |
| `requirements.txt` | 빌드용 의존성(PyInstaller). 런타임 의존성은 없음 |
| `MCGLauncher.spec` | PyInstaller가 생성한 spec (보관해도 무방) |

`build\`, `dist\`, `__pycache__\`는 `.gitignore`로 제외됩니다.

## 사용법

1. `dist\MCGLauncher.exe`(또는 `python mcg_launcher.py`)를 실행합니다.
2. **게임 폴더**: `MCX.EXE`가 있는 폴더를 고릅니다(`찾기`). `MCX.EXE`가 없으면 빨간 안내가 나오고
   실행/저장 버튼이 비활성화됩니다.
   기본값은 `D:\DEV\MCGExtracted-Mechcommader1\game-source\extracted\MCX`이며,
   런처 exe를 게임 폴더 안에 두면 그 폴더를 기본값으로 씁니다.
3. **cnc-ddraw 래퍼 원본 폴더**: `ddraw.dll`(+`Shaders\`, `cnc-ddraw config.exe`)이 있는 폴더.
   기본값은 `D:\DEV\MCGExtracted-Mechcommader1\game-source\tools\cnc-ddraw`(없으면 런처 옆 `cnc-ddraw\`).
4. 옵션을 고른 뒤 **게임 실행** 또는 **설정만 저장**을 누릅니다.
   두 버튼 모두 아래 "런처가 쓰는 파일"을 모두 반영하며, `게임 실행`은 그 다음 `MCX.EXE`를 시작합니다.

| UI 항목 | 반영되는 곳 |
|---|---|
| 해상도 640×480 / 800×600 / 1024×768 / 1280×1024 (기본 1280×1024) | `prefs.cfg` `l Resolution=0/1/2/3` |
| 화면 모드 창 모드 / 테두리 없는 전체화면 / 전체화면(독점) (기본 창 모드) | `ddraw.ini` `[ddraw]` (+ `prefs.cfg` `DirectDraw`) |
| 창 배율 원본 1:1(기본) / 1.25배 / 1.5배 / 2배 / 화면에 맞춤 (창 모드에서만 적용, 해상도 칸에 있음) | `ddraw.ini` `[ddraw]` `width` / `height` (아래 "창 배율" 참고) |
| 언어 English / 한국어 | `prefs.cfg` `l Language=0` / `1` (한글 오버레이 `lang\kor\` 필요) |
| 스프라이트 90픽셀(기본) / 45픽셀 | `b Use90Pixel` / `b Force45Pixel` |
| 난이도 0 쉬움 / 1 보통 / 2 어려움 | `l Difficulty` (게임 환경설정 화면의 버튼 3개가 기록하는 값과 동일. 0은 gamesys.fit `[DifficultySettings]`의 첫 열(아군 기술·무기 125 %, 적 50 %, 노획 확률 50 %), 2는 둘째 열(적 기술 125 %, 적 무기 110 %, 노획 40 %)을 적용하고 1은 보정 없음) |
| 밝기·음악·무전·효과음 슬라이더 (UI 0~100) | `l Brightness` / `MusicVolume` / `RadioVolume` / `SFXVolume` (정수 그대로 기록) |
| DirectDraw 래퍼 사용(cnc-ddraw) (기본 켬) | 게임 폴더에 `ddraw.dll`(+`Shaders\`)이 없으면 복사 |
| DPI 보정(HIGHDPIAWARE) (기본 켬) | 레지스트리 호환성 레이어 |
| 고급 cnc-ddraw 옵션 (기본 끔) | `ddraw.ini`에 `singlecpu=true`, `hook=4` 추가 |

버튼:

- **게임 실행**: 설정 반영 → `MCX.EXE`를 게임 폴더를 작업 폴더로 하여 실행. 실행 중에는 버튼이 비활성화되고,
  종료되면 종료 코드를 상태 줄에 표시합니다.
- **설정만 저장**: 게임을 실행하지 않고 설정만 반영합니다.
- **게임 폴더 열기**: 탐색기로 게임 폴더를 엽니다.
- **cnc-ddraw 설정 도구 열기**: 게임 폴더의 `cnc-ddraw config.exe`를 실행합니다. 게임 폴더에 없고
  래퍼 원본 폴더에 있으면 복사할지 물어봅니다. 이 도구로 바꾼 값 중 런처가 관리하는 `[ddraw]` 키는
  다음 저장/실행 때 런처 값으로 다시 덮어써집니다.

## 런처가 쓰는 파일

### 1. `<게임 폴더>\prefs.cfg`

FITini 텍스트 파일입니다. 런처는 `[MechCommander]` 섹션의 아래 키만 관리합니다.

`Resolution`, `Language`, `DirectDraw`, `Use90Pixel`, `Force45Pixel`, `Difficulty`,
`Brightness`, `MusicVolume`, `RadioVolume`, `SFXVolume`

- 이미 있는 키 줄은 그 자리에서 값만 바꾸고(중복 줄은 제거), 없는 키는 섹션 끝에 추가합니다.
- 그 밖의 줄(`PaletteCycle`, `Force16Mb`, 주석, 다른 섹션 등)은 그대로 둡니다.
- 첫 줄 `FITini`, 마지막 줄 `FITend`, CRLF 줄바꿈을 유지합니다. 파일이 없으면 출시본 내용을 기준으로 만듭니다.
- 게임이 종료할 때 `prefs.cfg`를 다시 쓰면서 모르는 키(`Resolution`, `Language`)를 지울 수 있으므로,
  **쓰기 전에 읽기 전용 속성을 해제하고 쓴 뒤 다시 읽기 전용으로 설정**합니다.
  직접 편집하려면 `attrib -R prefs.cfg`로 해제하세요.

`DirectDraw` 값: 게임 폴더에 `ddraw.dll`(cnc-ddraw)이 있으면 항상 `TRUE`(래퍼가 창/전체화면을 처리).
래퍼가 없을 때는 창 모드면 `FALSE`(게임 자체 GDI 창), 전체화면 모드면 `TRUE`(원래의 8bpp 독점 DirectDraw)입니다.

기본 설정으로 저장한 출시본 `prefs.cfg` 예시:

```
FITini

[MechCommander]
b PaletteCycle=FALSE
b DirectDraw=TRUE
b Use90Pixel=TRUE
b Force45Pixel=FALSE
b Force16Mb=FALSE
b Force32Mb=FALSE
l Difficulty=1
l Brightness=0
l MusicVolume=64
l RadioVolume=64
l SFXVolume=96
l Resolution=3
l Language=0

FITend
```

### 2. `<게임 폴더>\ddraw.ini` (cnc-ddraw 설정)

`ddraw.dll`이 게임 폴더에 있을 때만 갱신합니다. `[ddraw]` 섹션의 아래 키만 바꾸고, 주석·다른 키·
다른 섹션(게임별 섹션 포함)은 그대로 둡니다. 없는 키는 `[ddraw]` 섹션의 마지막 설정 줄 뒤에 추가하며,
파일이 없으면 `[ddraw]` 섹션만 있는 새 파일을 만듭니다. 기존 파일의 줄바꿈(CRLF/LF)과 BOM은 유지됩니다.

| 화면 모드 | 기록하는 키 |
|---|---|
| 창 모드 | `windowed=true` `fullscreen=false` `maintas=true` `boxing=false` `width` `height` (창 배율 1:1이면 `0` `0`, 아래 "창 배율" 참고) + 공통 키 |
| 테두리 없는 전체화면 | `windowed=true` `fullscreen=true` `maintas=true` `boxing=true` + 공통 키 |
| 전체화면(독점) | `windowed=false` `fullscreen=true` `maintas=true` `boxing=false` + 공통 키 |
| 공통 키(모든 모드) | `renderer=auto` `resolutions=2` `d3d9_filter=1` `nonexclusive=true` `vsync=true` `maxfps=60` |
| + 고급 옵션 체크 시 | `singlecpu=true` `hook=4` (체크 해제 시에는 이 두 키를 건드리지 않음) |

공통 키는 2026-10-17에 Windows 11에서 MCX.EXE를 1280×1024로 실제 구동해 확인한 값입니다.
`resolutions=2`는 전체 모드 목록을 노출해 1280×1024가 거부되지 않게 하고, `d3d9_filter=1`은
8비트(256색) 게임이 지원하지 않는 bicubic/lanczos 대신 bilinear를 쓰게 하며, `nonexclusive=true`는
direct3d9/opengl 렌더러에서 UI 요소가 사라지는 문제를 막습니다.

독점 모드의 `boxing=false`는 직전에 테두리 없는 모드(`boxing=true`)를 썼을 때 정수 배율이 남지 않도록
런처가 추가로 기록하는 값입니다.

#### 창 배율 (Window scale)

창 모드에서 게임 창을 키우는 옵션입니다. 게임은 선택한 해상도(예: 1280×1024)로 그대로 그리고,
**확대(업스케일)는 cnc-ddraw가** 합니다. 런처는 `ddraw.ini`의 `width`/`height`에
`게임 해상도 × 배율`(반올림)을 적고, `maintas=true`로 가로세로 비율(5:4 등)을 유지합니다.
`renderer`·`d3d9_filter` 등 다른 키는 그대로입니다.

| 창 배율 | 창 모드에서 쓰는 `width` / `height` |
|---|---|
| 원본 1:1 (기본) | `0` / `0` (창 = 게임 해상도, 확대 없음) |
| 1.25배 / 1.5배 / 2배 | 게임 해상도 × 배율. 예: 1280×1024 → 1600×1280 / 1920×1536 / 2560×2048 |
| 화면에 맞춤 | 주 모니터 작업 영역(화면 − 작업표시줄)에서 창 테두리·제목 표시줄 몫으로 40픽셀을 뺀 크기 안에 들어가는 가장 큰 크기 (비율 유지) |

- **크기 제한**: 작업 영역은 `SystemParametersInfo(SPI_GETWORKAREA)`로 실행/저장할 때마다 다시 읽습니다(런처가
  DPI 인식이라 물리 픽셀, DPI 보정을 켠 기본 설정 기준). 어떤 배율이든 이 작업 영역(−40픽셀)보다 큰 창은 쓰지 않으며,
  안 들어가면 "화면에 맞춤" 크기로 줄입니다. 원본 크기(1:1)조차 안 들어가면 `0` / `0`으로 되돌립니다
  (예: 1920×1080 모니터의 작업 영역 높이는 1040이라 1280×1024 창 + 40픽셀이 들어가지 않아 1:1이 됩니다).
  작업 영역을 읽지 못하면 "화면에 맞춤"은 1:1이 되고 나머지 배율은 제한 없이 그대로 씁니다.
- **창 모드에서만 적용**: 테두리 없는 전체화면/전체화면(독점)은 이미 화면 크기에 맞춰 확대되므로(`fullscreen=true`가
  `width`/`height`를 덮어씁니다) 이 옵션을 무시하고 `width`/`height`를 쓰지 않습니다.
- **화질**: 1.25배/1.5배는 정수 배율이 아니라서 `d3d9_filter=1`(bilinear)에서 약간 흐릿하게 보입니다.
  2배는 픽셀이 정확히 2×2가 되어 선명하지만, 1280×1024의 2배는 2560×2048이라 세로 2048픽셀보다 큰 모니터(4K 등)에서만
  들어갑니다. 그보다 작은 모니터에서는 위 크기 제한 때문에 "화면에 맞춤" 크기가 되어 정수 배율이 아닙니다.
  800×600의 2배(1600×1200)는 작업 영역 높이가 1240픽셀 이상이면 들어갑니다.
- 저장/실행 후 상태 줄에 실제로 쓴 창 크기가 `ddraw.ini 갱신 (창 W×H)` 형태로 표시됩니다.
- 이전 버전의 `settings.json`에는 이 항목이 없으며, 없으면 원본 1:1로 열립니다.

### 3. `<게임 폴더>\ddraw.dll`, `<게임 폴더>\Shaders\`

"DirectDraw 래퍼 사용"이 켜져 있고 게임 폴더에 없을 때만 래퍼 원본 폴더에서 복사합니다.
이미 있는 파일은 덮어쓰거나 지우지 않습니다. 체크를 꺼도 `ddraw.dll`이 남아 있으면 래퍼는 계속 적용되므로,
래퍼를 완전히 끄려면 게임 폴더의 `ddraw.dll`을 직접 지우거나 이름을 바꾸세요.

### 4. 레지스트리 (DPI 보정)

`HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers`에
값 이름 = `MCX.EXE` 전체 경로, 데이터 = `~ HIGHDPIAWARE`(REG_SZ)를 씁니다. 체크를 끄면 그 값을 삭제합니다.
cnc-ddraw와 충돌하는 `256COLOR`, `WIN95` 레이어는 쓰지 않습니다.

### 5. `%APPDATA%\MCGLauncher\settings.json`

런처 자체 설정(폴더 경로, 선택값). 저장/실행/창 닫기 때 저장됩니다. 파일이 없는 첫 실행 때는
게임의 `prefs.cfg`에서 난이도·볼륨 등을 읽어 초기값으로 씁니다.

### 6. `%TEMP%\MCGLauncher-selftest.log`

`--selftest` 실행 결과(콘솔이 없는 exe에서도 확인할 수 있도록).

## 크래시 로그

`게임 실행` 직전 `DEFAULT.ERR`의 수정 시각/크기를 기록해 두고, 게임이 끝난 뒤 파일이 새로 생기거나 바뀌었으면
처음 40줄을 런처 아래쪽 **크래시 로그** 상자에 표시합니다.

## 한국어

게임 폴더에 한글 오버레이(`lang\kor\strings.bin`)가 없으면 "한국어 (준비 중)"은 비활성화됩니다.
오버레이가 있으면 한국어 선택 시 `l Language=1`, English 선택 시 `l Language=0`을 씁니다.
패치된 `MCX.EXE`는 이 값이 0이 아닐 때 `lang\kor\strings.bin`에서 UI 문자열을 읽고,
모든 데이터 파일을 열기 전에 `lang\kor\<경로>`를 먼저 찾습니다(한글 글꼴·브리핑·버튼 이미지).

## 빌드

```powershell
python -m pip install --user pyinstaller
cd D:\DEV\MCGExtracted-Mechcommader1\launcher
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

`build.ps1`은 `python -m PyInstaller --onefile --noconsole --name MCGLauncher mcg_launcher.py`를 실행하고
(`--user` 설치 시 `pyinstaller` 명령이 PATH에 없을 수 있어 `python -m`을 사용),
결과물 `dist\MCGLauncher.exe --selftest`가 0으로 끝나는지 확인합니다.

## 테스트

```powershell
cd D:\DEV\MCGExtracted-Mechcommader1\launcher
python -m unittest -v test_launcher     # 임시 폴더에서 prefs/ddraw.ini/설치/실행 로직 검사 (게임 실행 안 함)
python mcg_launcher.py --selftest       # 창을 숨긴 채 GUI를 만들고 종료 (0 = 성공)
```

레지스트리 테스트는 실제 Layers 키가 아닌 `HKCU\Software\MCGLauncherUnitTest`를 쓰고 끝나면 지웁니다.

## 제한 사항

- 게임을 실제로 실행해 확인하지 않았습니다. 특히 `prefs.cfg`가 읽기 전용일 때 게임이 종료 시 저장에 실패하면서
  오류를 내는지, `Resolution` 2/3에서 화면이 정상인지는 직접 확인이 필요합니다.
- 밝기·볼륨은 UI 값(0~100)을 그대로 씁니다. 엔진의 실제 유효 범위는 확인하지 않았습니다.
- cnc-ddraw는 실행 파일 이름의 게임별 섹션(예: `[MCX]`)이 있으면 그 값이 `[ddraw]`보다 우선합니다.
  런처는 `[ddraw]`만 고치므로, 설정 도구 등으로 `[MCX]` 섹션이 생기면 그쪽 값이 적용될 수 있습니다.
- 게임 실행 중 상태는 1초 간격으로 확인합니다. 런처를 닫아도 게임은 계속 실행되지만 크래시 로그는 표시되지 않습니다.

## 게임 단축키 탭

런처 두 번째 탭 "게임 단축키"에 미션 중 키보드 단축키 표를 넣었습니다. 각 행의 "검증" 열은 그 키를 어떤 자료로 확인했는지 표시합니다.

| 표시 | 뜻 |
|---|---|
| M | MechCommander Gold 공식 매뉴얼 (pp.29-32, 키보드 기능 차트) |
| R | 게임 폴더의 `Readme.txt` (Desperate Measures 추가 기능: 웨이포인트, 탄약 절약, 화력 지원) |
| C | `MCX.EXE`의 `InterfaceObject::init` 키 테이블과 `handleEvent` 디컴파일 (스캔코드 기준) |
| T | EXE 문자열 테이블의 MFD 툴팁 (`Attack-Short Range [S]` 등) |
| W | 커뮤니티 자료 (ModDB 가이드, Let's Play Archive, Neoseeker) |

세 갈래 이상에서 일치한 키가 대부분이며, 매뉴얼에만 있는 키(E, TAB, ALT 조합 등)는 M 단독으로 표시했습니다.
`O` 키는 코드의 공격 모드 테이블에만 존재해 추정으로 표시했고, 그룹 재지정(CTRL+F1~F4)은 매뉴얼 표기를 따르되
코드상 수정키가 다를 수 있어 그렇게 적었습니다. 치트 코드는 별도 파일 조작이 필요하므로 표에 넣지 않았습니다.
