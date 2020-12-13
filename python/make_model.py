import unittest

class Mak(unittest.TestCase):
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

    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant("arxiv.org", "keras")
        self.prediction_pipe = self.ant("pdf", "layout.html")


    def test_make_model(self):
        model_pipe = self.ant("arxiv.org", "keras")
        print (list(model_pipe("https://arxiv.org")))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        pdfs = [".layouteagle/tex_data/2adf47ffbf65696180417ca86e91eb90//crypto_github_preprint_v1.pdf",
                ".layouteagle/tex_data/2922d1d785d9620f9cdf8ac9132c59a8//ZV_PRL_rev.pdf",
                ".layouteagle/tex_data/9389d5a6fd9fcc41050f32bcb2a204ef//Manuscript.tex1.labeled.pdf"]
        list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))


if __name__=="__init__":
    unittest()