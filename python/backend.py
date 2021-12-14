from pprint import pprint
from time import sleep
import falcon
import logging
from falcon_multipart.middleware import MultipartMiddleware
from wsgiref import simple_server

from layouteagle.RestPublisher.LayoutPublisher import LayoutPublisher


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

    from layouteagle.RestPublisher.DifferencePublisher import DifferencePublisher
    from layouteagle.pathant.AntPublisher import AntPublisher
    from layouteagle.pathant.ConfigRest import ConfigRest

    from controlflow import CachePublisher
    from dataset_workflow.annotator.annotation import Annotator, AnnotationQueueRest
    from dataset_workflow.upload_annotation.upload_annotation import UploadAnnotator
    from layouteagle.LayoutEagle import LayoutEagle
    from dataset_workflow.annotation_thread import annotate_train_model, UploadAnnotationQueueRest
    import threading
    from traceback_with_variables import activate_by_import

    # from nlp.Topics.TopicsPublisher import TopicsPublisher

    publishing = {
        '/layout': LayoutPublisher,
        '/difference': DifferencePublisher,
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

    api = create_app()

    pprint(get_all_routes(api))

    #t = threading.Thread(target=annotate_train_model)
    #t.start()

    httpd = simple_server.make_server('127.0.0.1', 7789, api)
    print("http://127.0.0.1:8000")
    httpd.serve_forever()


