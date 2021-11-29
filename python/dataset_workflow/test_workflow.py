from layout.ScienceTexScraper.scrape import ScienceTexScraper
from layout.LatexReplacer.latex_replacer import LatexReplacer
from layout.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
from layout.LayoutReader.box_feature_maker import BoxFeatureMaker
from layout.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX
from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
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
from layouteagle.StandardConverter import Tex2Pdf
from dataset_workflow.annotator import annotation, collection
from dataset_workflow.prediction import prediction
from dataset_workflow.training import training
import os
from helpers.os_tools import file_exists_regex
from helpers.list_tools import add_meta
from layouteagle import config
import subprocess
import regex
from dataset_workflow.model_helpers import find_best_model
from pprint import pprint

"""
Filters depending on existing annotation files if 
this file is in the annotation set
or not. Returns True for not used, False for has been used yet
"""
def unlabeled_not_existent_filter(x_m):
    hash = x_m[0][:54].replace("/", "-")
    res = file_exists_regex(config.COLLECTION_PATH, rf"{hash}.*")
    yet_not_res = file_exists_regex(config.NOT_COLLECTED_PATH, rf"{hash}.*")
    is_labeled = "labeled" in x_m[0]
    subprocess.call(["touch", config.NOT_COLLECTED_PATH + "/" + hash])
    return True
    return not (res or yet_not_res or is_labeled)

def annotate_train_model():
    ant = PathAnt()
    ant.info("workflow.png")

    if not os.path.isdir(config.TEXT_BOX_MODEL_PATH):
        os.makedirs(config.TEXT_BOX_MODEL_PATH)


    while True:
        samples_files = os.listdir(config.COLLECTION_PATH)
        n_samples = len(samples_files)
        best_model_path, scores = find_best_model()
        full_model_path = best_model_path

        training_rate = ( int(scores.groups()[0]) / n_samples )

        sample_pipe = ant("arxiv.org", "annotation.collection",
                          num_labels=config.NUM_LABELS,
                          via='pdf',
                          filter={'tex': unlabeled_not_existent_filter},
                          model_path=full_model_path,
                          #texs = ['.layouteagle/tex_data/e58dd6bbc7c23fd05c9b120fef282145//cccconstant-curvature.text']
                          #ignore_incomplete=True
                          )

        model_pipe = ant("annotation.collection", "model",
                         num_labels=config.NUM_LABELS,
                         filter={'tex': unlabeled_not_existent_filter},
                         collection_step=training_rate

                         )
        print (f"{training_rate = }")
        if training_rate < 0.8:
            # let's train

            model_meta = list(
                        model_pipe(add_meta(samples_files),
                                   collection_step=training_rate
                                   )
                    )
            pprint (model_meta)
            model_path = model_meta[0][0]
        else:
            # let's make more samples

            try:
                collection, collection_meta = list(
                    zip(
                        *list(
                            sample_pipe(
                                "https://arxiv.org",
                            model_path = best_model_path)
                        )
                    )
                )
            except KeyboardInterrupt as e:

                exit = input("Exit? [y]/n")

                if exit.startswith('n'):
                    continue
                else:
                    break


if __name__ == "__main__":
    annotate_train_model()