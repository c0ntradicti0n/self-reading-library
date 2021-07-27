import glob
import os
import sys
sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print(sys.path)
from layouteagle import config
from layouteagle.pathant.PathAnt import PathAnt

class LayoutEagle:

    from layout.ScienceTexScraper.scrape import ScienceTexScraper
    from layout.LatexReplacer.latex_replacer import LatexReplacer
    from layout.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.feature_prediction import LayoutPrediction
    from layout.LayoutReader.MarkupDocument import MarkupDocument
    from layout.LayoutReader.feature2features import Feature2Features
    from layout.LayoutModel.layouttrain import LayoutTrainer
    from layout.LayoutModel.layoutpredict import LayouPredictor

    from layout.LayoutReader.HTML2PDF import HTML2PDF
    from layout.LayoutReader.PDF2ETC import PDF2ETC

    from layout.LayoutReader.PDF2HTML import PDF2HTML

    from layouteagle.StandardConverter.Dict2Graph import Dict2Graph
    from layouteagle.StandardConverter.Wordi2Css import Wordi2Css
    from layouteagle.pathant.PathAnt import PathAnt
    from nlp.TransformerStuff.ElmoDifference import ElmoDifference
    from nlp.TransformerStuff.Pager import Pager
    from nlp.TransformerStuff.UnPager import UnPager

    def __init__(self):
        self.ant = PathAnt()
        self.html_pipeline = self.ant("pdf", "htm")



    def test_topics(self):
        self.model_pipe = self.ant("arxiv.org", "keras")

        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]
        self.ant.info()
        pipeline = self.ant("pdf", "topics")

        value, meta = list(zip(*list(pipeline([(pdf, {}) for pdf in pdfs]))))


    def make_model(self):
        model_pipe = self.ant("arxiv.org", "keras" )
        print (list(model_pipe("https://arxiv.org", mode = 'training')))
        os.system(
            f'cp -r {config.hidden_folder + config.layout_model_path} {config.hidden_folder + config.saved_layout_model_dir}')

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        self.prediction_pipe = self.ant("pdf", "css.layout")
        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]

        css = list(self.prediction_pipe([(pdfs[0], {})]))
        print (css)
        assert(css)


    def test_layout(self):
        self.layout_pipe = self.ant("pdf", f"css.layout")

        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]

        for pdf in pdfs:
            html, css = list(self.html_pipeline([(pdf,{})])), list(self.layout_pipe([(pdf, {})]))
            print(html, css)

            html_path = html[0][0]
            with open(html_path, "r") as f:
                contents = f.readlines()

            contents.insert(8, css[0][0])
            with open(html_path, "w") as f:
                contents = "".join(contents)
                f.write(contents)

            #os.system(f'google-chrome {html_path}')


    def test_difference(self):
        self.difference_pipe = self.ant("pdf", f"css.difference")

        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]
        result_paths = list(self.difference_pipe([(pdf, {}) for pdf in pdfs]))
        print(result_paths)
        for (html_path, json_path, txt_path), meta in result_paths:
            #os.system(f'google-chrome {html_path}')
            pass



if __name__=="__main__":

    le = LayoutEagle()
    le.ant.info()

    le.make_model()
    le.test_prediction()
    le.test_layout()
    le.test_prediction()
    #le.test_topics()
