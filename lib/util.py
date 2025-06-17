
# Memory offset is a tuple so it is passed by reference
def add_entry_to_dict(entry, dict, memory_offset):
  dict[entry['name']] = memory_offset[0]
  memory_offset[0] += entry['size']
