from allennlp.common import Params
from allennlp.predictors import Predictor
from texttable import Texttable
from core.pathant.PathSpec import PathSpec
from allennlp.models.model import Model
from language.transformer.difference_predictor.difference_predictor import DifferenceTaggerPredictor
import language.transformer.attentivecrftagger.attentivecrftagger
import os
import subprocess
import sys


class ElmoTrain(PathSpec):
    def __init__(self, *args, elmo_config=None, train_output_dir, **kwargs):
        super().__init__(*args, **kwargs)
        self.elmo_config = elmo_config

    def __call__(self, feature_meta, *args, **kwargs):
        try:

            cmd_parts = ["./language/transformer/do/train_difference_cp.sh", self.elmo_config]
            print(" ".join(cmd_parts))
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(cmd_parts,
                                  stdout=sys.stdout, stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            sleep(10)
