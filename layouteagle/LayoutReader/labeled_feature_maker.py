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

    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (labeled_pdf_path, meta) in enumerate(labeled_paths):
            logging.info(f"Got {doc_id}/{self.n}")

            labeled_html_path = labeled_pdf_path + ".htm"
            self.pdf2htmlEX(labeled_pdf_path, labeled_html_path)
            meta['pdf2htmlEX.html'] = labeled_html_path
            try:
                feature_df, soup = self.generate_data_for_file(labeled_html_path)
            except FileNotFoundError:
                logging.error("output of pdf2html looks damaged")
                continue

            feature_df["doc_id"] = doc_id
            if False and self.debug:
                debug_html_path = labeled_html_path+".debug.html"
                self.tfu = TrueFormatUpmarkerPDF2HTMLEX(debug=True)
                self.tfu.generate_css_tagging_document(premade_soup=soup, html_write_to=debug_html_path, premade_features=feature_df)
                os.system(f"google-chrome {debug_html_path}")

            #feature_df['chars'] = feature_df.divs.apply(lambda div: sum(div.text.count(c) for c in string.ascii_letters))
            #feature_df['nums'] = feature_df.divs.apply(lambda div: sum(div.text.count(c) for c in string.digits))
            #feature_df['signs'] = feature_df.divs.apply(lambda div: sum(div.text.count(c) for c in string.punctuation))

            meta['filename'] = labeled_pdf_path
            meta['soup'] = soup

            yield feature_df, meta



