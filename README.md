# MetalArmsModLoader

## Where to get Binaries
Download from [Releases](https://github.com/dj0wns/MetalArmsModLoader/releases)

## Setting up Repository
` git clone https://github.com/dj0wns/MetalArmsModLoader`  
` cd MetalArmsModLoader`  
` git submodule update --init --recursive`  

## Command Line Options
```
usage: modloader.py [-h] [input_iso] [output_iso] [mod_folder]

Add mods to Metal Arms ISO file

positional arguments:
  input_iso   A valid vanilla Metal Arms Iso File
  output_iso  Name of the new output iso which will be produced
  mod_folder  Folder containing all mods which the user will have the option
              of adding

options:
  -h, --help  show this help message and exit
```

## Compiling a release
`python -m PyInstaller -F modloader.py --add-data files\*;files`
