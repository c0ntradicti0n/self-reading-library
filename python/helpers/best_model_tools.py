import os

import regex


model_regex = r"(?P<shape>\d+)_(?P<f1>0,?\d*)_(?P<epoch>\d+)"
import logging


def find_best_model(model_dir, condition=None):
    try:
        models = os.listdir(model_dir)
        if condition:
            models = [m for m in models if condition(model_dir + "/" + m)]
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

        logging.debug(f"{scores=} {best_model_path =}")
        return best_model_path, scores
    except Exception as e:
        logging.error("Error finding model " + str(e))
        return [None, None]


if __name__ == "__main__":
    from config import config

    print(
        find_best_model(
            config.ELMO_DIFFERENCE_MODEL_PATH,
            lambda path: os.path.exists(path + "/vocabulary"),
        )
    )

    print(find_best_model(config.TEXT_BOX_MODEL_PATH))
