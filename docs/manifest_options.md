# manifest.json options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| title | String | [REQUIRED] Title of your mod |
| author | String | [REQUIRED] Author's name |
| hacks\_required | list(Hack) | See lib/hacks.py for the list, this also includes default mods now, they won't be applied unless a mod has them in this list. |
| scratch_memory | list(SCRATCH\_MEMORY) | Gives the mod a unique space in the exavolt managed scratch memory to store information between runs. This can be referenced by name as a jinja template in asm files. |
| csv_edits | list(CSV\_EDIT) | Edits to CSV files, doing them this way reduces liklihood of collision with other mods. These are applied after all files are replaced. |
| other\_mst\_files | list(String) | Currently unused, add [ "\_\_ALL\_\_" ] to be safe for future versions |
| non\_mst\_files | list(String) |  Currently unused, list all non mst files to be added to ise to be safe for future versions |
| movie\_files | list(String) |  List of all files to be added to the "Movies" directory in the iso - typically bink movies. |
| assembly\_files | list(ASSEMBLY\_FILE) | Assembly files included with the mod to be inserted into the dol. See ASSEMBLY\_FILE table below for more details |
| gecko\_codes | list(GECKO\_CODE) | 04 codes that are used to modify the dol. Only use this if you cannot use an assembly file for what you are trying to do. See GECKO\_CODE table below for more details |
| levels | list(LEVEL) | Any levels your mod contains. See LEVEL table below for more details |


# LEVEL options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| type | String | [REQUIRED] Refer to lib/level.py::LEVEL_TYPES |
| title | String | Level title, used in the game menu selection |
| location | String | Level locations, used in the game menu selection |
| thumbnail | String | Level thumbnail, used in the game menu selection |
| secret\_chip\_count | Integer | Number count of secret chips in the level |
| speed\_chip\_time | Integer | Time in seconds to earn the speed chip |
| player\_bot | String | The type of bot the player will spawn in as, see PLAYER_BOTS below |
| wld | String | [REQUIRED] Name of level wld file |
| csv | String | Name of the level csv file |
| gt | String | Name of the level gt file |
| custom\_inventory | CUSTOM\_INVENTORY | Define a custom inventory to override the one loaded from the save. See CUSTOM\_INVENTORY below for more details. |
| level\_assembly\_files | list(ASSEMBLY\_FILE) | Assembly files included with the level to be inserted into the dol. These files will be wrapped in an if statement so they only fire if the current level is the active level. See ASSEMBLY\_FILE table below for more details |
| load\_function\_offset | Integer | Address of a special function called during load, used in some special levels. Default is 0x0, don't use this option unless you know what you are doing |
| unload\_function\_offset | Integer | Address of a special function called during unload, used in some special levels. Default is 0x0, don't use this option unless you know what you are doing |
| work\_function\_offset | Integer | Address of a special function called every frame, used in some special levels. Default is 0x0, don't use this option unless you know what you are doing |
| draw\_function\_offset | Integer | Address of a special function called every draw, used in some special levels. Default is 0x0, don't use this option unless you know what you are doing |

# CSV\_EDIT options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| file | String | [REQUIRED] Name of CSV file to modify |
| operation | String | Either "replace" or "add_line". Default is "replace" |
| value | Any | [REQUIRED] If "replace" then a single value to replace, if "add_line" then a list of values to append to the end of the file |
| col | Any | [REQUIRED if "replace"] What column to replace |
| row | Any | [REQUIRED if "replace"] What row to replace |

# SCRATCH\_MEMORY options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| name | String | [REQUIRED] The name of the jinja template string used for this memory sector. |
| size | int | [REQUIRED] Size in bytes of the requested piece of scratch memory. |
| global | bool | [DEFAULT FALSE] When true this means other mods can access the jinja template defined in name, otherwise it is local to this mod package. |

# ASSEMBLY\_FILE options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| file | String | [REQUIRED] Name of assembly file |
| injection\_location | String | [REQUIRED] String in the form of a 32-bit hex offset ("0x80000000") where the code will be injected |

# GECKO\_CODE options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| opcode | String | [REQUIRED] Gecko opcode hex string in the form 04xxxxxx |
| injection\_location | String | [REQUIRED] Hex String in the form xxxxxxxx to be applied by the opcode |

# CUSTOM\_INVENTORY options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| primary | INVENTORY\_ITEM | [REQUIRED] Items in the primary slot of glitch's inventory. See INVENTORY\_ITEM below for more details |
| secondary | INVENTORY\_ITEM | [REQUIRED] Items in the secondary slot of glitch's inventory. See INVENTORY\_ITEM below for more details |
| battery\_count | Integer | Number of batteries glitch spawns with, default is 3 |
| default\_primary\_slot | Integer | 0 indexed value of the default selected primary weapon, default is 1 |
| default\_secondary\_slot | Integer | 0 indexed value of the default selected secondary weapon, default is 0 |
| washer\_count | Integer | Number of starting washers, default is 0 |
| chip\_count | Integer | Number of starting chips, default is 0 |
| secret\_chip\_count | Integer | Number of starting secret chips, default is 0 |
| arm\_servo\_count | Integer | Number of starting arm servos, default is 1 |
| det\_pack\_count | Integer | Number of starting det packs, default is 0 |
| goff\_part\_count | Integer | Number of starting goff parts, default is 0  |

# INVENTORY\_ITEM options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| name | String | See ITEM\_NAME table below for the list of possible options |
| clip\_ammo | Integer | The amount of starting ammo in the clip |
| reserve\_ammo | Integer | The amount of starting ammo in reserves |


# ITEM\_NAME - list of valid inventory item names #

| Item Name |
| -------- |
| **Primaries** |
| empty primary |
| laser l1 |
| laser l2 |
| laser l3 |
| rlauncher l1 |
| rlauncher l2 |
| rlauncher l3 |
| rivet gun l1 |
| rivet gun l2 |
| rivet gun l3 |
| flamer l1 |
| ripper l1 |
| ripper l2 |
| ripper l3 |
| spew l1 |
| spew l2 |
| spew l3 |
| blaster l1 |
| blaster l2 |
| blaster l3 |
| mortar l1 |
| tether l1 |
| tether l2 |
| tether l3 |
| **Secondaries** |
| empty secondary |
| coring charge |
| magma bomb |
| emp grenade |
| cleaner |
| recruiter grenade |
| scope l1 |
| scope l2 |
| wrench |

# PLAYER_BOTS  - list of valid bots players can spawn in as #

| Bot Name |
| -------- |
| Glitch |
| Mozer |
| Krunk |
| Slosh |
