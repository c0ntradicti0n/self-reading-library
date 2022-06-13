import glob
import json
import logging
import os
import pickle
from pprint import pprint

import falcon
import wordninja
from regex import regex

from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.react import react
from core.StandardConverter.Dict2Graph import Dict2Graph
from helpers.list_tools import unique
from topics.TopicMaker import TopicMaker
from core import config
from helpers.cache_tools import configurable_cache, uri_with_cache
from helpers.nested_dict_tools import type_spec_iterable
from core.pathant.Converter import converter
from flask import jsonify, Blueprint

bp = Blueprint('blueprint', __name__, template_folder='templates')

topic_maker = TopicMaker()


@converter("reading_order", "topics.dict")
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
        documents = list(documents)

        html_paths_json_paths_txt_paths, metas = list(zip(*documents))

        texts = [
            " ".join("\n".join([tb[0]
                                for utb in meta["used_text_boxes"]
                                for tb in utb]
                               ).split()[:10])
            for meta in metas
        ]

        self.topics, text_ids = topic_maker(texts, meta=metas)

        with open(config.topics_dump + f"_{len(documents)}", 'wb') as f:
            pickle.dump([self.topics, metas], f)

        yield self.topics, text_ids

    def on_get(self, req, resp):  # get all
        documents = list(self.ant("prediction", "reading_order", from_cache_only=True)([]))

        path = config.topics_dump + f"_{len(documents)}"
        if os.path.exists(path):
            with open(path, mode="rb") as f:
                d2g = Dict2Graph
                topics, meta = pickle.load(f)
                print("TOPICS")

                print(topics)
                value = list(d2g([topics]))[0][0][0]
                print(value)
        else:

            value, meta = list(zip(*list(self.ant("prediction", "topics.graph", from_cache_only=True)([]))))

        pprint(type_spec_iterable(value))

        resp.body = json.dumps([value, meta], ensure_ascii=False)
        resp.status = falcon.HTTP_OK
