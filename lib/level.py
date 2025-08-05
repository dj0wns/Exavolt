from .dol import apply_hack


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

def apply_level_count_overrides(dol, sp_count, mp_count):
  cmpwi = 0x2c170000 + count
  cmplwi = 0x28000000 + count


  # Everywhere i can find where level count is referred to in code
  # SP OVERRIDES
  apply_hack(dol, [0x041c87ac, cmpwi])
  apply_hack(dol, [0x04154e10, cmpwi])
  apply_hack(dol, [0x041c8c88, cmpwi])
  apply_hack(dol, [0x041c8d08, cmpwi - 1])
  apply_hack(dol, [0x04157cac, cmplwi])
  apply_hack(dol, [0x04158faf, cmplwi])
  # subi to subtract sp count
  apply_hack(dol, [0x04158f94, 0x3816ffff - sp_count + 1])
  # MP OVERRIDES
  apply_hack(dol, [0x0415903c, cmplwi + mp_count])
  apply_hack(dol, [0x04158f8c, cmplwi + mp_count])

  # TODO ASM CODE FOR AUTO EXECUTE

