from dataclasses import dataclass
import struct
import os
import tempfile
import shutil

from .ma_tools import mst_extract
from .ma_tools import mst_insert
from .ma_tools import csv_rebuilder
from .assembly import insert_assembly_into_codes_file
from .dol import apply_hack
from .csv_table_reader import read_ma_csv_to_dict, write_ma_csv_to_file

SP_CSV_DATA = {}
MP_CSV_DATA = {}

PICK_LEVEL_CSV_FILE = "pick_level$.csv"
MULTI_LEVEL_CSV_FILE = "multi_lvl$.csv"
CSV_SUFFIX = '.new'

LEVEL_TYPES = [
  "campaign",
  "multiplayer"
]

CAMPAIGN_LEVEL_NAMES = [
  "wedmmines01",
  "wedmmines02",
  "wedmmines03",
  "wedttown_01",
  "wewtrace_01",
  "wewjjourn01",
  "wewjjourn02",
  "wewjjourn03",
  "wewzzombi01",
  "wewccomm_01",
  "wewccomm_02",
  "wewccomm_03",
  "wewchold_01",
  "wewrresrch1",
  "wewrresrch2",
  "wewrresrch3",
  "wewrresrch4",
  "wewhchase01",
  "wermmorbot1",
  "wermmorbot2",
  "werrreactr1",
  "werrreactr2",
  "wemccity_01",
  "wemccity_03",
  "wecffacty01",
  "wemccity_05",
  "wecrruins01",
  "wecrruins02",
  "wemccity_02",
  "wecdsneak01",
  "wecdsneak02",
  "wediinvas01",
  "webccolis01",
  "webccolis02",
  "webccolis03",
  "webccolis04",
  "wewkrockt01",
  "weshhangr01",
  "wessstatn01",
  "wessstatn02",
  "wesrrepair1",
  "wesccorros1",
]

MULTIPLAYER_LEVEL_NAMES = [
  "we01multi01",
  "we02multi02",
  "we03multi03",
  "we05multi05",
  "we11multi11",
  "we15multi15",
  "we08multi08",
  "we12multi12",
  "we14multi14",
  "we09multi09",
  "we10multi10",
  "we07multi07",
  "we04multi04",
  "we06multi06",
]

LEVEL_BOT_MAP = [
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "mozer",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "krunk",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "slosh",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
  "glitch",
]

@dataclass
class Level:
  title: str
  starting_bot: str
  wld_resource_name: str
  #level_id: int - too be calculated at runtime, not stored
  csv_file: str
  csv_material_file: str
  load_ptr: int
  unload_ptr: int
  work_ptr: int
  draw_ptr: int
  projector_offsets: float
  projector_range_adjustment: float

  # For csv file
  def add_level_info(self, csv_row):
    self.location = csv_row[0]
    self.name = csv_row[1]
    self.screenshot = csv_row[2]
    self.secret_chips = csv_row[3]
    self.time_to_beat = csv_row[4]

  def get_level_info(self, level_index):
    return [self.location,
            self.name,
            self.screenshot,
            self.secret_chips,
            self.time_to_beat,
            # is a float for some reason
            str(level_index) + '.0']

  def get_string_offsets(self, current_offset):
    # self code is used for the injection assembly script to notice that it needs to be modified at run time
    offset_special_code = 0xdcba0000
    offset = current_offset
    ret_dict = {}

    # Handle the null level or null strings in general
    if not self.title:
      ret_dict['name_offset'] = 0
    else:
      ret_dict['name_offset'] = offset + offset_special_code
      offset += len(self.title) + 1 # null char

    if not self.wld_resource_name:
      ret_dict['wld_resource_name_offset'] = 0
    else:
      ret_dict['wld_resource_name_offset'] = offset + offset_special_code
      offset += len(self.wld_resource_name) + 1 # null char

    if not self.csv_file:
      ret_dict['csv_file_offset'] = 0
    else:
      ret_dict['csv_file_offset'] = offset + offset_special_code
      offset += len(self.csv_file) + 1 # null char

    if not self.csv_material_file:
      ret_dict['csv_material_file_offset'] = 0
    else:
      ret_dict['csv_material_file_offset'] = offset + offset_special_code
      offset += len(self.csv_material_file) + 1 # null char
    # Return the new offset
    return ret_dict, offset

  def get_concatenated_strings(self):
    ret_string = ""
    if self.title:
      ret_string += self.title + '\0'
    if self.wld_resource_name:
      ret_string += self.wld_resource_name + '\0'
    if self.csv_file:
      ret_string += self.csv_file + '\0'
    if self.csv_material_file:
      ret_string += self.csv_material_file + '\0'
    return ret_string

  def level_byte_count(self):
    return 11 * 4

  # convert to bytes before exported to game
  def to_bytes(self, offset_dict, index):
    bytes = bytearray()

    bytes.extend(struct.pack(">I", offset_dict['name_offset']))
    bytes.extend(struct.pack(">I", offset_dict['wld_resource_name_offset']))
    bytes.extend(struct.pack(">i", index))
    bytes.extend(struct.pack(">I", offset_dict['csv_file_offset']))
    bytes.extend(struct.pack(">I", offset_dict['csv_material_file_offset']))
    bytes.extend(struct.pack(">I", self.load_ptr))
    bytes.extend(struct.pack(">I", self.unload_ptr))
    bytes.extend(struct.pack(">I", self.work_ptr))
    bytes.extend(struct.pack(">I", self.draw_ptr))
    bytes.extend(struct.pack(">f", self.projector_offsets))
    bytes.extend(struct.pack(">f", self.projector_range_adjustment))

    return bytes

