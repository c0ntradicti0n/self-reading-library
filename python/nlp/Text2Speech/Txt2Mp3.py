import os
from pprint import pprint

from ant import Ant
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathAnt import PathAnt
from layouteagle.pathant.PathSpec import cache_flow


@converter('txt', 'mp3')
class Txt2Mp3(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def __call__(self, iterator, *args, **kwargs):
        for text, meta in iterator:
            txt_path = meta['html_path'] + ".txt"
            meta['txt_path'] = txt_path
            meta['mp3_path'] = txt_path + '.mp3'
            text = "\n\n".join(text)
            with open(txt_path, "w") as f:
                f.write(text)

                self.logger.info(f"encoding \"{text[100:]}\" as mp3 on path {meta['mp3_path']}")
            os.popen(f"text2wave -eval  '(nitech_us_bdl_arctic_hts)'  {meta['txt_path']} -o out.wave").read()
            os.popen(f"lame out.wave {meta['mp3_path']}").read()
            yield meta['mp3_path'], meta


if __name__ == "__main__":
    from layouteagle import config
    from layout.ScienceTexScraper.scrape import ScienceTexScraper
    from layout.LatexReplacer.latex_replacer import LatexReplacer
    from layout.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.box_feature_maker import BoxFeatureMaker
    from layout.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.MarkupDocument import MarkupDocument
    from layout.LayoutReader.feature2features import Feature2Features
    from layout.LayoutReader.HTML2PDF import HTML2PDF
    from layout.LayoutReader.PDF2ETC import PDF2ETC
    from layout.LayoutReader.PDF2HTML import PDF2HTML
    from layouteagle.StandardConverter.Dict2Graph import Dict2Graph
    from layouteagle.StandardConverter.Wordi2Css import Wordi2Css
    from layouteagle.pathant.PathAnt import PathAnt
    from nlp.TransformerStuff.Pager import Pager
    from nlp.TransformerStuff.UnPager import UnPager
    from layouteagle.StandardConverter import Tex2Pdf
    from dataset_workflow.annotator import annotation, collection
    from dataset_workflow.prediction import prediction
    from dataset_workflow.training import training
    from dataset_workflow import prediction2txt
    from dataset_workflow.model_helpers import find_best_model
    from helpers.list_tools import add_meta

    ant = PathAnt()
    print (ant.graph())
    model_path = model_pat=find_best_model()[0]
    pipe = ant("pdf", "mp3")
    res = list(pipe(add_meta(["./../test/glue.pdf"]), model_path=model_path))
    pprint(res)
    os.popen(f"mplayer {res[0][0]}").read()




