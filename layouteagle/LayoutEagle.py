import os

from layouteagle import config
from layouteagle.LatexReplacer.latex_replacer import LatexReplacer
from layouteagle.LayoutReader.feature_maker import FeatureMaker
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.ScienceTexScraper.scrape import ScienceTexScraper
from layouteagle.bi_lstm_crf_layout.bilstm_crf import Bi_LSTM_CRF

import logging
logging.basicConfig(level = logging.INFO)
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)

class LayoutEagle:
    def __init__(self,
                 model_path="best_model/",):
        try:
            os.mkdir(".layouteagle")
            os.mkdir(".layouteagle/cache")
            os.mkdir(".layouteagle/texdata")
            os.mkdir(".layouteagle/models/")
        except:
            logging.info("dirs exist")
        finally:
            logging.info("tried to create directories")

        self.bi_lstm_crf = Bi_LSTM_CRF(output_dir=model_path)
        self.feature_maker = FeatureMaker(
            pandas_pickle_path=".layouteagle/features.pckl",
            debug=True, parameterize=False)
        self.trueFormatPDF2HTMLEX = TrueFormatUpmarkerPDF2HTMLEX()

    def __call__(self, pdf_path=None, html1_path=None, html2_path=None, css_path=None):
        div_features = self.feature_maker.work(pdf_path, html1_path=None)
        labeled_div_features = self.bi_lstm_crf.predict(features=div_features)
        self.trueFormatPDF2HTMLEX(labeled_div_features, html2_path=html2_path)

    def make_model(self, n):
        science_tex_scraper = ScienceTexScraper(url = config.tex_source, n=n)
        latex_replacer = LatexReplacer(".labeled.tex")

        pipeline = [science_tex_scraper, latex_replacer, self.feature_maker, self.bi_lstm_crf, lambda x: print (x)]

        intermediate_result = []
        for functional_object in pipeline:
            if intermediate_result:
                intermediate_result = functional_object(intermediate_result)
            else:
                intermediate_result = functional_object()


if __name__ == '__main__':
    lea = LayoutEagle()
    lea.make_model(n=5)



