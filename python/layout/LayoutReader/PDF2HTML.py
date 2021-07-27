from helpers.os_tools import cwd_of
from layouteagle import config
from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from helpers.cache_tools import file_persistent_cached_generator
from layouteagle.pathant.Converter import converter


@converter(["labeled.pdf", "pdf"], "htm")
class PDF2HTML(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @file_persistent_cached_generator(config.cache + 'pdf2html.json' )
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (pdf_path, meta) in enumerate(labeled_paths):
            html_path = pdf_path + self.path_spec._to

            with cwd_of(html_path) as filename:
                self.pdf2htmlEX(pdf_path, filename)

            meta['pdf2htmlEX.html'] = html_path
            meta['filename'] = pdf_path

            yield html_path, meta
