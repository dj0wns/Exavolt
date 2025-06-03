###########################################################
# This code's job is to create a large space in memory for a secondary
# save file. This allows exavolt mods to save their own data distinct from the
# primary save file. So that large scale campaign mods can have their own memory
# region and also allow for more flexibilty in inventory specs etc.
###########################################################

## Inject at 0x8029e470 - after declaring scratch memory

## CONSTANTS
fnew=0x8028fa88
replaced_func=0x802ba0ac

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

lis r3, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r3, r3, {{ SECONDARY_SAVE_FILE_SIZE }}@l
mulli r3, r3, 4 # 4 players!
li r4, 0x4

call fnew

## Now store the result to SCRATCH_MEMORY_POINTER[SAVE_FILE_POINTER]

lis r4, {{ SCRATCH_MEMORY_POINTER }}@h
ori r4, r4, {{ SCRATCH_MEMORY_POINTER }}@l
lwz r4, 0(r4)

lis r12, {{ SAVE_FILE_POINTER }}@h
ori r12, r12, {{SAVE_FILE_POINTER }} @l
add r12, r4, r12
stw r3, 0(r12)

# command we are replacing!!!
call replaced_func

