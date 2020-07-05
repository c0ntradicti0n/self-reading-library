import logging
import os
import subprocess
import sys


class react:
    def __init__(self, *args, npm_project = "./layout_viewer", npm_resources = "resources", **kwargs):
        self.npm_project = npm_project
        self.npm_resources = r"/".join([npm_project, npm_resources])

        if not os.path.isdir(npm_project):

            try:
                subprocess.check_call(["npm", "init", "react-app", npm_project, "-y"], stdout=sys.stdout,
                                      stderr=subprocess.STDOUT)

                subprocess.check_call(["npm", "install", "esm-node", "esm"], stdout=sys.stdout,
                                      stderr=subprocess.STDOUT)
                subprocess.check_call(["npm", "install", "--save-dev", "ts-hybrid-esm-build"], stdout=sys.stdout,
                                      stderr=subprocess.STDOUT)

                os.mkdir(self.npm_resources)
            except Exception as e:
                logging.error(e)





    def __call__(self, *args, **kwargs):
        print (args, kwargs)
