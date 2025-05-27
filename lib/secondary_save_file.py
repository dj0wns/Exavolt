import .dol


def apply_secondary_save_file_codes(
    memory_dict,
    asm_path,
    codes_file_location):
  dol.inject_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "InitSecondarySaveFileMemory.asm"),
      0x8029e4a0,
      memory_dict)
  # Code to load file and create if not exists

  # Code to save file
