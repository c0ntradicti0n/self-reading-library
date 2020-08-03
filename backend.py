from pprint import pprint
from time import sleep

import falcon
import logging

from RestPublisher.PublishHtmls import MarkupPublisher
from Topics.Topics import Topics
from layouteagle.LayoutEagle import LayoutEagle

logging.basicConfig()

logging.getLogger().setLevel(logging.INFO)

api = application = falcon.API()

publishing = {
    '/markup': MarkupPublisher,
    '/topics':  Topics,
    #'commands':  RestPublisher("commands")
}

le = LayoutEagle()
le.test_info()

for route, module in publishing.items():
    api.add_route(route, module)

if __name__ ==  "__main__":
    import subprocess
    import sys
    import os

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(logging.INFO)



    # start react app and proceed
    os.chdir("layout_viewer_made")
    # os.popen("yarn dev")
    os.chdir("../")


    while True:
        try:
            cmd_parts = ["gunicorn", "--reload", "backend:api", "-b", "127.0.0.1:6666"]
            print(" ".join(cmd_parts))
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(cmd_parts,
                                  stdout=sys.stdout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            sleep(10)
