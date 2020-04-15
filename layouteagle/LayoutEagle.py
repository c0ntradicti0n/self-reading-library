import os

from layouteagle import config
from layouteagle.LatexReplacer.latex_replacer import LatexReplacer
from layouteagle.LayoutModel.layoutmodel import LayoutModeler
from layouteagle.LayoutReader.feature_maker import FeatureMaker
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.ScienceTexScraper.scrape import ScienceTexScraper

import logging
logging.basicConfig(level = logging.INFO)
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)

class LayoutEagle:
    def __init__(self,
                 model_path="best_model/",
                 pandas_path=".layouteagle/features.pckl"):
        try:
            os.mkdir(config.hidden_folder)
            os.mkdir(config.cache)
            os.mkdir(config.tex_data)
            os.mkdir(config.models)
        except:
            logging.info("dirs exist")
        finally:
            logging.info("tried to create directories")

        self.pandas_path = pandas_path

        self.model = LayoutModeler()
        self.feature_maker = FeatureMaker(
            pandas_pickle_path=".layouteagle/features.pckl",
            debug=True, parameterize=False)
        self.trueFormatPDF2HTMLEX = TrueFormatUpmarkerPDF2HTMLEX()

    def make_document(self, pdf_path=None, html1_path=None, html2_path=None, css_path=None):
        div_features = self.feature_maker.work(pdf_path, html1_path=None)
        self.feature_maker = FeatureMaker(
            pandas_pickle_path=self.pandas_path,
            debug=True,
            parameterize=False)
        labeled_div_features = self.model.predict(features=div_features)
        if pdf_path and not html1_path:
            return labeled_div_features

        self.trueFormatPDF2HTMLEX(labeled_div_features, html2_path=html2_path)

    def make_model(self, n):
        science_tex_scraper = ScienceTexScraper(url = config.tex_source)
        latex_replacer = LatexReplacer(".labeled.tex")
        self.feature_maker.set_n(n)

        pipeline = [science_tex_scraper, latex_replacer, self.feature_maker, self.model, lambda x: print (x)]

        intermediate_result = []
        for functional_object in pipeline:
            if intermediate_result:
                intermediate_result = functional_object(intermediate_result)
            else:
                intermediate_result = functional_object()


if __name__ == '__main__':
    lea = LayoutEagle()
    lea.make_model(n=18)



