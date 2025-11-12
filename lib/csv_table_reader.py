import csv

# Description dict is a dict of table names and field counts per row
# EX: (pick_level$.csv)
# description_dict = {
#     'pick_level_text' : 7,
#     'pick_level_meshes' : 5,
#     'pick_level_buttons' : 6,
#     'level_names' : 6,
#     'level_unlocking' : 1
# }
#
#
# Will return a dict of the following format:
# return_dict = {
#     'pick_level_text' : [[...]],
#     'pick_level_meshes' : [[...]],
#     'pick_level_buttons' : [[...]],
#     'level_names' : [[...]],
#     'level_unlocking' : [[...]]
# }


def read_ma_csv_to_dict(file, description_dict):
  # These may not properly be divided by rows, so have to go token by token
  ret_dict = {}
  current_table = None
  index = 0
  with open(file, 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
      for token in row:
        if not token:
          # ignore empty tokens, they only appear at line end
          continue
        if index == 0:
          # if we are outside of a row, look for a new column header
          if token in description_dict.keys():
            current_table = token
            if token not in ret_dict.keys():
              ret_dict[current_table] = []
          else:
            ret_dict[current_table].append([token])
            index += 1
        else:
            ret_dict[current_table][-1].append(token)
            index += 1

        if index == description_dict[current_table]:
          index = 0
  return ret_dict

# Input in the format of read_ma_csv_to_dict return
# csv_dict = {
#     'pick_level_text' : [[...]],
#     'pick_level_meshes' : [[...]],
#     'pick_level_buttons' : [[...]],
#     'level_names' : [[...]],
#     'level_unlocking' : [[...]]
# }

def write_ma_csv_to_file(file, value_dict):
  with open(file, 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key in value_dict.keys():
      writer.writerow([key])
      index = 0
      for row in value_dict[key]:
        # Add empty key at beginning for leading commas
        if index == len(value_dict[key]) - 1:
          # add trailing comma too
          writer.writerow([''] + row + [''])
        else:
          writer.writerow([''] + row)
        index += 1

