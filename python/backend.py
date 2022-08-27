import itertools
import logging
from wsgiref import simple_server
import threading

from config import config
from config.ant_imports import *


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


def run_extra_threads():
    from layout.annotation_thread import layout_annotate_train_model
    ant = PathAnt()

    filling_pipe = ant(
        "arxiv.org", f"reading_order",
        num_labels=config.NUM_LABELS,
        layout_model_path=full_model_path
    )

    ant.info("workflow.png",
             pipelines_to_highlight=[
                 elmo_difference_pipe,
                 sample_pipe,
                 model_pipe,
                 upload_pipe,
                 elmo_difference_model_pipe,
                 filling_pipe
             ]
             )

    layout = threading.Thread(target=layout_annotate_train_model, name="layout_captcha")
    layout.start()
    difference_elmo = threading.Thread(target=annotate_difference_elmo, name="difference_captcha")
    difference_elmo.start()


    def fill_library():
        x = None
        while not x:

            try:
                gen = forget_except(filling_pipe(itertools.islice((
                    metaize(["pdfs"] * 200)
                ), 200)), keys=["html_path"])
                for i in range(100):
                    k = next(gen, None)
                    del k
                break
            except Exception:
                logging.error("Getting first 100 threw", exc_info=True)
                break

    threading.Thread(target=fill_library, name="fill library").start()


def create_app():
    import falcon
    logging.info(f"STARTING APP")

    from language.transformer.ElmoDifference import ElmoDifferenceQueueRest

    from core.rest.LayoutPublisher import LayoutPublisher

    publishing = {
        '/ant':
            AntPublisher,

        # difference
        '/difference_captcha':
            ElmoDifferenceQueueRest,
        '/difference/{id}':
            ElmoDifferenceQueueRest,
        '/difference':
            DifferencePublisher,
        '/difference_annotation':
            DifferenceAnnotationPublisher,

        # topics
        '/library':
            TopicsPublisher,

        # layout
        '/annotation_captcha':
            AnnotationQueueRest,
        '/upload_annotation/{id}':
            UploadAnnotationQueueRest,
        '/layout': LayoutPublisher,

        # audiobook
        '/audiobook':
            AudioPublisher,
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

    from falcon_multipart.middleware import MultipartMiddleware

    api = falcon.App(middleware=[
        cors.middleware,
        MultipartMiddleware()])

    for route, module in publishing.items():
        api.add_route(route, module)

    run_extra_threads()
    logging.info(f"API: {api}")
    return api


if __name__ == "__main__":
    # os.system(f"kill $(lsof -t -i:{PORT}) || echo 'no running process on our port {PORT}, no killing needed'")

    api = create_app()

    logging.debug(get_all_routes(api))

    httpd = simple_server.make_server('0.0.0.0', config.PORT, api)
    httpd.serve_forever()
