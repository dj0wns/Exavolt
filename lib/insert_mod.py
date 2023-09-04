import tempfile
import zipfile
import os
import shutil
import pathlib
import sys

from .ma_tools import mst_extract
from .ma_tools import mst_insert
from .ma_tools import csv_rebuilder
from .level import CAMPAIGN_LEVEL_NAMES, MULTIPLAYER_LEVEL_NAMES, LEVEL_TYPES
from .assembly import insert_assembly_into_codes_file, insert_level_assembly_into_codes_file
from .dol import apply_hack

FIRST_SP_CSV_INDEX_LEVELS = 6
FIRST_MP_CSV_INDEX_LEVELS = 8
NUM_LINES_PER_LEVEL = 2

PICK_LEVEL_CSV_FILE = "pick_level$.csv"
CSV_SUFFIX = ".new"

MULTI_LEVEL_CSV_FILE = "multi_lvl$.csv"

DOL_LEVEL_ARRAY_OFFSET = 0x803c93ec
DOL_LEVEL_ARRAY_STRUCTURE_SIZE = 44 #bytes

def update_level_attributes(metadata, first_sp_level_index, first_mp_level_index, is_gc, dol):
  # Offset mp by 42 becuase it comes right after
  SP_OFFSET = DOL_LEVEL_ARRAY_OFFSET + (first_sp_level_index) * DOL_LEVEL_ARRAY_STRUCTURE_SIZE
  MP_OFFSET = DOL_LEVEL_ARRAY_OFFSET + (first_mp_level_index + 42) * DOL_LEVEL_ARRAY_STRUCTURE_SIZE
  for level in metadata.levels:
    # set up and increment offsets
    if level["type"] ==  LEVEL_TYPES[0]: #campaign
      offset = SP_OFFSET
      SP_OFFSET += DOL_LEVEL_ARRAY_STRUCTURE_SIZE
    else:
      offset = MP_OFFSET
      MP_OFFSET += DOL_LEVEL_ARRAY_STRUCTURE_SIZE

    # Now replace the 4 hard coded functions as needed. Null all by default unless someone specifically wants one
    load_function_offset = level["load_function_offset"] if "load_function_offset" in level else 0x0
    # Use an 04 code for address so we can reuse more code
    load_function_offset_address_code = ((offset + 20) & 0x00ffffff) | 0x04000000
    file_address = apply_hack(dol, [load_function_offset_address_code, load_function_offset])

    unload_function_offset = level["unload_function_offset"] if "unload_function_offset" in level else 0x0
    # Use an 04 code for address so we can reuse more code
    unload_function_offset_address_code = ((offset + 24) & 0x00ffffff) | 0x04000000
    file_address = apply_hack(dol, [unload_function_offset_address_code, unload_function_offset])

    work_function_offset = level["work_function_offset"] if "work_function_offset" in level else 0x0
    # Use an 04 code for address so we can reuse more code
    work_function_offset_address_code = ((offset + 28) & 0x00ffffff) | 0x04000000
    file_address = apply_hack(dol, [work_function_offset_address_code, work_function_offset])

    draw_function_offset = level["draw_function_offset"] if "draw_function_offset" in level else 0x0
    # Use an 04 code for address so we can reuse more code
    draw_function_offset_address_code = ((offset + 32) & 0x00ffffff) | 0x04000000
    file_address = apply_hack(dol, [draw_function_offset_address_code, draw_function_offset])


