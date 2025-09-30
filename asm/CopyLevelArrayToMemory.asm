###########################################################
# This code's job is to take the generated level array in exavolt
# and copy it into memory while fixing up relative jumps for string names
# and stuff like that.
##########################################################

## Execute immediately!

# Common pattern (stateful with contextual registers) for updating the million
# pointers to the level array....
.macro load_new_level_address lis_addr ori_addr ori_code
  # Here we only need to update the offset to the lis
  lis r6, \lis_addr@h
  ori r6, r6, \lis_addr@l

  sth r3, 0(r6)

  # Here we need a whole ori instruction so stage it in r5
  lis r6, \ori_addr@h
  ori r6, r6, \ori_addr@l

  lis r5, \ori_code@l
  add r5, r5, r4

  stw r5, 0(r6)
.endm

#Store current value in link register
mfspr r7, LR

#get pointer to start of code
bl START

LEVEL_ARRAY:

{{ LEVEL_ARRAY_RAW }}

START:

mflr r3 # r3 is initial pointer to the raw level array memory

bl LENGTH

LENGTH:
mflr r4 # r4 is length+8
sub r4, r4, r3 # subtract base
subi r4, r4, 0x8 # subtract extra commands

# We read by 4 bytes at a time so divide the counter by 4
li r5, 4
divw r4, r4, r5

mtctr r4 # set counter variable

## Get pointer to SCRATCH_MEMORY_POINTER[LEVEL_ARRAY]
## r4 as code offset
## r5 as current location to copy code

lis r5, {{ SCRATCH_MEMORY_POINTER }}@h
ori r5, r5, {{ SCRATCH_MEMORY_POINTER }}@l
lwz r5, 0(r5)

addis r5, r5, {{ LEVEL_LIST }}@h
addi r5, r5, {{ LEVEL_LIST }}@l

or r4, r5, r5 # store pointer for offset calculation

# Special encoding token we use to see if a value needs an offset!
li r8, 0
ori r8, r8, 0xdcba

# start loop
LOOP:
lhz r6, 0(r3)
cmpw r6, r8
beq RELATIVE

# simple fixed values
lwz r6, 0(r3)
addi r3, r3, 4
b LOOP_END

RELATIVE:
# This is a relatie value, a pointer to something not already in memory, so we need to increment by our base value.

# Increment by 2 and get the lower 16 bits and add to the base offset.
addi r3, r3, 2
lhz r6, 0(r3)
add r6, r6, r4

addi r3, r3, 2

LOOP_END:
stw r6, 0(r5)
addi r5, r5, 4
bdnz LOOP

# Update references to level lest to use the new level list!
# 0x3ac0 = prefix for lis
# TODO on a plane when i wrote this and didnt know how to get split the register into its 2 shorts. So we write to memory and load in each short separately

# r3 = Most significant short of offset
# r4 = Least significant short of offset
# r5 = start of level list, then used as temp
# r6 = level_array_offset... offset, then used as temp

lis r5, {{ SCRATCH_MEMORY_POINTER }}@h
ori r5, r5, {{ SCRATCH_MEMORY_POINTER }}@l
lwz r5, 0(r5)

addis r6, r5, {{ LEVEL_ARRAY_OFFSET }}@h
addi r6, r6, {{ LEVEL_ARRAY_OFFSET }}@l

addis r5, r5, {{ LEVEL_LIST }}@h
addi r5, r5, {{ LEVEL_LIST }}@l

stw r5, 0(r6)

lhz r3, 0(r6)
lhz r4, 2(r6)

# FIND_LEVEL_NAME_FROM_ID
load_new_level_address 0x8014bf42 0x8014bf44 0x60a6

# LEVEL_LOAD (r4)
load_new_level_address 0x801b0b56 0x801b0b58 0x6084

# LEVEL_LOAD_SECOND (r4)
load_new_level_address 0x801b0e16 0x801b0e20 0x6084

# UNKNOWN_FUNCTION (r3)
load_new_level_address 0x801b095a 0x801b0964 0x6063

# UNKNOWN_FUNCTION (r30, r4)
load_new_level_address 0x801b0a7e 0x801b0a8c 0x609e

# Now patch the logic with these new offsets

# Restore link register
mtspr LR, r7

