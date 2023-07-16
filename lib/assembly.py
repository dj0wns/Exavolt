import tempfile
import struct
from pathlib import Path
from lib.pyiiasmh.ppctools import PpcFormatter

# Anatomy of an assembmly injection
# At "injection point" add a branch instruction to the new code: b 0x8000xxxx - 0x48[relative jump]
# compile code at point.
# Add a trailing branch statement to return to the insertion point 0x4b?, maybe the b means negative for 2's complemenT

def assemble_code_to_bytes(file):
  # Pyiiashm modifies the original file for formatting sake so move the input file to a temp dir.
  tmpdir = Path(tempfile.mkdtemp(prefix="pyiiasmh-"))
  formatter = PpcFormatter()
  formatter.bapo = False
  machine_code = formatter.asm_opcodes(tmpdir, file)
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

def insert_assembly_into_codes_file(codes_file_location, file, address):
  bytes = assemble_code_to_bytes(file)

  # now inject the code into the dol
  with open(codes_file_location, "r+b") as dol_writer:
    dol_writer.write(struct.pack(">I", len(bytes)))
    dol_writer.write(struct.pack(">I", address))
    dol_writer.write(bytes)
