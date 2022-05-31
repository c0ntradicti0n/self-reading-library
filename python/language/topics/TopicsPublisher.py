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
from language.topics.TopicMaker import TopicMaker
from core import config
from helpers.cache_tools import file_persistent_cached_generator, uri_with_cache
from helpers.nested_dict_tools import type_spec_iterable
from core.pathant.Converter import converter
from flask import jsonify, Blueprint

bp = Blueprint('blueprint', __name__, template_folder='templates')


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
        documents = unique(list(documents), key=lambda x: x[1]['html_path'])
        self.topic_maker = TopicMaker()

        html_paths_json_paths_txt_paths, metas = list(zip(*documents))

        texts = [
            " ".join("\n".join([tb[0]
                                for utb in meta["used_text_boxes"]
                                for tb in utb]
                               ).split()[:10])
            for meta in metas
        ]
        paths = [meta["html_path"] for meta in metas]

        self.topics, text_ids = self.topic_maker(texts, paths)

        with open(config.topics_dump, 'wb') as f:
            pickle.dump([self.topics, metas], f)

        yield self.topics, text_ids

    def on_get(self, req, resp):  # get all
        if os.path.exists(config.topics_dump):
            with open(config.topics_dump, mode="rb") as f:
                d2g = Dict2Graph
                topics, meta = pickle.load(f)
                print("TOPICS")

                print(topics)
                value = list(d2g([topics]))[0][0][0]
                print(value)
        else:

            value, meta = list(zip(*list(self.ant("prediction", "topics.graph", if_cached_then_forever=True)([]))))

        pprint(type_spec_iterable(value))

        resp.body = json.dumps([value, meta], ensure_ascii=False)
        resp.status = falcon.HTTP_OK
