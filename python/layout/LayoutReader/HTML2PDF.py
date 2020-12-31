import os

from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec


@converter('html', 'pdf')
class HTML2PDF(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, paths, *args, **kwargs):
        for path, meta in paths:
            pdf_path = path + self.path_spec._to
            os.system(f"chrome --headless --print-to-pdf='{pdf_path}'")
            yield path, meta