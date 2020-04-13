import logging
import os
import string

import pandas

from layouteagle import config
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.helpers.cache_tools import persist_to_file, file_persistent_cached_generator


class FeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, pandas_pickle_path, add_html_extension=".html", debug=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug
        self.pandas_pickle_path =  pandas_pickle_path
        self.add_html_extension = add_html_extension

    @file_persistent_cached_generator(config.cache + 'collected_features.json')
    def __call__(self, labeled_paths):
        all_feature_dfs = []
        doc_id = 0
        while doc_id < self.n:
            logging.info(f"Got {doc_id}/{self.n}")
            labeled_pdf_path = next(labeled_paths)
            labeled_html_path = labeled_pdf_path + self.add_html_extension
            self.pdf2htmlEX(labeled_pdf_path, labeled_html_path)
            try:
                features, soup = self.generate_data_for_file(labeled_html_path)
            except FileNotFoundError:
                logging.error("output of pdf2html looks damaged")
                continue
            pdf_doc = self.collect_data_for_file
            pdf_doc.features["doc_id"] = doc_id
            all_feature_dfs.append(pdf_doc.features)

            if self.debug:
                debug_html_path = labeled_html_path+".debug.html"
                self.tfu = TrueFormatUpmarkerPDF2HTMLEX(debug=True)
                self.tfu.generate_css_tagging_document(premade_soup=soup, html_write_to=debug_html_path, premade_features=features)
                os.system(f"google-chrome {debug_html_path}")
            doc_id += 1

        df = pandas.concat(all_feature_dfs)
        df['chars'] = df.divs.apply(lambda div: sum(div.text.count(c) for c in string.ascii_letters))
        df['nums'] = df.divs.apply(lambda div: sum(div.text.count(c) for c in string.digits))
        df['signs'] = df.divs.apply(lambda div: sum(div.text.count(c) for c in string.punctuation))
        df.divs = df.divs.astype(str)
        df.to_pickle(self.pandas_pickle_path)

        yield self.pandas_pickle_path

    def set_n(self, n):
        self.n = n

