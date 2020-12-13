from python.layouteagle.RestPublisher.Resource import Resource
from python.layouteagle.RestPublisher.RestPublisher import RestPublisher
from python.layouteagle.RestPublisher.react import react
from python.helpers.cache_tools import uri_with_cache
from python.layouteagle.pathant.Converter import converter

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
        print("giving ant info")
        return self.ant.graph()[0][0]


