###########################################################
# This code stops the continue button from being grayed out!
###########################################################

# Insert at 0x8015da28

{% import "SeeIfGameCompleted.asm" as sfd -%}

# Looks like r0 and r5 are free to use

{{ sfd.SeeIfGameCompleted(
    "r0",
    "r6",
    "r28",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED,
    SP_LEVEL_COUNT)
}}

