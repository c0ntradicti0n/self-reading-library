import itertools
import os
import tkinter

from python.layouteagle import config
from python.helpers.cache_tools import file_persistent_cached_generator
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec


@converter('replaced.pdf', 'labeled.pdf')
class OK(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    @file_persistent_cached_generator(config.cache + 'user_ok_tex_paths.json')
    def __call__(self, paths, *args, cache=None, **kwargs):
        while True:
            batch = list(itertools.islice(paths, 165))

            for in_path, meta in batch:
                out_path = in_path + self.path_spec._to
                if out_path in cache:
                    continue
                os.system(f"FoxitReader {in_path}")


                app = tkinter.Tk()
                choice = tkinter.messagebox.askquestion("Yes/No", "Take this document?", icon='warning')
                print('User chosen: {}'.format(choice))
                app.destroy()
                app.mainloop()

                if choice=='yes':
                    os.system(f"cp {in_path} {out_path}")
                    yield out_path, meta
                else:
                    pass