DEFAULT_SP_LEVEL_ARRAY = [
  Level(
    "1 Seal the Mines",
    "glitch",
    "WEDMmines01",
    "WEDMmines01",
    "ms_mines01",
    0,
    0,
    0,
    0,
    0.0,
    1.0
  ),
  Level(
    "2 Seal the Mines",
    "glitch",
    "WEDMmines02",
    "WEDMmines02",
    "ms_mines02",
    0,
    0,
    0,
    0,
    0.0,
    1.0
  ),
  Level(
    "3 Seal the Mines",
    "glitch",
    "WEDMmines03",
    "WEDMmines03",
    "ms_mines03",
    0,
    0,
    0,
    0,
    10.0,
    4.0
  ),
  Level(
    "4 Clean Up",
    "glitch",
    "WEDTtown_01",
    "WEDTtown_01",
    "ms_town_01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "5 RAT race",
    "glitch",
    "WEWTrace_01",
    "WEWTrace_01",
    "ms_race_01",
    0,
    0,
    0,
    0,
    50.0,
    4.0,
  ),
  Level(
    "6 Wasteland Journey",
    "glitch",
    "WEWJjourn01",
    "WEWJjourn01",
    "ms_journ01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "7 Wasteland Journey",
    "glitch",
    "WEWJjourn02",
    "WEWJjourn02",
    "ms_journ02",
    0,
    0,
    0,
    0,
    10.0,
    4.0,
  ),
  Level(
    "8 Wasteland Journey",
    "mozer",
    "WEWJjourn03",
    "WEWJjourn03",
    "ms_journ03",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "9 ZombieBot Boss",
    "glitch",
    "WEWZzombi01",
    "WEWZzombi01",
    "ms_zombi01",
    0x80132ba0,
    0x80142c24,
    0x80142c90,
    0x801b10b8,
    0.0,
    1.0,
  ),
  Level(
    "10 Destroy Comm Cntr",
    "glitch",
    "WEWCcomm_01",
    "WEWCcomm_01",
    "ms_comm_01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "11 Destroy Comm Cntr",
    "glitch",
    "WEWCcomm_02",
    "WEWCcomm_02",
    "ms_comm_02",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "12 Destroy Comm Cntr",
    "glitch",
    "WEWCcomm_03",
    "WEWCcomm_03",
    "ms_comm_03",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "13 Hold Your Ground",
    "glitch",
    "WEWChold_01",
    "WEWChold_01",
    "ms_hold_01",
    0x8012a548,
    0x8012bbf4,
    0x8012bc40,
    0x801b10b8,
    0.0,
    1.0,
  ),
  Level(
    "14 R & D",
    "glitch",
    "WEWRresrch1",
    "WEWRresrch1",
    "ms_resrch1",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "15 R & D",
    "glitch",
    "WEWRresrch2",
    "WEWRresrch2",
    "ms_resrch2",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "16 R & D",
    "glitch",
    "WEWRresrch3",
    "WEWRresrch3",
    "ms_resrch3",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "17 R & D",
    "krunk",
    "WEWRresrch4",
    "WEWRresrch4",
    "ms_resrch4",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "18 Wasteland Chase",
    "glitch",
    "WEWHchase01",
    "WEWHchase01",
    "ms_chase01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "19 Morbot Region",
    "glitch",
    "WERMmorbot1",
    "WERMmorbot1",
    "ms_morbot1",
    0,
    0,
    0,
    0,
    10.0,
    4.0,
  ),
  Level(
    "20 Morbot Region",
    "glitch",
    "WERMmorbot2",
    "WERMmorbot2",
    "ms_morbot2",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "21 Reactor",
    "glitch",
    "WERRreactr1",
    "WERRreactr1",
    "ms_reactr1",
    0,
    0,
    0,
    0,
    10.0,
    4.0,
  ),
  Level(
    "22 Reactor",
    "slosh",
    "WERRreactr2",
    "WERRreactr2",
    "ms_reactr2",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "23 Mil City Hub",
    "glitch",
    "WEMCcity_01",
    "WEMCcity_01",
    "ms_city_01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "24 Mil City Hub",
    "glitch",
    "WEMCcity_03",
    "WEMCcity_03",
    "ms_city_03",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "25 Spy vs. Spy",
    "glitch",
    "WECFfacty01",
    "WECFfacty01",
    "ms_facty01",
    0x8013bb2c,
    0x8013c11c,
    0x8013c224,
    0,
    0.0,
    1.0,
  ),
  Level(
    "26 Ruins",
    "glitch",
    "WEMCcity_05",
    "WEMCcity_05",
    "ms_city_05",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "27 Ruins",
    "glitch",
    "WECRruins01",
    "WECRruins01",
    "ms_ruins01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "28 Ruins",
    "glitch",
    "WECRruins02",
    "WECRruins02",
    "ms_ruins02",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "29 Secret Rendezvous",
    "glitch",
    "WEMCcity_02",
    "WEMCcity_02",
    "ms_city_02",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "30 Night Sneak",
    "glitch",
    "WECDsneak01",
    "WECDsneak01",
    "ms_sneak01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "31 Night Sneak",
    "glitch",
    "WECDsneak02",
    "WECDsneak02",
    "ms_sneak02",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "32 Invasion",
    "glitch",
    "WEDiinvas01",
    "WEDiinvas01",
    "ms_invas01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "33 Coliseum",
    "glitch",
    "WEBCcolis01",
    "WEBCcolis01",
    "ms_colis01",
    0x8014405c,
    0x80144d10,
    0x80145748,
    0,
    0.0,
    1.0,
  ),
  Level(
    "34 Coliseum",
    "glitch",
    "WEBCcolis02",
    "WEBCcolis02",
    "ms_colis02",
    0x80144100,
    0x80144d10,
    0x80145748,
    0,
    0.0,
    1.0,
  ),
  Level(
    "35 Coliseum",
    "glitch",
    "WEBCcolis03",
    "WEBCcolis03",
    "ms_colis03",
    0x80144224,
    0x80144d10,
    0x80145748,
    0,
    0.0,
    1.0,
  ),
  Level(
    "36 Coliseum",
    "glitch",
    "WEBCcolis04",
    "WEBCcolis04",
    "ms_colis04",
    0x80144330,
    0x80144d10,
    0x80145748,
    0,
    0.0,
    1.0,
  ),
  Level(
    "37 Race to the Rocket",
    "glitch",
    "WEWKrockt01",
    "WEWKrockt01",
    "ms_rockt01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "38 Space Dock",
    "glitch",
    "WESHhangr01",
    "WESHhangr01",
    "ms_hangr01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "39 Space Station",
    "glitch",
    "WESSstatn01",
    "WESSstatn01",
    "ms_statn01",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "40 Space Station",
    "glitch",
    "WESSstatn02",
    "WESSstatn02",
    "ms_statn02",
    0,
    0,
    0,
    0,
    0.0,
    1.0,
  ),
  Level(
    "41 Gen. Corrosive",
    "glitch",
    "WESRrepair1",
    "WESRrepair1",
    "ms_repair1",
    0x80127954,
    0x801279f0,
    0x801b0908,
    0x801b10b8,
    0.0,
    1.0,
  ),
  Level(
    "42 Final Battle",
    "glitch",
    "WESCcorros1",
    "WESCcorros1",
    "ms_corros1",
    0x80129fec,
    0x8012a07c,
    0x801b092c,
    0,
    0.0,
    1.0,
  ),
]

