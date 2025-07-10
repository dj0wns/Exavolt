###########################################################
# This code's job is to set up default values for the second memory file.
# Including but not limited to the inital level array, and some version information
###########################################################

## Inject at 0x8019ca94 - inside of CPlayerProfile::InitData

{% import "SaveFileDefaults.asm" as sfd -%}


## CONSTANTS
fres_AlignedAllocAndZero=0x8028fac8

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

# r30 is player index

{{ sfd.SaveFileDefaults("r30",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SECONDARY_SAVE_FILE_SIZE,
    SAVE_FILE_OFFSET_VERSION) }}

# command we are replacing!!!
li r3, 1

