
WEAPON_STRING_ADDR_DICT = {
  # primaries
  "empty primary" : 0x803ae8a9,
  "laser l1" : 0x803ae855,
  "laser l2" : 0x803ad50c,
  "laser l3" : 0x803ad515,
  "rlauncher l1" : 0x803ae85e,
  "rlauncher l2" : 0x803ad570,
  "rlauncher l3" : 0x803ad57d,
  "rivet gun l1" : 0x803ae86b,
  "rivet gun l2" : 0x803ae94d,
  "rivet gun l3" : 0x803ad556,
  "flamer l1" : 0x803ae878,
  "ripper l1" : 0x803ae882,
  "ripper l2" : 0x803ad528,
  "ripper l3" : 0x803ad532,
  "spew l1" : 0x803ae88c,
  "spew l2" : 0x803ad5d1,
  "spew l3" : 0x803ad5d9,
  "blaster l1" : 0x803ae894,
  "blaster l2" : 0x803ad595,
  "blaster l3" : 0x803ad5a0,
  "mortar l1" : 0x803ae89f,
  "tether l1" : 0x803ae926,
  "tether l2" : 0x803ad5b5,
  "tether l3" : 0x803ae95a,

  # secondaries
  "empty secondary" : 0x803ae8ff,
  "coring charge" : 0x803ae8b7,
  "magma bomb" : 0x803ae8c5,
  "emp grenade" : 0x803ae8d0,
  "cleaner" : 0x803ae8e5,
  "recruiter grenade" : 0x803ae8ed,
  "scope l1" : 0x803ae930,
  "scope l2" : 0x803ae8dc,
  "wrench" : 0x803ae939,
}

