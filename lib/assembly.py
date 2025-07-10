import tempfile
import os
import struct
import shutil
import lib.assembly_codes
import jinja2
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
  print(file, new_file_path)
  new_file = shutil.copyfile(file, new_file_path)
  formatter = PpcFormatter()
  formatter.bapo = False
  machine_code = formatter.asm_opcodes(str(tmpdir)+os.sep, new_file)
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

def insert_assembly_into_codes_file(codes_file_location, file, address, jinja_replacement_dict, include_type = True):

  result_file = file + '.tmp'
  # Read in the file to apply the template code
  with open(file, 'r') as original:
    data = original.read()

  # Apply jinja scratch memory overrides
  path = Path(__file__).parent / 'macros'
  environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
  template = environment.from_string(data)
  data = template.render(jinja_replacement_dict)

  with open(result_file, 'w') as new_file:
    new_file.write(data)

  bytes = assemble_code_to_bytes(result_file)
  insert_bytes_into_codes_file(codes_file_location, bytes, address, include_type)

def insert_level_assembly_into_codes_file(dol, codes_file_location, file, address, level_index, jinja_replacement_dict):
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
  result_file = file + '.tmp'
  # Prepend switch code to file
  # first read entire file into memory so we can do that
  with open(file, 'r') as original:
    data = original.read()

  data = level_switch_code + data + "\nEND_OF_CODE_EXAVOLT_UNIQUE_NAME:\n"


  # Apply jinja scratch memory overrides
  environment = jinja2.Environment()
  template = environment.from_string(data)
  data = template.render(jinja_replacement_dict)

  with open(result_file, 'w') as new_file:
    new_file.write(data)

  bytes = assemble_code_to_bytes(result_file)
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
      default_primary_slot = level_invent_map["default_primary_slot"] if "default_primary_slot" in level_invent_map else 1
      default_secondary_slot = level_invent_map["default_secondary_slot"] if "default_secondary_slot" in level_invent_map else 0

      # now set up inventory sizes
      code_string += f"""
        li r0, {battery_count} ; battery count
        stb r0, 0xc7(r31)

        li r0, {len(level_invent_map["primary"])}
        stb r0, 0xc4(r31)

        li r0, {len(level_invent_map["secondary"])}
        stb r0, 0xc5(r31)

        li r0, {default_primary_slot} ; Default primary slot
        stb r0, 0x55c(r31)

        li r0, {default_secondary_slot} ; Default secondary slot
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

      # now load secondary items
      washer_count = level_invent_map["washer_count"] if "washer_count" in level_invent_map else 0
      code_string += f"""
         or r3, r31, r31 ; inventory pointer
         li r4, 0 ; Inventory position
         lis r5, 0x803ae820@h ; "Washer"
         ori r5, r5, 0x803ae820@l
         li r6, {washer_count}
         call SetupItem
      """

      chip_count = level_invent_map["chip_count"] if "chip_count" in level_invent_map else 0
      code_string += f"""
         or r3, r31, r31 ; inventory pointer
         li r4, 1 ; Inventory position
         lis r5, 0x803ae827@h ; "Chip"
         ori r5, r5, 0x803ae827@l
         li r6, {chip_count}
         call SetupItem
      """

      secret_chip_count = level_invent_map["secret_chip_count"] if "secret_chip_count" in level_invent_map else 0
      code_string += f"""
         or r3, r31, r31 ; inventory pointer
         li r4, 2 ; Inventory position
         lis r5, 0x803ae82c@h ; "Secret Chip"
         ori r5, r5, 0x803ae82c@l
         li r6, {secret_chip_count}
         call SetupItem
      """

      arm_servo_count = level_invent_map["arm_servo_count"] if "arm_servo_count" in level_invent_map else 1
      code_string += f"""
         or r3, r31, r31 ; inventory pointer
         li r4, 3 ; Inventory position
         lis r5, 0x803ae838@h ; "Arm Servo"
         ori r5, r5, 0x803ae838@l
         li r6, {arm_servo_count}
         call SetupItem
      """

      det_pack_count = level_invent_map["det_pack_count"] if "det_pack_count" in level_invent_map else 0
      code_string += f"""
         or r3, r31, r31 ; inventory pointer
         li r4, 4 ; Inventory position
         lis r5, 0x803ae842@h ; "Det Pack"
         ori r5, r5, 0x803ae842@l
         li r6, {det_pack_count}
         call SetupItem
      """

      goff_part_count = level_invent_map["goff_part_count"] if "goff_part_count" in level_invent_map else 0
      code_string += f"""
         or r3, r31, r31 ; inventory pointer
         li r4, 5 ; Inventory position
         lis r5, 0x803ae84b@h ; Goff Part
         ori r5, r5, 0x803ae84b@l
         li r6, {goff_part_count}
         call SetupItem
      """

      # Now final inventory fixups
      code_string += r"""
         li r3, 0x6 ; inventory item count
         stb r3, 0xc6(r31)
         li r0, 0 ; num inventory pickups??
         stb r0, 0x0(r31)
      """
      # now finish up, pull items off stack and revert the stack
      code_string += r"""

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

  # Windows wont allow 2 file handles i guess. shutil fails to work with this
  code_file = tempfile.NamedTemporaryFile(delete=False)
  code_file.write(bytes(player_invent_code, 'ascii'))
  code_file.flush()
  code_file.close()

  insert_assembly_into_codes_file(
    codes_file_location, code_file.name, insertion_address, {})
  # manually delete code file!
  os.unlink(code_file.name)

