

HEADERS = r"""
## Function pointers
fnew=0x8028fa88
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
