import logging

import pandas

from layouteagle import config
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.helpers.cache_tools import persist_to_file, file_persistent_cached_generator


class FeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, pandas_pickle_path, add_html_extension=".html", *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                self.generate_data_for_file(labeled_html_path)
            except FileNotFoundError:
                logging.error("output of pdf2html looks damaged")
                continue
            pdf_doc = self.collect_data_for_file
            pdf_doc.features["doc_id"] = doc_id
            all_feature_dfs.append(pdf_doc.features)
            doc_id += 1

        df = pandas.concat(all_feature_dfs)
        df.divs = df.divs.astype(str)
        df.to_pickle(self.pandas_pickle_path)

        yield self.pandas_pickle_path

    def set_n(self, n):
        self.n = n

