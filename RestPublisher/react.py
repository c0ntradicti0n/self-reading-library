import logging
import os
import shlex
import subprocess
import sys
from time import sleep


class react:
    def __init__(self, *args, npm_project = "./layout_viewer_made", patch_project="./layout_viewer",  npm_resources = "resources", **kwargs):
        self.logger = logging.getLogger(str(self) + __name__)

        self.npm_project = npm_project
        self.npm_resources = r"/".join([npm_project,  npm_resources])
        self.npm_components = r"/".join(["components", npm_resources])
        self.npm_pages = r"/".join([ npm_project, "pages"])

        installing = not os.path.isdir(npm_project)

        cwd = os.getcwd()

        if installing:
            parts = ["yarn", "create", "next-app", npm_project,  "--example", "with-three-js"]
            print (" ".join(parts))
            subprocess.check_call(parts, stdout=sys.stdout,
                                      stderr=subprocess.STDOUT)

            os.mkdir(self.npm_resources)

        sleep(2)

        command = r"""
        echo "while read -r fullpath
        
                do
                        rsync -r {source}/* {target}
                done < <(inotifywait -mr --format '%w%f' -e  modify,create,delete,move {source}/)">sync_patch_app.sh && /bin/bash sync_patch_app.sh &""".format(source=patch_project,
                                                                                            target=npm_project)
        self.logger.warning(f"Setting up sync")
        os.popen (r"rsync -r {source}/* {target}".format(source=patch_project, target=npm_project))
        print (command)
        print (shlex.split(command))
        p = os.popen(command)
        sleep(2)

        self.logger.warning(f"Installing app to {npm_project}")




    def __call__(self, *args, **kwargs):
        print (args, kwargs)
