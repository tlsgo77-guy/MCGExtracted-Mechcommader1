# MCX.EXE string table (STRINGTABLE resource, LANGID 1033)

835 strings, ids 1..1257; 229 `cLoadString` call sites analysed (VA 0x75aa30).

## Counts per scope

| scope | strings | of which format templates | identifiers/debug |
|---|---:|---:|---:|
| pre-mission | 245 | 5 | 5 |
| multiplayer | 30 | 4 | 0 |
| system | 9 | 3 | 4 |
| in-mission | 496 | 8 | 0 |
| unknown | 55 | 6 | 3 |
| **total** | **835** | | |

Of the 245 pre-mission strings: 138 are mech/vehicle names (ids 700-783, 1200-1255, loaded through `DescIndex`), 9 are only used by the mission-results screen, 5 are identifiers (file-name templates, registry values) that must not be translated, leaving about 93 ordinary UI strings.

## How the engine uses the table

* `cLoadString(hInst, id, buf, size)` (VA 0x75aa30) calls `LoadStringA(hInst, id + languageOffset, ...)`.  `languageOffset` (VA 0x80a86c) is read from `SYSTEM.CFG` key `Language` in `_systemInit`, so one EXE can hold several languages in a single STRINGTABLE (second language at e.g. id+1000).  Strings 900 (`English`) and 901 are written to the registry by `WriteRegistryVersionNumber`.
* Only 229 call sites exist; the id is the second `push` before the call.  Several sites share one call through jumps (`push id1 / jmp L / push id2 / jmp L / L: call`), so a call site can name up to ~12 ids (`call_sites` lists them).
* Register ids (`dynamic`) come from data: mech names `DescIndex + 300`, vehicle names `DescIndex + 700` (MISSION.FST profiles `PM*.FIT` / `PV*.FIT` / `PE*.FIT`), object names directly from `BuildingName = <id>` in OBJECT2.PAK building packets and `Name = <id>` in train packets.
* printf templates are filled with `sprintf` (`%s Lance %i`, `Objective %i: %s -- `, `%.0f Ton %s 'Mech`...); the placeholder order is fixed by the code, so a translation may not reorder `%s`/`%i`.  `placeholders` in strings.json lists them.
* `\n` inside a string is a real newline (97, 153, 154, 1257).

## Pre-mission strings

Scope `pre-mission` = every screen reachable before a mission starts (main menu, new/load/save, preferences, logistics: inventory, pilots, purchase, repair/refit, briefing) plus the post-mission results screen (`MissionResults`, optional).  `kind`: ui-text / format (printf template) / identifier.  Mech and vehicle names are collapsed into one row each.

