import os

from .assembly import insert_assembly_into_codes_file
from .util import add_entry_to_dict
from .dol import apply_hack

SAVE_FILE_VERSION = 3


def save_file_layout_common_offsets():
    default_save_file_entries = [
        {"name": "SAVE_FILE_OFFSET_VERSION", "size": 4},
        {"name": "SAVE_FILE_OFFSET_EXTRA_LEVELS_COMPLETED", "size": 4},
        {"name": "SAVE_FILE_OFFSET_SP_LEVELS", "size": 100000},  # We support 200 levels
        {"name": "SAVE_FILE_OFFSET_EXAVOLT_RESERVED", "size": 100000},
        {"name": "SAVE_FILE_OFFSET_EXAVOLT_SANDBOX", "size": 5000},
        {"name": "SAVE_FILE_OFFSET_DJOWNS_SANDBOX", "size": 5000},
        {"name": "SAVE_FILE_OFFSET_AVOHKII_SANDBOX", "size": 5000},
        {"name": "SAVE_FILE_OFFSET_EXAVOLT_RESERVED_2", "size": 100000},
        {"name": "SAVE_FILE_OFFSET_FREE_MEMORY_BEGIN", "size": 0},
    ]
    mem_offset = [0]
    ret_dict = {}
    for entry in default_save_file_entries:
        add_entry_to_dict(entry, ret_dict, mem_offset)
    ret_dict["SAVE_FILE_VERSION"] = 3
    return ret_dict


def apply_secondary_save_file_codes(dol, memory_dict, asm_path, codes_file_location):
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "InitSecondarySaveFileMemory.asm"),
        0,
        memory_dict,
        immediate_exec=True,
    )
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "SetDefaultSaveFileValues.asm"),
        0x8019CA94,
        memory_dict,
    )
    # Code to create file if not exist when saving
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "CreateSecondarySaveFile.asm"),
        0x8019CD40,
        memory_dict,
    )

    # Code to delete save file
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "DeleteSecondarySaveFile.asm"),
        0x8019CE08,
        memory_dict,
    )

    # Code to save file
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "SaveSecondarySaveFileMemoryToDisk.asm"),
        0x8019CD74,
        memory_dict,
    )

    # Code to load file
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "LoadSecondarySaveFileFromDisk.asm"),
        0x8019CBB4,
        memory_dict,
    )

    # Null out index check in GetProfileInfos because we need to first see if any
    # profiles are secondary before incrementing the counter, this logic check is
    # moved in to the HideSecondaryProfilesFromMenuesScript.
    apply_hack(dol, [0x042BF6CC, 0x60000000])

    # Code to hide excess files
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "HideSecondaryProfilesFromMenues.asm"),
        0x802BF6E0,
        memory_dict,
    )

    # Code to prevent counting extra files
    insert_assembly_into_codes_file(
        codes_file_location,
        os.path.join(asm_path, "SkipCountSecondaryProfiles.asm"),
        0x802BE3F0,
        memory_dict,
    )
