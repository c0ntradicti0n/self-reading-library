import glob
import logging
import os
import pickle
from pprint import pprint
import wordninja
from regex import regex

from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.react import react
from core.StandardConverter.Dict2Graph import Dict2Graph
from language.topics.TopicMaker import TopicMaker
from core import config
from helpers.cache_tools import file_persistent_cached_generator, uri_with_cache
from helpers.nested_dict_tools import type_spec_iterable
from core.pathant.Converter import converter


@converter("reading_order", "topics.dict")
class TopicsPublisher(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="topics",
            type="graph",
            path="topics",
            route="topics",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))

        self.topics = None

    reading_order_regex = regex.compile(" *\d+:(.*)")

    """@file_persistent_cached_generator(
        config.cache + os.path.basename(__file__).replace('.py', '') +
        '.json',
        if_cache_then_finished=True,
        if_cached_then_forever=False)"""
    def __call__(self, documents):
        documents = list(documents)
        self.topic_maker = TopicMaker()

        # print(len(list(zip(documents))))
        html_paths_json_paths_txt_paths, metas = list(zip(*documents))

        reading_order_paths = [meta["reading_order_path"] for meta in metas]
        # print(reading_order_paths)
        texts = []
        paths = []
        print("Topicizing documents")

        for i, reading_order in enumerate(reading_order_paths):
            o = os.getcwd()
            print(f"opening {reading_order} {o}  {i+1} of {len(reading_order_paths)}")
            try:
                with open(reading_order, 'r', encoding='utf-8', errors='ignore')  as f:
                    firstlines = [f.readline() for i in range(1000)]

                    words = [TopicsPublisher.reading_order_regex.search(w).group(1) for w in firstlines if TopicsPublisher.reading_order_regex.search(w)]
                    words = [w for w in words if w]
                    if words:
                        text = wordninja.split("".join(words)[:1000].replace(" ", ""))
                        texts.append(text)
                        paths.append(reading_order)
                        print (text[:3])
            except FileNotFoundError:
                logging.error(f"no {reading_order}, was not created?")

        self.topics, text_ids = self.topic_maker(texts, paths)
        yield self.topics, text_ids

    @uri_with_cache
    def on_get(self, req, resp):  # get all
        if os.path.exists(config.topics_dump):
            with open(config.topics_dump, mode="rb") as f:
                d2g = Dict2Graph
                topics = pickle.load(f)
                print ("TOPICS")

                print (topics)
                value = list(d2g([topics]))[0][0][0]
                print (value)
        else:
            pdfs = [file for file in glob.glob(config.pdf_dir + "*.pdf")]

            value, meta = list(zip(*list(self.ant("pdf", "topics.graph")([(pdf, {}) for pdf in pdfs]))))

            pprint(type_spec_iterable(value))

        return value

