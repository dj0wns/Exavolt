import argparse

import os
import lib.iso
import lib.metadata_loader

def execute(input_iso, output_iso, mod_folder):
  tmp_dir = lib.iso.extract_iso(input_iso)
  mod_metadatas = lib.metadata_loader.collect_mods(mod_folder)
  print(len(mod_metadatas))
  for metadata in mod_metadatas:
    print(metadata.summary())
  lib.iso.rebuild_iso(os.path.abspath(output_iso), os.path.join(tmp_dir.name,"root"))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Add mods to Metal Arms ISO file")
  parser.add_argument("input_iso", help="A valid vanilla Metal Arms Iso File")
  parser.add_argument("output_iso", help="Name of the new output iso which will be produced")
  parser.add_argument("mod_folder", help="Folder containing all mods which the user will have the option of adding")
  args = parser.parse_args()

  execute(args.input_iso, args.output_iso, args.mod_folder)
