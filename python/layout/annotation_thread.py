import itertools
import logging

from layout.model_helpers import changed_labels
from core.event_binding import RestQueue
from core.standard_converter.Scraper import Scraper
from layout.box_feature_maker.box_feature_maker import BoxFeatureMaker
from core.standard_converter.HTML2PDF import HTML2PDF
from core.standard_converter.PDF2ETC import PDF2ETC
from core.standard_converter.PDF2HTML import PDF2HTML
from core.standard_converter.Dict2Graph import Dict2Graph
from language.PredictionAlignment2Css import PredictionAlignment2Css
from core.pathant.PathAnt import PathAnt
from language.transformer.Pager import Pager
from language.transformer.UnPager import UnPager
from core.standard_converter.Tex2Pdf import Tex2Pdf
from layout.annotator import annotation, collection
from layout.training import training
from layout.upload_annotation.upload_annotation import UploadAnnotator
from layout.Layout2ReadingOrder import Layout2ReadingOrder

import os
from helpers.os_tools import file_exists_regex
from helpers.list_tools import metaize, forget_except
from config import config
import subprocess
from helpers.model_tools import find_best_model
from helpers.model_tools import model_in_the_loop

if not os.path.isdir(config.COLLECTION_PATH):
    os.makedirs(config.COLLECTION_PATH)
if not os.path.isdir(config.TEXT_BOX_MODEL_PATH):
    os.makedirs(config.TEXT_BOX_MODEL_PATH)

samples_files = os.listdir(config.COLLECTION_PATH)
n_samples = len(samples_files)
best_model_path, scores = find_best_model(config.TEXT_BOX_MODEL_PATH)
full_model_path = best_model_path
if scores:
    training_rate = int(scores.groups()[0]) / n_samples
else:
    training_rate = 0
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

sample_pipe = ant("feature", "annotation.collection", model_path=full_model_path)

model_pipe = ant(
    "annotation.corrected",
    "model",
    num_labels=config.NUM_LABELS,
    collection_step=training_rate,
)

upload_pipe = ant(
    "arxiv.org",
    "annotation.collection",
    via="upload_annotation",
    num_labels=config.NUM_LABELS,
    model_path=full_model_path,
    from_function_only=True,
)


def annotate_uploaded_file(path_to_pdf, service_id=None, url=None):
    logging.info(f"Working on {path_to_pdf} {service_id}")
    return next(
        forget_except(
            upload_pipe(metaize([path_to_pdf]), service_id=service_id, url=url),
            keys=["labels", "image", "image_path", "used_text_boxes"],
        ),
        None,
    )


UploadAnnotationQueueRest = RestQueue(
    update_data=changed_labels,
    service_id="upload_annotation",
    work_on_upload=annotate_uploaded_file,
)


def on_predict(args):
    gen = forget_except(
        sample_pipe(
            metaize(itertools.cycle(["http://export.arxiv.org/"])),
            model_path=args["best_model_path"],
            layout_model_path=["full_model_path"],
        ),
        keys=["html_path"],
    )
    return gen


def layout_annotate_train_model():
    model_in_the_loop(
        model_dir=config.TEXT_BOX_MODEL_PATH,
        collection_path=config.COLLECTION_PATH,
        on_train=lambda args: list(
            model_pipe(
                metaize(args["samples_files"]), collection_step=args["training_rate"]
            )
        ),
        service_id="gold_annotation",
        on_predict=on_predict,
    )


if __name__ == "__main__":
    layout_annotate_train_model()