DEFAULT_MP_LEVEL_ARRAY = [
  Level(
    "1 Big E",
    "glitch",
    "WE01multi01",
    "WE01multi01",
    "ms_mp_01",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "2 Spy v Spy",
    "glitch",
    "WE02multi02",
    "WE02multi02",
    "ms_mp_02",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "3 Tanks Alot",
    "glitch",
    "WE03multi03",
    "WE03multi03",
    "ms_mp_03",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "4 MacMines",
    "glitch",
    "WE05multi05",
    "WE05multi05",
    "ms_mp_05",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "5 Inferno Machine",
    "glitch",
    "WE11multi11",
    "WE11multi11",
    "ms_mp_11",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "6 Clean Up",
    "glitch",
    "WE15multi15",
    "WE15multi15",
    "ms_mp_15",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "7 Trenches",
    "glitch",
    "WE08multi08",
    "WE08multi08",
    "ms_mp_08",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "8 Comm AAGun",
    "glitch",
    "WE12multi12",
    "WE12multi12",
    "ms_mp_12",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "9 Morbotland",
    "glitch",
    "WE14multi14",
    "WE14multi14",
    "ms_mp_14",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "10 Reactor",
    "glitch",
    "WE09multi09",
    "WE09multi09",
    "ms_mp_09",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "11 Lost Boss",
    "glitch",
    "WE10multi10",
    "WE10multi10",
    "ms_mp_10",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "12 Ruins",
    "glitch",
    "WE07multi07",
    "WE07multi07",
    "ms_mp_07",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "13 Coliseum",
    "glitch",
    "WE04multi04",
    "WE04multi04",
    "ms_mp_04",
    0x80143cd4,
    0x80143fa0,
    0x80145900,
    00000000,
    0.0,
    1.0,
  ),
  Level(
    "14 Corrosive City",
    "glitch",
    "WE06multi06",
    "WE06multi06",
    "ms_mp_06",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  )
]

