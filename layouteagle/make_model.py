import logging
from collections import Callable

from more_itertools import pairwise

from layouteagle import config
from layouteagle.LatexReplacer.latex_replacer import LatexReplacer
from layouteagle.LayoutReader.feature_maker import FeatureMaker
from layouteagle.ScienceTexScraper.scrape import ScienceTexScraper
from layouteagle.bi_lstm_crf_layout.bilstm_crf import Bi_LSTM_CRF

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)

science_tex_scraper = ScienceTexScraper(url = config.tex_source, n=120)
latex_replacer = LatexReplacer(".labeled.tex")
true_format_upmarker = FeatureMaker(pandas_pickle_path="tex_data/features.pckl", debug=True, parameterize=False)
bi_lstm_crf =  Bi_LSTM_CRF()



pipeline = [science_tex_scraper, latex_replacer, true_format_upmarker, bi_lstm_crf, lambda x: print (x)]

intermediate_result = []
for functional_object in pipeline:
    if intermediate_result:
        intermediate_result = functional_object(intermediate_result)
    else:
        intermediate_result = functional_object()



