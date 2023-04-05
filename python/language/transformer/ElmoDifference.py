import os
from core.pathant.PathSpec import PathSpec
from config import config
from helpers.cache_tools import configurable_cache
from core.pathant.Converter import converter
from core.pathant.PathAnt import PathAnt
from core.event_binding import RestQueue
from helpers.model_tools import model_in_the_loop
from helpers.list_tools import metaize, forget_except
from language.transformer.ElmoPredict import find_best_tagger_model
from layout.annotation_thread import full_model_path
from language.transformer.ElmoDifferenceTrain import ElmoDifferenceTrain
from language.transformer.ElmoDifferencePredict import ElmoDifferencePredict


@converter("css.difference", "elmo.css_html.difference")
class ElmoDifference(PathSpec):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    cache_folder = config.cache + os.path.basename(__file__)

    @configurable_cache(filename=cache_folder)
    def __call__(self, labeled_paths, *args, **kwargs):

        try:
            for doc_id, (_pdf_path, meta) in enumerate(labeled_paths):
                css_str = meta["css"]
                html_path = meta["html_path"]
                output_html_path = html_path + ".difference.html"
                with open(html_path, errors="ignore") as f:
                    content = f.read()
                content = content.replace(
                    "</head>", f"<style>\n{css_str}\n</style>\n</head>"
                )
                with open(output_html_path, "w") as f:
                    f.write(content)

                if "chars_and_char_boxes" in meta:
                    del meta["chars_and_char_boxes"]

                yield _pdf_path, meta
        except StopIteration as e:
            raise e


ant = PathAnt()


def annotate_uploaded_file(file, service_id, url, dont_save=False):
    elmo_difference_single_pipe = ant(
        "arxiv.org",
        f"elmo.html",
        num_labels=config.NUM_LABELS,
        layout_model_path=full_model_path,
        from_function_only=True,
    )
    result = next(
        forget_except(
            [
                next(
                    elmo_difference_single_pipe(
                        metaize(
                            [file],
                        ),
                        difference_model_path=find_best_tagger_model(),
                        service_id=service_id,
                        url=url,
                        dont_save=dont_save,
                    ),
                    None,
                )
            ],
            keys=["css"],
        )
    )

    return result


ElmoDifferenceQueueRest = RestQueue(
    service_id="difference", work_on_upload=annotate_uploaded_file
)


def on_predict(args, service_id=None):
    elmo_difference_pipe = ant(
        "arxiv.org",
        f"elmo.html",
        via="reading_order",
        num_labels=config.NUM_LABELS,
        layout_model_path=full_model_path,
    )

    gen = forget_except(
        elmo_difference_pipe(
            metaize(["http://export.arxiv.org/"] * 100),
            difference_model_path=args["best_model_path"],
            service_id=service_id,
        ),
        keys=["html_path", "css", "html"],
    )
    return gen


def annotate_difference_elmo():
    elmo_difference_model_pipe = ant(
        None, f"elmo_model.difference", layout_model_path=full_model_path
    )
    model_in_the_loop(
        model_dir=config.ELMO_DIFFERENCE_MODEL_PATH,
        collection_path=config.ELMO_DIFFERENCE_COLLECTION_PATH,
        on_train=lambda args: list(
            elmo_difference_model_pipe(
                metaize(args["samples_files"]), collection_step=args["training_rate"]
            )
        ),
        service_id="difference",
        trigger_service="gold_span_annotation",
        on_predict=on_predict,
        training_rate_mode="ls",
        training_rate_file=config.ELMO_DIFFERENCE_COLLECTION_PATH
        + "/train_over.conll3",
    )
