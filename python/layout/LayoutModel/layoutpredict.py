import itertools
from python.layout.LayoutModel.layoutmodel import LayoutModeler
from python.layouteagle.pathant.Converter import converter

@converter("keras", "predictor")
class LayouPredictor(LayoutModeler):
    def __init__(self,
                 *args,
                 debug: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def __call__(self, model_path_meta):
        if model_path_meta:
            _, meta = next(model_path_meta)

        self.load()
        yield from itertools.cycle([self])


if __name__ == '__main__':
    pass
