{% macro SaveFileDefaults(player_register,
    scratch_memory_pointer,
    save_file_pointer,
    secondary_save_file_size,
    save_file_offset_version) -%}

SAVE_VERSION = 0x3

# Get base save pointer

lis r4, {{ scratch_memory_pointer }}@h
ori r4, r4, {{ scratch_memory_pointer }}@l
lwz r4, 0(r4)

lis r12, {{ save_file_pointer }}@h
ori r12, r12, {{save_file_pointer }} @l
add r12, r4, r12
lwz r12, 0(r12)# Get base save pointer

lis r3, {{ secondary_save_file_size }}@h
ori r3, r3, {{ secondary_save_file_size }}@l
mullw r3, r3, {{ player_register }} # 4 players!
add r12, r12, r3

# Write version information
lis r3, {{ save_file_offset_version }}@h
ori r3, r3, {{ save_file_offset_version }}@l

lis r4, SAVE_VERSION@h
ori r4, r4, SAVE_VERSION@l
stwx r4, r3, r12

# TODO Write default level framing
# TODO Current plan is to make smalls mods to and just reuse the CPlayerProfile::ResetToBeginning function here to just simplify building the level array in the save file


{% endmacro %}
