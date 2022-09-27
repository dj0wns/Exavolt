import collections

pack_int = '>i' #dols can only be big endian

def parse_dol_table(dol):
  dol_table = {}
  dol_reader = open(dol, "rb")

  file_offsets = []
  memory_offsets = []
  # 7 text segments and 11 data segments
  for i in range(18):
    file_offsets.append(int.from_bytes(dol_reader.read(4), byteorder='big', signed=False))
  for i in range(18):
    memory_offsets.append(int.from_bytes(dol_reader.read(4), byteorder='big', signed=False))

  for i in range(len(memory_offsets)):
    dol_table[memory_offsets[i]] = file_offsets[i]
  return collections.OrderedDict(sorted(dol_table.items()))

def get_file_from_memory_address(table, address):
  memory_offset = -1
  for i in table.keys():
    if i > memory_offset and i < address:
      memory_offset = i
  file_offset = table[memory_offset]
  address -= memory_offset
  file_offset += address
  return file_offset

def apply_hack(dol, hack):
  dol_table = parse_dol_table(dol)
  state = -1
  address = -1
  for i in hack:
    code = i.to_bytes(4, byteorder='big')
    if state == -1:
      #item this item needs to contain state
      if code[0] == 0x4:
        #04 code, simple replace
        state = code[0]
      else:
        print(f'Invalid gecko code entry {code[0]}')
        exit()
      #now get address
      address = int.from_bytes(code[1:4], byteorder='big')
      #add address offset
      address += 0x80000000
      print (f'{hex(state)}, {hex(address)}')
    else:
      if state == 0x4:
        #calculate file address
        file_address = get_file_from_memory_address(dol_table, address)
        #get original data for debug purposes
        with open(dol, "r+b") as dol_reader:
          dol_reader.seek(file_address)
          original = int.from_bytes(dol_reader.read(4), byteorder='big', signed=False)
          dol_reader.seek(file_address)
          dol_reader.write(code)

        #now do the simple replace with the new data
        print(f'replacing {hex(original)} with {code.hex()}) at {hex(address)}:{hex(file_address)}')
        #only 4 bytes can be swallowed here
        state = -1
