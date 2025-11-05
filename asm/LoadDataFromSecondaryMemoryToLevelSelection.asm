###########################################################
# This code's job is to calculate the new load location for the level select
# commands
###########################################################

## Inject at 0x8015dd50

cmpwi r0, 42 # -1 because its zero indexed
blt STANDARD_FLOW

EXTRA_LEVELS_FLOW:

# r0 gives me some issues with opcodes, so just use r6
or r6, r0, r0

{% import "CalculateNewInventorySaveLocation.asm" as sfd -%}

{{ sfd.CalculateNewInventorySaveLocation(
    "r5",
    "r6",
    "r28",
    "r12",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_SP_LEVELS) }}

addi r28, r28, 0x74

b END

STANDARD_FLOW:
# Replace command
add r28, r29, r28

END:

