import json
import logging
import os
import pickle
import falcon
from regex import regex
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.react import react
from core.StandardConverter.Dict2Graph import Dict2Graph
from helpers.list_tools import forget_except
from topics.TopicMaker import TopicMaker
from core import config
from core.pathant.Converter import converter
from flask import Blueprint

bp = Blueprint('blueprint', __name__, template_folder='templates')

topic_maker = TopicMaker()


@converter("reading_order", "topics.graph")
class TopicsPublisher(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="library",
            type="graph",
            path="library",
            route="library",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))

        self.topics = None

    reading_order_regex = regex.compile(" *\d+:(.*)")

    def __call__(self, documents):
        print ("started")
        documents = list(forget_except(documents, keys=[]))

        html_paths_json_paths_txt_paths, metas = list(zip(*documents))
        print ("started2")

        texts = [
            " ".join("\n".join([tb[0]
                                for utb in meta["used_text_boxes"]
                                for tb in utb]
                               ).split()[:10])
            for meta in metas
        ]
        print ("started3")

        metas = forget_except(metas, )

        self.topics, text_ids = topic_maker(texts, meta=metas)

        with open(config.topics_dump + f"_{len(documents)}", 'wb') as f:
            pickle.dump([self.topics, metas], f)

        yield self.topics, text_ids

    def on_get(self, req, resp):
        logging.info("Computing topics")
        documents = list(self.ant("feature", "reading_order", from_cache_only=True)([]))
        print (documents[:1])
        path = config.topics_dump + f"_{len(documents)}"
        if os.path.exists(path):
            with open(path, mode="rb") as f:
                d2g = Dict2Graph
                topics, meta = pickle.load(f)
                value = list(d2g([topics]))[0][0][0]
        else:
            logging.info("recreate")

            value, _ = list(zip(*list(self.ant("arxiv.org", "topics.graph", from_cache_only=True)([]))))

        logging.info("computed topics")
        resp.body = json.dumps([value, {}], ensure_ascii=False)
        resp.status = falcon.HTTP_OK