GENERIC_LEVEL = Level(
    "Generic",
    "glitch",
    "",
    "Level01",
    "ms_gtest_01",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    1.0,
  )

NULL_LEVEL = Level(
    "",
    "glitch",
    "",
    "",
    "",
    00000000,
    00000000,
    00000000,
    00000000,
    0.0,
    0.0,
  )


def level_array_to_bytes(level_array):
  level_buffer = bytearray()
  string_buffer = []
  # add 4 bytes for some buffer
  string_offset = level_array[0].level_byte_count() * len(level_array) + 4
  index = -1 # Generic level is -1
  for level in level_array:
    offset_dict, string_offset = level.get_string_offsets(string_offset)
    for k,v in offset_dict.items():
      print(k, hex(v))
    print(string_offset)
    level_buffer += level.to_bytes(offset_dict, index)
    string_buffer += level.get_concatenated_strings()
    # increment index!
    index += 1

  # Convert to assembly string
  bytes_written = 0
  out_string = ""
  for byte in level_buffer:
    out_string += f'.byte {byte}\n'
    bytes_written += 1
  for i in range(4):
    out_string += f'.byte 0x0\n'
    bytes_written += 1
  for byte in string_buffer:
    out_string += f'.byte {ord(byte)}\n'
    bytes_written += 1
  out_string += f'.byte 0x0\n'
  bytes_written += 1

  while (bytes_written % 4) != 0:
    out_string += f'.byte 0x0\n'
    bytes_written += 1

  return out_string



def apply_level_count_overrides(dol, codes_file_location, asm_path, sp_count, mp_count, memory_dict):

  memory_dict['SP_LEVEL_COUNT'] = sp_count
  memory_dict['MP_LEVEL_COUNT'] = mp_count

  cmpwi = 0x2c170000 + sp_count
  cmpwir31 = 0x2c1f0000 + sp_count
  cmplwi = 0x28000000 + sp_count
  cmplwir4 = 0x28040000 + sp_count


  # Everywhere i can find where level count is referred to in code
  # SP OVERRIDES
  apply_hack(dol, [0x041c87ac, cmpwi])
  apply_hack(dol, [0x04154e10, cmpwir31])
  apply_hack(dol, [0x041c8c88, cmpwi])
  apply_hack(dol, [0x041c8d08, cmpwi - 1])
  apply_hack(dol, [0x04157cac, cmplwi])
  apply_hack(dol, [0x04158fac, cmplwi])
  apply_hack(dol, [0x04158f6c, cmplwi])
  apply_hack(dol, [0x04155010, cmplwi])
  apply_hack(dol, [0x04154ffc, cmplwir4])
  apply_hack(dol, [0x0414b6fc, cmplwi])
  # subi to subtract sp count
  apply_hack(dol, [0x04158f94, 0x3816ffff - sp_count + 1])
  # MP OVERRIDES
  apply_hack(dol, [0x0415903c, cmplwi + mp_count + 1])
  apply_hack(dol, [0x04158f8c, cmplwi + mp_count + 1])

  # Now apply code injections
  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "EnableContinueOfExtraLevels.asm"),
      0x8015d854,
      memory_dict)
  # Update following branch to a bne
  apply_hack(dol, [0x0415d858, 0x40820018])

  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "DontGrayOutContinueOfExtraLevels.asm"),
      0x8015da28,
      memory_dict)
  # Update following branch to a bne
  apply_hack(dol, [0x0415da2c, 0x40820008])

  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "IncrementExtraCurrentLevelVariable.asm"),
      0x801c8d9c,
      memory_dict)

  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "CheckCompletedCampaignInPlayerProfile.asm"),
      0x801c8da4,
      memory_dict)

  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "GetLevelToContinueTo.asm"),
      0x80164688,
      memory_dict)

  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "ListExtraLevelsInReplayMenu.asm"),
      0x8015dcd0,
      memory_dict)

