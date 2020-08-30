import glob
import json
import os
import networkx as nx
import falcon
import wordninja

from RestPublisher.Resource import Resource
from RestPublisher.RestPublisher import RestPublisher
from RestPublisher.react import react
from Topics.TopicMaker import TopicMaker
from layouteagle import config
from layouteagle.helpers.cache_tools import file_persistent_cached_generator
from layouteagle.pathant.Converter import converter


@converter("layout.wordi", "topics")
class Topics(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Topics",
            path="topics",
            route="topics",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))

        self.topics = None

    @file_persistent_cached_generator(config.cache + 'topics.json', if_cache_then_finished=True,
                                      if_cached_then_forever=True)
    def __call__(self, documents):
        documents = list(documents)
        self.topic_maker = TopicMaker()

        print(len(list(zip(documents))))
        html_paths_json_paths_txt_paths, metas = list(zip(*documents))
        print(html_paths_json_paths_txt_paths)
        html_paths, json_paths, txt_paths = list(zip(*html_paths_json_paths_txt_paths))
        print(txt_paths)
        texts = []
        for txt in txt_paths:
            o = os.getcwd()
            print(f"opening {txt} {o}")
            with open(txt, 'r') as f:
                texts.append(wordninja.split(" ".join(f.readlines())[:1000]))

        print(texts)

        self.topics, text_ids = self.topic_maker(texts, txt_paths)
        # self.dig = self.to_graph_dcit(self.topics)
        yield self.dig, text_ids

    def to_graph_dcit(self, topics):
        dig = nx.DiGraph(topics)
        ddic = nx.to_dict_of_dicts(dig)
        print(ddic)
        levels = 3
        nodes = [{'id': k, 'name': k.replace("test/pdfs/", "").replace("pdf.htmlayout.txt", ""),
                  'val': 2 ** (levels - 1) if v else 2 ** (levels - 2)} for k, v in ddic.items()] \
                + [{'id': "CENTER", 'name': "The One", 'val': 2 ** (levels)}]

        center_links = [{'source': "CENTER", 'target': k} for k, v in ddic.items() if list(v.items())]
        links = [{'source': k, 'target': n} for k, v in ddic.items() for n in v if v] + center_links
        d = {'nodes': nodes, 'links': links}
        return d

    def on_get(self, req, resp):  # get all
        # self.prediction_pipe = self.ant("pdf", "layout.html")
        pdfs = [file for file in glob.glob("test/pdfs/*.pdf")]

        # result_paths = list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))
        value, meta = list(zip(*list(self.ant("pdf", "topics")([(pdf, {}) for pdf in pdfs]))))
        res = {
            'value': self.to_graph_dcit(value[0]),
            'meta': meta
        }
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"response": res, "status": resp.status})


import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