HEADERS = r"""
## Function pointers
fnew=0x8028fa88
fang_MemZero=0x8027b728

## Item Functions
InitItemInst=0x801ade1c
SetupItem=0x801ae8e8
RetrieveEntry=0x801b0090
RetrieveEntryEUK=0x801b0090
SetUpgradeLevel=0x801ea6d4
GetWeaponName=0x801ad5d0
UnknownInventoryFunc=0x8039a00c

## Hud functions
GetInventory=0x801c92a4
HudCreate=0x801a1ac4
GetHudForPlayer=0x801a17d8
OverrideAmmoData=0x801a3440
OverrideWeaponBox=0x801a3384
SetHudMode=0x800f38a4
gamecam_SwitchPlayerToThirdPersonCamera=0x8019a0d4
gamecam_SetActiveCamera=0x8019a294
gamecam_GetActiveCamera=0x8019a2dc
gamecam_GetViewport=0x802d0960

## Titan specific
ChaingunRestoreDefaultValues=0x801f0ea8
TitanEnableLight=0x8008db54

## Bot functions
BotGlitchConstructor=0x80023b6c
BotGlitchCreate=0x80023dfc
BotSloshConstructor=0x80075c00
BotSloshCreate=0x80075ce0
BotKrunkConstructor=0x80047324
BotKrunkCreate=0x800474e4
BotMozerConstructor=0x800572d0
BotMozerCreate=0x80057414
BotTitanConstructor=0x80086c2c

## String pointers
default_string_offset=0x803add4e
bot_titan_string_offset=0x803aa81e


##

## MACROS
.macro call addr
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

# Custom bot functions are overriding the create hud attribute to allow for custom values
# ALL custom bots must include this macro
# player index must be in r31
.macro CreateBotHud bot_pointer
  or r3, r31, r31 # player index
  or r4, \bot_pointer, \bot_pointer
  call gamecam_SwitchPlayerToThirdPersonCamera
  or r3, r22, r22
  call gamecam_SetActiveCamera
  call gamecam_GetActiveCamera
  call gamecam_GetViewport # Using r3 from previous
  stw r23, 0x10(r24)

  or r3, r31, r31
  call GetHudForPlayer
  # r3 is player hud
  or r4, r31, r31 # player index
  call HudCreate
.endm

# Expects bot pointer in r20
# Expects hud pointer in r21
# expects player index in r31
.macro PossessInventoryAndUiSetup
  or r3, r31, r31 # player index
  li r4, 0x1
  call GetInventory # Get player inventory

  stw r3, 0x3e0(r20) # store player invent pointer in bot invent pointer

  li r0, 0x0
  stw r0, 0x560(r3) # inventory callback = null
  stw r0, 0x55c(r3) # primary weapon index = 0
  stw r0, 0x55d(r3) # seconday weapon index = 0
  li r0, 0x1
  stb r0, 0xc4(r3) # num primary weapons
  lwz r4, 0x3bc(r20) # m_apweapon[1]
  subic r0, r4, 0x1
  subfe r0, r0, r4
  stb r0, 0xc5(r3) # count secondary weapons = secondary[0] not null

  # I have no idea what this block does
  # I believe this block of code sets us to 1 battery
  lfs f1, 0x160(r20)
  call UnknownInventoryFunc
  lwz r4, 0x3e0(r20)
  stb r3, 0xc7(r4) # unknown but in possess

  lfs f0, 0x160(r20)
  lwz r3, 0x3e0(r20)
  fctiwz f0, f0
  stfd f0, 0x8(r1)
  lwz r0, 0xc(r1)
  stb r0, 0xc7(r3)

  # set up primary weapon inventory
  # if no primary then set empty hand
  lwz r3, 0x3b8(r20)
  cmpwi r3, 0x0
  #beq LABEL_0 # if empty hand
  # set up primary upgrade level, possess increments but we dont care about that and that gives us finer weapon level control
  lwz r3, 0x3b8(r20) # weapon[0]
  lwz r4, 0x1bc(r3) # upgrade level i think
  call SetUpgradeLevel

  lwz r3, 0x3b8(r20) # weapon[0]
  call GetWeaponName

  li r4, 0 # EUK level ??
  li r5, 0 # some index??
  call RetrieveEntryEUK

  lwz r4, 0x3e0(r20) # bot invent pointer
  stw r3, 0xcc(r4) # Invent> weapon 0 item data?

  lwz r3, 0x3e0(r20) # bot invent ptr
  lwz r4, 0x3b8(r20) # weapon[0]
  lhz r0, 0x238(r4) # weapon[0]->clip_ammo ??
  sth r0, 0xd6(r3) # inventory->weapon[0]->clip ammo

  lwz r3, 0x3e0(r20) # bot invent ptr
  lwz r4, 0x3b8(r20) # weapon[0]
  lhz r0, 0x23a(r4) # weapon[0]->reserve_ammo ??
  sth r0, 0xd8(r3) # inventory->weapon[0]->reserve ammo

  lwz r3, 0x3b8(r20) # weapon[0]
  lwz r4, 0x3e0(r20) # bot invent ptr
  addi r4, r4, 0xc8 # inventory->weapon[0]??
  li r5, 1
  lwz r12, 0x1a0(r3) # weapon[0]->iteminst ??
  lwz r12, 0xb8(r12) # SetItemInst
  mtspr CTR, r12
  bctrl

  lwz r3, 0x3e0(r20) # bot invent
  stw r3, 0xc8(r3) # set owner invent to bot invent ptr

  b LABEL_1

 LABEL_0:
  # no primary so do empty hand
  lis r3, 0x803a
  ori r3, r3, 0x9d2d # "Empty Primary"
  li r4, 0x0
  call RetrieveEntry
  lwz r4, 0x3e0(r20)
  stw r3, 0xcc(r4)
 LABEL_1:

  # set up secondary weapon inventory
  # if no secondary then set empty hand
  lwz r3, 0x3bc(r20)
  cmpwi r3, 0x0
  beq LABEL_2 # if empty hand

  # set up secondary upgrade level, possess increments but we dont care about that and that gives us finer weapon level control
  lwz r3, 0x3bc(r20) # weapon[1]
  lwz r4, 0x1bc(r3) # upgrade level i think
  call SetUpgradeLevel

  lwz r3, 0x3bc(r20) # weapon[1]
  call GetWeaponName

  li r4, 0 # EUK level ??
  li r5, 0 # some index??
  call RetrieveEntryEUK

  lwz r4, 0x3e0(r20) # bot invent pointer
  stw r3, 0x24c(r4) # Invent> weapon 1 item data?

  lwz r3, 0x3e0(r20) # bot invent ptr
  lwz r4, 0x3bc(r20) # weapon[1]
  lhz r0, 0x238(r4) # weapon[1]->clip_ammo ??
  sth r0, 0x256(r3) # inventory->weapon[1]->clip ammo

  lwz r3, 0x3e0(r20) # bot invent ptr
  lwz r4, 0x3bc(r20) # weapon[1]
  lhz r0, 0x23a(r4) # weapon[1]->reserve_ammo ??
  sth r0, 0x258(r3) # inventory->weapon[0]->reserve ammo

  lwz r3, 0x3bc(r20) # weapon[1]
  lwz r4, 0x3e0(r20) # bot invent ptr
  addi r4, r4, 0x248 # inventory->weapon[1]??
  li r5, 1
  lwz r12, 0x1a0(r3) # weapon[1]->iteminst ??
  lwz r12, 0xb8(r12) # SetItemInst
  mtspr CTR, r12
  bctrl

  lwz r3, 0x3e0(r20) # bot invent
  stw r3, 0x248(r3) # set owner invent to bot invent ptr

  b LABEL_3

 LABEL_2:
  # no secondary so do empty hand
  lis r3, 0x803a
  ori r3, r3, 0x9d3b # "Empty Secondary"
  li r4, 0x0
  call RetrieveEntry
  lwz r4, 0x3e0(r20)
  stw r3, 0x24c(r4)
 LABEL_3:
  or r3, r21, r21
  lwz r4, 0x1a8(r20)
  call SetHudMode
.endm
##

"""

