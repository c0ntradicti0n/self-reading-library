import os
from core.pathant.PathSpec import PathSpec
from config import config
from helpers.cache_tools import configurable_cache
from core.pathant.Converter import converter
from core.pathant.PathAnt import PathAnt
from core.event_binding import RestQueue, queue_put
from helpers.json_tools import json_file_update
from helpers.model_tools import model_in_the_loop, BEST_MODELS
from helpers.list_tools import metaize, forget_except
from layout.annotation_thread import full_model_path
from language.transformer.ElmoDifferenceTrain import ElmoDifferenceTrain
from language.transformer.ElmoDifferencePredict import ElmoDifferencePredict
from allennlp_models.tagging.models import crf_tagger


@converter("css.difference", "elmo.css_html.difference")
class ElmoDifference(PathSpec):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @configurable_cache(filename=config.cache + os.path.basename(__file__))
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

elmo_difference_pipe = ant(
    "arxiv.org",
    f"elmo.html",
    via="reading_order",
    num_labels=config.NUM_LABELS,
    layout_model_path=full_model_path,
)

elmo_difference_single_pipe = ant(
    "arxiv.org",
    f"elmo.html",
    num_labels=config.NUM_LABELS,
    layout_model_path=full_model_path,
    from_function_only=True,
)

elmo_difference_model_pipe = ant(
    None, f"elmo_model.difference", layout_model_path=full_model_path
)


def annotate_uploaded_file(file, service_id, url):
    BEST_MODELS = json_file_update(config.BEST_MODELS_PATH)

    result = forget_except(
        [
            next(
                elmo_difference_single_pipe(
                    metaize(
                        [file],
                    ),
                    difference_model_path=BEST_MODELS["difference"]["best_model_path"],
                    service_id=service_id,
                    url=url,
                ),
                None,
            )
        ],
        keys=["css"],
    )
    queue_put(service_id, result)
    return result


ElmoDifferenceQueueRest = RestQueue(
    service_id="difference", work_on_upload=annotate_uploaded_file
)


def on_predict(args):
    gen = forget_except(
        elmo_difference_pipe(
            metaize(["http://export.arxiv.org/"] * 100),
            difference_model_path=args["best_model_path"],
            service_id="difference",
        ),
        keys=["html_path", "css", "html"],
    )
    return gen


def annotate_difference_elmo():
    model_in_the_loop(
        model_dir=config.ELMO_DIFFERENCE_MODEL_PATH,
        collection_path=config.ELMO_DIFFERENCE_COLLECTION_PATH,
        on_train=lambda args: list(
            elmo_difference_model_pipe(
                metaize(args["samples_files"]), collection_step=args["training_rate"]
            )
        ),
        service_id="difference",
        on_predict=on_predict,
        training_rate_mode="size",
        training_rate_file=config.ELMO_DIFFERENCE_COLLECTION_PATH
        + "/train_over.conll3",
    )