def update_pick_level(metadata, iso_dir, first_sp_level_index, first_mp_level_index, is_gc):
  #first extract pick level and multilvl to temp dir
  tmpdirname = tempfile.TemporaryDirectory()
  csv_dir_name = tmpdirname.name

  iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")
  mst_extract.extract(iso_mst, csv_dir_name, False, PICK_LEVEL_CSV_FILE, False)
  mst_extract.extract(iso_mst, csv_dir_name, False, MULTI_LEVEL_CSV_FILE, False)

  #load in sp csv file
  with open(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), 'r') as pick_levels:
    sp_data = pick_levels.readlines()

  #load in mp csv file
  with open(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE), 'r') as mp_levels:
    mp_data = mp_levels.readlines()

  sp_level_name_index = FIRST_SP_CSV_INDEX_LEVELS + NUM_LINES_PER_LEVEL * first_sp_level_index
  mp_level_name_index = FIRST_MP_CSV_INDEX_LEVELS + NUM_LINES_PER_LEVEL * first_mp_level_index
  sp_edited = False
  mp_edited = False
  for level in metadata.levels:
    if level["type"] ==  LEVEL_TYPES[0]: #campaign
      if ("location" in level or
          "title" in level or
          "thumbnail" in level or
          "secret_chip_count" in level,
          "speed_chip_time" in level):
        sp_edited = True
      else:
        continue
      #location index
      if "location" in level:
        sp_data[sp_level_name_index] = f'{sp_data[sp_level_name_index].split("|")[0]}|{level["location"]}\n'

      sp_level_name_index += 1
      #title index
      if "title" in level:
        sp_data[sp_level_name_index] = f'{sp_data[sp_level_name_index].split("|")[0]}|{level["title"]}\n'

      sp_level_name_index += 1
      if ("thumbnail" in level or
          "secret_chip_count" in level or
          "speed_chip_time" in level):
        #convert row to comma segments
        row = sp_data[sp_level_name_index].split(",")
        if "thumbnail" in level:
          #thumbnail index
          row[1] = level["thumbnail"]
        if "secret_chip_count" in level:
          #secret chip index, make sure to format as float!!
          row[2] = f"{level['secret_chip_count']}.0"
        if "speed_chip_time" in level:
          #speed chip time index, make sure to format as float!!
          row[3] = f"{level['speed_chip_time']}.0"
        sp_data[sp_level_name_index] = ",".join(row)
    else: #MP
      if "title" in level or "thumbnail" in level:
        mp_edited = True
      else:
        continue
      #title index
      if "title" in level:
        mp_data[mp_level_name_index] = f'{mp_data[mp_level_name_index].split("|")[0]}|{level["title"]}\n'
      if "thumbnail" in level:
        mp_level_name_index += 1
        #thumbnail index
        #convert row to comma segments
        row = mp_data[mp_level_name_index].split(",")
        row[1] = level["thumbnail"]
        mp_data[mp_level_name_index] = ",".join(row)
      mp_level_name_index += 1

  to_insert = []

  if sp_edited:
    #write sp csv file
    with open(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), 'w') as pick_levels:
      pick_levels.writelines(sp_data)

    csv_rebuilder.execute(is_gc, False, os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE + CSV_SUFFIX))
    shutil.move(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE + CSV_SUFFIX), os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE))
    to_insert.append(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE))

  if mp_edited:
    #write mp csv file
    with open(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE), 'w') as mp_levels:
      mp_levels.writelines(mp_data)

    csv_rebuilder.execute(is_gc, False, os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE), os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE + CSV_SUFFIX))
    shutil.move(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE + CSV_SUFFIX), os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE))
    to_insert.append(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE))

  if len(to_insert):
    mst_insert.execute(True, iso_mst, to_insert, "")

