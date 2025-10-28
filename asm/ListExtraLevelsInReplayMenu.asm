###########################################################
# Update the index used for replay level selection to take into account bonus
# levels completed.
###########################################################

# Insert at 0x8015dcd0

{% import "SeeIfGameCompleted.asm" as sfd -%}


{{ sfd.SeeIfGameCompleted(
    "r6",
    "r4",
    "r31",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED,
    SP_LEVEL_COUNT)
}}

