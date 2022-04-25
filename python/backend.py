from pprint import pprint
from time import sleep
import logging
from falcon_multipart.middleware import MultipartMiddleware
from wsgiref import simple_server


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


    # from language.topics.TopicsPublisher import TopicsPublisher

    import falcon
    import threading
    from core.RestPublisher.LayoutPublisher import LayoutPublisher
    from layout.annotation_thread import annotate_train_model

    publishing = {
        '/latex': LayoutPublisher,
        '/elmo_difference': ElmoDifferenceQueueRest,

        # '/topics': TopicsPublisher,
        '/ant': AntPublisher,
        '/cache': CachePublisher,
        '/annotation/{id}': AnnotationQueueRest,
        '/upload_annotation/{id}': UploadAnnotationQueueRest,

        '/config': ConfigRest,
    }

    le = LayoutEagle()
    #le.test_info()

    from falcon_cors import CORS

    cors = CORS(
        allow_origins_list=['*'],
        allow_all_origins=True,
        allow_all_headers=True,
        allow_all_methods=True,
    )


    api = falcon.App(middleware=[ cors.middleware, MultipartMiddleware()])

    for route, module in publishing.items():
        api.add_route(route, module)

    return  api

if __name__ == "__main__":
    import threading
    from traceback_with_variables import activate_by_import

    from core.pathant.PathAnt import PathAnt
    from controlflow import CachePublisher

    from core.RestPublisher.DifferencePublisher import DifferencePublisher
    from core.pathant.AntPublisher import AntPublisher
    from core.pathant.ConfigRest import ConfigRest
    from core.layout_eagle import LayoutEagle
    from core.StandardConverter.ScienceTexScraper.scrape import ScienceTexScraper
    from core.StandardConverter.HTML2PDF import HTML2PDF
    from core.StandardConverter.PDF2HTML import PDF2HTML

    from layout.annotator.annotation import Annotator, AnnotationQueueRest
    from layout.upload_annotation.upload_annotation import UploadAnnotator
    from layout.upload_annotation.upload_annotation import UploadAnnotator
    from layout.annotation_thread import annotate_train_model, UploadAnnotationQueueRest, sample_pipe, model_pipe, upload_pipe

    from language.layout2reading_order import Layout2ReadingOrder
    from language.transformer.ElmoDifference import ElmoDifference, ElmoDifferenceQueueRest, elmo_difference_pipe, elmo_difference_model_pipe, annotate_difference_elmo
    #from language.heuristic.heuristic_difference import HeurisiticalLogician

    api = create_app()

    pprint(get_all_routes(api))

    ant = PathAnt()

    ant.info("workflow.png", pipelines_to_highlight=[
        elmo_difference_pipe,
        sample_pipe,
        model_pipe,
        upload_pipe,
        elmo_difference_model_pipe
    ]
    )


    layout = threading.Thread(target=annotate_train_model)
    layout.start()
    difference_elmo = threading.Thread(target=annotate_difference_elmo)
    difference_elmo.start()
    """difference_sokrates = threading.Thread(target=annotate_difference_sokrates)
    difference_sokrates.start()
    difference_gpt3 = threading.Thread(target=write_difference_gpt3)
    difference_gpt3.start()"""


    #httpd = simple_server.make_server('127.0.0.1', 7789, api)
    print("http://127.0.0.1:8000")
    #httpd.serve_forever()