| id | text | screens | kind |
|---:|---|---|---|
| 29 | Interface help information is displayed here. | Briefing, Purchase, Repair/Refit | ui-text |
| 30 | View mission briefing and deploy forces. | Briefing, Purchase, Repair/Refit | ui-text |
| 31 | Current Resource Points | Briefing, Purchase, Repair/Refit | ui-text |
| 32 | Drag a unit here from the Ready Area. | Briefing | ui-text |
| 33 | Ready to deploy into mission. | Briefing | ui-text |
| 34 | Deploy Force Groups into mission. | Briefing | ui-text |
| 35 | Displays selected unit's information. | Briefing | ui-text |
| 36 | Drag into a Force Group to deploy. | Briefing | ui-text |
| 38 | Click to restart video. | Briefing | ui-text |
| 39 | Review current operation briefing. | Briefing | ui-text |
| 40 | Review current mission briefing. | Briefing | ui-text |
| 41 | View BattleMechs in inventory. | Purchase, Repair/Refit | ui-text |
| 42 | View pilots in roster. | Purchase, Repair/Refit | ui-text |
| 43 | View BattleMech components in inventory. | Purchase, Repair/Refit | ui-text |
| 44 | View support vehicles in inventory. | Purchase, Repair/Refit | ui-text |
| 45 | Drag into Battalion Inventory to sell. | Inventory (mech bay / pilots / vehicles / components), Purchase | ui-text |
| 46 | Drag into Battalion Inventory to transfer. | Inventory (mech bay / pilots / vehicles / components), Purchase | ui-text |
| 47 | Click on bar to scroll inventory list. | Purchase, Repair/Refit | ui-text |
| 48 | Drag to inventory to buy. | Purchase | ui-text |
| 49 | Drag into Ready Area to add a pilot, repair, or rearm. | Inventory (mech bay / pilots / vehicles / components), Repair/Refit | ui-text |
| 50 | Drag into BattleMech to install. | Inventory (mech bay / pilots / vehicles / components), Repair/Refit | ui-text |
| 51 | Drag into BattleMech to assign. | Inventory (mech bay / pilots / vehicles / components), Repair/Refit | ui-text |
| 52 | Drag to current inventory to remove vehicle. | Repair/Refit | ui-text |
| 53 | Drag pilot's picture from Batallion Inventory to assign. | Repair/Refit | ui-text |
| 54 | Drag pilot's picture to Batallion Inventory to remove. | Repair/Refit | ui-text |
| 55 | Combat effectiveness of unit. | Purchase, Repair/Refit | ui-text |
| 56 | Overall status of unit. | Repair/Refit | ui-text |
| 57 | Replace all damaged or destroyed components. | Repair/Refit | ui-text |
| 58 | Repair all damaged systems. | Repair/Refit | ui-text |
| 59 | Slide right to repair armor. | Repair/Refit | ui-text |
| 60 | Slide right to repair internal structure. | Repair/Refit | ui-text |
| 61 | Slide right to repair engine. | Repair/Refit | ui-text |
| 62 | Current component load of BattleMech. | Repair/Refit | ui-text |
| 63 | Drag into inventory to remove. | Repair/Refit | ui-text |
| 64 | Drag to Batallion Inventory to un-deploy 'Mech. | Repair/Refit | ui-text |
| 65 | Purchase from Battalion Inventory. | Briefing, Purchase, Repair/Refit | ui-text |
| 66 | Outfit and repair units. | Briefing, Purchase, Repair/Refit | ui-text |
| 67 | Drag units into Ready Area to prepare for deployment. | Repair/Refit | ui-text |
| 68 | View Armor BattleMech variant. | Purchase | ui-text |
| 69 | View Weapon Load BattleMech variant. | Purchase | ui-text |
| 70 | View Jump capable BattleMech variant. | Purchase | ui-text |
| 71 | Drag into Ready Area to prepare for deployment. | Inventory (mech bay / pilots / vehicles / components), Repair/Refit | ui-text |
| 72 | Unit Cost | Purchase | ui-text |
| 73 | Quantity Desired | Purchase | ui-text |
| 74 | RP Remaining | Purchase | ui-text |
| 75 | RP | Purchase | ui-text |
| 76 | This unit violates mission deployment restrictions. | Briefing | ui-text |
| 77 | You do not have enough resource points to purchase this item. | Purchase | ui-text |
| 78 | %.0f Ton %s 'Mech | Inventory (mech bay / pilots / vehicles / components), Repair/Refit | format |
| 79 | Light | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 80 | Medium | In-mission HUD, Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase, Repair/Refit | ui-text |
| 81 | Heavy | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 82 | Assault | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 83 | %.0f Ton %s Vehicle | Inventory (mech bay / pilots / vehicles / components), Repair/Refit | format |
| 84 | The following components could not be replaced: | Repair/Refit | ui-text |
| 85 | Short | In-mission HUD, Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase, Repair/Refit | ui-text |
| 86 | Very Short | Logistics, Purchase | ui-text |
| 87 | You do not have enough resource points to fully repair this BattleMech. | Repair/Refit | ui-text |
| 95 | Permanently remove pilot | Inventory (mech bay / pilots / vehicles / components) | ui-text |
| 98 | Do you wish to remove these damaged components? | Repair/Refit | ui-text |
| 99 | There is insufficient room for the component. | Inventory (mech bay / pilots / vehicles / components) | ui-text |
| 100 | Very Lgt | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 101 | Moderate | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 102 | Very Hvy | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 103 | Devastating | Purchase | ui-text |
| 104 | Very Fast | Purchase | ui-text |
| 105 | Fast | Purchase | ui-text |
| 106 | Slow | Purchase | ui-text |
| 107 | Very Slow | Purchase | ui-text |
| 108 | N/A | Inventory (mech bay / pilots / vehicles / components), Logistics, Purchase | ui-text |
| 109 | Long | In-mission HUD, Inventory (mech bay / pilots / vehicles / components), Purchase, Repair/Refit | ui-text |
| 110 | Tons | Inventory (mech bay / pilots / vehicles / components), Purchase, Repair/Refit | ui-text |
| 111 | Sensor | Repair/Refit | ui-text |
| 112 | Green | Inventory (mech bay / pilots / vehicles / components), MissionResults, Purchase, Repair/Refit | ui-text |
| 113 | Regular | Inventory (mech bay / pilots / vehicles / components), MissionResults, Purchase, Repair/Refit | ui-text |
| 114 | Veteran | Inventory (mech bay / pilots / vehicles / components), MissionResults, Purchase, Repair/Refit | ui-text |
| 115 | Elite | Inventory (mech bay / pilots / vehicles / components), MissionResults, Purchase, Repair/Refit | ui-text |
| 116 | Are you sure you want to delete this file? | SaveScreen | ui-text |
| 117 | Overwrite this saved game? | SaveScreen | ui-text |
| 118 | Game saved. | SaveScreen | ui-text |
| 182 | Friendly | MissionResults | ui-text |
| 183 | Enemy | MissionResults | ui-text |
| 639 | %.1f tons | Purchase | format |
| 645 | The Ready Area only has room for 15 units. | Inventory (mech bay / pilots / vehicles / components) | ui-text |
| 646 | Exit to Main Menu. | Briefing, Purchase, Repair/Refit | ui-text |
| 647 | MechWarrior | Inventory (mech bay / pilots / vehicles / components) | ui-text |
| 700-783 | 84 mech names, e.g. Atlas A, Atlas W, Atlas J (chassis + A/W/J variant letter) | In-mission object names, Logistics, Purchase | ui-text |
| 854 | Dead | MissionResults | ui-text |
| 855 | Injured | MissionResults | ui-text |
| 856 | Active | MissionResults | ui-text |
| 861 | 'Mech cannot be deployed with damaged engine. Engine must be repaired in MechBay. | Briefing | ui-text |
| 864 | Bonus Objectives | MissionResults | ui-text |
| 865 | No Salvage Recovered | MissionResults | ui-text |
| 866 | Secondary Objectives | MissionResults | ui-text |
| 867 | RP | MissionResults | ui-text |
| 868 | Cannot deploy 'Mech. Chassis missing internal structure in key location. | Briefing | ui-text |
| 882 | Current inventory of 'Mechs and vehicles is %d. Maximum is %d.  You must sell back units or risk losing future salvage. | Purchase | format |
| 883 | Current inventory of 'Mechs and vehicles is %d. Maximum is %d. You must sell back at least %d units before deployment. | Briefing | format |
| 884 | Inventory of 'Mechs and vehicles is at maximum.  Until you sell back units, you may not purchase new units and you will lose all future salvage. | Purchase | ui-text |
| 890 | PortArthurAfter_Op%i_Mis%i | Logistics | identifier |
| 891 | PortArthurBefore_Op%i_Mis%i | Logistics | identifier |
| 892 | savegame%03i | SaveScreen | identifier |
| 893 | Inventory:  | Inventory (mech bay / pilots / vehicles / components) | ui-text |
| 897 | <empty> | Logistics | ui-text |
| 901 | U | Purchase | ui-text |
| 902 | CermakAfter_Op%i_Mis%i | Logistics | identifier |
| 903 | CermakBefore_Op%i_Mis%i | Logistics | identifier |
| 1200-1255 | 54 vehicle names, e.g. APC, Armored Car, Bulldog | In-mission object names, Logistics, Purchase | ui-text |
| 1256 | Please insert the MechCommander Expansion compact disc in your CD-ROM drive. | LoadScreen, MainMenu/Cinema, MainMenu/NewCampaign, Multiplayer, Preferences, SaveScreen, System | ui-text |

## Ids that no code path references

355 strings have no `cLoadString` call site and no object/profile data pointing at them (`referenced: false` in strings.json); 55 of them stay `scope: unknown` (with a `guess_scope` where the neighbours or the text suggest one), the rest are spare object-name ids (`in-mission`).  Ids: 1-28, 37, 88-94, 96-97, 119, 155, 163-165, 168-170, 174, 180-181, 207, 233-238, 240-251, 253, 257-259, 261-263, 265-267, 269-273, 275-277, 279-281, 283-285, 287-289, 291-294, 296-297, 300-301, 303-304, 306-350, 352-354, 356, 358-360, 362-364, 366-376, 379-383, 387, 393-395, 397, 399, 401, 403-409, 412-414, 418-422, 425-431, 433-437, 439-440, 444-447, 449-453, 455-461, 463, 465, 467, 471, 473-479, 481-495, 498, 500, 502-504, 506-512, 523-527, 529-533, 535-539, 541-547, 549-551, 553-555, 568-571, 578, 580-583, 585-587, 592, 599-613, 615-620, 628-638, 648, 857-860, 862, 872, 874-877, 885, 904-905, 1228, 1248.
