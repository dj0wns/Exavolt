###########################################################
# This code's job is to calculate the new save location for the save inventory
# commands
###########################################################

## Inject at 0x801c8d50

cmpwi r23, 41 # -1 because we use +1 here
blt STANDARD_FLOW

EXTRA_LEVELS_FLOW:

# increment level by 1 because we save inventory to the next level.
addi r5, r23, 1

{% import "CalculateNewInventorySaveLocation.asm" as sfd -%}

{{ sfd.CalculateNewInventorySaveLocation(
    "r28",
    "r5",
    "r3",
    "r12",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_SP_LEVELS) }}


# Index into the level struct to the inventory section
addi r3, r3, 0x80

# Now this should be the correct location in memory!
b END

STANDARD_FLOW:
# Replace command
add r3, r27, r3

END:

