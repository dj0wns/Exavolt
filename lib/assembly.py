import tempfile
from pathlib import Path
from pyiiasmh.ppctools import PpcFormatter


def assemble_code_to_bytes(code):
  tmpdir = Path(tempfile.mkdtemp(prefix="pyiiasmh-"))
  formatter = PpcFormatter()
  formatter.bapo = False
  machine_code = formatter.asm_opcodes(tmpdir, "/home/dj0wns/Programming/MetalArmsModLoader/asm/DataHudV2.asm")
  print(machine_code)


