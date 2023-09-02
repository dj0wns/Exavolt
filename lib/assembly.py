import tempfile
import os
import struct
import shutil
import lib.assembly_codes
from pathlib import Path
from lib.pyiiasmh.ppctools import PpcFormatter
from enum import Enum

# Anatomy of an assembmly injection
# At "injection point" add a branch instruction to the new code: b 0x8000xxxx - 0x48[relative jump]
# compile code at point.
# Add a trailing branch statement to return to the insertion point 0x4b?, maybe the b means negative for 2's complemenT

class CodeTypes(Enum) :
  STANDARD = 0
  CUSTOM_RETURN = 1

def assemble_code_to_bytes(file):
  # Pyiiashm modifies the original file for formatting sake so move the input file to a temp dir.
  tmpdir = Path(tempfile.mkdtemp(prefix="pyiiasmh-"))
  # copy file in the short term to not mess with formatting
  new_file_path = os.path.join(tmpdir, os.path.basename(file))
  new_file = shutil.copyfile(file, new_file_path)
  formatter = PpcFormatter()
  formatter.bapo = False
  machine_code = formatter.asm_opcodes(tmpdir, new_file)
  # remove spaces and convert to bytes
  machine_code = machine_code.replace(" ", "").replace("\n","")
  return bytes.fromhex(machine_code)

def get_jump_instruction(start, end):
  jump_distance = end - start
  if jump_distance < 0:
    # jump backwards
    return 0x4b000000 | (jump_distance & 0x00ffffff)
  else:
    # jump forwards
    return 0x48000000 | (jump_distance & 0x00ffffff)

def insert_assembly_into_codes_file(codes_file_location, file, address, include_type = True):
  bytes = assemble_code_to_bytes(file)
  insert_bytes_into_codes_file(codes_file_location, bytes, address, include_type)

# code type is the enum declared above
def insert_bytes_into_codes_file(codes_file_location, bytes, address, include_type = True):
  # now inject the code into the dol
  with open(codes_file_location, "ab") as dol_writer:
    if include_type:
      dol_writer.write(struct.pack(">I", CodeTypes.STANDARD.value))
    dol_writer.write(struct.pack(">I", len(bytes)))
    dol_writer.write(struct.pack(">I", address))
    dol_writer.write(bytes)

# code type is the enum declared above
def insert_code_with_explicit_return_address_into_codes_file(codes_file_location, file, address, return_address):
  bytes = assemble_code_to_bytes(file)
  # now inject the code into the dol
  with open(codes_file_location, "ab") as dol_writer:
    dol_writer.write(struct.pack(">I", CodeTypes.CUSTOM_RETURN.value))
    dol_writer.write(struct.pack(">I", len(bytes)))
    dol_writer.write(struct.pack(">I", address))
    dol_writer.write(struct.pack(">I", return_address))
    dol_writer.write(bytes)

def insert_assembly_into_codes_file(codes_file_location, file, address, include_type = True):
  bytes = assemble_code_to_bytes(file)
  insert_bytes_into_codes_file(codes_file_location, bytes, address, include_type)

def insert_level_assembly_into_codes_file(dol, codes_file_location, file, address, level_index):
  level_switch_code = f"""
 ####### LEVEL BYPASS CODES ######

 lis r12, 0x804b # Level index offset
 ori r12, r12, 0x891c
 lwz r12, 0(r12)
 cmpwi r12, {level_index}
 beq CODE_BLOCK_EXAVOLT_UNIQUE_NAME # correct level so do code stuff, use a contrived long name so we dont clash
 ori r0, r0, 0 #dummy noop to be replaced with the original code at the insertion point, 0x60000000
 b END_OF_CODE_EXAVOLT_UNIQUE_NAME
 CODE_BLOCK_EXAVOLT_UNIQUE_NAME:

 ####### LEVEL BYPASS CODES ######

  """
  # Prepend switch code to file
  # first read entire file into memory so we can do that
  with open(file, 'r') as original:
    data = original.read()

  data = level_switch_code + data + "\nEND_OF_CODE_EXAVOLT_UNIQUE_NAME:\n"

  with open(file, 'w') as new_file:
    new_file.write(data)

  bytes = assemble_code_to_bytes(file)
  #now replace the noop with the orignal code at the target location
  from lib.dol import parse_dol_table, get_file_from_memory_address
  table = parse_dol_table(dol)
  file_address = get_file_from_memory_address(table, address)
  with open(dol, "rb") as dol_reader:
    dol_reader.seek(file_address)
    original = dol_reader.read(4)
  bytes = bytes.replace(int(0x60000000).to_bytes(4, byteorder='big'), original)

  insert_bytes_into_codes_file(codes_file_location, bytes, address)

