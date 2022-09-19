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


recursive_indexes_path = "**/index.html"


def get_files_from_recursive_path(path):
    for f in iglob(path, recursive=True):
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


PathInfo = namedtuple(
    "PathInfo", ["path", "filename", "extension", "filename_without_extension"]
)


def get_path_filename_extension(adress):
    extension = os.path.splitext(adress)[1]
    path = os.path.dirname(adress) + "/"
    if path == r"/":
        path = "./"
    filename = os.path.basename(adress)
    filename_without_extension = filename[: -len(extension)]
    return PathInfo(path, filename, extension, filename_without_extension)


class cwd_of:
    def __init__(self, fpath):
        (
            self.path,
            self.filename,
            self.extension,
            self.filename_without_extension,
        ) = get_path_filename_extension(fpath)

    def __enter__(self):
        self.cwd = os.getcwd()
        os.chdir(self.path)
        return self.filename

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)
        return self.filename


import regex


def file_exists_regex(dir, regexp):
    pattern = regex.compile(regexp)
    return any(pattern.match(filepath) for filepath in os.listdir(dir))


def rm_r(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)
    else:
        shutil.rmtree(path)
