import pandas

import layouteagle.config
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPdf2HTMLEX
from layouteagle.helpers.cache_tools import persist_to_file


class FeatureMaker(TrueFormatUpmarkerPdf2HTMLEX):
    def __init__(self, pandas_pickle_path, add_html_extension=".html", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pandas_pickle_path =  pandas_pickle_path
        self.add_html_extension = add_html_extension

    @persist_to_file(config.scrape_cache + 'collected_features.json')
    def __call__(self, labeled_paths):
        all_feature_dfs = []

        for doc_id, labeled_pdf_path in enumerate(labeled_paths):
            labeled_html_path = labeled_pdf_path + self.add_html_extension
            self.pdf2htmlEX(labeled_pdf_path, labeled_html_path)
            self.generate_data_for_file(labeled_html_path)
            pdf_doc = self.collect_data_for_file
            pdf_doc.features["doc_id"] = doc_id
            all_feature_dfs.append(pdf_doc.features)

        df = pandas.concat(all_feature_dfs)
        df.divs = df.divs.astype(str)
        df.to_pickle(self.pandas_pickle_path)

        return self.pandas_pickle_path

