from time import sleep

import falcon

from RestPublisher.PublishHtmls import MarkupPublisher


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


    # start react app and proceed
    os.chdir("layout_viewer")
    os.popen("npm start")
    os.chdir("../")

    while True:
        try:
            # start the resource server with gunicorn, that it can recompile, when changed
            subprocess.check_call(["gunicorn",  "--reload", "backend:api"], stdout=sys.stdout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            sleep(10)
