###########################################################
# Now load in the new file when loading in the main file!
# Do the truthy path where everything succeeded for the main profile.
# This code is functionally identical to the save profile code.
###########################################################

## Inject at 0x8019cbb4

{% import "SaveFileDefaults.asm" as sfd -%}

## CONSTANTS
read_profile=0x802bf780
create_profile=0x802bf1e4
write_profile=0x802bf928
base_player_profile_address=0x804169bc

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

# Store registers to stack to make sure we keep the state safe
subi r1, r1, 0x20
stw r4, 0x8(r1)
stw r5, 0xc(r1)
stw r6, 0x10(r1)
stw r7, 0x14(r1)
stw r19, 0x18(r1)
stw r20, 0x1c(r1)

# r3 is device_id
# r4 is name
# r5 is 0
# r6 is data
# r7 is size of data

# Point to scratch memory
lis r4, {{ SCRATCH_MEMORY_POINTER }}@h
ori r4, r4, {{ SCRATCH_MEMORY_POINTER }}@l
lwz r4, 0(r4)

# Copy profile name to scratch memory and add a special untypable character to
# the end for file uniqueness
# Simple loop for name
li r3, 0 # loop counter
addi r5, r31, 0x68ac # original name pointer

lis r6, {{ MODIFIED_NAME_BUFFER }}@h
ori r6, r6, {{ MODIFIED_NAME_BUFFER }}@l
add r6, r6, r4 # new name buffer

SAVE_SECONDARY_FILE_NAME_LOOP_START:
  lhz r7, 0(r5)
  cmpwi r7, 0 # if null byte, exit, replace, add null char
  beq SAVE_SECONDARY_FILE_NAME_SUFFIX
  sth r7, 0(r6) # TODO store short not word
  addi r3, r3, 2 # Wide char is 2 bytes
  addi r6, r6, 2
  addi r5, r5, 2
  cmpwi r3, 24 # max name length of 12 * size
  bne SAVE_SECONDARY_FILE_NAME_LOOP_START

SAVE_SECONDARY_FILE_NAME_SUFFIX:
li r7, 126 # tilde
sth r7, 0(r6)
addi r6, r6, 2 #wide char length
li r7, 0x0 # null byte
sth r7, 0(r6)

# need to somehow figure out the player index here, since we dont have it.
# Need to compare the data pointer with the base data pointer.
# get the offset into the save file
lis r5, base_player_profile_address@h
ori r5, r5, base_player_profile_address@l
lwz r5, 0(r5)
cmpw 0, r5, r31
bne CALCULATE_PLAYER_INDEX

li r5, 0

b DONE_WITH_PLAYER_INDEX

# TODO calculate player id, this just assumes
# we are always saving player 1
CALCULATE_PLAYER_INDEX:

li r5, 0

DONE_WITH_PLAYER_INDEX:

# Now we can index in to the save file memory
lis r7, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r7, r7, {{ SECONDARY_SAVE_FILE_SIZE }}@l

# Move r6 (player name string) to r4 to prep arguments
lis r6, {{ MODIFIED_NAME_BUFFER }}@h
ori r6, r6, {{ MODIFIED_NAME_BUFFER }}@l
add r20, r6, r4 # new name buffer

# multiply the player index by the size to find the offset
mullw r5, r5, r7

# Get the save file pointer
lis r3, {{ SAVE_FILE_POINTER }}@h
ori r3, r3, {{ SAVE_FILE_POINTER }} @l
add r4, r3, r4
lwz r4, 0(r4) # make sure to load the save file pointer!
or r19, r4, r4 # save for later

# And add to the base pointer and now we have the memory offset
add r6, r4, r5

# And now fix the name
or r4, r20, r20

# Load the device id
lwz r3, 0x6868(r31)

# Call read profile!!!
call read_profile

# Check if we successfully loaded, if not create a new profile
cmpwi r3, 0

beq END

# Unsuccessful load so make a new profile!
# Set up arguments, saving name in modified name buffer simplifies this since we
# can still call it

# Now we can index in to the save file memory
lis r5, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r5, r5, {{ SECONDARY_SAVE_FILE_SIZE }}@l

# Load the device id
lwz r3, 0x6868(r31)

# Player name string
or r4, r20, r20

# Call write profile!!!
call create_profile

# Now init the save file memory since its not yet init for this profile
# TODO we dont know the real index of the player so pass r5 as a dummy to assume we are just profile 1, likely breaks in mp
li r5, 0

{{ sfd.SaveFileDefaults("r5",
    SCRATCH_MEMORY_POINTER,
    SAVE_FILE_POINTER,
    SECONDARY_SAVE_FILE_SIZE,
    SAVE_FILE_OFFSET_VERSION,
    SAVE_FILE_VERSION) }}


# Now we need to save to file to make sure the player has a valid save file

# Load the device id
lwz r3, 0x6868(r31)

# get name
or r4, r20, r20

# null for some reason
li r5, 0

# Memory offset
or r6, r19, r19

# save size
lis r7, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r7, r7, {{ SECONDARY_SAVE_FILE_SIZE }}@l

# Call write profile!!!
call write_profile

END:

# Restore registers to stack to make sure we keep the state safe
lwz r4, 0x8(r1)
lwz r5, 0xc(r1)
lwz r6, 0x10(r1)
lwz r7, 0x14(r1)
lwz r19, 0x18(r1)
lwz r20, 0x1c(r1)
addi r1, r1, 0x20

# command we are replacing!!!
li r3, 0x1

