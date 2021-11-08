from pprint import pprint
from time import sleep
import falcon
import logging

from layouteagle.RestPublisher.LayoutPublisher import LayoutPublisher


if __name__ == "__main__":
    import subprocess
    import sys

    while True:
        try:
            cmd_parts = ["gunicorn", "--reload", "backend:api", "-b", "127.0.0.1:7789",
                         "-t", "90000"]
            print(" ".join(cmd_parts))
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(cmd_parts,
                                  stdout=sys.stdout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            sleep(10)

else:
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

    from layouteagle.RestPublisher.DifferencePublisher import DifferencePublisher
    from layouteagle.pathant.AntPublisher import AntPublisher
    # from nlp.Topics.TopicsPublisher import TopicsPublisher
    from controlflow import CachePublisher
    from dataset_workflow.annotator.annotation import Annotator, AnnotationRest
    from layouteagle.LayoutEagle import LayoutEagle
    from dataset_workflow.test_workflow import annotate_train_model
    import threading
    from traceback_with_variables import activate_by_import

    publishing = {
        '/layout': LayoutPublisher,
        '/difference': DifferencePublisher,
        # '/topics': TopicsPublisher,
        '/ant': AntPublisher,
        '/cache': CachePublisher,
        '/annotation/{id}':  AnnotationRest
    }

    le = LayoutEagle()
    #le.test_info()

    from falcon_cors import CORS

    cors = CORS(
        allow_all_origins=True,
        allow_all_headers=True,
        allow_all_methods=True,
    )

    api = falcon.API(middleware=[cors.middleware])

    for route, module in publishing.items():
        api.add_route(route, module)

    pprint(get_all_routes(api))

    t = threading.Thread(target=annotate_train_model)
    t.start()


