# manifest.json options #

| Field Name | Type | Notes |
| ---------- | ---- | ----- |
| title | String | [REQUIRED] Title of your mod |
| author | String | [REQUIRED] Author's name |
| hacks\_required | list(Hack) | See lib/hacks.py for the list |
| other\_mst\_files | list(String) | Currently unused, add [ "\_\_ALL\_\_" ] to be safe for future versions |
| non\_mst\_files | list(String) |  Currently unused, list all non mst files to be added to ise to be safe for future versions |
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
| wld | String | [REQUIRED] Name of level wld file |
| csv | String | Name of the level csv file |
| gt | String | Name of the level gt file |
| level\_assembly\_files | list(ASSEMBLY\_FILE) | Assembly files included with the level to be inserted into the dol. These files will be wrapped in an if statement so they only fire if the current level is the active level. See ASSEMBLY\_FILE table below for more details |


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
