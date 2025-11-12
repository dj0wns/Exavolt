import tempfile
import zipfile
import os
import shutil
import pathlib
import sys

from .ma_tools import mst_extract
from .ma_tools import mst_insert
from .ma_tools import csv_rebuilder
from .level import Level, LEVEL_TYPES
from .assembly import insert_assembly_into_codes_file, insert_level_assembly_into_codes_file
from .dol import apply_hack
from .scratch_memory import add_entry_to_dict

def insert_mod(metadata, iso_dir, sp_level_index, mp_level_index, dol, is_gc, codes_file_location, sp_level_list, mp_level_list, insert_level_list, default_scratch_memory_entries, memory_offset):

  assembly_files = {}
  level_assembly_files = []

  data = metadata.data

  for assembly_file in data['assembly_files']:
    assembly_files[assembly_file['file']] = int(assembly_file['injection_location'], 16)

  for gecko_code in data['gecko_codes']:
    apply_hack(dol, [int(gecko_code['opcode'], 16), int(gecko_code['content'], 16)])

  local_scratch_memory_replacement_dict = default_scratch_memory_entries.copy()

  for entry in data['scratch_memory']:
    if not entry['global']:
      # Global entries handled earlier in the process
      add_entry_to_dict(entry, local_scratch_memory_replacement_dict, memory_offset)

  # map of files that get replaced, usually level names
  for level in data['levels']:
    if level['type'] == LEVEL_TYPES[0] and(
          'mode' not in level or level['mode'] == 'replace'):

      if level['type'] == LEVEL_TYPES[0]: #campaign
        level_list = sp_level_list
        level_index = sp_level_index[0]
        sp_level_index[0] += 1
      else:
        raise ValueError(f'Invalid type: {level["type"]} for replace')

      # Replace the level at the current index in the level array
      # TODO check timing on level info (name/location/screenshot) and make sure those arent overwritten
      if 'wld' in level:
        level_list[level_index].wld_resource_name = level['wld']
      if 'csv' in level:
        level_list[level_index].csv_file = level['csv']
      if 'csv_material_file' in level:
        level_list[level_index].csv_file = level['csv']
      if 'title' in level:
        level_list[level_index].name = level['title']
      if 'internal_title' in level:
        level_list[level_index].title = level['internal_title']
      if 'location' in level:
        level_list[level_index].location = level['location']
      if 'thumbnail' in level:
        level_list[level_index].screenshot = level['thumbnail']
      if 'secret_chip_count' in level:
        level_list[level_index].secret_chips = level['secret_chip_count']
      if 'speed_chip_time' in level:
        level_list[level_index].time_to_beat = level['speed_chip_time']
      if 'load_function_offset' in level:
        level_list[level_index].load_ptr = level['load_function_offset']
      if 'unload_function_offset' in level:
        level_list[level_index].unload_ptr = level['unload_function_offset']
      if 'work_function_offset' in level:
        level_list[level_index].work_ptr = level['work_function_offset']
      if 'draw_function_offset' in level:
        level_list[level_index].draw_ptr = level['draw_function_offset']
      if 'projector_offsets' in level:
        level_list[level_index].projector_offsets = level['projector_offsets']
      if 'projector_range_adjustment' in level:
        level_list[level_index].projector_offsets = level['projector_range_adjustment']
      if 'player_bot' in level:
        level_list[level_index].starting_bot = level['player_bot'].lower()
      if "custom_inventory" in level:
        level_list[level_index].inventory_override = level["custom_inventory"]
    elif level['type'] == LEVEL_TYPES[1] or level['mode'] == 'insert':
      # Always insert mp levels at the end
      # We need to create a new level and send it back to insert later
      # All fields are required!!

      new_level = Level(
        level['internal_title'] if 'internal_title' in level else level['wld'],
        level['player_bot'] if 'player_bot' in level else 'glitch',
        level['wld'],
        level['csv'],
        level['csv_material_file'] if 'csv_material_file' in level else 'WEDMmines01',
        level['load_function_offset'] if 'load_function_offset' in level else 0,
        level['unload_function_offset'] if 'unload_function_offset' in level else 0,
        level['work_function_offset'] if 'work_function_offset' in level else 0,
        level['draw_function_offset'] if 'draw_function_offset' in level else 0,
        level['projector_offsets'] if 'projector_offsets' in level else 0.0,
        level['projector_range_adjustment'] if 'projector_range_adjustment' in level else 1.0,
        level['custom_inventory'] if 'custom_inventory' in level else {},
        []
      )
      new_level.name = level['title']
      new_level.location = level['location']
      new_level.screenshot = level['thumbnail']
      new_level.secret_chips = level['secret_chip_count'] if 'secret_chip_count' in level else 0
      new_level.time_to_beat = level['speed_chip_time'] if 'speed_chip_time' in level else 0

      if level['type'] == LEVEL_TYPES[0]: #campaign
          insert_level_list.append(
              [level['index'] if 'index' in level else -1,
               new_level])
      else:
        mp_level_list.append(new_level)

    if 'level_assembly_files' in level:
        for asm_file in level['level_assembly_files']:
          # TODO! move this later in the process so we can give it the proper indices!
          asm_file['owning_level'] = level_list[level_index]
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

        mst_extract_path = os.path.join(tmpdirname.name, "extract")
        print(f'Extracting mst to {mst_extract_path}')
        mst_extract.extract(mst_path, mst_extract_path, False, False, True)
        path = pathlib.Path(mst_extract_path)

        files_to_insert = []

        for filename in path.iterdir():
          new_filename = os.path.join(insert_file_dir.name, os.path.basename(filename))
          shutil.move(filename, new_filename)
          filename = new_filename
          files_to_insert.append(filename)

        iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")
        mst_insert.execute(True, iso_mst, files_to_insert, "")

      elif os.path.basename(info.filename).lower() != "manifest.json":
        for level_assembly_file in level_assembly_files:
          # TODO this needs to be rewritten!
          # list of dicts that shouldnt be too long so we are just going to iterate over everyone one for the O(n^2) dream, lazy. Fix if it matters someday
          if os.path.basename(info.filename) == level_assembly_file["file"]:
            # this is an assembly file pertaining to a specific level and should be injected specially
            # But we won't know the level offset until later in the process, so copy the raw data to the level entity.
            tmpdirname = tempfile.TemporaryDirectory()
            mod_zip.extract(info.filename, tmpdirname.name)
            file_path = os.path.join(tmpdirname.name, info.filename)
            with open(file_path, "r") as file:
              level.assembly_files.append((level_assembly_file["injection_location"], file.read(), local_scratch_memory_replacement_dict))
        if os.path.basename(info.filename) in assembly_files.keys():
          # this is an assembly file that needs to be injected into the dol not added to the iso
          tmpdirname = tempfile.TemporaryDirectory()
          mod_zip.extract(info.filename, tmpdirname.name)
          file_path = os.path.join(tmpdirname.name, info.filename)
          insert_assembly_into_codes_file(codes_file_location, file_path, assembly_files[os.path.basename(info.filename)], local_scratch_memory_replacement_dict)
        elif os.path.basename(info.filename) in data['movie_files']:
          tmpdirname = tempfile.TemporaryDirectory()
          mod_zip.extract(info.filename, tmpdirname.name)
          file_path = os.path.join(tmpdirname.name, info.filename)
          new_filename = os.path.join(iso_dir, "root", "files", "Movies", os.path.basename(info.filename))
          print(file_path, new_filename)
          shutil.move(file_path, new_filename)
        else:
          print(f'Extracting {info.filename} to {os.path.join(iso_dir, "root")}')
          #first move to temporary directory and then copy to the right spot to dodge added folders
          tmpdirname = tempfile.TemporaryDirectory()
          mod_zip.extract(info.filename, tmpdirname.name)
          file_path = os.path.join(tmpdirname.name, info.filename)
          new_filename = os.path.join(iso_dir, "root", "files", os.path.basename(info.filename))
          print(file_path, new_filename)
          shutil.move(file_path, new_filename)

