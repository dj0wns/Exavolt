###########################################################
# This code's job is to set up default values for the second memory file.
# Including but not limited to the inital level array, and some version information
###########################################################

## Inject at 0x8019ca94 - inside of CPlayerProfile::InitData

{% import "SaveFileDefaults.asm" as sfd -%}

# r30 is player index

{{ sfd.SaveFileDefaults("r30",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SECONDARY_SAVE_FILE_SIZE,
    SAVE_FILE_OFFSET_VERSION,
    SAVE_FILE_VERSION) }}

# command we are replacing!!!
li r3, 1

