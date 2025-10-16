import argparse

import os
import shutil
import pathlib
import math
import sys
import traceback

import lib.assembly
import lib.iso
import lib.metadata_loader
import lib.insert_mod
import lib.level
import lib.dol
import lib.hacks
import lib.scratch_memory
import lib.secondary_save_file
import lib.file_edits
import lib.ma_tools.mst_insert

STAGE2_FILE="stage2.bin"
CODES_FILE="codes.bin"

class IsoExtractionException(Exception):
    def __init__(self,
                 msg="Error occured with iso extraction, verify that the .iso file is a Metal Arms NTSC unmodified iso (not nkit.iso or .ciso) and that it is on the same system drive as Exavolt",
                 *args,
                 **kwargs):
        super().__init__(msg, *args, **kwargs)

class ModInsertionException(Exception):
    def __init__(self,
                 msg="Error inserting mods, verify that all mods are valid and try again.",
                 *args,
                 **kwargs):
        super().__init__(msg, *args, **kwargs)

class IsoRebuildException(Exception):
    def __init__(self,
                 msg="Error rebuilding iso, verify that you have enough free space and that the input iso and mods are valid",
                 *args,
                 **kwargs):
        super().__init__(msg, *args, **kwargs)

def execute(input_iso, output_iso, mod_folder, extract_only, no_rebuild, files):
  sp_level_index = 0
  mp_level_index = 0
  hacks = set()
  csv_edits = []
  assembly_files = set()
  # Scratch memory is used by mods that want to store and access constants at
  # runtime. This is to prevent this issue where mods just use a random space of
  # likely unused code without any checks or verification.
  # Scratch memory is stored in a list to be passed by value
  scratch_memory_size = [0]
  scratch_memory_dict = lib.scratch_memory.default_scratch_memory_entries(scratch_memory_size)

  player_bot_list = lib.level.LEVEL_BOT_MAP.copy()
  sp_level_list = lib.level.DEFAULT_SP_LEVEL_ARRAY.copy()
  mp_level_list = lib.level.DEFAULT_MP_LEVEL_ARRAY.copy()

  level_invent_dict_list_initial = [False] * 58 # used for seeing if its modified
  level_invent_dict_list = level_invent_dict_list_initial.copy()
  try:
    if extract_only or no_rebuild:
      tmp_dir_name = lib.iso.extract_iso(input_iso, str(output_iso))
      if extract_only:
        return
    else:
      tmp_dir = lib.iso.extract_iso(input_iso)
      tmp_dir_name = tmp_dir.name
    dol = os.path.join(tmp_dir_name,"root", "sys", "main.dol")
  except Exception:
    raise IsoExtractionException()

  lib.level.init_default_levels(tmp_dir_name)

  has_assembly_files = False
  stage2_file_location = os.path.join(tmp_dir_name, STAGE2_FILE)
  pathlib.Path(stage2_file_location).touch()
  codes_file_location = os.path.join(tmp_dir_name, CODES_FILE)
  pathlib.Path(codes_file_location).touch()
  # first add default mods
  # These mods add baseline new functionality to metal arms mods and this allows modders to assume the user has access to these.
  mod_metadatas = lib.metadata_loader.collect_mods(os.path.join(os.path.dirname(os.path.realpath(__file__)),"default_mods"))

  for metadata in mod_metadatas:
    # tag these mods as default
    metadata.is_default = True

  try:
    if files is None or not len(files):
      mod_metadatas += lib.metadata_loader.collect_mods(mod_folder)
    else:
      mod_metadatas += lib.metadata_loader.collect_mods_from_files(files)

    for metadata in mod_metadatas:
      summary = metadata.summary()
      #add hacks
      for hack in summary["Hacks Required"]:
        hacks.add(hack)
      # see if there are any assembly injections, if so need to expand the dol
      if metadata.has_assembly_files:
        has_assembly_files = True
        print("Injecting assembly")


    for metadata in mod_metadatas:
      if metadata.is_default:
        # Skip default mods which arent explicitly mentioned
        print (metadata.title, hacks)
        if metadata.title not in hacks:
          continue
      summary = metadata.summary()
      print(summary)
      campaign_level_count = summary["Campaign Levels"]
      mp_level_count = summary["Multiplayer Levels"]
      #add global scratch memory entries
      for entry in summary["Scratch memory entries"]:
        if entry['global']:
          lib.scratch_memory.add_entry_to_dict(entry, scratch_memory_dict, scratch_memory_size)
      #add csv edits
      for csv_edit in summary["CSV Edits"]:
        csv_edits.append(csv_edit)
      if campaign_level_count + sp_level_index > len(lib.level.CAMPAIGN_LEVEL_NAMES):
        print(f'Too many single player levels being injected! {campaign_level_count + sp_level_index} exceeds the limit of {len(lib.level.CAMPAIGN_LEVEL_NAMES)} ')
        raise ModInsertionException()
      if mp_level_count + mp_level_index > len(lib.level.MULTIPLAYER_LEVEL_NAMES):
        print(f'Too many single player levels being injected! {mp_level_count + mp_level_index} exceeds the limit of {len(lib.level.MULTIPLAYER_LEVEL_NAMES)} ')
        raise ModInsertionException()
      lib.insert_mod.insert_mod(metadata, tmp_dir_name, sp_level_index, mp_level_index, dol, True, codes_file_location, player_bot_list, level_invent_dict_list, scratch_memory_dict, scratch_memory_size)
      sp_level_index += campaign_level_count
      mp_level_index += mp_level_count
  except Exception:
    raise ModInsertionException()


  try:
    # copy over the corrected bi2.bin
    new_bi2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "bi2.bin")
    old_bi2 = os.path.join(tmp_dir_name,"root", "sys", "bi2.bin")
    shutil.copy(new_bi2, old_bi2)
  except Exception:
    raise ValueError("Error modifying bi2.bin")

  try:
    #apply dol hacks
    for hack in hacks:
      if lib.hacks.HACKS[hack] == True:
        # These are fake hacks that are actually default mods.
        continue
      print(f'Applying {hack}')
      lib.dol.apply_hack(dol, lib.hacks.HACKS[hack])
  except Exception:
    raise ValueError("Error applying dol hacks")

  try:
    #apply csv edits
    # First combine to a dict of file : edits
    csv_dict = {}
    for csv_edit in csv_edits:
      if csv_edit['file'] not in csv_dict:
        # lazy copy just leave file in both places
        csv_dict[csv_edit['file']] = [csv_edit]
      else:
        csv_dict[csv_edit['file']].append(csv_edit)

    for csv_file, values in csv_dict.items():
      print(f'Applying csv edits to {csv_file}\n{values}')
      lib.file_edits.apply_csv_edits(metadata, tmp_dir_name, csv_file, values, True)
  except Exception:
    raise ValueError("Error applying csv edits")

  try:
    # Always insert bot type spawning
    print("Inserting player bot modifications")
    #has_assembly_files = True
    #lib.dol.apply_hack(dol, lib.hacks.DISABLE_HUD_CREATE)
    #player_bot_list = [level.starting_bot for level in sp_level_list + mp_level_list]
    #lib.assembly.insert_player_spawn_into_codes_file(codes_file_location, player_bot_list)

    # Insert player invent changes
    if level_invent_dict_list != level_invent_dict_list_initial:
      print("Inserting player inventory modifications")
      has_assembly_files = True
      lib.assembly.insert_player_inventory_into_codes_file(codes_file_location, level_invent_dict_list)

    asm_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"asm")

    # With the addition of scratch memory,
    # we will always have assembly files to insert
    print("Updating dol table from:")
    lib.dol.parse_dol_table(dol, True)
    lib.dol.add_code_section(dol)
    print("Updating dol table to:")
    lib.dol.parse_dol_table(dol, True)
    print("Injecting stage 1 injector")
    lib.dol.inject_assembly(dol, os.path.join(asm_path, "CodeInjectorStage1.asm"), 0x80003258)

    print("Injecting stage 2 injector")
    # First stage parse cant handle type information so don't include it
    lib.assembly.insert_assembly_into_codes_file(stage2_file_location,
        os.path.join(asm_path, "CodeInjectorStage2.asm"),
        0x8029e468, {}, False)

    # Add scratch memory declaration script
    scratch_memory_dict['SCRATCH_MEMORY_SIZE'] = scratch_memory_size[0]
    lib.assembly.insert_assembly_into_codes_file(codes_file_location,
        os.path.join(asm_path, "DeclareScratchMemory.asm"),
        0x80156758, scratch_memory_dict, immediate_exec = True)

    # Add secondary save file codes
    lib.secondary_save_file.apply_secondary_save_file_codes(
        scratch_memory_dict,
        asm_path,
        codes_file_location)

    iso_mst = os.path.join(tmp_dir_name, "root", "files", "mettlearms_gc.mst")

    # Override level array!
    lib.level.apply_level_array_codes(
        dol,
        scratch_memory_dict,
        asm_path,
        codes_file_location,
        sp_level_list,
        mp_level_list,
        tmp_dir_name,
        True)

    print(scratch_memory_dict)

    lib.ma_tools.mst_insert.execute(True, iso_mst, [stage2_file_location, codes_file_location], "")

  except Exception:
    raise ValueError("Error assembling assembly models")

  try:
    if no_rebuild:
      return
    #rebuild iso
    lib.iso.rebuild_iso(os.path.abspath(output_iso), os.path.join(tmp_dir_name,"root"))

    #Pad iso to be divisible by 80 bytes
    file_stat = os.stat(os.path.abspath(output_iso))
    file_size = file_stat.st_size
    # Always add 80 bytes for safety or something idk / maybe im having file size issues?
    bytes_to_add = (int(math.ceil(file_size / 80.0)) * 80) - file_size + 80
    print(bytes_to_add)
    with open(os.path.abspath(output_iso), 'ab') as iso_file:
      iso_file.write(b'\x00' * bytes_to_add)
  except Exception:
    raise IsoRebuildException()

