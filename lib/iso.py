import tempfile
import os
from pathlib import Path
from pyisotools.iso import GamecubeISO

# Extracts the iso to a tmp dir and returns that directory
def extract_iso(input_iso, out_dir = ""):
  tmpdir = ""
  debug = len(out_dir) > 0
  if debug:
    os.makedirs(out_dir, exist_ok=True)
  else:
    tmpdir = tempfile.TemporaryDirectory()
    out_dir = tmpdir.name
  print(f'Extracting {input_iso} to {out_dir}')
  src = Path(input_iso).resolve()
  iso = GamecubeISO.from_iso(src)
  iso.extract(out_dir)
  if debug:
    return None
  else:
    # preserve temporary directory by passing it back
    return tmpdir

# Rebuilds a gc iso given a folder and a destinatioN
def rebuild_iso(output_iso, iso_dir):
  print(f'Rebuilding {iso_dir} to {output_iso}')
  src = Path(iso_dir).resolve()
  iso = GamecubeISO.from_root(src)
  iso.build(output_iso)
