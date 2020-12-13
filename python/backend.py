from time import sleep

import falcon

import logging

from python.layouteagle.pathant.PathAnt import PathAnt

logging.basicConfig()

logging.getLogger().setLevel(logging.INFO)

if __name__ ==  "__main__":
    import subprocess
    import sys
    import os

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(logging.INFO)

    # start react app and proceed
    os.chdir("../react/layout_viewer_made")
    # os.popen("yarn dev")
    os.chdir("../../python")


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

    from python.layouteagle.RestPublisher.MarkupPublisher import MarkupPublisher
    from python.layouteagle.pathant.AntPublisher import AntPublisher
    from python.nlp.Topics.TopicsPublisher import TopicsPublisher
    from python.layouteagle.LayoutEagle import LayoutEagle

    publishing = {
        '/markup': MarkupPublisher,
        '/topics': TopicsPublisher,
        '/ant': AntPublisher
        # 'commands':  RestPublisher("commands")
    }

    le = LayoutEagle()
    le.test_info()


    from falcon_cors import CORS

    cors = CORS(
        allow_all_origins=True,
        allow_all_headers=True,
        allow_all_methods=True,
    )

    api = falcon.API(middleware=[cors.middleware])

    for route, module in publishing.items():
        api.add_route(route, module)

