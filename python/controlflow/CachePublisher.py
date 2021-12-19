import os
from typing import List

from helpers.cache_tools import uri_with_cache
from core import config
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.pathant.Converter import converter


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


        # pdf -> reading_order
        #     -> reading_order.page
        #     -> reading_order.page.difference
        #     -> reading_order.page.difference
        #     -> reading_order.difference
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
