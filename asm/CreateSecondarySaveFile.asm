###########################################################
# When we save our file we also want to save our secondary chunk of memory to a
# separate file, so this injection latches on to the SaveToCard function and
# saves the second block of memory too
###########################################################

## Inject at 0x8019cd40

## CONSTANTS
create_profile=0x802bf1e4
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
# r5 is size of data

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

# Now we can index in to the save file memory
lis r5, {{ SECONDARY_SAVE_FILE_SIZE }}@h
ori r5, r5, {{ SECONDARY_SAVE_FILE_SIZE }}@l

# Move r6 (player name string) to r4 to prep arguments
lis r6, {{ MODIFIED_NAME_BUFFER }}@h
ori r6, r6, {{ MODIFIED_NAME_BUFFER }}@l
add r4, r6, r4 # new name buffer

# Load the device id
lwz r3, 0x6868(r31)

# Call write profile!!!
call create_profile

# command we are replacing!!!
cmpwi r3, 0x0

