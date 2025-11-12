from .secondary_save_file import save_file_layout_common_offsets
from .util import add_entry_to_dict

# Memory offset is a tuple so it is passed by reference
def default_scratch_memory_entries(memory_offset):
  # Register any exavolt controlled memory sectors here
  default_scratch_memory_entries = [
    {"name": "SAVE_FILE_POINTER",
     "size": 4},
    {"name": "LEVEL_LIST",
     "size": 18000}, # space for 400 levels
    {"name": "MODIFIED_NAME_BUFFER",
     "size": 32}, # Used for save files to make the secondary file unique - each characters is 2 bytes!
    {"name": "LEVEL_ARRAY_OFFSET",
     "size": 4}, # Offset in memory to the new level array! Hacky because it can
     # be derived by looking at the address above but I was on a flight so....
     # No google = no good assembly.
  ]
  ret_dict = {
    'SCRATCH_MEMORY_POINTER':'0x8000333c',
    # 512 KB secondary save file should be larger than our needs
    'SECONDARY_SAVE_FILE_SIZE':'0x00080000'
  }
  for entry in default_scratch_memory_entries:
    add_entry_to_dict(entry, ret_dict, memory_offset)

  # Add save file tags
  ret_dict = ret_dict | save_file_layout_common_offsets()

  return ret_dict