def insert_mod(metadata, iso_dir, first_sp_level_index, first_mp_level_index, dol, is_gc, codes_file_location, player_bot_list, level_invent_dict_list):
  #add mod to pick level
  if len(metadata.levels):
    update_pick_level(metadata, iso_dir, first_sp_level_index, first_mp_level_index, is_gc)
    # also patch exe with level attributes
    update_level_attributes(metadata, first_sp_level_index, first_mp_level_index, is_gc, dol)

  assembly_files = [assembly_file["file"] for assembly_file in metadata.assembly_files]
  level_assembly_files = []

  for gecko_code in metadata.gecko_codes:
    apply_hack(dol, [gecko_code['opcode'], gecko_code['content']])

  # map of files that get replaced, usually level names
  replacement_map = {}
  sp_level_index = first_sp_level_index
  mp_level_index = first_mp_level_index
  for level in metadata.levels:
    if level['type'] == LEVEL_TYPES[0]: #campaign
      level_list = CAMPAIGN_LEVEL_NAMES
      level_index = sp_level_index
      sp_level_index += 1
    else:
      level_list = MULTIPLAYER_LEVEL_NAMES
      level_index = mp_level_index
      mp_level_index += 1
    if 'wld' in level:
      replacement_map[level['wld']] = f"{level_list[level_index]}.wld"
    if 'csv' in level:
      replacement_map[level['csv']] = f"{level_list[level_index]}.csv"
    if 'gt' in level:
      replacement_map[level['gt']] = f"{level_list[level_index]}.gt"
      if level['type'] == LEVEL_TYPES[0]: #campaign
        game_level_index = level_index + 1
      else: # MP
        game_level_index = level_index + 43 # mp levels come after campaign levels for this
      if 'player_bot' in level:
        player_bot_list[game_level_index] = level['player_bot'].lower()
      else:
        # Default any unmentioned player bot to glitch
        player_bot_list[game_level_index] = "glitch"
      if "custom_inventory" in level:
        level_invent_dict_list[game_level_index] = level["custom_inventory"]
      if 'level_assembly_files' in level:
        for asm_file in level['level_assembly_files']:
          # set up indices for loading in later
          asm_file['level_index'] = game_level_index
          level_assembly_files.append(asm_file)

  #insert relevant files into the mst
  with zipfile.ZipFile(metadata.zip_file_path) as mod_zip:
    for info in mod_zip.infolist():
      if os.path.splitext(info.filename)[1].lower() == ".mst":
        #extract the mst to a temp directory and insert the files
        tmpdirname = tempfile.TemporaryDirectory()
        insert_file_dir = tempfile.TemporaryDirectory()
        mst_path = os.path.join(tmpdirname.name, info.filename)
        print(f'Extracting {info.filename} to {tmpdirname.name}')
        mod_zip.extract(info.filename, tmpdirname.name)
        # now rename files if needed
        mst_extract_path = os.path.join(tmpdirname.name, "extract")
        print(f'Extracting mst to {mst_extract_path}')
        mst_extract.extract(mst_path, mst_extract_path, False, False, True)
        path = pathlib.Path(mst_extract_path)

        files_to_insert = []

        for filename in path.iterdir():
          if os.path.basename(filename) in replacement_map:
            new_filename = os.path.join(insert_file_dir.name, replacement_map[os.path.basename(filename)])
          else:
            new_filename = os.path.join(insert_file_dir.name, os.path.basename(filename))
          shutil.move(filename, new_filename)
          filename = new_filename
          files_to_insert.append(filename)

        iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")
        mst_insert.execute(True, iso_mst, files_to_insert, "")

      elif os.path.basename(info.filename).lower() != "manifest.json":
        for level_assembly_file in level_assembly_files:
          # list of dicts that shouldnt be too long so we are just going to iterate over everyone one for the O(n^2) dream, lazy. Fix if it matters someday
          if os.path.basename(info.filename) == level_assembly_file["file"]:
            # this is an assembly file pertaining to a specific level and should be injected specially
            tmpdirname = tempfile.TemporaryDirectory()
            mod_zip.extract(info.filename, tmpdirname.name)
            file_path = os.path.join(tmpdirname.name, info.filename)
            insert_level_assembly_into_codes_file(dol, codes_file_location, file_path, level_assembly_file["injection_location"], level_assembly_file['level_index'])
        if os.path.basename(info.filename) in assembly_files:
          # this is an assembly file that needs to be injected into the dol not added to the iso
          tmpdirname = tempfile.TemporaryDirectory()
          mod_zip.extract(info.filename, tmpdirname.name)
          file_path = os.path.join(tmpdirname.name, info.filename)
          insert_assembly_into_codes_file(codes_file_location, file_path, metadata.assembly_files[assembly_files.index(os.path.basename(info.filename))]["injection_location"])
        else:
          print(f'Extracting {info.filename} to {os.path.join(iso_dir, "root")}')
          #first move to temporary directory and then copy to the right spot to dodge added folders
          tmpdirname = tempfile.TemporaryDirectory()
          mod_zip.extract(info.filename, tmpdirname.name)
          file_path = os.path.join(tmpdirname.name, info.filename)
          new_filename = os.path.join(iso_dir, "root", "files", os.path.basename(info.filename))
          print(file_path, new_filename)
          shutil.move(file_path, new_filename)

