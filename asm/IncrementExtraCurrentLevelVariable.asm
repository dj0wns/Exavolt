###########################################################
# This code will increment the value in the secondary save file for current level.
# If the primary count = 42, then increment the value in secondary save file.
###########################################################


# Insert at 0x801c8d9c

# r0 has the new number of levels
# r3 is scratch
# r27 is the profile pointer

cmpwi r0, 42 # default number of levels

bgt ADDITIONAL_LEVEL

STANDARD_LEVEL:

# Just increment the byte and be on our way

stb r0, 0x15(r27)
b END

ADDITIONAL_LEVEL:

# store 42 in the main profile memory and increment the secondary save file value
li r0, 42
stb r0, 0x15(r27)

# now do secondary save file
lis r3, {{ SCRATCH_MEMORY_POINTER }}@h
ori r3, r3, {{ SCRATCH_MEMORY_POINTER }}@l
lwz r3, 0(r3)

lis r0, {{ SAVE_FILE_POINTER }}@h
ori r0, r0, {{ SAVE_FILE_POINTER }}@l
add r3, r3, r0
lwz r3, 0(r3) # base save file pointer

# now index into the save file for our piece of memory
lis r0, {{ SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED }}@h
ori r0, r0, {{ SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED }}@l
add r3, r0, r3

lwz r12, 0(r3) # extra levels completed

# Increment and store - r0 breaks addi because it treats it as 0, so use r12 here.
addi r12, r12, 1
stw r12, 0(r3)


END:

# Nothing needed here, logic fully replaced

