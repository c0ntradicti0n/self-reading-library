import os

from pathant.Converter import converter
from pathant.PathSpec import PathSpec


@converter(('text.html', 'text.css'), 'apache')
class NLPPublisher(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, paths, *args, **kwargs):
        for path, meta in paths:
            pdf_path = path + self.path_spec._to
            yield path, meta



@converter('topics', 'apache')
class TopicPublisher(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, paths, *args, **kwargs):
        for path, meta in paths:
            pdf_path = path + self.path_spec._to
            os.system(f"chrome --headless --print-to-pdf='{pdf_path}'")
            yield path, meta