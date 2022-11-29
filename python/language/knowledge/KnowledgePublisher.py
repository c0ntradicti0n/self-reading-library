import falcon

from core.rest.Resource import Resource
from core.rest.RestPublisher import RestPublisher

from helpers.encode import jsonify

from config.ant_imports import *


@converter("The Idea", "The Idea")
class KnowledgePublisher(RestPublisher):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            resource=Resource(
                title="Knowledge",
                type="knowledge",
                path="knowledge",
                route="knowledge",
                access={
                    "fetch": True,
                    "read": True,
                    "upload": True,
                    "correct": True,
                    "delete": True,
                },
            ),
        )
        ant = PathAnt()
        self.pipeline = ant(
            "span_annotation.collection.fix",
            "span_annotation.collection.nodes_edges",
        )

    def on_get(self, req, resp, id=None):
        result = list(self.pipeline(metaize([id]), search=id))
        resp.status = falcon.HTTP_OK
        resp.text = jsonify(result)

    def on_post(self, req, resp, id=None):
        search = id
        self.logger.info(f"Searching for {search}")
        result = list(self.pipeline(metaize([search]), search=id))
        resp.status = falcon.HTTP_OK
        resp.text = jsonify(result)
