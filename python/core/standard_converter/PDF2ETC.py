import os

from core.pathant.PathSpec import PathSpec

from config import config
from helpers.cache_tools import configurable_cache
from core.pathant.Converter import converter

outputs = {
    'html': 'html',  # same looking html
    'feat': 'feat'  # json with indexed single words as they can be reapplied via css to the html-document
}


@converter('pdf', list(outputs.values()))
class PDF2ETC(PathSpec):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    def pdf2htmlEX(self, pdf_filename, html_filename):
        assert (pdf_filename.endswith(".pdf"))
        self.logger.info(f"converting pdf {pdf_filename} to html {html_filename} ")
        from pathlib import Path

        origin = Path(os.getcwd()).resolve()
        destination = Path(html_filename).resolve()
        rel_html_path = os.path.relpath(destination, start=origin)
        return_code = os.system(f"{config.pdf2htmlEX} "
                                f"--space-as-offset 1 "
                                f"--decompose-ligature 1 "
                                f"--optimize-text 1 "
                                f"--fit-width {config.reader_width}  "
                                f"\"{pdf_filename}\" \"{rel_html_path}\"")

        if return_code != 0:
            raise FileNotFoundError(f"{pdf_filename} was not found!")

    @configurable_cache(config.cache + os.path.basename(__file__))
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (pdf_path, meta) in enumerate(labeled_paths):
            html_path = pdf_path + outputs['html']
            pdf2htmlEX_wordi_path = pdf_path + "." + outputs['reading_order']
            feat_path = pdf_path + "." + outputs['feat']

            self.logger.warning(f"working on {pdf_path}")
            self.pdf2htmlEX(pdf_path, html_path)

            meta['pdf2htmlEX.html'] = html_path
            meta['pdf_path'] =  pdf_path
            meta['pdf2htmlEX_wordi_path'] = pdf2htmlEX_wordi_path
            meta['feat_path'] = feat_path

            yield (html_path, pdf2htmlEX_wordi_path, feat_path), meta
