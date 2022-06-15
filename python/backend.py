import itertools
import os
from pprint import pprint
from time import sleep
import logging
from falcon_multipart.middleware import MultipartMiddleware
from wsgiref import simple_server
import threading
from core import config
from core.RestPublisher.DifferencePublisher import DifferencePublisher
from core.StandardConverter import PATH2HTML
from core.config import PORT
from core.pathant.PathAnt import PathAnt

from core.pathant.AntPublisher import AntPublisher
from core.pathant.ConfigRest import ConfigRest
from core.layout_eagle import LayoutEagle
from core.StandardConverter.Scraper import Scraper
from core.StandardConverter.HTML2PDF import HTML2PDF
from core.StandardConverter.PDF2HTML import PDF2HTML
from helpers.list_tools import metaize, forget_except
from helpers.model_tools import TRAINING_RATE
from topics.TopicsPublisher import TopicsPublisher

from layout.annotator.annotation import Annotator, AnnotationQueueRest
from layout.upload_annotation.upload_annotation import UploadAnnotator
from layout.upload_annotation.upload_annotation import UploadAnnotator
from layout.annotation_thread import layout_annotate_train_model, UploadAnnotationQueueRest, sample_pipe, model_pipe, \
    upload_pipe, full_model_path
from language.PredictionAlignment2Css import PredictionAlignment2Css
from layout.Layout2ReadingOrder import Layout2ReadingOrder
from language.transformer.ElmoDifference import ElmoDifference, ElmoDifferenceQueueRest, elmo_difference_pipe, \
    elmo_difference_model_pipe, annotate_difference_elmo


#from language.heuristic.heuristic_difference import HeurisiticalLogician

from hanging_threads import start_monitoring
monitoring_thread = start_monitoring(seconds_frozen=30, test_interval=1000)


def get_all_routes(api):
    routes_list = []

    def get_children(node):
        if len(node.children):
            for child_node in node.children:
                get_children(child_node)
        else:
            routes_list.append((node.uri_template, node.resource))

    [get_children(node) for node in api._router._roots]
    return routes_list


def create_app():
    # from topics.TopicsPublisher import TopicsPublisher

    from language.transformer.ElmoDifference import ElmoDifferenceQueueRest
    import falcon
    import threading
    from core.RestPublisher.LayoutPublisher import LayoutPublisher
    from layout.annotation_thread import layout_annotate_train_model

    publishing = {
        '/ant':
            AntPublisher,

        # difference
        '/difference':
            ElmoDifferenceQueueRest,
        '/difference/{id}':
            ElmoDifferenceQueueRest,

        # topics
        '/library':
            TopicsPublisher,

        # layout
        '/annotation/{id}':
            AnnotationQueueRest,
        '/upload_annotation/{id}':
            UploadAnnotationQueueRest,
    }

    from falcon_cors import CORS

    cors = CORS(
        allow_origins_list=['*'],
        allow_all_origins=True,
        allow_all_headers=True,
        allow_credentials_all_origins=True,
        allow_all_methods=falcon.HTTP_METHODS,
        log_level="DEBUG"
    )

    os.system(f"kill $(lsof -t -i:{PORT}) || echo 'no running process on our port {PORT}, no killing needed'")

    api = falcon.App(middleware=[
        cors.middleware,
        MultipartMiddleware()])

    for route, module in publishing.items():
        api.add_route(route, module)

    return api


if __name__ == "__main__":
    api = create_app()

    logging.debug(get_all_routes(api))

    ant = PathAnt()

    filling_pipe = ant(
        "arxiv.org", f"reading_order",
        num_labels=config.NUM_LABELS,
        layout_model_path=full_model_path
    )

    ant.info("workflow.png", pipelines_to_highlight=[
        elmo_difference_pipe,
        sample_pipe,
        model_pipe,
        upload_pipe,
        elmo_difference_model_pipe,
        filling_pipe
    ]
             )

    layout = threading.Thread(target=layout_annotate_train_model, name="layout")
    layout.start()
    difference_elmo = threading.Thread(target=annotate_difference_elmo, "difference")
    difference_elmo.start()
    """difference_sokrates = threading.Thread(target=annotate_difference_sokrates)
    difference_sokrates.start()
    difference_gpt3 = threading.Thread(target=write_difference_gpt3)
    difference_gpt3.start()"""


    def fill_library():
        x = None
        while not x:
            try:
                x = list(forget_except(filling_pipe(itertools.islice((
                    metaize(itertools.cycle(["http://export.arxiv.org/"]))
                ), 100)), keys=["html_path"])),
            except Exception:
                logging.error("Getting first 100 threw", exc_info=True)
                raise


    fill_library_thread = threading.Thread(target=fill_library, name="fill library").start()

    httpd = simple_server.make_server('0.0.0.0', PORT, api)
    httpd.serve_forever()
