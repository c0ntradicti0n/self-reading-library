import logging
import os
import string

import pandas

from layouteagle import config
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.helpers.cache_tools import file_persistent_cached_generator
from pathant.Converter import converter


@converter(["labeled.pdf", "pdf"], "feature")
class LabeledFeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @file_persistent_cached_generator(config.cache + 'collected_features.json')
    def __call__(self, labeled_paths, *args, **kwargs):
        all_feature_dfs = []
        doc_id = 0
        while doc_id < self.n:
            logging.info(f"Got {doc_id}/{self.n}")
            labeled_pdf_path, meta = next(labeled_paths)

            labeled_html_path = labeled_pdf_path + ".htm"
            self.pdf2htmlEX(labeled_pdf_path, labeled_html_path)
            try:
                features, soup = self.generate_data_for_file(labeled_html_path)
            except FileNotFoundError:
                logging.error("output of pdf2html looks damaged")
                continue
            pdf_doc = self.pdf_obj
            pdf_doc.features["doc_id"] = doc_id
            all_feature_dfs.append(pdf_doc.features)

            if False and self.debug:
                debug_html_path = labeled_html_path+".debug.html"
                self.tfu = TrueFormatUpmarkerPDF2HTMLEX(debug=True)
                self.tfu.generate_css_tagging_document(premade_soup=soup, html_write_to=debug_html_path, premade_features=features)
                os.system(f"google-chrome {debug_html_path}")

            pandas_pickle_path = labeled_pdf_path + self.path_spec._to
            pdf_doc.features.divs = pdf_doc.features.divs.astype(str)

            pdf_doc.features.to_pickle(pandas_pickle_path)

            yield pandas_pickle_path, meta



