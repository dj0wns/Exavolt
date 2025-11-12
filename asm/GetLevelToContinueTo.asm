###########################################################
# This code sums the 2 level completed counts to find the correct level to
# continue to.
# Can cheat by using see if game completed and ignoring the cmpwi
###########################################################

# Insert at 0x80164684

{% import "SeeIfGameCompleted.asm" as sfd -%}

# Looks like r0 and r5 are free to use

{{ sfd.SeeIfGameCompleted(
    "r0",
    "r3",
    "r4",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED,
    SP_LEVEL_COUNT)
}}