# Expected dict format:
# "primary" : list(dict("name", "clip_ammo", "reserve_ammo"))
# "secondary" : list(dict("name", "clip_ammo", "reserve_ammo"))
# "battery_count" : int - default 3
def insert_player_inventory_into_codes_file(codes_file_location, level_invent_dict_list):
  insertion_address = 0x801c87d0
  player_invent_code = lib.assembly_codes.HEADERS
  for i in range(1,58):
    code_string = ""
    # no mods to the weapons so don't add any code
    # ALL keys must be specified!!!
    level_invent_map = level_invent_dict_list[i]
    if not level_invent_map:
      continue
    if level_invent_map["primary"]:
      # store some stuff on the stack, copied from CInventory::SetToDefaults
      code_string += r"""
        stwu r1, -0x10(r1) ; Move stack up 10
        mfspr r0, LR ; save link register
        stw r0, 0x14(r1) ; save r0
        stw r31, 0xc(r1) ; save r31

        addi r31, r26, 0x19b0 ; Bot inventory pointer

        or r3, r31, r31
        li r4, 0x568
        call fang_MemZero ; zero out the inventory
      """

      battery_count = level_invent_map["battery_count"] if "battery_count" in level_invent_map else 3
      code_string += f"li r0, {battery_count}\n"
      code_string += "stb r0, 0xc7(r31)\n" # store batteries

      # now set up inventory sizes
      code_string += f"""
        li r0, {len(level_invent_map["primary"])}
        stb r0, 0xc4(r31)

        li r0, {len(level_invent_map["secondary"])}
        stb r0, 0xc5(r31)

        li r0, 1 ; Default primary slot
        stb r0, 0x55c(r31)

        li r0, 0 ; Default secondary slot
        stb r0, 0x55d(r31)

        lbz r0, 0x55c(r31) ; primary saved weapons??
        stb r0, 0x55e(r31)

        lbz r0, 0x55d(r31) ; secondary saved weapons??
        stb r0, 0x55f(r31)

        li r0, 0 ; euk flags??
        sth r0, 0x548(r31)
      """
      item_size = 24
      primary_offset = 200
      secondary_offset = 584
      for item in level_invent_map["primary"]:
        # Set up player inventory pointer
        if item["name"].lower() not in lib.assembly_codes.WEAPON_STRING_ADDR_DICT:
          raise ValueException(f"Unknown weapon type: {item['name']} on level {i}")
        weapon_offset = lib.assembly_codes.WEAPON_STRING_ADDR_DICT[item['name'].lower()]
        # increment offset
        code_string += f"""
          or r3, r31, r31 ; inventory pointer
          addi r4, r31, {primary_offset}
          lis r5, {weapon_offset}@h
          ori r5, r5, {weapon_offset}@l
          li r6, {item['clip_ammo']}
          li r7, {item['reserve_ammo']}
          call InitItemInst
        """
        primary_offset += item_size
      for item in level_invent_map["secondary"]:
        # Set up player inventory pointer
        if item["name"].lower() not in lib.assembly_codes.WEAPON_STRING_ADDR_DICT:
          raise ValueException(f"Unknown weapon type: {item['name']} on level {i}")
        weapon_offset = lib.assembly_codes.WEAPON_STRING_ADDR_DICT[item['name'].lower()]
        # increment offset
        code_string += f"""
          or r3, r31, r31 ; inventory pointer
          addi r4, r31, {secondary_offset}
          lis r5, {weapon_offset}@h
          ori r5, r5, {weapon_offset}@l
          li r6, {item['clip_ammo']}
          li r7, {item['reserve_ammo']}
          call InitItemInst
        """
        secondary_offset += item_size
      # now finish up, pull items off stack and revert the stack
      code_string += r"""
          or r3, r31, r31 ; Temp because seems to be needed to load glitch
          call SetupDefaultItems

          lwz r0, 0x14(r1)
          lwz r31, 0xc(r1)
          mtspr LR, r0
          addi r1, r1, 0x10
      """

    # add if statements for all levels
    player_invent_code += lib.assembly_codes.LEVEL_IF_CHECK.format(
        level_index=i, code_string=code_string,
        next_label=f"PLAYER_INVENT_LEVEL_INDEX_{i}",
        end_label=f"END_OF_PLAYER_INVENT_CODE")
  # add final jump code
  player_invent_code += "\nEND_OF_PLAYER_INVENT_CODE:\n"
  player_invent_code += "cmpwi r1, -1\n" # never be true

  with tempfile.NamedTemporaryFile() as code_file:
    code_file.write(bytes(player_invent_code, 'ascii'))
    code_file.flush()

    insert_assembly_into_codes_file(
        codes_file_location, code_file.name, insertion_address)

def insert_player_spawn_into_codes_file(codes_file_location, level_bot_map):
  insertion_address = 0x80197dd4
  return_address = 0x80197fb4
  player_spawn_code = lib.assembly_codes.HEADERS
  for i in range(1,58):
    code_string = ""
    if level_bot_map[i].lower() == "glitch":
      code_string=lib.assembly_codes.SPAWN_AS_GLITCH
    elif level_bot_map[i].lower() == "mozer":
      code_string=lib.assembly_codes.SPAWN_AS_MOZER
    elif level_bot_map[i].lower() == "krunk":
      code_string=lib.assembly_codes.SPAWN_AS_KRUNK
    elif level_bot_map[i].lower() == "slosh":
      code_string=lib.assembly_codes.SPAWN_AS_SLOSH
    else:
      raise ValueException(f"Unknown player bot type: {level_bot_map[i]} on level {i}")
    # add if statements for all levels
    player_spawn_code += lib.assembly_codes.LEVEL_IF_CHECK.format(
        level_index=i, code_string=code_string,
        next_label=f"PLAYER_SPAWN_LEVEL_INDEX_{i}",
        end_label=f"END_OF_PLAYER_SPAWN_CODE")
  # add final jump code
  player_spawn_code += "\nEND_OF_PLAYER_SPAWN_CODE:\n"

  with tempfile.NamedTemporaryFile() as code_file:
    code_file.write(bytes(player_spawn_code, 'ascii'))
    code_file.flush()

    insert_code_with_explicit_return_address_into_codes_file(
        codes_file_location, code_file.name, insertion_address, return_address)



