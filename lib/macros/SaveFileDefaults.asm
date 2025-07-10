{% macro SaveFileDefaults(player_register,
    scratch_memory_pointer,
    save_file_pointer,
    secondary_save_file_size,
    save_file_offset_version,
    save_version) -%}

.macro sfd_call_macro addr
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

MemZero = 0x8027b728

# Get base save pointer

lis r4, {{ scratch_memory_pointer }}@h
ori r4, r4, {{ scratch_memory_pointer }}@l
lwz r4, 0(r4)

lis r12, {{ save_file_pointer }}@h
ori r12, r12, {{save_file_pointer }} @l
add r12, r4, r12
lwz r12, 0(r12)# Get base save pointer

lis r4, {{ secondary_save_file_size }}@h
ori r4, r4, {{ secondary_save_file_size }}@l
mullw r3, r4, {{ player_register }} # 4 players!
add r12, r12, r3

# Zero memory
or r3, r12, r12
# r4 is already save file size
sfd_call_macro MemZero

# Write version information
lis r3, {{ save_file_offset_version }}@h
ori r3, r3, {{ save_file_offset_version }}@l

lis r4, {{ save_version }}@h
ori r4, r4, {{ save_version }}@l
stwx r4, r3, r12

# TODO Write default level framing
# TODO Current plan is to make smalls mods to and just reuse the CPlayerProfile::ResetToBeginning function here to just simplify building the level array in the save file


{% endmacro %}
