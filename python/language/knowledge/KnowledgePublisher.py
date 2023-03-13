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

        self.search = ant(
            "text",
            "span_annotation.collection.nodes_edges",
        )

        self.expand = ant(
            "text",
            "span_annotation.collection.nodes_edges",
        )

    def on_get(self, req, resp, id=None):
        result = list(
            self.search(metaize(["premise"]), search="premise", from_function_only=True)
        )[0]
        resp.status = falcon.HTTP_OK
        resp.text = jsonify(result)

    def on_post(self, req, resp, id=None):
        search = req.media[0]
        self.logger.info(f"Searching for {search=}")
        result = list(
            self.search(metaize([search]), search=search, from_function_only=True)
        )[0]
        resp.status = falcon.HTTP_OK
        resp.text = jsonify(result)

    def on_put(self, req, resp, id=None):
        node_id = req.media[0]
        self.logger.info(f"Expanding on term '{node_id=}'")
        result = list(
            self.expand(
                metaize([node_id]),
                node_id=node_id,
                expand=True,
                from_function_only=True,
            )
        )[0]
        resp.status = falcon.HTTP_OK
        resp.text = jsonify(result)
