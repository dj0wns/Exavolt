###########################################################
# This code's job is to set up default values for the second memory file.
# Including but not limited to the inital level array, and some version information
###########################################################

## Inject at 0x8019ca94 - inside of CPlayerProfile::InitData


## CONSTANTS
fres_AlignedAllocAndZero=0x8028fac8
SAVE_VERSION=1

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

# r30 is player index

# Get base save pointer

lis r4, {{ SCRATCH_MEMORY_POINTER }}@h
ori r4, r4, {{ SCRATCH_MEMORY_POINTER }}@l
lwz r4, 0(r4)

lis r12, {{ SAVE_FILE_POINTER }}@h
ori r12, r12, {{SAVE_FILE_POINTER }} @l
add r12, r4, r12
lwz r12, 0(r12)# Get base save pointer

lis r3, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r3, r3, {{ SECONDARY_SAVE_FILE_SIZE }}@l
mullw r3, r3, r30 # 4 players!
add r12, r12, r3

# Write version information
lis r3, {{ SAVE_FILE_OFFSET_VERSION }}@h
ori r3, r3, {{ SAVE_FILE_OFFSET_VERSION }}@l

lis r4, SAVE_VERSION@h
ori r4, r4, SAVE_VERSION@l
stwx r4, r3, r12

# TODO Write default level framing

# command we are replacing!!!
li r3, 1

