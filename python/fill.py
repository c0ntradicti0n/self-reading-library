import threading

import config.config
from config.ant_imports import *
from helpers.time_tools import wait_for_change


def run_extra_threads():
    from layout.annotation_thread import layout_annotate_train_model

    ant = PathAnt()
    gold_annotation = ant("annotation.collection", "annotation.collection.fix")
    gold_span_annotation = ant(
        "span_annotation.collection", "span_annotation.collection.fix"
    )

    def fill_annotation_thread():
        while True:
            gen = gold_annotation(metaize(["x"] * 100), service_id="gold_annotation")
            # suck 1 item from it and then restart to reload cache
            list(itertools.islice(gen, 1))

    threading.Thread(target=fill_annotation_thread, name="gold_annotation").start()

    def fill_span_annotation_thread():
        while True:
            gen = gold_span_annotation(
                metaize(["x"] * 100), service_id="gold_span_annotation"
            )
            # suck 1 item from it and then restart to reload cache
            list(itertools.islice(gen, 1))

    threading.Thread(
        target=fill_span_annotation_thread, name="gold_span_annotation"
    ).start()

    def update_knowledge_graph_thread():
        path = config.GOLD_DATASET_PATH + "/" + config.GOLD_SPAN_ID

        def graph_db_update():
            result = list(
                ant(
                    "span_annotation.collection.fix",
                    "span_annotation.collection.graph_db",
                )([metaize([None])], service_id=config.GOLD_SPAN_ID)
            )
            assert result

        wait_for_change(path, graph_db_update, on_first=True)

    threading.Thread(target=update_knowledge_graph_thread, name="knowledge").start()

    def update_topics_thread():
        path = config.tex_data

        def topics_update():
            result = list(
                zip(*list(ant("arxiv.org", "topics.graph", from_cache_only=True)([])))
            )
            assert result

        wait_for_change(path, topics_update)

    threading.Thread(target=update_topics_thread, name="topics").start()



    def update_all_documents():
        path = config.tex_data

        def update():
            result = list(
                zip(*list(ant("arxiv.org", "recompute", from_cache_only=True)([])))
            )
            assert result

        wait_for_change(path, update)

    threading.Thread(target=update_all_documents, name="topics").start()

if __name__ == "__main__":
    run_extra_threads()

    # Cristian Ciupitu @ https://stackoverflow.com/a/50218501
    for thread in threading.enumerate():
        try:
            thread.join()
        except RuntimeError:
            # trying to join the main thread, which would create a deadlock (see https://docs.python.org/3/library/threading.html#threading.Thread.join for details)
            pass
