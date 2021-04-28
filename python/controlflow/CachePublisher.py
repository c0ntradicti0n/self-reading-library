import os
from typing import List

from python.helpers.cache_tools import uri_with_cache
from python.layouteagle import config
from python.layouteagle.RestPublisher.Resource import Resource
from python.layouteagle.RestPublisher.RestPublisher import RestPublisher
from python.layouteagle.pathant.Converter import converter


def fs_tree_to_dict(path_):
    file_token = ''
    for root, dirs, files in os.walk(path_):
        tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
        tree.update({f: file_token for f in files})
        return tree  # note we discontinue iteration trough os.walk


@converter("admin", 'controlflow')
class CachePublisher(RestPublisher):

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Cache",
            type = "html",
            path="cache",
            route="cache",
            access={"fetch": True, "read": True, "upload":True, "correct":True, "delete":True}))
        self.dir = config.markup_dir


        # pdf -> wordi
        #     -> wordi.page
        #     -> wordi.page.difference
        #     -> wordi.page.difference
        #     -> wordi.difference
        #     -> css.difference


    def on_put(self, file, meta_data):
        print ("dfdf")

    def on_get(self, file, meta_data):
        print("dfdf")

    def on_get(self, req, resp):
        _, self.r = fs_tree_to_dict(config.cache)
        print(self.r)

        return self.r

    def on_delete(self, i):
        try:
            os.remove(self.r[i])
        except OSError:
            pass
