
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
  "rivet gun l3" : 0x803ad556
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
InitItemInst=0x801ade1c
SetupDefaultItems=0x801aeabc
BotGlitchConstructor=0x80023b6c
BotGlitchCreate=0x80023dfc
BotSloshConstructor=0x80075c00
BotSloshCreate=0x80075ce0
BotKrunkConstructor=0x80047324
BotKrunkCreate=0x800474e4
BotMozerConstructor=0x800572d0
BotMozerCreate=0x80057414

##

## MACROS
.macro call addr
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
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

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_MOZER =r"""

li r3, 0xb48
li r4, 0x8
call fnew

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

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_KRUNK =r"""

li r3, 0xf30
li r4, 0x8
call fnew

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

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_SLOSH =r"""

li r3, 0x9d0
li r4, 0x8
call fnew

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

"""
