import glob
import os
import sys

from layout.latex.LayoutReader.feature2features import Feature2Features
from layout.latex.LayoutReader.feature_label_assigner import FeatureAssigner
from layout.training.training import Training

sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core import config
from core.pathant.PathAnt import PathAnt
from core.StandardConverter.ScienceTexScraper.scrape import ScienceTexScraper
from layout.box_feature_maker.box_feature_maker import BoxFeatureMaker
from core.StandardConverter.HTML2PDF import HTML2PDF
from core.StandardConverter.PDF2ETC import PDF2ETC
from core.StandardConverter.PDF2HTML import PDF2HTML
from core.StandardConverter.Dict2Graph import Dict2Graph
from core.StandardConverter.ReadingOrder2Css import ReadingOrder2Css
from core.pathant.PathAnt import PathAnt
from language.transformer.Pager import Pager
from language.transformer.UnPager import UnPager
from core.StandardConverter.Tex2Pdf import Tex2Pdf
from layout.annotator import annotation, collection
from layout.prediction import prediction
from layout.training import training
from layout.upload_annotation.upload_annotation import UploadAnnotator

Training
class LayoutEagle:
    #from latex.LayoutReader.feature_prediction import LayoutPrediction

    def __init__(self):
        self.ant = PathAnt()
        self.html_pipeline = self.ant("pdf", "htm", dont_use_cache=True)
        self.model_pipe = self.ant("pdf", "htm", dont_use_cache=True)
        self.prediction_pipe = self.ant("pdf", "htm", dont_use_cache=True)



    def test_topics(self):
        self.model_pipe = self.ant("arxiv.org", "keras")

        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]
        self.ant.info()
        pipeline = self.ant("pdf", "topics")

        value, meta = list(zip(*list(pipeline([(pdf, {}) for pdf in pdfs]))))


    def make_layout_model(self):
        model_pipe = self.ant("arxiv.org", "keras" )
        print (list(model_pipe("https://arxiv.org", training = True)))
        os.system(
            f'cp -r {config.hidden_folder + config.layout_model_path} {config.hidden_folder + config.saved_layout_model_dir}')

    def make_box_layout_model(self):
        model_pipe = self.ant("arxiv.org", "model" )
        print (list(model_pipe("https://arxiv.org", training = True, layout_model_path=config.layout_model_path)))
        os.system(
            f'cp -r {config.hidden_folder + config.layout_model_path} {config.hidden_folder + config.saved_layout_model_dir}')

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        self.prediction_pipe = self.ant("pdf", "css.latex")
        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]
        css = list(self.prediction_pipe([(pdfs[0], {})]))
        assert(css)


    def test_layout(self):
        self.layout_pipe = self.ant("pdf", f"css.latex")

        pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]

        for pdf in pdfs:
            css = list(self.layout_pipe([(pdf, {})]))
            html_path = css[0][1]['html_path']
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
        for (html_path, json_path, txt_path), meta in result_paths:
            #os.system(f'google-chrome {html_path}')
            pass



if __name__=="__main__":
    le = LayoutEagle()
    le.ant.info()
    le.make_box_layout_model()
    #le.make_layout_model()

    #le.make_layout_model()
    le.test_layout()
    #le.test_topics()
