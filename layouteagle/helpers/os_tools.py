import os
import shutil
from collections import namedtuple
from glob import iglob
from pathlib import Path

def make_dirs_recursive(dir_dict, base_dir=""):
    if isinstance(dir_dict, dict):
        for dir, sub in dir_dict.items():
            if base_dir:
                new_dir = f"{base_dir}/{dir}"
            else:
                new_dir = dir
            if not os.path.isdir(new_dir):
                os.system(f"mkdir {new_dir}")
            make_dirs_recursive(sub, base_dir=new_dir)
    elif isinstance(dir_dict, (list, tuple)):
        for dir in dir_dict:
            new_dir = f"{base_dir}/{dir}"
            if not os.path.isdir(new_dir):
                os.system(f"mkdir {new_dir}")

recursive_indexes_path = '**/index.html'
def get_files_from_recursive_path(path):
    for f in iglob(path, recursive=True) :
        if os.path.isfile(f):
            yield str(Path(f).resolve())

def make_fresh_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        shutil.rmtree(dir)  # removes all the subdirectories!
        os.makedirs(dir)

def get_filename_from_path(path):
    return os.path.basename(path)

PathInfo = namedtuple("PathInfo", ["path", "filename", "extension", "filename_without_extension"])
def get_path_filename_extension(adress):
    extension = os.path.splitext(adress)[1]
    path = os.path.dirname(adress) + "/"
    if path == r"/":
        path = "./"
    filename = os.path.basename(adress)
    filename_without_extension = filename[:-len(extension)]
    return PathInfo(path, filename, extension, filename_without_extension)
