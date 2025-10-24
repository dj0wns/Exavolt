###########################################################
# This code's job is to check if the player has completed all the main and extra levels and use that to determine if we need to open
###########################################################

# Insert at 0x8015da28

{% import "SeeIfGameCompleted.asm" as sfd -%}

# Looks like r0 and r4 are free to use

{{ sfd.SeeIfGameCompleted(
    "r0",
    "r4",
    "r30",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED,
    SP_LEVEL_COUNT)
}}

