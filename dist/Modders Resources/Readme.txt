Metal Arms game files (excluding streaming audio and videos) are compiled into mettlearms_gc.mst. Exavolt only needs an mst containing your custom files as well as a json with details about the mod to install it into the game.



Setting up your mod for Exavolt:
1. In Pasm, go to Edit > Configuration Settings
2. Change the GC Master File Dir to a new folder that does not contain an mst
3. Compile your files, this will create a new mst only containing what your files
4. Put your mst, a manifest.json file, and any wvb or other files into a .zip



Go here for a more detailed explanation of manifest options:
https://github.com/dj0wns/Exavolt/blob/main/docs/manifest_options.md

Basic manifest.json info:
Manifests describe important info about your mod so Exavolt understands how to add it into the game.

"title": "Mod title"			Required. Title of the mod.
"author": "Mod author"			Required. Author of the mod.
"hacks_required": ["extended_heap"]	Sets whether to extend the game's memory. Recommended in most cases.

"levels"		List of levels in the mod. Refer to example_multiplelevels.json
"type"			Level type, can be campaign or multiplayer.
"mode"			Level insertion mode. Can be used to insert a new level or replace an existing level
"index"			Where to place the level in the level array (from 1 to 42 in singleplayer) more info below
"title"			Name of the level that appears in the game menu selection.
"location"		Level location that appears in the game menu selection.
"thumbnail"		Texture tga to use as the thumbnail for this level.
"secret_chip_count"	Number of secret chips in this level.
"speed_chip_time"	Time in seconds to beat the level for a speed chip.
"player_bot"		Optional. Sets what bot to start as for this level: Glitch, Mozer, Krunk, Slosh.
"wld"			Name of the level .wld file.
"csv"			Name of the level .csv file.
"gt"			Name of the level .gt node graph file.
"custom_inventory"	Customize the player inventory for this level. See below for more info.

"non_mst_files"		Names of files (usually wvb or bik) that don't belong in the mst.



Level array and index:
The levels in Metal Arms are in an array from 0 (Hero Training) to 41 (Final Battle). You can specify if you want your mod to replace an existing level in this array or add a new one to it.
Multiplayer levels will always be added to the end of the MP array regardless of the Mode and Index settings.
Mode: insert	Insert your level into the level array at the specified index
Mode: replace	Replace the level in the array specified by the index
Index: 0	Inserts at the beginning of the level array, before Hero Training
Index: -1	Inserts at the end of the level array



Editing CSV files:
example_CSVedit.json shows how CSV files can be modified. The column and row where a value is stored must be specified so the new value can be written to that spot.
New lines can also be added to a csv.



04 Gecko codes:
Example_04code.json shows how the following code is written in a modloader manifest:
040dcf84 90bf0d88
040dcf88 90bf0d8c
040dd2b4 907f0d8c
Additional codes can be added by including more "opcode" and "content" lines.



"custom_inventory"
Refer to example_custominventory.json for an example of how to edit the player inventory for your level. 
This is not necassary for custom multiplayer levels since they use a level .csv for the player inventory.

Note that "empty primary" and "empty secondary" must always be the first entries in their respective slots. Do not remove them.

"name"				Weapon name
"clip_ammo"			Amount of ammo in the weapon's clip
"reserve_ammo"			Amount of reserve ammo
"default_primary_slot"		Primary weapon for the player to start with
"default_secondary_slot"	Secondary weapon for the player to start with
"battery_count"			How many batteries the player starts with
"washer_count"			Washer count
"chip_count"			Chip count
"secret_chip_count"		Secret chip count
"arm_servo_count"		Arm Servo Upgrade level the player starts with
"det_pack_count"		Det Pack count
"goff_part_count"		Agent Goff part count

List of primary weapons:
empty primary
laser l1
laser l2
laser l3
rlauncher l1
rlauncher l2
rlauncher l3
rivet gun l1
rivet gun l2
rivet gun l3
flamer l1
ripper l1
ripper l2
ripper l3
spew l1
spew l2
spew l3
blaster l1
blaster l2
blaster l3
mortar l1
tether l1
tether l2
tether l3

List of secondaries:
empty secondary
coring charge
magma bomb
emp grenade
cleaner
recruiter grenade
scope l1
scope l2
wrench






