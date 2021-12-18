from core.pathant.PathAnt import PathAnt
from layout.model_helpers import repaint_image_from_labels
from helpers.event_binding import RestQueue
from core.StandardConverter.ScienceTexScraper.scrape import ScienceTexScraper
from layout.box_feature_maker.box_feature_maker import BoxFeatureMaker
from core.StandardConverter.HTML2PDF import HTML2PDF
from core.StandardConverter.PDF2ETC import PDF2ETC
from core.StandardConverter.PDF2HTML import PDF2HTML
from core.StandardConverter.Dict2Graph import Dict2Graph
from core.StandardConverter.Wordi2Css import Wordi2Css
from core.pathant.PathAnt import PathAnt
from language.TransformerStuff.ElmoDifference import ElmoDifference
from language.TransformerStuff.Pager import Pager
from language.TransformerStuff.UnPager import UnPager
from core.StandardConverter.Tex2Pdf import Tex2Pdf
from layout.annotator import annotation, collection
from layout.prediction import prediction
from layout.training import training
from layout.upload_annotation.upload_annotation import UploadAnnotator
import os
from helpers.os_tools import file_exists_regex
from helpers.list_tools import add_meta
from core import config
import subprocess
from layout.model_helpers import find_best_model
from pprint import pprint

samples_files = os.listdir(config.COLLECTION_PATH)
n_samples = len(samples_files)
best_model_path, scores = find_best_model()
full_model_path = best_model_path
training_rate = (int(scores.groups()[0]) / n_samples)

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
    return not (res or yet_not_res or is_labeled)


ant = PathAnt()

sample_pipe = ant(
    "arxiv.org", "annotation.collection",
    num_labels=config.NUM_LABELS,
    via='pdf',
    filter={'tex': unlabeled_not_existent_filter},
    model_path=full_model_path,
    # texs = ['.core/tex_data/e58dd6bbc7c23fd05c9b120fef282145//constant-curvature.tex']
    # ignore_incomplete=True
)

model_pipe = ant(
    "annotation.collection", "model",
    num_labels=config.NUM_LABELS,
    filter={'tex': unlabeled_not_existent_filter},
    collection_step=training_rate
)

upload_pipe = ant(
    "pdf", "annotation.collection",
    via="upload_annotation",
    num_labels=config.NUM_LABELS,
    model_path=full_model_path
)

ant.info("workflow.png", pipelines_to_highlight=[sample_pipe, model_pipe, upload_pipe])

def annotate_uploaded_file(path_to_pdf):
    print(f"working on {path_to_pdf}")
    return upload_pipe(add_meta([path_to_pdf]))

UploadAnnotationQueueRest = RestQueue(
    update_data=repaint_image_from_labels,
    service_id="upload_annotation",
    work_on_upload=annotate_uploaded_file
)


def annotate_train_model():
    global full_model_path
    if not os.path.isdir(config.TEXT_BOX_MODEL_PATH):
        os.makedirs(config.TEXT_BOX_MODEL_PATH)
    if not os.path.isdir(config.PDF_UPLOAD_DIR):
        os.makedirs(config.PDF_UPLOAD_DIR)

    while True:
        samples_files = os.listdir(config.COLLECTION_PATH)
        n_samples = len(samples_files)
        best_model_path, scores = find_best_model()
        full_model_path = best_model_path

        training_rate = (int(scores.groups()[0]) / n_samples)

        print(f"{training_rate = }")
        if training_rate < 0.8:
            # let's train

            model_meta = list(
                model_pipe(add_meta(samples_files),
                           collection_step=training_rate
                           )
            )
            pprint(model_meta)
            model_path = model_meta[0][0]
        else:
            # let's make more samples

            try:
                collection, collection_meta = list(
                    zip(
                        *list(
                            sample_pipe(
                                "https://arxiv.org",
                                model_path=best_model_path)
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
