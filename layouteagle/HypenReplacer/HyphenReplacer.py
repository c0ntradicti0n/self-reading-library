import json
import os
from pprint import pprint

from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathSpec import PathSpec
from layouteagle.HypenReplacer.miss_matching_tokenization_assingment import MismatchingTokenisationManipulation


@converter('layout.json', 'unhypen.json')
class MarkupDocument(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


    def __call__(self, feature_meta, *args, **kwargs):
        for json_path, meta in feature_meta:
            with open(json_path, 'r') as f:
                content = json.load(f, indent=4)

            mtm = MismatchingTokenisationManipulation(content['indexed_words'])

            yield mtm, meta