# Requires 4 args and wraps a code block
# 1. Level_Index
# 2. Code_String
# 3. Next_Label
# 3. End_Label
LEVEL_IF_CHECK = r"""

lis r12, 0x804b # Level index offset
ori r12, r12, 0x891c
lwz r12, 0(r12)
cmpwi r12, {level_index}
bne {next_label} # correct level so do code stuff, use a contrived long name so we dont clash
{code_string}
b {end_label}
{next_label}:

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_GLITCH =r"""

li r3, 0xdf8
li r4, 0x8
call fnew
or r20, r3, r3 #save ptr to bot

or r4, r3, r3
call BotGlitchConstructor

or r4, r3, r3
mulli r0, r31, 0x24c8
lis r3, 0x8048
addi r3, r3, 0x1af8
add r3, r3, r0
stw r4, 0x18d8(r3)
lwz r3, 0x18d8(r3)

lis r4, 0x803b
or r7, r30, r30
subi r5, r4, 0x2320
addi r6, r1, 0x8
addi r8, r5, 0x6e
or r4, r31, r31
li r5, 0x0
call BotGlitchCreate

CreateBotHud r20

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_MOZER =r"""

li r3, 0xb48
li r4, 0x8
call fnew
or r20, r3, r3 #save ptr to bot

or r4, r3, r3
call BotMozerConstructor

or r4, r3, r3
mulli r0, r31, 0x24c8
lis r3, 0x8048
addi r3, r3, 0x1af8
add r3, r3, r0
stw r4, 0x18d8(r3)
lwz r3, 0x18d8(r3)

lis r4, 0x803b
or r7, r30, r30
subi r5, r4, 0x2320
addi r6, r1, 0x8
addi r8, r5, 0x6e
or r4, r31, r31
li r5, 0x0
call BotMozerCreate

CreateBotHud r20

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_KRUNK =r"""

li r3, 0xf30
li r4, 0x8
call fnew
or r20, r3, r3 #save ptr to bot

or r4, r3, r3
call BotKrunkConstructor

or r4, r3, r3
mulli r0, r31, 0x24c8
lis r3, 0x8048
addi r3, r3, 0x1af8
add r3, r3, r0
stw r4, 0x18d8(r3)
lwz r3, 0x18d8(r3)

