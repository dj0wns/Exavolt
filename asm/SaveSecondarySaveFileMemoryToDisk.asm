###########################################################
# When we save our file we also want to save our secondary chunk of memory to a
# separate file, so this injection latches on to the SaveToCard function and
# saves the second block of memory too
###########################################################

## Inject at 0x8019cd74

## CONSTANTS
write_profile=0x802bf928
base_player_profile_address=0x80416d54

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

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
  lwz r7, r3(r5) # TODO load short not word
  # TODO add logic to check if we got null character, so we replace with our new character and then null the rest.
  stw r7, r3(r6) # TODO store short not word
  addi r3, r3, 2 # Wide char is 2 bytes
  cmpwi r3, 24 # max name length of 12 * size
  beq SAVE_SECONDARY_FILE_NAME_LOOP_START


# Get the save file pointer
lis r3, {{ SAVE_FILE_POINTER }}@h
ori r3, r3, {{SAVE_FILE_POINTER }} @l
lwz r4, r4(r3)

# need to somehow figure out the player index here, since we dont have it.
# Need to compare the data pointer with the base data pointer.
# get the offset into the save file
lis r5, base_player_profile_address@h
ori r5, r5, base_player_profile_address@l
# r31 holds the class pointer
sub r5, r5, r31
divw r5, r5, 4 # 4 bytes per player

# Now we can index in to the save file memory
lis r7, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r7, r7, {{ SECONDARY_SAVE_FILE_SIZE }}@l

# multiply the player index by the size to find the offset
mullw r5, r5, r7

# And add to the base pointer and now we have the memory offset
add r6, r4, r5

# Load the device id
lwz r3, 0x6868(r31)

# command we are replacing!!!
cmpwi r3, 0x0