if __name__ == '__main__':
  if getattr(sys, 'frozen', False):
    # if running in a frozen exe
    root_path = pathlib.Path(sys.executable).resolve().parent
  else:
    root_path = pathlib.Path(__file__).resolve().parent

  parser = argparse.ArgumentParser(description="Add mods to Metal Arms ISO file")
  parser.add_argument("input_iso", help="A valid vanilla Metal Arms Iso File", type=pathlib.Path, nargs='?', default=root_path / "metalarms.iso")
  parser.add_argument("output_iso", help="Name of the new output iso which will be produced", type=pathlib.Path, nargs='?', default=root_path / 'mod.iso')
  parser.add_argument("mod_folder", help="Folder containing all mods which the user will have the option of adding", type=pathlib.Path, nargs='?', default=root_path / "mods")
  parser.add_argument("-E", "--extract_only", help="Extracts the iso to a folder named [output_iso] and does no processing, useful for debugging", action='store_true')
  parser.add_argument("-N", "--no-rebuild", help="Extracts the iso to a folder named [output_iso] and adds mods but does not rebuild, useful for debugging", action='store_true')
  parser.add_argument("-f", "--file", help="Manually named files to insert, disables usage of mod folder", action='append_const', const=str)
  args = parser.parse_args()

  try:
    execute(args.input_iso, args.output_iso, args.mod_folder, args.extract_only, args.no_rebuild, args.file)
    print("Success! Press <Enter> to continue...")
  except Exception:
    print(sys.exc_info()[0])
    print(traceback.format_exc())
    print("Error, press <Enter> to continue...")
  finally:
    input()
