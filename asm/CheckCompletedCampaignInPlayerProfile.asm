###########################################################
# This code is run at the end of the playerprofile code to see if the profile needs to be updated since it completed another level.
###########################################################

# Insert at 0x801c8da4

{% import "SeeIfGameCompleted.asm" as sfd -%}

# Looks like r0 and r5 are free to use

{{ sfd.SeeIfGameCompleted(
    "r0",
    "r3",
    "r27",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED,
    SP_LEVEL_COUNT)
}}

