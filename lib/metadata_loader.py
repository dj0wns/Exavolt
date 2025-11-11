import json
import zipfile
import os
import jsonschema
from .level import LEVEL_TYPES
from .hacks import HACKS

SCHEMA = {
    "properties" : {
        "title": { "type": "string" },
        "author": { "type": "string" },
        "hacks_required": {
            "type": "array",
            "items" : {
              "type": "string"
            },
        },
        "csv_edits": {
            "type": "array",
            "items" : {
                "type" : "object",
                "properties": {
                    "file": { "type": "string" },
                    "operation": {
                        "type": "string",
                        "default": "replace",
                        "enum": ["replace", "add_line"],
                    },
                    "row" : { "type": "integer" },
                    "col" : { "type": "integer" },
                    "value" : {}
                },
                "required" : ["file", "value"],
            }
        },
        "other_mst_files" : {"type" : "array"},
        "non_mst_files" : {"type" : "array"},
        "movie_files" : {"type" : "array"},
        "assembly_files" : {
            "type" : "array",
            "items" : {
                "type" : "object",
                "properties" : {
                    "file" : {"type" : "string"},
                    "injection_location": {"type": "string"},
                },
                "required" : ["file", "injection_location"],
            }
        },
        "scratch_memory" : {
            "type" : "array",
            "items" : {
                "type" : "object",
                "properties" : {
                    "name" : {"type" : "string"},
                    "size": {"type": "integer"},
                    "global": {"type": "boolean", "default": False},
                },
                "required" : ["name", "size"],
            },
        },
        "gecko_codes" : {
            "type" : "array",
            "items" : {
                "type" : "object",
                "properties" : {
                    "opcode" : {"type" : "string"},
                    "content" : {"type" : "string"},
                },
                "required" : ["opcode", "content"]
            }
        },
        "levels" : {
            "type" : "array",
            "items" : {
                "type" : "object",
                "properties" : {
                    "mode" : {"type" : "string",
                              "default" : "replace",
                              "note" : "For mp levels the mode will always be insert at end"},
                    "index" : {"type" : "integer",
                               "default" : "-1",
                               "note" : "-1 means end otherwise put the level index you want to insert before, zero indexed"},
                    "title" : {"type" : "string"},
                    "location" : {"type" : "string"},
                    "player_bot" : {"type" : "string",
                                    "default": "glitch"},
                    "thumbnail" : {"type" : "string"},
                    "secret_chip_count" : {"type" : "integer",
                                           "note" : "default is 0 if new level"},
                    "speed_chip_time" : {"type" : "integer",
                                         "note" : "default is 0 if new level"},
                    "load_function_offset" : {"type" : "integer"},
                    "unload_function_offset" : {"type" : "integer"},
                    "work_function_offset" : {"type" : "integer"},
                    "draw_function_offset" : {"type" : "integer"},
                    "wld" : {"type" : "string"},
                    "csv" : {"type" : "string"},
                    "csv_material_file" : {"type" : "string"},
                    "gt" : {"type" : "string"},
                    "projector_offsets" : {"type": "number"},
                    "projector_range_adjustment" : {"type": "number"},
                    "custom_inventory" : {
                        "type": "object",
                        "properties" : {
                            "primary" : {
                                "type": "array",
                                "items" : {
                                    "type" : "object",
                                    "properties" : {
                                        "name" : {"type" : "string" },
                                        "clip_ammo" : {"type" : "integer"},
                                        "reserve_ammo" : {"type" : "integer"}
                                    },
                                    "required" : ["name", "clip_ammo", "reserve_ammo"]
                                },
                            },
                            "secondary" : {
                                "type" : "array",
                                "items" : {
                                    "type" : "object",
                                    "properties" : {
                                        "name" : {"type" : "string" },
                                        "clip_ammo" : {"type" : "integer"},
                                        "reserve_ammo" : {"type" : "integer"}
                                    },
                                    "required" : ["name", "clip_ammo", "reserve_ammo"]
                                }
                            },
                            "battery_count" : {"type" : "integer"},
                            "default_primary_slot" : {"type" : "integer"},
                            "default_secondary_slot": {"type": "integer"},
                            "washer_count" : {"type": "integer"},
                            "chip_count" : {"type": "integer"},
                            "secret_chip_count" : {"type": "integer"},
                            "arm_servo_count" : {"type": "integer"},
                            "det_pack_count" : {"type": "integer"},
                            "goff_part_count" : {"type": "integer"}
                        },
                        "required" : [
                            "primary",
                            "secondary",
                            "battery_count",
                            "default_primary_slot",
                            "default_secondary_slot",
                            "washer_count",
                            "chip_count",
                            "secret_chip_count",
                            "arm_servo_count",
                            "det_pack_count",
                            "goff_part_count"
                        ],

                    },
                    "level_assembly_files" : {
                        "type" : "array",
                        "items" : {
                            "type": "object",
                            "properties" : {
                                "file" : {"type" : "string"},
                                "injection_location" : {"type" : "string"}
                            },
                            "required" : ["file", "injection_location"]
                        }
                    }
                }
            }
        },
    }
}

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
    self.data = {}
    self.is_default = False
    self.zip_file_path = zip_file_path

  def from_json(self, json_file):
    print("from json")
    mod_dict = json.load(json_file)

    try:
      jsonschema.validate(instance=mod_dict, schema=SCHEMA)
      print(f"JSON instance valid for: {mod_dict['title']}")
    except jsonschema.ValidationError as e:
      print(f"JSON instance is invalid for {mod_dict['title']}: {e.message}")

    self.data = mod_dict
    # fix up lists for easier navigation
    if 'assembly_files' not in self.data:
      self.data['assembly_files'] = []
    if 'csv_edits' not in self.data:
      self.data['csv_edits'] = []
    if 'gecko_codes' not in self.data:
      self.data['gecko_codes'] = []
    if 'levels' not in self.data:
      self.data['levels'] = []
    if 'movie_files' not in self.data:
      self.data['movie_files'] = []
    if 'scratch_memory' not in self.data:
      self.data['scratch_memory'] = []
