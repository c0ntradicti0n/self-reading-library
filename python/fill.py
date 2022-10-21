import itertools
import logging
import threading
from config import config
from config.ant_imports import *


def run_extra_threads():
    from layout.annotation_thread import layout_annotate_train_model

    ant = PathAnt()

    filling_pipe = ant(
        "arxiv.org",
        f"reading_order",
        num_labels=config.NUM_LABELS,
        layout_model_path=full_model_path,
    )
    gold_annotation = ant("annotation.collection", "annotation.collection.platinum")

    layout = threading.Thread(target=layout_annotate_train_model, name="layout_captcha")
    layout.start()
    difference_elmo = threading.Thread(
        target=annotate_difference_elmo, name="difference_captcha"
    )
    difference_elmo.start()

    def fill_library():
        x = None
        while not x:

            try:
                gen = forget_except(
                    filling_pipe(itertools.islice((metaize(["pdfs"] * 200)), 200)),
                    keys=["html_path"],
                )
                for i in range(100):
                    k = next(gen, None)
                    del k
                break
            except Exception:
                logging.error("Getting first 100 threw", exc_info=True)
                break

    threading.Thread(target=fill_library, name="fill library").start()

    def fill_annotation_thread():
        gen = gold_annotation(metaize(["x"] * 100), service_id="gold_annotation")
        list(gen)

    threading.Thread(target=fill_annotation_thread, name="layout_gold").start()


if __name__ == "__main__":
    run_extra_threads()
