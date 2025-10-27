###########################################################
# This code will increment the value in the secondary save file for current level.
# If the primary count = 42, then increment the value in secondary save file.
###########################################################


# Insert at 0x801c8d9c

# r0 has the new nuber of levels
# r3 is scratch
# r27 is the profile pointer

cmpwi r0, 42 # defult number of levels

beq ADDITONAL_LEVEL

STANDARD_LEVEL:

# Just increment the byte and be on our way

stb r0, 0x15(r27)
b END

ADDITIONAL_LEVEL:

# store 42 in the main profile memory and increment the secondary save file value
li r0, 42
stb r0, 0x15(r27)

# now do secondary save file
lis r3, {{ scratch_memory_pointer }}@h
ori r3, r3, {{ scratch_memory_pointer }}@l
lwz r3, 0(r3)

lis r0, {{ save_file_pointer }}@h
ori r0, r0, {{ save_file_pointer }}@l
add r3, r3, r0
lwz r3, 0(r3) # base save file pointer

# now index into the save file for our piece of memory
lis r0, {{ save_file_offset_extra_levels_completed }}@h
ori r0, r0, {{ save_file_offset_extra_levels_completed }}@l
add r3, r0, r3

lwz r0, 0(r3) # extra levels completed

# Increment and store
addi r0, r0, 1
stw r0, 0(r3)


END:

# Nothing needed here, logic fully replaced

