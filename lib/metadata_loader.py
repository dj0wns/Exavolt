import json
import zipfile
import os
from .level import LEVEL_TYPES
from .hacks import HACKS

def collect_mods(folder):
  mod_metadatas = []
  for file in os.listdir(folder):
    if file.endswith(".zip"):
      path = os.path.join(folder, file)
      mod_metadatas.append(collect_mod_metadata(path))
  return mod_metadatas

def collect_mods_from_files(files):
  mod_metadatas = []
  for file in files:
    if file.endswith(".zip"):
      mod_metadatas.append(collect_mod_metadata(file))
  return mod_metadatas

def collect_mod_metadata(zip_file_path):
  metadata = ModMetadata(zip_file_path)
  with zipfile.ZipFile(zip_file_path) as mod_zip:
    for info in mod_zip.infolist():
      if os.path.basename(info.filename).lower() == "manifest.json":
        with mod_zip.open(info) as file:
          metadata.from_json(file)
          #TODO replace __all__ in manifest and check files
          return metadata

class ModMetadata:
  def __init__(self, zip_file_path):
    self.title = ""
    self.author = ""
    self.zip_file_path = zip_file_path
    self.has_assembly_files = False
    self.hacks_required = []
    self.levels = []
    self.other_mst_files = []
    self.non_mst_files = []
    self.assembly_files = []
    self.gecko_codes = []

  def summary(self):
    campaign_level_count = 0;
    mp_level_count = 0
    for level in self.levels:
      if level["type"] == "campaign":
        campaign_level_count += 1
      elif level["type"] == "multiplayer":
        mp_level_count += 1
    return { "Title":self.title,
             "Author":self.author,
             "Campaign Levels":campaign_level_count,
             "Multiplayer Levels":mp_level_count,
             "Hacks Required": self.hacks_required,
             "Assembly Files": self.assembly_files,
             "Gecko codes": self.gecko_codes,
             "Total Files": len(self.other_mst_files) + len(self.non_mst_files),
             "Path": self.zip_file_path}

  def __str__(self):
    retstring = ""
    retstring += f'Title: {self.title}\n'
    retstring += f'Author: {self.author}\n'
    retstring += f'Hacks_required:\n'
    for mod in self.hacks_required:
      retstring += f'\t{mod}\n'
    retstring += f'Levels:\n'
    for level in self.levels:
      retstring += f'\t{level}\n'
    retstring += f'Other MST Files:\n'
    for other_mst_file in self.other_mst_files:
      retstring += f'\t{other_mst_file}\n'
    retstring += f'Non MST Files:\n'
    for non_mst_file in self.non_mst_files:
      retstring += f'\t{non_mst_file}\n'
    retstring += f'Assembly Files:\n'
    for assembly_file in self.assembly_files:
      retstring += f'\t{assembly_file}\n'
    retstring += f'Gecko codes:\n'
    for gecko_code in self.gecko_codes:
      retstring += f'\t{gecko_code}\n'
    return retstring

  def from_json(self, json_file):
    mod_dict = json.load(json_file)

    if "title" in mod_dict:
      if not isinstance(mod_dict['title'], str):
        raise ValueError('title')
      self.title = mod_dict['title']
    else:
      # Required field
      raise KeyError('title')

    if "author" in mod_dict:
      if not isinstance(mod_dict['author'], str):
        raise ValueError('author')
      self.author = mod_dict['author']
    else:
      # Required field
      raise KeyError('author')

    self.hacks_required = []
    if "hacks_required" in mod_dict:
      if not isinstance(mod_dict['hacks_required'], list):
        raise ValueError('hacks_required')
      index = 0
      for mod in mod_dict['hacks_required']:
        if not isinstance(mod, str):
          raise ValueError('hacks_required[' + str(index) + ']')
        if mod not in HACKS:
          raise ValueError('hacks_required[' + str(index) + ']')
        self.hacks_required.append(mod)
        index += 1

    self.other_mst_files = []
    if "other_mst_files" in mod_dict:
      if not isinstance(mod_dict['other_mst_files'], list):
        raise ValueError('other_mst_files')
      index = 0
      for other_mst_file in mod_dict['other_mst_files']:
        if not isinstance(other_mst_file, str):
          raise ValueError('other_mst_files[' + str(index) + ']')
        self.other_mst_files.append(other_mst_file)
        index += 1

    self.non_mst_files = []
    if "non_mst_files" in mod_dict:
      if not isinstance(mod_dict['non_mst_files'], list):
        raise ValueError('non_mst_files')
      index = 0
      for non_mst_file in mod_dict['non_mst_files']:
        if not isinstance(non_mst_file, str):
          raise ValueError('non_mst_files[' + str(index) + ']')
        self.non_mst_files.append(non_mst_file)
        index += 1

    self.assembly_files = []
    if "assembly_files" in mod_dict:
      if not isinstance(mod_dict['assembly_files'], list):
        raise ValueError('assembly_files')
      index = 0
      for assembly_file in mod_dict['assembly_files']:
        new_assembly_file = {}
        if not isinstance(assembly_file, dict):
          raise ValueError('assembly_files[' + str(index) + ']')
        if "file" in assembly_file:
          if not isinstance(assembly_file['file'], str):
            raise ValueError('assembly_files[' + str(index) + ']["file"]')
          new_assembly_file["file"] = assembly_file["file"]
        else:
          # Required field
          raise KeyError('assembly_files[' + str(index) + ']["file"]')
        if "injection_location" in assembly_file:
          if not isinstance(assembly_file['injection_location'], str):
            raise ValueError('assembly_files[' + str(index) + ']["injection_location"]')
          try:
            assembly_int_location = int(assembly_file['injection_location'], 16)
          except ValueError:
            raise ValueError('assembly_files[' + str(index) + ']["injection_location"] must be of the form 0x80xxxxxx')
          new_assembly_file["injection_location"] = assembly_int_location
        else:
          # Required field
          raise KeyError('assembly_files[' + str(index) + ']["injection_location"]')
        self.has_assembly_files = True
        self.assembly_files.append(new_assembly_file)
        index += 1

    self.gecko_codes = []
    if "gecko_codes" in mod_dict:
      if not isinstance(mod_dict['gecko_codes'], list):
        raise ValueError('gecko_codes')
      index = 0
      for gecko_code in mod_dict['gecko_codes']:
        new_gecko_code = {}
        if not isinstance(gecko_code, dict):
          raise ValueError('gecko_codes[' + str(index) + ']')
        if "opcode" in gecko_code:
          if not isinstance(gecko_code['opcode'], str):
            raise ValueError('gecko_code[' + str(index) + ']["opcode"]')
          try:
            opcode_int = int(gecko_code['opcode'], 16)
          except ValueError:
            raise ValueError('gecko_codes[' + str(index) + ']["opcode"] must be of the form 0x04xxxxxx')
          new_gecko_code["opcode"] = opcode_int
        else:
          # Required field
          raise KeyError('gecko_codes[' + str(index) + ']["opcode"]')
        if "content" in gecko_code:
          if not isinstance(gecko_code['content'], str):
            raise ValueError('gecko_codes[' + str(index) + ']["content"]')
          try:
            content_int = int(gecko_code['content'], 16)
          except ValueError:
            raise ValueError('gecko_codes[' + str(index) + ']["content"] must be of the form 0x80xxxxxx')
          new_gecko_code["content"] = content_int
        else:
          # Required field
          raise KeyError('gecko_codes[' + str(index) + ']["content"]')
        self.gecko_codes.append(new_gecko_code)
        index += 1

    self.levels = []
    if "levels" in mod_dict:
      if not isinstance(mod_dict['levels'], list):
        raise ValueError('levels')
      index = 0
      for level in mod_dict['levels']:
        new_level = {}
        if not isinstance(level, dict):
          raise ValueError('levels[' + str(index) + ']')
        if "type" in level:
          if not isinstance(level['type'], str):
            raise ValueError('levels[' + str(index) + ']["type"]')
          if level['type'] not in LEVEL_TYPES:
            raise ValueError('levels[' + str(index) + ']["type"]')
          new_level['type'] = level['type']
        else:
          # Required field
          raise KeyError('levels[' + str(index) + ']["type"]')

        if "title" in level:
          if not isinstance(level['title'], str):
            raise ValueError('levels[' + str(index) + ']["title"]')
          new_level['title'] = level['title']

        if "location" in level:
          if not isinstance(level['location'], str):
            raise ValueError('levels[' + str(index) + ']["location"]')
          new_level['location'] = level['location']

        if "player_bot" in level:
          if not isinstance(level['player_bot'], str):
            raise ValueError('levels[' + str(index) + ']["player_bot"]')
          new_level['player_bot'] = level['player_bot']

        if "thumbnail" in level:
          if not isinstance(level['thumbnail'], str):
            raise ValueError('levels[' + str(index) + ']["thumbnail"]')
          new_level['thumbnail'] = level['thumbnail']

        if "secret_chip_count" in level:
          if not isinstance(level['secret_chip_count'], int):
            raise ValueError('levels[' + str(index) + ']["secret_chip_count"]')
          new_level['secret_chip_count'] = level['secret_chip_count']

        if "speed_chip_time" in level:
          if not isinstance(level['speed_chip_time'], int):
            raise ValueError('levels[' + str(index) + ']["speed_chip_time"]')
          new_level['speed_chip_time'] = level['speed_chip_time']

        if "load_function_offset" in level:
          if not isinstance(level['load_function_offset'], int):
            raise ValueError('levels[' + str(index) + ']["load_function_offset"]')
          new_level['load_function_offset'] = level['load_function_offset']

        if "unload_function_offset" in level:
          if not isinstance(level['unload_function_offset'], int):
            raise ValueError('levels[' + str(index) + ']["unload_function_offset"]')
          new_level['unload_function_offset'] = level['unload_function_offset']

        if "work_function_offset" in level:
          if not isinstance(level['work_function_offset'], int):
            raise ValueError('levels[' + str(index) + ']["work_function_offset"]')
          new_level['work_function_offset'] = level['work_function_offset']

        if "draw_function_offset" in level:
          if not isinstance(level['draw_function_offset'], int):
            raise ValueError('levels[' + str(index) + ']["draw_function_offset"]')
          new_level['draw_function_offset'] = level['draw_function_offset']

        if "wld" in level:
          if not isinstance(level['wld'], str):
            raise ValueError('levels[' + str(index) + ']["wld"]')
          new_level['wld'] = level['wld']
        else:
          # Required field
          raise KeyError('levels[' + str(index) + ']["wld"]')

        if "csv" in level:
          if not isinstance(level['csv'], str):
            raise ValueError('levels[' + str(index) + ']["csv"]')
          new_level['csv'] = level['csv']

        if "gt" in level:
          if not isinstance(level['gt'], str):
            raise ValueError('levels[' + str(index) + ']["gt"]')
          new_level['gt'] = level['gt']

        if "custom_inventory" in level:
          new_custom_inventory = {}
          if not isinstance(level["custom_inventory"], dict):
            raise ValueError('levels[' + str(index) + ']["custom_inventory"]')
          # primary weapons!
          if "primary" in level["custom_inventory"]:
            new_custom_inventory["primary"] = []
            if not isinstance(level["custom_inventory"]["primary"], list):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["primary"]')
            item_index = 0
            for item in level["custom_inventory"]["primary"]:
              if "name" not in item or not isinstance(item["name"], str):
                raise ValueError('levels[' + str(index) + ']["custom_inventory"]["primary"][' + str(item_index) + ']["name"]')
              if "clip_ammo" not in item or not isinstance(item["clip_ammo"], int):
                raise ValueError('levels[' + str(index) + ']["custom_inventory"]["primary"][' + str(item_index) + ']["clip_ammo"]')
              if "reserve_ammo" not in item or not isinstance(item["reserve_ammo"], int):
                raise ValueError('levels[' + str(index) + ']["custom_inventory"]["primary"][' + str(item_index) + ']["reserve_ammo"]')
              new_custom_inventory["primary"].append({"name":item["name"], "clip_ammo":item["clip_ammo"], "reserve_ammo":item["reserve_ammo"]})
          else:
            # Required field
            raise KeyError('levels[' + str(index) + ']["custom_inventory"]["primary"]')

          # secondary weapons!
          if "secondary" in level["custom_inventory"]:
            new_custom_inventory["secondary"] = []
            if not isinstance(level["custom_inventory"]["secondary"], list):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["secondary"]')
            item_index = 0
            for item in level["custom_inventory"]["secondary"]:
              if "name" not in item or not isinstance(item["name"], str):
                raise ValueError('levels[' + str(index) + ']["custom_inventory"]["secondary"][' + str(item_index) + ']["name"]')
              if "clip_ammo" not in item or not isinstance(item["clip_ammo"], int):
                raise ValueError('levels[' + str(index) + ']["custom_inventory"]["secondary"][' + str(item_index) + ']["clip_ammo"]')
              if "reserve_ammo" not in item or not isinstance(item["reserve_ammo"], int):
                raise ValueError('levels[' + str(index) + ']["custom_inventory"]["secondary"][' + str(item_index) + ']["reserve_ammo"]')
              new_custom_inventory["secondary"].append({"name":item["name"], "clip_ammo":item["clip_ammo"], "reserve_ammo":item["reserve_ammo"]})
          else:
            # Required field
            raise KeyError('levels[' + str(index) + ']["custom_inventory"]["secondary"]')

          if "battery_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["battery_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["battery_count"]')
            new_custom_inventory["battery_count"] = level["custom_inventory"]["battery_count"]

          if "default_primary_slot" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["default_primary_slot"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["default_primary_slot"]')
            new_custom_inventory["default_primary_slot"] = level["custom_inventory"]["default_primary_slot"]

          if "default_secondary_slot" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["default_secondary_slot"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["default_secondary_slot"]')
            new_custom_inventory["default_secondary_slot"] = level["custom_inventory"]["default_secondary_slot"]

          if "washer_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["washer_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["washer_count"]')
            new_custom_inventory["washer_count"] = level["custom_inventory"]["washer_count"]

          if "chip_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["chip_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["chip_count"]')
            new_custom_inventory["chip_count"] = level["custom_inventory"]["chip_count"]

          if "secret_chip_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["secret_chip_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["secret_chip_count"]')
            new_custom_inventory["secret_chip_count"] = level["custom_inventory"]["secret_chip_count"]

          if "arm_servo_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["arm_servo_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["arm_servo_count"]')
            new_custom_inventory["arm_servo_count"] = level["custom_inventory"]["arm_servo_count"]

          if "det_pack_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["det_pack_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["det_pack_count"]')
            new_custom_inventory["det_pack_count"] = level["custom_inventory"]["det_pack_count"]

          if "goff_part_count" in level["custom_inventory"]:
            if not isinstance(level["custom_inventory"]["goff_part_count"], int):
              raise ValueError('levels[' + str(index) + ']["custom_inventory"]["goff_part_count"]')
            new_custom_inventory["goff_part_count"] = level["custom_inventory"]["goff_part_count"]

          new_level["custom_inventory"] = new_custom_inventory

        if "level_assembly_files" in level:
          if not isinstance(level['level_assembly_files'], list):
            raise ValueError('levels[' + str(index) + ']["level_assembly_files"]')
          asm_index = 0
          for level_assembly_file in level['level_assembly_files']:
            new_level_assembly_file = {}
            if not isinstance(level_assembly_file, dict):
              raise ValueError('levels[' + str(index) + ']["level_assembly_files"][' + str(asm_index) + ']')
            if "file" in level_assembly_file:
              if not isinstance(level_assembly_file['file'], str):
                raise ValueError('levels[' + str(index) + ']["level_assembly_files"][' + str(asm_index) + ']["file"]')
              new_level_assembly_file["file"] = level_assembly_file["file"]
            else:
              # Required field
              raise KeyError('levels[' + str(index) + ']["level_assembly_files"][' + str(asm_index) + ']["file"]')
            if "injection_location" in level_assembly_file:
              if not isinstance(level_assembly_file['injection_location'], str):
                raise ValueError('levels[' + str(index) + ']["level_assembly_files"][' + str(asm_index) + ']["injection_location"]')
              try:
                level_assembly_int_location = int(level_assembly_file['injection_location'], 16)
              except ValueError:
                raise ValueError('levels[' + str(index) + ']["level_assembly_files"][' + str(asm_index) + ']["injection_location"] must be of the form 0x80xxxxxx')
              new_level_assembly_file["injection_location"] = level_assembly_int_location
            else:
              # Required field
              raise KeyError('levels[' + str(index) + ']["level_assembly_files"][' + str(asm_index) + ']["injection_location"]')
            if "level_assembly_files" not in new_level:
              new_level["level_assembly_files"] = []
            new_level["level_assembly_files"].append(new_level_assembly_file)
            self.has_assembly_files = True
            asm_index += 1

        self.levels.append(new_level)
        index += 1

