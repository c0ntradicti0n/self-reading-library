import json
import logging
import os
import pickle
import falcon
from regex import regex
from core.rest.Resource import Resource
from core.rest.RestPublisher import RestPublisher
from core.rest.react import react
from core.standard_converter.Dict2Graph import Dict2Graph
from helpers.list_tools import forget_except
from topics.TopicMaker import TopicMaker
from config import config
from core.pathant.Converter import converter
from flask import Blueprint

bp = Blueprint("blueprint", __name__, template_folder="templates")

topic_maker = TopicMaker()


@converter("reading_order", "topics.graph")
class TopicsPublisher(RestPublisher, react):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            resource=Resource(
                title="library",
                type="graph",
                path="library",
                route="library",
                access={
                    "fetch": True,
                    "read": True,
                    "upload": True,
                    "correct": True,
                    "delete": True,
                },
            ),
        )

        self.topics = None

    reading_order_regex = regex.compile(" *\d+:(.*)")

    def __call__(self, documents):
        documents = list(
            forget_except(
                documents, keys=["used_text_boxes", "doc_id", "title", "html_path"]
            )
        )

        html_paths_json_paths_txt_paths, metas = list(zip(*documents))

        texts = [
            " ".join(
                "\n".join(
                    [tb[0] for utb in meta["used_text_boxes"] for tb in utb]
                ).split()[:10]
            )
            for meta in metas
        ]

        self.topics, text_ids = topic_maker(texts, meta=metas)

        with open(config.topics_dump + f"_{len(documents)}", "wb") as f:
            pickle.dump([self.topics, metas], f)

        yield self.topics, text_ids

    def on_get(self, req, resp):
        logging.info("Computing topics")
        documents = list(self.ant("feature", "reading_order", from_cache_only=True)([]))

        path = config.topics_dump + f"_{len(documents)}"
        if os.path.exists(path):
            with open(path, mode="rb") as f:
                d2g = Dict2Graph
                topics, meta = pickle.load(f)
                value = list(d2g([topics]))[0][0][0]
        else:
            logging.info("recreate")

            value, _ = list(
                zip(
                    *list(
                        self.ant("arxiv.org", "topics.graph", from_cache_only=True)([])
                    )
                )
            )

        logging.info("computed topics")
        resp.text = json.dumps(["topics", value], ensure_ascii=False)
        resp.status = falcon.HTTP_OK

    def on_post(self, req, resp, *args, **kwargs):
        return self.on_get(req, resp)