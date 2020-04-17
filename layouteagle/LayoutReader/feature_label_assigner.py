from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from pathant.Converter import converter


@converter(('feature', 'keras'), 'layoutprediction')
class FeatureAssigner(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, *args, **kwargs):
        pass