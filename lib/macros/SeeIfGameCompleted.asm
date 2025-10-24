{% macro SeeIfGameCompleted(extra_count_register,
  default_count_register,
  player_profile_register,
  scratch_memory_pointer,
  save_file_pointer,
  save_file_offset_extra_levels_completed,
  sp_level_count) -%}

lis {{ default_count_register }}, {{ scratch_memory_pointer }}@h
ori {{ default_count_register }}, {{ default_count_register }}, {{ scratch_memory_pointer }}@l
lwz {{ default_count_register }}, 0({{ default_count_register }})

lis {{ extra_count_register }}, {{ save_file_pointer }}@h
ori {{ extra_count_register }}, {{ extra_count_register }}, {{ save_file_pointer }}@l
add {{ default_count_register }}, {{ default_count_register }}, {{ extra_count_register }}
lwz {{ default_count_register }}, 0({{ default_count_register }}) # base save file pointer

# now index into the save file for our piece of memory
lis {{ extra_count_register }}, {{ save_file_offset_extra_levels_completed }}@h
ori {{ extra_count_register }}, {{ extra_count_register }}, {{ save_file_offset_extra_levels_completed }}@l
add {{ default_count_register }}, {{ extra_count_register }}, {{ default_count_register}}

lwz {{ extra_count_register }}, 0({{ default_count_register }}) # extra levels completed
lbz {{ default_count_register }}, 0x15({{ player_profile_register }})

# sum the levels and see if they are greater than the total levels
add {{ extra_count_register }}, {{ extra_count_register }}, {{ default_count_register }}

cmpwi {{ extra_count_register }}, {{ sp_level_count }}

{% endmacro %}
