{% macro CalculateNewInventorySaveLocation(
    player_register,
    level_index_register,
    destination_register,
    scratch_register,
    scratch_memory_pointer,
    save_file_pointer,
    save_file_offset_sp_levels) -%}

# Get base save pointer
lis {{ destination_register }}, {{ scratch_memory_pointer }}@h
ori {{ destination_register }}, {{ destination_register }}, {{ scratch_memory_pointer }}@l
lwz {{ destination_register }}, 0({{ destination_register }})

lis {{ scratch_register }}, {{ save_file_pointer }}@h
ori {{ scratch_register }}, {{ scratch_register }}, {{save_file_pointer }}@l
add {{ destination_register }}, {{ scratch_register }}, {{ destination_register }}
lwz {{ destination_register }}, 0({{ destination_register }})# Get base save pointer

# Get start of sp_levels address
lis {{ scratch_register }}, {{ save_file_offset_sp_levels }}@h
ori {{ scratch_register }}, {{ scratch_register }}, {{ save_file_offset_sp_levels }}@l

add {{ destination_register }}, {{ destination_register }}, {{ scratch_register }}

# start of sp memory is now in destination register

# now find the offset, zero indexed
subi {{ scratch_register }}, {{ level_index_register }}, 42

# 0x268 is the struct size for the end of level stuff
mulli {{ scratch_register }}, {{ scratch_register }}, 0x268

add {{ destination_register }}, {{ destination_register }}, {{ scratch_register }}

{% endmacro %}
