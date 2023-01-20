import logging

import os
import subprocess
import sys

from config import config
from core.pathant.PathSpec import PathSpec
from helpers.conll_tools import conll_concat_train_valid


class ElmoTrain(PathSpec):
    def __init__(
        self, *args, elmo_config=None, train_output_dir, collection_path, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.elmo_config = elmo_config
        self.train_output_dir = train_output_dir
        self.collection_path = collection_path



    def on_train(self, samples_files, training_rate):
        from core.pathant.PathAnt import PathAnt
        from helpers.list_tools import metaize

        ant = PathAnt()
        elmo_difference_model_pipe = ant(
            None, f"elmo_model.difference"
        )
        elmo_difference_model_pipe(
            metaize(samples_files), collection_step=training_rate
        )

    def __call__(self, feature_meta, *args, **kwargs):
        try:
            conll_concat_train_valid(self.on)
            path = f"{config.ELMO_DIFFERENCE_MODEL_PATH}/" +str (self.flags["collection_step"]) + "_0_0"
            self.service_config = self.elmo_config.replace('elmo', self.service_id)
            os.system(f"cp {self.elmo_config} {self.service_config}")
            os.system(f"""jq '.train_data_path = "{config.GOLD_SPAN_SET}/train.conll"' {self.service_config} | sponge {self.service_config}""")
            os.system(f"""jq '.validation_data_path = "{config.GOLD_SPAN_SET}/valid.conll"' {self.service_config} | sponge {self.service_config}""")

            cmd_parts = [
                "./language/transformer/do/train_difference_cp.sh",
                self.service_config,
                path,
            ]
            self.logger.info(" ".join(cmd_parts))
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(
                cmd_parts, stdout=sys.stdout, stderr=subprocess.STDOUT
            )

        except subprocess.CalledProcessError as e:
            logging.error("Training of Elmo model failed", exc_info=True)
