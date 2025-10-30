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

# game_UnloadLevel (r3)
load_new_level_address 0x801962e6 0x801962ec 0x6063

# UNKNOWN (r4, r0)
load_new_level_address 0x80195e96 0x80195ea0 0x6080

# UNKNOWN (r3)
load_new_level_address 0x801b0ba2 0x801b0ba4 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801b0bbe 0x801b0bc0 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801b0bda 0x801b0bdc 0x6063

# UNKNOWN (r4)
load_new_level_address 0x801b15fa 0x801b15fc 0x6084

# UNKNOWN (r3)
load_new_level_address 0x801b0ba2 0x801b0ba4 0x6063

# UNKNOWN (r3)
load_new_level_address 0x800cebba 0x800cebc4 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801b2cca 0x801b2ccc 0x6063

# UNKNOWN (r4, r0)
load_new_level_address 0x80195eda 0x80195ee0 0x6080

# UNKNOWN (r3)
load_new_level_address 0x801b0d7e 0x801b0d80 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801c8b1a 0x801c8b1c 0x6063

# UNKNOWN (r3)
load_new_level_address 0x80179006 0x80179008 0x6063

# UNKNOWN (r3)
load_new_level_address 0x8019826e 0x80198270 0x6063

# UNKNOWN (r4)
load_new_level_address 0x80197daa 0x80197dac 0x6084

# UNKNOWN (r3)
load_new_level_address 0x8002469e 0x800246a0 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801a3792 0x801a3798 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801983ba 0x801983bc 0x6063

# UNKNOWN (r3)
load_new_level_address 0x8016bef6 0x8016bef8 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801b0fe6 0x801b0fe8 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801b108a 0x801b108c 0x6063

# UNKNOWN (r3, r4)
load_new_level_address 0x80198146 0x80198148 0x6064

# UNKNOWN (r3)
load_new_level_address 0x801987aa 0x801987ac 0x6063

# UNKNOWN (r3)
load_new_level_address 0x8015493e 0x80154948 0x6063

# UNKNOWN (r3)
load_new_level_address 0x80155bde 0x80155be0 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801c8c22 0x801c8c24 0x6063

# UNKNOWN (r3)
load_new_level_address 0x801b0ee2 0x801b0ee4 0x6063

# UNKNOWN (r6)
load_new_level_address 0x80063f7a 0x80063f8c 0x60c6

# UNKNOWN (r10)
load_new_level_address 0x801840ee 0x801840f0 0x614a

# Now patch the logic with these new offsets

# Restore link register
mtspr LR, r7

