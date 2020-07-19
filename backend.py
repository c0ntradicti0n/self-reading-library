from time import sleep

import falcon
import logging

from RestPublisher.PublishHtmls import MarkupPublisher

logging.basicConfig()

logging.getLogger().setLevel(logging.INFO)

api = application = falcon.API()

publishing = {
    '/content': MarkupPublisher,
    #'readmarkup':  RestPublisher("readmarkup"),
    #'commands':  RestPublisher("commands")
}

if __name__ ==  "__main__":
    import subprocess
    import sys
    import os

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(logging.INFO)



    # start react app and proceed
    os.chdir("layout_viewer_made")
    os.popen("yarn dev")
    os.chdir("../")


    while True:
        try:
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(["gunicorn",  "--reload", "backend:api"], stdout=sys.stdout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            sleep(10)
