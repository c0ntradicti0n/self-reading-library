import threading

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
    gold_annotation = ant("annotation.collection", "annotation.collection.fix")
    gold_span_annotation = ant(
        "span_annotation.collection", "span_annotation.collection.fix"
    )

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
        while True:
            gen = gold_annotation(metaize(["x"] * 100), service_id="gold_annotation")
            # suck 5 items from it and then restart to reload cache
            list(itertools.islice(gen, 5))

    threading.Thread(target=fill_annotation_thread, name="gold annotation").start()

    def fill_span_annotation_thread():
        while True:
            gen = gold_span_annotation(
                metaize(["x"] * 100), service_id="gold_span_annotation"
            )
            # suck 5 items from it and then restart to reload cache
            list(itertools.islice(gen, 5))

    threading.Thread(target=fill_span_annotation_thread, name="gold annotation").start()


if __name__ == "__main__":
    run_extra_threads()

    # Cristian Ciupitu @ https://stackoverflow.com/a/50218501
    for thread in threading.enumerate():
        try:
            thread.join()
        except RuntimeError:
            # trying to join the main thread, which would create a deadlock (see https://docs.python.org/3/library/threading.html#threading.Thread.join for details)
            pass
