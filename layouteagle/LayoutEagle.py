import glob
import os

from layouteagle.pathant.PathAnt import PathAnt


class LayoutEagle:
    from layouteagle.ScienceTexScraper.scrape import ScienceTexScraper
    from layouteagle.LatexReplacer.latex_replacer import LatexReplacer
    from layouteagle.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
    from layouteagle.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX
    from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
    from layouteagle.LayoutReader.feature_prediction import LayoutPrediction
    from layouteagle.LayoutReader.MarkupDocument import MarkupDocument
    from layouteagle.LayoutReader.feature2features import Feature2Features
    from layouteagle.LayoutModel.layouttrain import LayoutTrainer
    from layouteagle.LayoutModel.layoutpredict import LayouPredictor

    from layouteagle.LayoutReader.HTML2PDF import HTML2PDF
    from layouteagle.LayoutReader.PDF2HTML import PDF2HTML

    from TestArchitecture.publisher import NLPPublisher, TopicPublisher
    from TestArchitecture.NLP.nlp_blub import NLPBlub
    from TestArchitecture.NLP.topicape import TopicApe

    def __init__(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant("arxiv.org", "keras")
        self.prediction_pipe = self.ant("pdf", "layout.html")


    def make_model(self):
        model_pipe = self.ant("arxiv.org", "keras")
        print (list(model_pipe("https://arxiv.org")))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        pdfs = [file for file in glob.glob("test/*.pdf")]
        result_paths = list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))
        print(result_paths)
        for (html_path, json_path, txt_path), meta in result_paths:
            os.system(f'google-chrome {html_path}')


if __name__=="__main__":
    le = LayoutEagle()
    le.make_model()
    le.test_prediction()