def random_bot_code(level_prefix):
  total_bots = len(lib.assembly_codes.BOT_NAME_DICT)
  random_code = f"""
  call fmath_RandomInt32 # puts random int in r3
  # modulus
  li r4, {total_bots}
  divwu r4, r3, r4
  mulli r4, r4, {total_bots}
  subf r3, r4, r3
  """
  # now lazy jump table to iterate to the matching bot
  bot_number = 0
  for bot_code in lib.assembly_codes.BOT_NAME_DICT.values():
    random_code += f"""
      cmplwi r3, {bot_number}
      bne {level_prefix}_BOT_LABEL_{bot_number}
      # dont forget to replace generic labels to make sure they are unique!
      {bot_code.replace("LABEL", level_prefix + "_BOT_SUB_LABEL_" + str(bot_number))}
      b {level_prefix}_BOT_LABEL_{total_bots-1}
      {level_prefix}_BOT_LABEL_{bot_number}:
    """
    bot_number += 1
  return random_code


def insert_player_spawn_into_codes_file(codes_file_location, level_bot_map):
  internal_label_count = 0
  insertion_address = 0x80197dd4
  return_address = 0x80197fb4
  player_spawn_code = lib.assembly_codes.HEADERS
  for i in range(1,58):
    code_string = ""
    level_prefix = f"LEVEL_{i}_PREFIX_"
    lower_bot_name = level_bot_map[i].lower()
    if lower_bot_name == "random":
      code_string = random_bot_code(level_prefix)
    elif lower_bot_name in lib.assembly_codes.BOT_NAME_DICT:
      # Make sure to replace generic labels to make sure they are unique
      code_string = lib.assembly_codes.BOT_NAME_DICT[lower_bot_name].replace("LABEL", level_prefix)
    else:
      raise ValueException(f"Unknown player bot type: {level_bot_map[i]} on level {i}")
    # perform fixups for labels, allow 25 for now, this is kinda slow though so...
    # This allows for fully unique labels
    for j in range (25):
      if f"{level_prefix}LABEL_{j}" in code_string:
        code_string = code_string.replace(f"{level_prefix}LABEL_{j}", f"{level_prefix}LABEL_{internal_label_count}")
        internal_label_count += 1
      else:
        # no more labels so don't keep looking
        break
    # add if statements for all levels
    player_spawn_code += lib.assembly_codes.LEVEL_IF_CHECK.format(
        level_index=i, code_string=code_string,
        next_label=f"PLAYER_SPAWN_LEVEL_INDEX_{i}",
        end_label=f"END_OF_PLAYER_SPAWN_CODE")
  # add final jump code
  player_spawn_code += "\nEND_OF_PLAYER_SPAWN_CODE:\n"

  # Windows wont allow 2 file handles i guess. shutil fails to work with this
  code_file = tempfile.NamedTemporaryFile(delete=False)
  code_file.write(bytes(player_spawn_code, 'ascii'))
  code_file.flush()
  code_file.close()

  insert_code_with_explicit_return_address_into_codes_file(
        codes_file_location, code_file.name, insertion_address, return_address)
  # manually delete code file!
  os.unlink(code_file.name)