def init_default_levels(iso_dir):
    sp_description_dict = {
        'pick_level_text' : 7,
        'pick_level_meshes' : 5,
        'pick_level_buttons' : 6,
        'level_names' : 6,
        'level_unlocking' : 1
    }
    mp_description_dict = {
        'multi_level_text' : 7,
        'multi_level_meshes' : 5,
        'multi_level_buttons' : 6,
        'deathmatchlevels' : 6,
    }
    # Get picklevel and multilvl out of mst and lost the info into the level array
    tmpdirname = tempfile.TemporaryDirectory()
    csv_dir_name = tmpdirname.name

    iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")
    mst_extract.extract(iso_mst, csv_dir_name, False, PICK_LEVEL_CSV_FILE, False)
    mst_extract.extract(iso_mst, csv_dir_name, False, MULTI_LEVEL_CSV_FILE, False)

      #load in sp csv file
    with open(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), 'r') as pick_levels:
      sp_data = pick_levels.readlines()
    print(sp_data)


    #load in sp csv file
    global SP_CSV_DATA
    SP_CSV_DATA = read_ma_csv_to_dict(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), sp_description_dict)
    index = 0
    for level in SP_CSV_DATA['level_names']:
      DEFAULT_SP_LEVEL_ARRAY[index].add_level_info(level)
      index += 1

    global MP_CSV_DATA
    MP_CSV_DATA = read_ma_csv_to_dict(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE), mp_description_dict)
    index = 0
    for level in MP_CSV_DATA['deathmatchlevels']:
      DEFAULT_MP_LEVEL_ARRAY[index].add_level_info(level)
      index += 1

def fixup_single_player_csv(sp_array, iso_dir, is_gc):
    tmpdirname = tempfile.TemporaryDirectory()
    csv_dir_name = tmpdirname.name
    iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")

    index = 1 # 1 indexed!
    level_data = []
    for level in sp_array:
      level_data.append(level.get_level_info(index))
      index += 1
    SP_CSV_DATA['level_names'] = level_data
    write_ma_csv_to_file(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), SP_CSV_DATA)

    csv_rebuilder.execute(is_gc, False, os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE), os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE + CSV_SUFFIX))
    shutil.move(os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE + CSV_SUFFIX), os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE))
    mst_insert.execute(True, iso_mst, [os.path.join(csv_dir_name, PICK_LEVEL_CSV_FILE)], "")

def fixup_multi_player_csv(sp_array, mp_array, iso_dir, is_gc):
    tmpdirname = tempfile.TemporaryDirectory()
    csv_dir_name = tmpdirname.name
    iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")

    index = len(sp_array) + 1
    level_data = []
    for level in mp_array:
      level_data.append(level.get_level_info(index))
      index += 1
    MP_CSV_DATA['deathmatchlevels'] = level_data
    write_ma_csv_to_file(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE), MP_CSV_DATA)

    csv_rebuilder.execute(is_gc, False, os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE), os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE + CSV_SUFFIX))
    shutil.move(os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE + CSV_SUFFIX), os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE))
    mst_insert.execute(True, iso_mst, [os.path.join(csv_dir_name, MULTI_LEVEL_CSV_FILE)], "")

    print(MP_CSV_DATA)


def apply_level_array_codes(
    dol,
    memory_dict,
    asm_path,
    codes_file_location,
    sp_array,
    mp_array,
    iso_dir,
    is_gc):

  local_dict = memory_dict.copy()
  local_dict['LEVEL_ARRAY_RAW'] = level_array_to_bytes(
      [GENERIC_LEVEL] + # Level array starts with this
      sp_array +
      mp_array +
      [NULL_LEVEL]) # Level array ends with this

  apply_level_count_overrides(dol, codes_file_location, asm_path, len(sp_array), len(mp_array) - 1, memory_dict)

  fixup_single_player_csv(sp_array, iso_dir, is_gc)
  fixup_multi_player_csv(sp_array, mp_array, iso_dir, is_gc)

  insert_assembly_into_codes_file(codes_file_location,
      os.path.join(asm_path, "CopyLevelArrayToMemory.asm"),
      0,
      local_dict,
      immediate_exec=True)

