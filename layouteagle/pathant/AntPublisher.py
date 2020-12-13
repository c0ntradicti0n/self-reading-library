from RestPublisher.Resource import Resource
from RestPublisher.RestPublisher import RestPublisher
from RestPublisher.react import react
from ant import Ant
from layouteagle.helpers.cache_tools import uri_with_cache
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathSpec import cache_flow

@converter("a",'o')
class AntPublisher(RestPublisher, react) :
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Ant",
            type = "text",
            path="ant",
            route="ant",
            access={"fetch": True, "read": True, "upload":True, "correct":True, "delete":True}))

    def call(self, graph, meta=None):
        return self.ant.graph(), meta

    @uri_with_cache
    def on_get(self, req, resp):
        print("giving ant info")
        return self.ant.graph()


