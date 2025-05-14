import tempfile
import zipfile
import os
import shutil
import pathlib
import sys
import csv

from .ma_tools import mst_extract
from .ma_tools import mst_insert
from .ma_tools import csv_rebuilder

CSV_SUFFIX = ".new"

def apply_csv_edits(metadata, iso_dir, csv_file, values, is_gc):

  # First we need to extract the csv
  tmpdirname = tempfile.TemporaryDirectory()
  csv_dir_name = tmpdirname.name

  iso_mst = os.path.join(iso_dir, "root", "files", "mettlearms_gc.mst")
  mst_extract.extract(iso_mst, csv_dir_name, False, csv_file, False)

  # log
  print (f"Before: ({csv_file})")
  with open(os.path.join(csv_dir_name, csv_file), 'r') as file:
    # Read the entire content of the file.
    content = file.read()
    # Print the content.
    print(content)

  csv_matrix = []
  with open(os.path.join(csv_dir_name, csv_file), newline='') as file:
    reader = csv.reader(file)
    # materialize the csv
    for row in reader:
      csv_matrix.append(row)

    for edit in values:
      match edit["operation"]:
          case "replace":
            csv_matrix[edit['row']][edit['col']] = edit['value']
          case "add_line":
            csv_matrix.append(edit['value'])
          case _:
            raise Exception(f"Invalid operation type: {edit['operation']}")

  # overwrite the original file
  with open(os.path.join(csv_dir_name, csv_file), 'w', newline='') as file:
    writer = csv.writer(file)
    for row in csv_matrix:
      writer.writerow(row)

  # log
  print (f"After: ({csv_file})")
  with open(os.path.join(csv_dir_name, csv_file), 'r') as file:
    # Read the entire content of the file.
    content = file.read()
    # Print the content.
    print(content)

  # Rebuild csv
  csv_rebuilder.execute(is_gc, False, os.path.join(csv_dir_name, csv_file), os.path.join(csv_dir_name, csv_file + CSV_SUFFIX))
  shutil.move(os.path.join(csv_dir_name, csv_file + CSV_SUFFIX), os.path.join(csv_dir_name, csv_file))

  mst_insert.execute(True, iso_mst, [os.path.join(csv_dir_name, csv_file)], "")
