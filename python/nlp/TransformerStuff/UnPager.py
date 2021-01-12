from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec


@converter("wordi.page.*", 'wordi.*')
class UnPager(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, feature_meta, *args, **kwargs):
        for wordi, meta in feature_meta:
            css = "?"
            yield css, meta
