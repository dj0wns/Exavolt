import os

from .assembly import insert_assembly_into_codes_file



def apply_secondary_save_file_codes(
    memory_dict,
    asm_path,
    codes_file_location):
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "InitSecondarySaveFileMemory.asm"),
      0x8029e4a0,
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
