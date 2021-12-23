from helpers.os_tools import get_path_filename_extension
from core import config
from layout.latex.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from helpers.cache_tools import file_persistent_cached_generator
from core.pathant.Converter import converter
import os

@converter(["labeled.pdf", "pdf"], "htm")
class PDF2HTML(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug
        self.cwd  = os.getcwd()

    @file_persistent_cached_generator(config.cache + 'pdf2html.json')
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (pdf_path, meta) in enumerate(labeled_paths):
            html_path = pdf_path + self.path_spec._to

            path, pdf_filename, _, _  = get_path_filename_extension(pdf_path)
            path, html_filename, _, _ = get_path_filename_extension(html_path)

            os.chdir(path)
            try:
                self.pdf2htmlEX(pdf_filename, html_filename)
                meta['html_path'] = html_path
                meta['pdf_path'] = pdf_path
                meta['html_filename'] = html_filename
                meta['pdf_filename'] = pdf_filename
                os.chdir(self.cwd)

                yield html_path, meta
            except FileNotFoundError as e:
                self.logger.error (f"Could not convert {pdf_path} to html file!")