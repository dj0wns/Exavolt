import tempfile
import zipfile
import os
import pathlib
import sys

from .ma_tools import mst_extract
from .ma_tools import mst_insert
from .ma_tools import csv_rebuilder
from .level import CAMPAIGN_LEVEL_NAMES

FIRST_CSV_INDEX_LEVELS = 6
NUM_LINES_PER_LEVEL = 2

PICK_LEVEL_CSV_FILE = "pick_level$.csv"
PICK_LEVEL_CSV_SUFFIX = ".new"

def update_pick_level(metadata, iso_dir, first_level_index, is_gc):
  #first extract pick level to temp dir
  tmpdirname = tempfile.TemporaryDirectory()
  csv_dir_name = tmpdirname.name

  iso_mst = os.path.join(iso_dir.name, "root", "files", "mettlearms_gc.mst")
  mst_extract.extract(iso_mst, csv_dir_name, False, PICK_LEVEL_CSV_FILE, False)

  #load in csv file
  with open(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), 'r') as pick_levels:
    data = pick_levels.readlines()


  level_name_index = FIRST_CSV_INDEX_LEVELS + NUM_LINES_PER_LEVEL * first_level_index
  for level in metadata.levels:
    if level["type"] != "campaign":
      continue

    #location index|
    data[level_name_index] = f'{data[level_name_index].split("|")[0]}|{level["location"]}\n'
    level_name_index += 1
    #title index
    data[level_name_index] = f'{data[level_name_index].split("|")[0]}|{level["title"]}\n'
    if "thumbnail" in level:
      level_name_index += 1
      #thumbnail index
      #convert row to comma segments
      row = data[level_name_index].split(",")
      row[1] = level["thumbnail"]
      data[level_name_index] = ",".join(row)

    level_name_index += NUM_LINES_PER_LEVEL

  #write csv file
  with open(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), 'w') as pick_levels:
    pick_levels.writelines(data)

  #rebuild csv file in place
  csv_rebuilder.execute(is_gc, False, os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE + PICK_LEVEL_CSV_SUFFIX))

  #move file to original
  os.rename(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE + PICK_LEVEL_CSV_SUFFIX), os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE))

  mst_insert.execute(True, iso_mst, [os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE)], "")

def insert_mod(metadata, iso_dir, first_level_index, is_gc):
  #add mod to pick level
  if len(metadata.levels):
    update_pick_level(metadata, iso_dir, first_level_index, is_gc)

  # map of files that get replaced, usually level names
  replacement_map = {}
  level_index = first_level_index
  for level in metadata.levels:
    if 'wld' in level:
      replacement_map[level['wld']] = f"{CAMPAIGN_LEVEL_NAMES[level_index]}.wld"
    if 'csv' in level:
      replacement_map[level['csv']] = f"{CAMPAIGN_LEVEL_NAMES[level_index]}.csv"
    if 'gt' in level:
      replacement_map[level['gt']] = f"{CAMPAIGN_LEVEL_NAMES[level_index]}.gt"
    level_index += 1

  #insert relevant files into the mst
  with zipfile.ZipFile(metadata.zip_file_path) as mod_zip:
    for info in mod_zip.infolist():
      if os.path.splitext(info.filename)[1].lower() == ".mst":
        #extract the mst to a temp directory and insert the files
        tmpdirname = tempfile.TemporaryDirectory()
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
            new_filename = os.path.join(os.path.split(filename)[0], replacement_map[os.path.basename(filename)])
            os.rename(filename, new_filename)
            filename = new_filename
          files_to_insert.append(filename)

        iso_mst = os.path.join(iso_dir.name, "root", "files", "mettlearms_gc.mst")
        mst_insert.execute(True, iso_mst, files_to_insert, "")

      elif os.path.basename(info.filename).lower() != "manifest.json":
        print(f'Extracting {info.filename} to {os.path.join(iso_dir.name, "root")}')
        #first move to temporary directory and then copy to the right spot to dodge added folders
        tmpdirname = tempfile.TemporaryDirectory()
        mod_zip.extract(info.filename, tmpdirname.name)
        file_path = os.path.join(tmpdirname.name, info.filename)
        new_filename = os.path.join(iso_dir.name, "root", "files", os.path.basename(info.filename))
        print(file_path, new_filename)
        os.rename(file_path, new_filename)

