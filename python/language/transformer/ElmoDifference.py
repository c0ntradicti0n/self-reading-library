import os
from core import config
from layout.latex.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from helpers.cache_tools import file_persistent_cached_generator
from core.pathant.Converter import converter
from core.pathant.parallel import paraloop
from core.pathant.PathAnt import PathAnt
from core.event_binding import RestQueue
from helpers.model_tools import model_in_the_loop
from helpers.list_tools import metaize
from layout.annotation_thread import full_model_path
from language.transformer.ElmoDifferenceTrain import ElmoDifferenceTrain
from language.transformer.ElmoDifferencePredict import ElmoDifferencePredict
from allennlp_models.tagging.models import crf_tagger


@converter('css.difference', "elmo.css_html.difference")
class ElmoDifference(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @file_persistent_cached_generator(config.cache + os.path.basename(__file__) + '.json', if_cache_then_finished=True)
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (css_str, meta) in enumerate(labeled_paths):

            html_path = meta['html_path']
            output_html_path = html_path + ".difference.html"
            with open(html_path, errors="ignore") as f:
                content = f.read()
            content = content.replace("</head>", f"<style>\n{css_str}\n</style>\n</head>")
            with open(output_html_path, "w") as f:
                f.write(content)

            if "chars_and_char_boxes" in meta:
                del meta['chars_and_char_boxes']

            yield output_html_path, meta



ant = PathAnt()

elmo_difference_pipe = ant(
    "arxiv.org", f"elmo.css_html.difference", via='prediction',
    num_labels=config.NUM_LABELS,
    layout_model_path = full_model_path
)

elmo_difference_model_pipe = ant(
    None, f"elmo_model.difference",
    layout_model_path = full_model_path

)

def annotate_uploaded_file(file):
    return elmo_difference_pipe(metaize(file))

ElmoDifferenceQueueRest = RestQueue(
    service_id="elmo_difference",
    work_on_upload=annotate_uploaded_file
)

def annotate_difference_elmo():
    model_in_the_loop(
        model_dir=config.ELMO_DIFFERENCE_MODEL_PATH,
        collection_path=config.ELMO_DIFFERENCE_COLLECTION_PATH,
        on_train=lambda args:
        list(
            elmo_difference_model_pipe(metaize(args['samples_files']),
                       collection_step=args['training_rate']
                       )
        ),

        on_predict=lambda args: list(
            zip(
                *list(
                    elmo_difference_pipe(
                        "????",
                        difference_model_path=args['best_model_path'])
                )
            )
        ),
        training_rate_mode='size',
        training_rate_file=config.ELMO_DIFFERENCE_COLLECTION_PATH + "/train_over.conll3"
    )
