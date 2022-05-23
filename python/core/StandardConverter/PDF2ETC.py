import os
from core import config
from layout.latex.LayoutReader.trueformatpdf2htmlEX import PDF_AnnotatorTool
from helpers.cache_tools import file_persistent_cached_generator
from core.pathant.Converter import converter
from core.pathant.parallel import paraloop

outputs = {
    'html': 'html',  # same looking html
    'reading_order': 'reading_order',  # numbered word list
    'feat': 'feat'  # json with indexed single words as they can be reapplied via css to the html-document
}


@converter('pdf', list(outputs.values()))
class PDF2ETC(PDF_AnnotatorTool):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @file_persistent_cached_generator(config.cache + os.path.basename(__file__) + '.json', if_cache_then_finished=True)
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (pdf_path, meta) in enumerate(labeled_paths):
            html_path = pdf_path + outputs['html']
            reading_order_path = pdf_path + "." + outputs['reading_order']
            feat_path = pdf_path + "." + outputs['feat']

            self.logger.warning(f"working on {pdf_path}")
            self.pdf2htmlEX(pdf_path, html_path)

            meta['pdf2htmlEX.html'] = html_path
            meta['pdf_path'] =  pdf_path
            meta['reading_order_path'] = reading_order_path
            meta['feat_path'] = feat_path

            yield (html_path, reading_order_path, feat_path), meta
