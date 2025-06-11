import os

from .assembly import insert_assembly_into_codes_file
from .util import add_entry_to_dict


def save_file_layout_common_offsets():
  default_save_file_entries = [
    {"name": "SAVE_FILE_OFFSET_VERSION",
     "size": 4},
    {"name": "SAVE_FILE_OFFSET_SP_LEVELS",
     "size": 5000},
    {"name": "SAVE_FILE_OFFSET_EXAVOLT_RESERVED",
     "size": 100000},
    {"name": "SAVE_FILE_OFFSET_EXAVOLT_SANDBOX",
     "size": 5000},
    {"name": "SAVE_FILE_OFFSET_DJOWNS_SANDBOX",
     "size": 5000},
    {"name": "SAVE_FILE_OFFSET_AVOHKII_SANDBOX",
     "size": 5000},
    {"name": "SAVE_FILE_OFFSET_EXAVOLT_RESERVED_2",
     "size": 100000},
    {"name": "SAVE_FILE_OFFSET_FREE_MEMORY_BEGIN",
     "size": 0},
  ]
  mem_offset = [0]
  ret_dict = {}
  for entry in default_save_file_entries:
    add_entry_to_dict(entry, ret_dict, mem_offset)
  return ret_dict

def apply_secondary_save_file_codes(
    memory_dict,
    asm_path,
    codes_file_location):
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "InitSecondarySaveFileMemory.asm"),
      0x8015675c,
      memory_dict)
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "SetDefaultSaveFileValues.asm"),
      0x8019ca94,
      memory_dict)
  # Code to create file if not exist when saving
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "CreateSecondarySaveFile.asm"),
      0x8019cd40,
      memory_dict)

  # Code to save file
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "SaveSecondarySaveFileMemoryToDisk.asm"),
      0x8019cd74,
      memory_dict)

  # Code to load file
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "LoadSecondarySaveFileFromDisk.asm"),
      0x8019cbb4,
      memory_dict)

  # Code to hide excess files
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "HideSecondaryProfilesFromMenues.asm"),
      0x802bf6e0,
      memory_dict)

  # Code to prevent counting extra files
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "SkipCountSecondaryProfiles.asm"),
      0x802be3f0,
      memory_dict)
