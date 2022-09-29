# add database queue, that contains samples with scores, based on 2 visitor ratings or corrections
# unpack pickle and offer it by that queue between page navigation
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter("annotation.collection", "annotation.corrected")
class Captcha(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, annotation_metas, *args, **kwargs):
        for id, meta in annotation_metas:
            yield id, meta
