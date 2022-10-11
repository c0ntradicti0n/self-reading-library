import itertools
import os
import tkinter

from config import config
from helpers.cache_tools import configurable_cache
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter("replaced.pdf", "labeled.pdf")
class OK(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    @configurable_cache(config.cache + "user_ok_tex_paths.json")
    def __call__(self, paths, *args, cache=None, **kwargs):
        while True:
            batch = list(itertools.islice(paths, 165))

            for in_path, meta in batch:
                out_path = in_path + self.path_spec._to
                if out_path in cache:
                    continue
                os.system(f"FoxitReader {in_path}")

                app = tkinter.Tk()
                choice = tkinter.messagebox.askquestion(
                    "Yes/No", "Take this document?", icon="warning"
                )
                print("User chosen: {}".format(choice))
                app.destroy()
                app.mainloop()

                if choice == "yes":
                    os.system(f"cp {in_path} {out_path}")
                    yield out_path, meta
                else:
                    pass
