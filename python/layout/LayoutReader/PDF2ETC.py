import os
import logging

from layouteagle import config
from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from helpers.cache_tools import file_persistent_cached_generator
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.parallel import paraloop

outputs = {
    'html': 'html',  # same looking html
    'wordi': 'wordi',  # numbered word list
    'feat': 'feat'  # json with indexed single words as they can be reapplied via css to the html-document
}


@converter('pdf', list(outputs.values()))
class PDF2ETC(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @file_persistent_cached_generator(config.cache + os.path.basename(__file__) + '.json', if_cache_then_finished=True)
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (pdf_path, meta) in enumerate(labeled_paths):
            html_path = pdf_path + outputs['html']
            wordi_path = pdf_path + "." + outputs['wordi']
            feat_path = pdf_path + "." + outputs['feat']

            logging.warning(f"working on {pdf_path}")
            self.pdf2htmlEX(pdf_path, html_path)

            meta['pdf2htmlEX.html'] = html_path
            meta['pdf_path'] =  pdf_path
            meta['wordi_path'] = wordi_path
            meta['feat_path'] = feat_path

            yield (html_path, wordi_path, feat_path), meta
