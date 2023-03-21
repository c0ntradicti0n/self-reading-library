import os

import regex


model_regex = r"(?P<shape>\d+)_(?P<f1>0,?\d*)_(?P<epoch>\d+)"
import logging


def find_best_model(model_dir):
    models = os.listdir(model_dir)
    try:
        best_model_path, scores = max(
            [
                (model_dir + "/" + p, next(m, regex.match(model_regex, "0_0,0_0")))
                for p in models
                if (m := regex.finditer(model_regex, p))
            ],
            key=lambda t: t[1] and float(t[1][0].replace(",", ".")),
        )
    except ValueError:
        logging.warning(f"No models found in {model_dir}")
        return None, None

    logging.info(f"{scores=} {best_model_path =}")
    return best_model_path, scores
