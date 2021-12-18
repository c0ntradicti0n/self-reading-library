import os
from core import config
from layout.latex.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from helpers.cache_tools import file_persistent_cached_generator
from core.pathant.Converter import converter
from core.pathant.parallel import paraloop
from core.pathant.PathAnt import PathAnt
from core.event_binding import RestQueue



@converter('css.difference', "elmo.css_html.difference")
class ElmoDifference(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.debug = debug

    @file_persistent_cached_generator(config.cache + os.path.basename(__file__) + '.json', if_cache_then_finished=True)
    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (pdf_path, meta) in enumerate(labeled_paths):
            html_path = pdf_path + outputs['html']
            wordi_path = pdf_path + "." + outputs['wordi']
            feat_path = pdf_path + "." + outputs['feat']

            self.logger.warning(f"working on {pdf_path}")
            self.pdf2htmlEX(pdf_path, html_path)

            meta['pdf2htmlEX.html'] = html_path
            meta['pdf_path'] =  pdf_path
            meta['wordi_path'] = wordi_path
            meta['feat_path'] = feat_path

            yield (html_path, wordi_path, feat_path), meta



ant = PathAnt()

elmo_difference_pipe = ant(
    "pdf", "elmo.css_html.difference",
    num_labels=config.NUM_LABELS,
    via='annotation'
)

def annotate_uploaded_file(file):
    return elmo_difference_pipe(metaize(file))

ElmoDifferenceQueueRest = RestQueue(
    service_id="elmo_difference",
    work_on_upload=annotate_uploaded_file
)