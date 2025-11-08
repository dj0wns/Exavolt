###########################################################
# This code's job is to calculate the new save location for the save inventory
# commands
###########################################################

## Inject at 0x801c87c8

cmpwi r23, 42 # -1 because its zero indexed
blt STANDARD_FLOW

EXTRA_LEVELS_FLOW:

{% import "CalculateNewInventorySaveLocation.asm" as sfd -%}

{{ sfd.CalculateNewInventorySaveLocation(
    "r27",
    "r23",
    "r3",
    "r5",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SAVE_FILE_OFFSET_SP_LEVELS) }}


# Index into the level struct to the inventory section
addi r3, r3, 0x80

# If we don't have info for this level, we need to return the inventory used for level 42
cmpwi r23, 42
bne FINALIZE

# See if first value is null, if so then this is not a valid inventory, link back to original
lwz r5, 0xc(r3)
cmpwi r5, 0
bne FINALIZE

# now calculate the original pointer!
# First do offset
subi r5, r23, 1
mulli r5, r5, 0x268
addi r5, r5, 0x80
# Then fix the value to the original csv
add r3, r29, r5

FINALIZE:

# Now this should be the correct location in memory!
b END

STANDARD_FLOW:
# Replace command
add r3, r29, r3

END:

