import logging
import os
import subprocess
import sys
from time import sleep


class react:
    def __init__(self, *args, npm_project = "./layout_viewer_made", patch_project="./layout_viewer/",  npm_resources = "resources", **kwargs):
        self.logger = logging.getLogger(str(self) + __name__)

        self.npm_project = npm_project
        self.source_dir = "src"
        self.npm_resources = r"/".join([npm_project, self.source_dir, npm_resources])
        self.npm_components = r"/".join(["components",  self.source_dir, npm_resources])
        self.npm_pages = r"/".join([ npm_project, "pages"])

        installing = not os.path.isdir(npm_project)

        cwd = os.getcwd()

        if installing:
            parts = ["yarn", "create", "next-app", npm_project,  "--example", "with-typescript"]
            print (" ".join(parts))
            subprocess.check_call(parts, stdout=sys.stdout,
                                      stderr=subprocess.STDOUT)

        sleep(2)

        self.logger.warning(f"Setting up sync")
        os.popen ("rsync -r {source} {target}".format(source=patch_project, target=npm_project))
        os.popen("""
        while inotifywait -r -e modify,create,delete,move {source}; do
            rsync -rahzv {source} {target}
        done""".format(source=patch_project, target=npm_project))
        sleep(2)

        self.logger.warning(f"Installing app to {npm_project}")




    def __call__(self, *args, **kwargs):
        print (args, kwargs)
