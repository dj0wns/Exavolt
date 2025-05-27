# Memory offset is a tuple so it is passed by reference
def default_scratch_memory_entries(memory_offset):
  # Register any exavolt controlled memory sectors here
  default_scratch_memory_entries = [
    {"name": "SAVE_FILE_POINTER",
     "size": 4},
    {"name": "LEVEL_LIST",
     "size": 5000} #overreserving
  ]
  ret_dict = {
    'SCRATCH_MEMORY_POINTER':'0x800032b0'
    # 512 KB secondary save file should be larger than our needs
    'SECONDARY_SAVE_FILE_SIZE':'0x00080000'
  }
  for entry in default_scratch_memory_entries:
    add_entry_to_dict(entry, ret_dict, memory_offset)

  return ret_dict

# Memory offset is a tuple so it is passed by reference
def add_entry_to_dict(entry, dict, memory_offset):
  dict[entry['name']] = memory_offset[0]
  memory_offset[0] += entry['size']
