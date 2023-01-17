import argparse

import os
import shutil
import pathlib
import math

import lib.iso
import lib.metadata_loader
import lib.insert_mod
import lib.level
import lib.dol
import lib.hacks

def execute(input_iso, output_iso, mod_folder, extract_only, no_rebuild):
  sp_level_index = 0
  mp_level_index = 0
  hacks = set()
  assembly_files = set()

  if extract_only or no_rebuild:
    tmp_dir_name = lib.iso.extract_iso(input_iso, str(output_iso))
    if extract_only:
      return
  else:
    tmp_dir = lib.iso.extract_iso(input_iso)
    tmp_dir_name = tmp_dir.name


  dol = os.path.join(tmp_dir_name,"root", "sys", "main.dol")

  mod_metadatas = lib.metadata_loader.collect_mods(mod_folder)
  for metadata in mod_metadatas:
    # see if there are any assembly injections, if so need to expand the dol
    if metadata.assembly_files:
      # 42000 bytes is the current maximum we can expand by
      print("Updating dol table from:")
      lib.dol.parse_dol_table(dol, True)
      lib.dol.add_code_section(dol)
      print("Updating dol table to:")
      lib.dol.parse_dol_table(dol, True)
      break

  for metadata in mod_metadatas:
    summary = metadata.summary()
    print(summary)
    campaign_level_count = summary["Campaign Levels"]
    mp_level_count = summary["Multiplayer Levels"]
    #add hacks
    for hack in summary["Hacks Required"]:
      hacks.add(hack)
    if campaign_level_count + sp_level_index > len(lib.level.CAMPAIGN_LEVEL_NAMES):
      #Just skip mods if they have too many levels
      continue
    if mp_level_count + mp_level_index > len(lib.level.MULTIPLAYER_LEVEL_NAMES):
      #Just skip mods if they have too many levels
      continue
    lib.insert_mod.insert_mod(metadata, tmp_dir_name, sp_level_index, mp_level_index, dol, True)
    sp_level_index += campaign_level_count
    mp_level_index += mp_level_count

  # copy over the corrected bi2.bin
  new_bi2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "bi2.bin")
  old_bi2 = os.path.join(tmp_dir_name,"root", "sys", "bi2.bin")
  shutil.copy(new_bi2, old_bi2)

  #apply dol hacks
  for hack in hacks:
    print(f'Applying {hack}')
    lib.dol.apply_hack(dol, lib.hacks.HACKS[hack])

  if no_rebuild:
    return
  #rebuild iso
  lib.iso.rebuild_iso(os.path.abspath(output_iso), os.path.join(tmp_dir_name,"root"))

  #Pad iso to be divisible by 80 bytes
  file_stat = os.stat(os.path.abspath(output_iso))
  file_size = file_stat.st_size

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Add mods to Metal Arms ISO file")
  parser.add_argument("input_iso", help="A valid vanilla Metal Arms Iso File", type=pathlib.Path, nargs='?', default='metalarms.iso')
  parser.add_argument("output_iso", help="Name of the new output iso which will be produced", type=pathlib.Path, nargs='?', default='mod.iso')
  parser.add_argument("mod_folder", help="Folder containing all mods which the user will have the option of adding", type=pathlib.Path, nargs='?', default='mods')
  parser.add_argument("-E", "--extract_only", help="Extracts the iso to a folder named [output_iso] and does no processing, useful for debugging", action='store_true')
  parser.add_argument("-N", "--no-rebuild", help="Extracts the iso to a folder named [output_iso] and adds mods but does not rebuild, useful for debugging", action='store_true')
  args = parser.parse_args()

  execute(args.input_iso, args.output_iso, args.mod_folder, args.extract_only, args.no_rebuild)
