######################################################
# This code's job is to create the scratch memory blob in heap for mods and
# exavolt internal functions to use.
######################################################

## Inject at 0x8029e49c - after injection stage 2

## CONSTANTS
fnew=0x8028fa88

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

lis r3, {{ SCRATCH_MEMORY_SIZE }}@h
ori r3, r3, {{ SCRATCH_MEMORY_SIZE }}@l
li r4, 0x4

call fnew

## Now store the result to SCRATCH_MEMORY_POINTER

lis r4, {{ SCRATCH_MEMORY_POINTER }}@h
ori r4, r4, {{ SCRATCH_MEMORY_POINTER }}@l
stw r3, 0(r4)

# command we are replacing!!!
or r12, r29, r29

