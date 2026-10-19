# FIT / CSV strings that matter before (and around) a mission

1699 entries in `fit_strings.json` (fields: file, section, key, text, category, scope + extras).

## Counts per source

| source | files | strings |
|---|---:|---:|
| MISSION.FST mission FITs (objectives) | 107 | 271 |
| MISSION.FST pilots (war*/PMW*/PCREW*) | 342 | 684 |
| MISSION.FST mech/vehicle profiles (PM*/PV*/PE*) | 150 | 239 |
| MISC.FST/desc.fit | 1 | 217 |
| MISC.FST/MECHTEXT.FIT | 1 | 49 |
| MISC.FST/MECHREP.FIT | 1 | 8 |
| MISC.FST/Menus.fit | 1 | 2 |
| MISC.FST/compbas.csv | 1 | 229 |
| **total** | **604** | **1699** |

Unique texts: 1163.  Entries per category:

* pilot name: 337
* pilot callsign: 337
* mission objective name: 271
* component description (SMUTI markup): 217
* component name: 129
* component abbreviation: 100
* mech variant designation (MechType): 89
* mech variant designation (Name): 89
* vehicle designation (Name): 59
* mech panel heading / location / damage state: 49
* mech repair diagram box label: 8
* vehicle crew name: 5
* vehicle crew callsign: 5
* profile designation (Name): 2
* command-palette tooltip: 2

Objective names per campaign (entries, duplicates across variant FITs included): solo 18, multiplayer 94, dev/test 11, expansion 46, original 102; unique objective texts: 168.

## Per-file counts

