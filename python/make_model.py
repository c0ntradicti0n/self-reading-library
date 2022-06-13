import unittest

class Mak(unittest.TestCase):
    from core.StandardConverter.ScienceTexScraper.ScienceTexScraper import ScienceTexScraper
    from core.LatexReplacer.latex_replacer import LatexReplacer
    from core.LayoutReader.labeled_feature_maker import PDF_AnnotatorTool
    from core.LayoutReader.feature_label_assigner import PDF_AnnotatorTool
    from core.LayoutReader.trueformatpdf2htmlEX import PDF_AnnotatorTool
    from core.LayoutReader.feature_prediction import LayoutPrediction
    from core.LayoutReader.MarkupDocument import MarkupDocument
    from core.LayoutReader.feature2features import Feature2Features
    from core.LayoutModel.layouttrain import LayoutTrainer
    from core.LayoutModel.layoutpredict import LayouPredictor

    from core.LayoutReader.HTML2PDF import HTML2PDF
    from core.LayoutReader.PDF2HTML import PDF2HTML

    from TestArchitecture.publisher import NLPPublisher, TopicPublisher
    from TestArchitecture.NLP.nlp_blub import NLPBlub
    from TestArchitecture.NLP.topicape import TopicApe

    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")
        self.prediction_pipe = self.ant("pdf", "latex.html")

    def test_make_model(self):
        model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")
        print (list(model_pipe("https://arxiv.org")))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        pdfs = [".core/tex_data/2adf47ffbf65696180417ca86e91eb90//crypto_github_preprint_v1.pdf",
                ".core/tex_data/2922d1d785d9620f9cdf8ac9132c59a8//ZV_PRL_rev.pdf",
                ".core/tex_data/9389d5a6fd9fcc41050f32bcb2a204ef//Manuscript.tex1.labeled.pdf"]
        list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))


if __name__=="__init__":
    unittest()