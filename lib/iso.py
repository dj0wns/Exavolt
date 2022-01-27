import tempfile
from pathlib import Path
from pyisotools.iso import GamecubeISO

# Extracts the iso to a tmp dir and returns that directory
def extract_iso(input_iso):
  tmpdirname = tempfile.TemporaryDirectory()
  print(f'Extracting {input_iso} to {tmpdirname.name}')
  src = Path(input_iso).resolve()
  iso = GamecubeISO.from_iso(src)
  iso.extract(tmpdirname.name)
  return tmpdirname

# Rebuilds a gc iso given a folder and a destinatioN
def rebuild_iso(output_iso, iso_dir):
  print(f'Rebuilding {iso_dir} to {output_iso}')
  src = Path(iso_dir).resolve()
  iso = GamecubeISO.from_root(src)
  iso.build(output_iso)