* `MISSION.FST/AceHunt.FIT`: 5
* `MISSION.FST/Achilles.FIT`: 4
* `MISSION.FST/Bakwoods.FIT`: 2
* `MISSION.FST/caldera.FIT`: 2
* `MISSION.FST/CaptIsld.FIT`: 2
* `MISSION.FST/DValley.FIT`: 4
* `MISSION.FST/E3_0101.FIT`: 3
* `MISSION.FST/E3_0101A.FIT`: 2
* `MISSION.FST/E3_0203.FIT`: 2
* `MISSION.FST/HvrDmmt.FIT`: 2
* `MISSION.FST/KingIsle.FIT`: 4
* `MISSION.FST/MCX0101.FIT`: 3
* `MISSION.FST/MCX0102.FIT`: 3
* `MISSION.FST/MCX0103.FIT`: 4
* `MISSION.FST/MCX0104.FIT`: 3
* `MISSION.FST/MCX0201.FIT`: 6
* `MISSION.FST/MCX0202.FIT`: 3
* `MISSION.FST/MCX0203.FIT`: 6
* `MISSION.FST/MCX0204.FIT`: 4
* `MISSION.FST/MCX0301.FIT`: 3
* `MISSION.FST/MCX0302.FIT`: 6
* `MISSION.FST/MCX0303.FIT`: 1
* `MISSION.FST/MCX0304.FIT`: 4
* `MISSION.FST/MCXS0401.FIT`: 5
* `MISSION.FST/MCXS0402.FIT`: 2
* `MISSION.FST/MIS0101.FIT`: 3
* `MISSION.FST/MIS0101c.fit`: 2
* `MISSION.FST/MIS0101n.fit`: 2
* `MISSION.FST/MIS0101s.fit`: 2
* `MISSION.FST/MIS0102.FIT`: 3
* `MISSION.FST/MIS0103.fit`: 2
* `MISSION.FST/MIS0104.FIT`: 3
* `MISSION.FST/MIS0105.FIT`: 1
* `MISSION.FST/MIS0106.FIT`: 1
* `MISSION.FST/MIS0201.FIT`: 1
* `MISSION.FST/MIS0202.FIT`: 2
* `MISSION.FST/MIS0203.FIT`: 1
* `MISSION.FST/MIS0204.FIT`: 1
* `MISSION.FST/MIS0205.FIT`: 1
* `MISSION.FST/MIS0206.FIT`: 2
* `MISSION.FST/MIS0301.FIT`: 3
* `MISSION.FST/MIS0302.FIT`: 2
* `MISSION.FST/MIS0303.FIT`: 2
* `MISSION.FST/MIS0304.FIT`: 3
* `MISSION.FST/MIS0305.FIT`: 4
* `MISSION.FST/MIS0306.FIT`: 3
* `MISSION.FST/MIS0401.FIT`: 2
* `MISSION.FST/MIS0402.FIT`: 2
* `MISSION.FST/MIS0403.fit`: 3
* `MISSION.FST/MIS0403c.fit`: 2
* `MISSION.FST/MIS0403c1_3p.fit`: 2
* `MISSION.FST/MIS0403c1_5p.fit`: 2
* `MISSION.FST/MIS0403c2_3p.fit`: 2
* `MISSION.FST/MIS0403c2_5p.fit`: 2
* `MISSION.FST/MIS0403c3_5p.fit`: 2
* `MISSION.FST/MIS0403c4_5p.fit`: 2
* `MISSION.FST/MIS0403c_2p.fit`: 2
* `MISSION.FST/MIS0403mp.fit`: 2
* `MISSION.FST/MIS0403s.fit`: 2
* `MISSION.FST/MIS0403s_2p.fit`: 2
* `MISSION.FST/MIS0403s_3p.fit`: 2
* `MISSION.FST/MIS0403s_5p.fit`: 2
* `MISSION.FST/MIS0404.FIT`: 3
* `MISSION.FST/MIS0405.FIT`: 1
* `MISSION.FST/MIS0406.FIT`: 3
* `MISSION.FST/MIS0501.FIT`: 1
* `MISSION.FST/MIS0502.FIT`: 1
* `MISSION.FST/MIS0503.FIT`: 3
* `MISSION.FST/MIS0504.FIT`: 3
* `MISSION.FST/MIS0505.FIT`: 2
* `MISSION.FST/MIS0506.FIT`: 1
* `MISSION.FST/MIS0507.FIT`: 4
* `MISSION.FST/MIS0801.FIT`: 3
* `MISSION.FST/MISE303.FIT`: 3
* `MISSION.FST/MouseTrp.FIT`: 2
* `MISSION.FST/MP0304.fit`: 4
* `MISSION.FST/MP0701.FIT`: 4
* `MISSION.FST/MP0702.FIT`: 2
* `MISSION.FST/MP0703.FIT`: 2
* `MISSION.FST/MP0705.FIT`: 2
* `MISSION.FST/MP0706.FIT`: 2
* `MISSION.FST/MP0707.FIT`: 2
* `MISSION.FST/MP0708.FIT`: 4
* `MISSION.FST/MP0709.FIT`: 2
* `MISSION.FST/MP0712.FIT`: 2
* `MISSION.FST/MP0714.FIT`: 4
* `MISSION.FST/MP0715.FIT`: 2
* `MISSION.FST/MP0716.FIT`: 2
* `MISSION.FST/MP0718.FIT`: 2
* `MISSION.FST/MP0719.FIT`: 2
* `MISSION.FST/MP0720.FIT`: 4
* `MISSION.FST/MP0721.FIT`: 2
* `MISSION.FST/MP0722.FIT`: 2
* `MISSION.FST/MP0723.FIT`: 2
* `MISSION.FST/MP0725.FIT`: 4
* `MISSION.FST/MP0726.FIT`: 2
* `MISSION.FST/MP0727.FIT`: 2
* `MISSION.FST/MP0728.FIT`: 2
* `MISSION.FST/MP0729.FIT`: 2
* `MISSION.FST/MP0730.FIT`: 2
* `MISSION.FST/MP0731.FIT`: 2
* `MISSION.FST/MXM0502.FIT`: 4
* `MISSION.FST/PARedux.FIT`: 4
* `MISSION.FST/testmis1.FIT`: 1
* `MISSION.FST/TheGuns.FIT`: 2
* `MISSION.FST/Urbana.FIT`: 2
* `MISSION.FST/WetNWild.FIT`: 2
* `MISC.FST/desc.fit`: 217
* `MISC.FST/MECHTEXT.FIT`: 49
* `MISC.FST/MECHREP.FIT`: 8
* `MISC.FST/Menus.fit`: 2
* `MISC.FST/compbas.csv`: 229
* (492 pilot / crew / mech / vehicle profile files with 1-2 strings each are not listed one by one)

