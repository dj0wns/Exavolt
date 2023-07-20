import collections
import os
from lib.assembly import assemble_code_to_bytes, get_jump_instruction

pack_int = '>i' #dols can only be big endian

ntsc_dol_initial_stack_value = 0X804c2aa0
ntsc_safe_new_section_start = 0x804c2b00
stack_added_offset = 0xa0 # this is probably due to a flaw in pointers, investigate

next_code_injection_offset = -1
next_code_injection_virtual_offset = -1
code_injection_max_offset = -1

#The names of the offsets in the dol
offset_names = [
  "Text0",
  "Text1",
  "Text2",
  "Text3",
  "Text4",
  "Text5",
  "Text6",
  "Data0",
  "Data1",
  "Data2",
  "Data3",
  "Data4",
  "Data5",
  "Data6",
  "Data7",
  "Data8",
  "Data9",
  "Data10",
]

def add_code_section(dol):
  # we are going to add a large code block between the heap and the stack. The
  # initial heap allocation is 11.5 MB, so since its a 24 mb system it must be
  # leaving at most 13 MB to the stack so lets start our code section at +15MB
  # past 0x8000000. Give it 1 MB for code which is a lot, can extend later if
  # needed.
  megabyte = 1024*1024
  data_start = 0x80000000 + 15 * megabyte
  data_size = 640
  modify_entry(dol, "Data8", 0x3ffe80, data_size, data_start)

def modify_entry(dol, entry_name, file_start, size, memory_address):
  if entry_name not in offset_names:
    print(f"Invalid entry name: {entry_name}")
    return
  table = parse_dol_table(dol)

  # update globals to keep written state
  global next_code_injection_offset
  global next_code_injection_virtual_offset
  global code_injection_max_offset
  next_code_injection_offset = file_start
  code_injection_max_offset = memory_address + size
  next_code_injection_virtual_offset = memory_address

  dol_table = parse_dol_table(dol)

  index = offset_names.index(entry_name)
  file_offset = 4 * index
  memory_address_offset = 4 * index + 0x48
  size_offset = 4 * index + 0x90
  bss_size_offset = 0xdc
  print(size)
  bytes_to_add = [int(0).to_bytes(1, byteorder='big') for i in range(size)]
  print (hex(file_offset), hex(memory_address_offset), hex(size_offset))
  with open(dol, "r+b") as dol_writer:
    dol_writer.seek(file_offset)
    dol_writer.write(file_start.to_bytes(4, byteorder='big'))
    dol_writer.seek(memory_address_offset)
    dol_writer.write(memory_address.to_bytes(4, byteorder='big'))
    dol_writer.seek(size_offset)
    dol_writer.write(size.to_bytes(4, byteorder='big'))

    dol_writer.seek(bss_size_offset)
    bss_size = int.from_bytes(dol_writer.read(4), byteorder='big', signed=False)
    dol_writer.seek(bss_size_offset)
    dol_writer.write((size + bss_size).to_bytes(4, byteorder='big'))
  with open(dol, "ab") as dol_writer:
    for byte in bytes_to_add:
      dol_writer.write(byte)

def parse_dol_table(dol, debug = False):
  dol_table = {}
  dol_reader = open(dol, "rb")
  file_offsets = []
  memory_offsets = []
  section_sizes = []
  # 7 text segments and 11 data segments
  for i in range(18):
    file_offsets.append(int.from_bytes(dol_reader.read(4), byteorder='big', signed=False))
  for i in range(18):
    memory_offsets.append(int.from_bytes(dol_reader.read(4), byteorder='big', signed=False))
  for i in range(18):
    section_sizes.append(int.from_bytes(dol_reader.read(4), byteorder='big', signed=False))

  if (debug):
    bss_address = int.from_bytes(dol_reader.read(4), byteorder='big', signed=False)
    bss_size = int.from_bytes(dol_reader.read(4), byteorder='big', signed=False)
    entry_point = int.from_bytes(dol_reader.read(4), byteorder='big', signed=False)
    print(f"bss addr: {bss_address}({hex(bss_address)}), size: {bss_size}({hex(bss_size)})")
    print(f"entry_point: {entry_point}({hex(entry_point)})")
    for i in range(len(file_offsets)):
      print(f"{offset_names[i]}: {file_offsets[i]}({hex(file_offsets[i])}) -> {memory_offsets[i]}({hex(memory_offsets[i])}), {section_sizes[i]}({hex(section_sizes[i])}) bytes, end: {section_sizes[i]+file_offsets[i]}({hex(section_sizes[i]+file_offsets[i])}) -> {section_sizes[i]+memory_offsets[i]}({hex(section_sizes[i]+memory_offsets[i])})")

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

def get_memory_from_file_address(table, address):
  file_offset = -1
  for k,v in table.items():
    if v > file_offset and v < address:
      file_offset = v
      memory_offset = k
  address -= file_offset
  memory_offset += address
  return memory_offset

def inject_assembly(dol, file, address):
  global next_code_injection_offset
  global next_code_injection_virtual_offset
  global code_injection_max_offset

  dol_table = parse_dol_table(dol)
  print(f'Injecting {os.path.basename(file)} into main.dol @ {hex(address)}')
  # first assemble the assembly
  bytes = assemble_code_to_bytes(file)

  # now append the return jump
  final_address = next_code_injection_virtual_offset + len(bytes)
  jump_delta = address - final_address
  jump_instruction = get_jump_instruction(final_address, address+4) #dont forget to jump after the caller!
  bytes += jump_instruction.to_bytes(4, byteorder='big')
  print(f'Injection starts at {hex(next_code_injection_virtual_offset)}, and ends at {hex(final_address)} and is {len(bytes)} bytes long. It makes a jump of length {jump_delta}, ({hex(jump_delta)}) with opcode {hex(jump_instruction)}')

  # make sure we dont go past the end of the file!
  if next_code_injection_offset + len(bytes) > code_injection_max_offset:
    raise OverflowError("Too many cheats for the cheat buffer!")

  # now inject the code into the dol
  with open(dol, "r+b") as dol_writer:
    dol_writer.seek(next_code_injection_offset)
    dol_writer.write(bytes)
    # lastly insert the jump to our new code in the main dol
    jump_instruction = get_jump_instruction(address, next_code_injection_virtual_offset)
    print(f'Injecting jump to inserted assembly at {hex(address)} to {hex(next_code_injection_virtual_offset)} with opcode {hex(jump_instruction)}')
    file_address = get_file_from_memory_address(dol_table, address)
    dol_writer.seek(file_address)
    original = int.from_bytes(dol_writer.read(4), byteorder='big', signed=False)
    dol_writer.seek(file_address)
    jump_bytes = jump_instruction.to_bytes(4, byteorder='big')
    dol_writer.write(jump_bytes)
    print(f'replacing {hex(original)} with {jump_bytes.hex()} at {hex(address)}:{hex(file_address)}')

  # now update the globals
  next_code_injection_offset += len(bytes)
  next_code_injection_virtual_offset += len(bytes)

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
