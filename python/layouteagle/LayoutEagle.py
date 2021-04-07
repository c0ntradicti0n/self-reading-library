import glob
import os
from pprint import pprint

from python.layouteagle import config
from python.layouteagle.pathant.PathAnt import PathAnt
import sys

class LayoutEagle:

    from python.layout.ScienceTexScraper.scrape import ScienceTexScraper
    from python.layout.LatexReplacer.latex_replacer import LatexReplacer
    from python.layout.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
    from python.layout.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX
    from python.layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
    from python.layout.LayoutReader.feature_prediction import LayoutPrediction
    from python.layout.LayoutReader.MarkupDocument import MarkupDocument
    from python.layout.LayoutReader.feature2features import Feature2Features
    from python.layout.LayoutModel.layouttrain import LayoutTrainer
    from python.layout.LayoutModel.layoutpredict import LayouPredictor

    from python.layout.LayoutReader.HTML2PDF import HTML2PDF
    from python.layout.LayoutReader.PDF2ETC import PDF2ETC

    from python.layout.LayoutReader.PDF2HTML import PDF2HTML

    from python.TestArchitecture.publisher import NLPPublisher, TopicPublisher
    from python.TestArchitecture.NLP.nlp_blub import NLPBlub
    from python.TestArchitecture.NLP.topicape import TopicApe
    from python.layouteagle.StandardConverter.Dict2Graph import Dict2Graph



    def __init__(self):
        self.ant = PathAnt()
        print (self.ant.graph())
        self.model_pipe = self.ant("arxiv.org", "keras")
        self.prediction_pipe = self.ant("pdf", "layout.html")

    def test_topics(self):
        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]
        self.ant.info()
        pipeline = self.ant("pdf", "topics")

        value, meta = list(zip(*list(pipeline([(pdf, {}) for pdf in pdfs]))))
        pprint(value)

    def make_model(self):
        model_pipe = self.ant("arxiv.org", "keras" )
        print (list(model_pipe("https://arxiv.org")))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]
        result_paths = list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))
        print(result_paths)
        for (html_path, json_path, txt_path), meta in result_paths:
            os.system(f'google-chrome {html_path}')


if __name__=="__main__":
    le = LayoutEagle()
    le.ant.info()
    #print(list(AntPublisher([123])))
    le.test_topics()
    #le.make_model()
    #le.test_prediction()