lis r4, 0x803b
or r7, r30, r30
subi r5, r4, 0x2320
addi r6, r1, 0x8
addi r8, r5, 0x6e
or r4, r31, r31
li r5, 0x0
call BotKrunkCreate

CreateBotHud r20

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_SLOSH =r"""

li r3, 0x9d0
li r4, 0x8
call fnew
or r20, r3, r3 #save ptr to bot

or r4, r3, r3
call BotSloshConstructor

or r4, r3, r3
mulli r0, r31, 0x24c8
lis r3, 0x8048
addi r3, r3, 0x1af8
add r3, r3, r0
stw r4, 0x18d8(r3)
lwz r3, 0x18d8(r3)

lis r4, 0x803b
or r7, r30, r30
subi r5, r4, 0x2320
addi r6, r1, 0x8
addi r8, r5, 0x6e
or r4, r31, r31
li r5, 0x0
call BotSloshCreate

CreateBotHud r20

"""

BASE_TITAN =r"""
  stwu r1, -0x30(r1) # add 0x30 bytes to stack

# Step 1, call fnew
  li r3, 0xac0 # BotTitan class size
  li r4, 0x8 #no idea, some constant fnew needs
  call fnew

# Step 2, call bot constructor
  call BotTitanConstructor
  or r20, r3, r3 #store the address in register 20 so its not lost
  mulli r0, r31, 0x24c8
  lis r3, 0x8048
  addi r3, r3, 0x1af8
  add r3, r3, r0
  stw r20, 0x18d8(r3)

# Step 3, Get this bots builder
  lwz r3, 0x1a0(r20) # Get vtable for bot
  lwz r3, 0x84(r3) # get the pointer stored at bot_vtable + 84
  mtspr CTR, r3 #Call the function
  bctrl #returns builder class into r3
  or r19, r3, r3 # persist builder in r19

# Step 4, call set defaults for BotTitanBuilder
  lwz r4, 0xd78(r3)
  lwz r0, 0x8(r4)
  # setup arguments
  # r3 already has the class instance
  li r4, 0
  li r5, 0
  li r6, 0
  li r7, 0
  li r8, 0
  lis r9, bot_titan_string_offset@h
  ori r9, r9, bot_titan_string_offset@l
  mtspr CTR, r0
  bctrl

  # Update shield value for builder
  li r3, SHIELD_VALUE
  stw r3, 0xdd4(r19)

#Step 5 call krunk create (any create works tbh)
  or r3, r20, r20
  or r4, r31, r31
  li r5, 0
  addi r6, r1, 0x8
  or r7, r30, r30
  lis r8, default_string_offset@h
  ori r8, r8, default_string_offset@l
  call BotKrunkCreate

  # Update chaingun level to possessed titan
  lwz r3, 0x3b8(r20) # weapon[0]
  li r4, CHAINGUN_LEVEL # possessed titan upgrade level
  call SetUpgradeLevel

  # Store player hud ptr
  or r3, r31, r31
  call GetHudForPlayer
  or r21, r3, r3 # store hud in r21

# Step 6 Init HUD - these things normally happen after create player bot, so we are splicing them in so we have control of the hud
  CreateBotHud r20

# Step 7 set up bot inventory (from bot::possess)
  PossessInventoryAndUiSetup

# Step 8 fixup Hud (From bottitan::possess)
  li r0, 0x3c26
  stw r0, 0x54(r21) # draw flags

  # build colors for right hud override
  lfs f7, -0x796c(r13) # FLOAT_804b3274 = 1.0
  lfs f6, -0x7968(r13) # FLOAT_804b3278 = 1.0
  lfs f5, -0x7964(r13) # FLOAT_804b327c = 0.0
  lfs f4, -0x7960(r13) # FLOAT_806b3280 = 1.0
  lfs f3, -0x794c(r13) # FLOAT_804b3294 = 1.0
  lfs f2, -0x7948(r13) # FLOAT_804b3298 = 0.0
  lfs f1, -0x7944(r13) # FLOAT_804b329c = 0.0
  lfs f0, -0x7940(r13) # FLOAT_804b32a0 = 1.0
  stfs f7, 0x18(r1)
  stfs f6, 0x1c(r1)
  stfs f5, 0x20(r1)
  stfs f4, 0x24(r1)
  stfs f3, 0x8(r1)
  stfs f2, 0xc(r1)
  stfs f1, 0x10(r1)
  stfs f0, 0x14(r1)

  or r3, r21, r21 # hud pointer
  li r4, 0 # CHud2::right
  li r5, 3 # chud2::override_meter_mil
  addi r6, r20, 0xaa8 # titan.ChaingunHeat
  li r7, 0x1 # Override color
  addi r8, r1, 0x18 # start color
  addi r9, r1, 0x8 # end color
  call OverrideAmmoData

  # build colors for left hud override
  lfs f7, -0x793c(r13) # FLOAT_804b32a4 = 1.0
  lfs f6, -0x7938(r13) # FLOAT_804b32a8 = 1.0
  lfs f5, -0x7934(r13) # FLOAT_804b32ac = 1.0
  lfs f4, -0x7930(r13) # FLOAT_804b32b0 = 1.0
  lfs f3, -0x795c(r13) # FLOAT_804b3284 = 0.0
  lfs f2, -0x7958(r13) # FLOAT_804b3288 = 0.0
  lfs f1, -0x7954(r13) # FLOAT_804b328c = 1.0
  lfs f0, -0x7950(r13) # FLOAT_804b3290 = 1.0
  stfs f7, 0x18(r1)
  stfs f6, 0x1c(r1)
  stfs f5, 0x20(r1)
  stfs f4, 0x24(r1)
  stfs f3, 0x8(r1)
  stfs f2, 0xc(r1)
  stfs f1, 0x10(r1)
  stfs f0, 0x14(r1)

  or r3, r21, r21 # hud pointer
  li r4, 1 # CHud2::left
  li r5, 3 # chud2::override_meter_mil
  addi r6, r20, 0xaa4 # titan.ShieldHealth
  li r7, 0x1 # Override color
  addi r8, r1, 0x18 # start color
  addi r9, r1, 0x8 # end color
  call OverrideAmmoData

  # Override left weapon box images
  or r3, r21, r21 # hud pointer
  li r4, 1 # bool override
  li r5, 1 # CHud2::left
  lis r6, 0x803a
  addi r6, r6, 0x6c76 # "RLauncher L1" string
  li r7, 1 # bool reverse
  call OverrideWeaponBox

  # Override right weapon box images
  or r3, r21, r21 # hud pointer
  li r4, 1 # bool override
  li r5, 0 # CHud2::Right
  lis r6, 0x803a
  addi r6, r6, 0x6c83 # "Spew L1" string
  li r7, 0 # bool reverse
  call OverrideWeaponBox

  lwz r3, 0x3b8(r20) # Weapon[0]
  call ChaingunRestoreDefaultValues

  lwz r3, 0x3c8(r20) # DupWeapon[0]
  call ChaingunRestoreDefaultValues

  # Enable titan light
  or r3, r20, r20 # Bot titan
  li r4, 1 #Enable probably
  call TitanEnableLight

  # clean up stack
  addi r1, r1, 0x30

"""
SPAWN_AS_TITAN = BASE_TITAN.replace("SHIELD_VALUE", "0").replace("CHAINGUN_LEVEL", "2")
SPAWN_AS_TITAN_SHIELD = BASE_TITAN.replace("SHIELD_VALUE", "1").replace("CHAINGUN_LEVEL", "2")

BOT_SPAWN_CODES = [
  SPAWN_AS_GLITCH,
  SPAWN_AS_MOZER,
  SPAWN_AS_KRUNK,
  SPAWN_AS_SLOSH,
  SPAWN_AS_TITAN,
  SPAWN_AS_TITAN_SHIELD
]

