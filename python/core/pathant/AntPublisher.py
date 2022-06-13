from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.react import react
from helpers.cache_tools import uri_with_cache
from core.pathant.Converter import converter

@converter("The One",'The One')
class AntPublisher(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Ant",
            type="graph",
            path="ant",
            route="ant",
            access={"fetch": True, "read": True, "upload":True, "correct":True, "delete":True}))

    def call(self, graph, meta=None):
        return self.ant.graph(), meta

    @uri_with_cache
    def on_get(self, req, resp):
        print("Ant info")
        return self.ant.graph()[0][0]


