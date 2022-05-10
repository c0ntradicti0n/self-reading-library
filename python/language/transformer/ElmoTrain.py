import logging

from allennlp.common import Params
from allennlp.predictors import Predictor
from texttable import Texttable
from core import config
from core.pathant.PathSpec import PathSpec
from allennlp.models.model import Model
from language.transformer.difference_predictor.difference_predictor import DifferenceTaggerPredictor
import os
import subprocess
import sys


class ElmoTrain(PathSpec):
    def __init__(self, *args, elmo_config=None, train_output_dir, collection_path, **kwargs):
        super().__init__(*args, **kwargs)
        self.elmo_config = elmo_config
        self.train_output_dir = train_output_dir
        self.collection_path = collection_path

    def __call__(self, feature_meta, *args, **kwargs):
        try:
            train_size = os.path.getsize(f"{self.collection_path}/train_over.conll3")
            path = f"{config.ELMO_DIFFERENCE_MODEL_PATH}/{train_size}_0_0"

            cmd_parts = ["./language/transformer/do/train_difference_cp.sh", self.elmo_config, path]
            print(" ".join(cmd_parts))
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(cmd_parts,
                                  stdout=sys.stdout, stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            print(os.getcwd())
            logging.error("Training of Elmo model failed", exc_info=True)
