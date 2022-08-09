import tempfile
import zipfile
import os
import pathlib
import sys

from .ma_tools import mst_extract
from .ma_tools import mst_insert

def insert_mod(metadata, iso_dir):
  #insert relevant files into the mst
  with zipfile.ZipFile(metadata.zip_file_path) as mod_zip:
    for info in mod_zip.infolist():
      if os.path.splitext(info.filename)[1].lower() == ".mst":
        #extract the mst to a temp directory and insert the files
        tmpdirname = tempfile.TemporaryDirectory()
        mst_path = os.path.join(tmpdirname.name, info.filename)
        print(f'Extracting {info.filename} to {tmpdirname.name}')
        mod_zip.extract(info.filename, tmpdirname.name)
        # now rename files if needed
        mst_extract_path = os.path.join(tmpdirname.name, "extract")
        print(f'Extracting mst to {mst_extract_path}')
        mst_extract.extract(mst_path, mst_extract_path, False, False)
        path = pathlib.Path(mst_extract_path)
        for filename in path.iterdir():
          if os.path.basename(filename) == metadata.levels[0]['wld']:
            continue
            new_filename = os.path.join(os.path.split(filename)[0], "wedmmines01.wld")
            os.rename(filename, new_filename)
            filename = new_filename
          elif os.path.basename(filename) == metadata.levels[0]['csv']:
            continue
            new_filename = os.path.join(os.path.split(filename)[0], "wedmmines01.csv")
            os.rename(filename, new_filename)
            filename = new_filename
          elif os.path.basename(filename) == metadata.levels[0]['gt']:
            continue
            new_filename = os.path.join(os.path.split(filename)[0], "wedmmines01.gt")
            os.rename(filename, new_filename)
            filename = new_filename
          iso_mst = os.path.join(iso_dir.name, "root", "files", "mettlearms_gc.mst")
          print (iso_mst, filename)
          mst_insert.execute(True, iso_mst, [filename], "")
          print(filename)
      elif os.path.basename(info.filename).lower() != "manifest.json":
        print(f'Extracting {info.filename} to {os.path.join(iso_dir.name, "root")}')
        #first move to temporary directory and then copy to the right spot to dodge added folders
        tmpdirname = tempfile.TemporaryDirectory()
        mod_zip.extract(info.filename, tmpdirname.name)
        file_path = os.path.join(tmpdirname.name, info.filename)
        new_filename = os.path.join(iso_dir.name, "root", "files", os.path.basename(info.filename))
        print(file_path, new_filename)
        os.rename(file_path, new_filename)

