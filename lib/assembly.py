import tempfile
import os
import struct
import shutil
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

# code type is the enum declared above
def insert_bytes_into_codes_file(codes_file_location, bytes, address, include_type = True):
  # now inject the code into the dol
  with open(codes_file_location, "ab") as dol_writer:
    if include_type:
      dol_writer.write(struct.pack(">I", CodeTypes.STANDARD.value))
    dol_writer.write(struct.pack(">I", len(bytes)))
    dol_writer.write(struct.pack(">I", address))
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
