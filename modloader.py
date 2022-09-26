import argparse

import os
import shutil
import lib.iso
import lib.metadata_loader
import lib.insert_mod
import lib.level

def execute(input_iso, output_iso, mod_folder):
  sp_level_index = 0
  mp_level_index = 0

  tmp_dir = lib.iso.extract_iso(input_iso)
  mod_metadatas = lib.metadata_loader.collect_mods(mod_folder)
  for metadata in mod_metadatas:
    summary = metadata.summary()
    print(summary)
    campaign_level_count = summary["Campaign Levels"]
    mp_level_count = summary["Multiplayer Levels"]
    if campaign_level_count + sp_level_index >= len(lib.level.CAMPAIGN_LEVEL_NAMES):
      #Just skip mods if they have too many levels
      continue
    if mp_level_count + mp_level_index >= len(lib.level.MULTIPLAYER_LEVEL_NAMES):
      #Just skip mods if they have too many levels
      continue
    lib.insert_mod.insert_mod(metadata, tmp_dir, sp_level_index, mp_level_index, True)
    sp_level_index += campaign_level_count
    mp_level_index += mp_level_count

  # copy over the corrected bi2.bin
  new_bi2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "bi2.bin")
  old_bi2 = os.path.join(tmp_dir.name,"root","sys","bi2.bin")
  shutil.copy(new_bi2, old_bi2)
  lib.iso.rebuild_iso(os.path.abspath(output_iso), os.path.join(tmp_dir.name,"root"))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Add mods to Metal Arms ISO file")
  parser.add_argument("input_iso", help="A valid vanilla Metal Arms Iso File", nargs='?', default='metalarms.iso')
  parser.add_argument("output_iso", help="Name of the new output iso which will be produced", nargs='?', default='mod.iso')
  parser.add_argument("mod_folder", help="Folder containing all mods which the user will have the option of adding", nargs='?', default='mods')
  args = parser.parse_args()

  execute(args.input_iso, args.output_iso, args.mod_folder)