## Notes and ambiguous sources

* **Objective names** (`[ObjectiveN] st Name`) are the only free text in a mission FIT.  They are shown in the in-mission objective list and on the results screen (`MissionResultsScreen::drawObjectives`), not on the briefing screen (the briefing prose lives in `brfXXXX.txt`, see `briefings.json`).  There is no mission *title* field: titles such as `***LIBERATE WORK CAMPS***` are the first lines of the briefing text.
* **`campaign*.fit`, `mechcmdr1.fit`, `Xmechcmdr1.fit`, `purchase*.fit`, `xpurchase*.fit`, `solopurchase.fit`, `soloispurchase.fit`, `netpur.fit`, `clanpur.fit`, `ispur.fit`, `xpur.fit`**: no player-facing text at all (movie names, mission file names, purchase file names, numbers).  Nothing extracted.
* **Pilots**: `PMW*.FIT` carry the roster names and callsigns (`Hitman / HITMAN`, `Countess`, ...) plus a portrait name (`Picture = pilot16.TGA`, see `art.json`).  `war*.fit` are developer test pilots (Amy Bios, Kermit, Piggy ...).  Many `PMW` files are generic AI crews (`Allied`, `Clan`, `CLAN GREEN`).  There are **no pilot bios** in any FIT (`DescIndex` is empty).
* **Mech / vehicle profiles**: `General.Name` (`COM-A`) and `General.MechType` (`Commando A`) are developer designations; the logistics screens show the EXE string `DescIndex + 300` (mechs) / `+ 700` (vehicles) instead (`LogMechList::addMech`).  They are listed with `exe_string_id` so the two can be kept consistent.
* **`desc.fit`** uses the `%` markup of `markup.md`; `Desc<N>` = component id `N` of `compbas.csv` (name added as `component_name`).  Entries containing `IF YOU SEE THIS DESCRIPTION PLEASE REPORT IT AS A BUG` are placeholders for components that never got text.
* **`compbas.csv`**: only the `name` and `abbr` columns are text; `type` (Engine, Actuator, ...) and `side` (IS/Clan/Both) are parsed by the game as keywords and must not be translated.  Rows named `undefined` are skipped.
* **`MECHTEXT.FIT`** headings are used by the mech status panels (both in the logistics repair/purchase screens and in the mission); `MECHREP.FIT` `name` fields label the damage diagram boxes.
* **`Menus.fit`**: `ItemHelp` exists for two command-palette entries only.  The menu items themselves are art (`Action`, `Att`, `Role` shape sets).  In-mission.
* **`radio.csv`**: pure data (`RADIO_MOVETO,priority,shelflife,movie,...`); the spoken text is audio.  In-mission only, nothing to translate.
* **`IFACE.FIT`, `windows.fit`, `allcomp.fit`, `CAMERAS.FIT`, `Palette*.fit`, `cursor.fit`**: shape/palette/layout data, no text (`allcomp.fit` has the component names only in `//` comments).
* **ART.FST screen FITs** (`mainscreen`, `prefscreen`, `lanscreen`, `loadscreen`, `savescreen`, `modem`, `readyroom`, `mpscreen`, `serial`) contain *no* text: every label of those screens is baked into the TGA buttons, see `art.json`.  Their `//` comments (`// new cermak`, `// save`, `// multi-player` ...) were used to annotate the art.
* **ABL scripts** (`*.ABL`, 774 files) contain only developer debug strings (`Gametime: `, `Moving to Step `...), no player text.
