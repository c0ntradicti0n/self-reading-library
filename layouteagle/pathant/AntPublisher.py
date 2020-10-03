from ant import Ant
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathSpec import cache_flow

@converter("a",'o')
class AntPublisher(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached= cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def call(self, graph, meta=None):
        return self.ant.graph(), meta
