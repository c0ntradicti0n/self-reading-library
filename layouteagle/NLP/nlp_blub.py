from pathant.Converter import converter
from pathant.PathSpec import PathSpec


@converter('text.json', 'text.css')
class NLPBlub(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, *args, **kwargs):
        pass