import logging
import os
from collections import defaultdict
from pprint import pprint

from sklearn import mixture
from sklearn.manifold import TSNE

from config import config
import numpy as np
import spacy

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from core.standard_converter.Dict2Graph import Dict2Graph
from core.microservice import microservice
from layout.Layout2ReadingOrder import titelize, topicize
from topics.clustering import cluster


@microservice
@converter("documents", "topics")
class TopicMaker(PathSpec):
    options_file = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x1024_128_2048cnn_1xhighway/elmo_2x1024_128_2048cnn_1xhighway_options.json"
    weight_file = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x1024_128_2048cnn_1xhighway/elmo_2x1024_128_2048cnn_1xhighway_weights.hdf5"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.alphabet = [f"{chr(value)}" for value in range(ord("a"), ord("a") + 26)]
        self.numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.stop_words = [
            "abstract",
            "paper",
            "difference",
            "conference",
            "similar",
            "same",
            "terms",
            "introduction",
            "contents",
            *self.alphabet,
            *[str(i) for i in range(1000)],
        ]
        self.nlp = spacy.load("en_core_web_trf")


    def __call__(micro, self, texts_metas, *args, **kwargs):
        return micro.predict(list(texts_metas))

    def load(self):
        logging.info("Loading spacy model")
        self.nlp = spacy.load("en_core_web_md")
        logging.info("Loaded")

    def predict(self, texts_metas):
        texts_metas = list(texts_metas)
        texts, metas = list(zip(*texts_metas))
        embeddingl = []
        logging.info(f"Making embeddings")
        for i, (text, meta) in enumerate(texts_metas):
            try:
                embedding = self.nlp(text[: config.TOPIC_TEXT_LENGTH]).vector
                shape = embedding.shape
            except Exception as e:
                logging.error(f"could not create embedding", exc_info=True)
                embedding = np.random.random(shape)
            embeddingl.append(embedding)
        embeddings = np.vstack(embeddingl)
        n_components = int(min(100, len(texts_metas) / 3))
        logging.info(f"Reducing from {embeddings.shape} to {n_components} dimensions")
        tsne = TSNE(n_components, method="exact")
        tsne_result = tsne.fit_transform(embeddings)
        logging.info(f"Reduced embeddings to {tsne_result.shape=}")
        del embeddingl
        del embeddings
        clusters, nesting = cluster(tsne_result)
        print(f"({clusters=} {nesting=}")

        cluster_texts = {i: [texts[c] for c in C] for i, C in clusters.items()}
        pprint(cluster_texts)
        cluster_titles = {i: topicize(t) for i, t in cluster_texts.items()}
        pprint(cluster_titles)

        topics = self.topicize_recursively(tsne_result, metas, texts)
        return topics, metas

    def topicize_recursively(
        self, embeddings, meta, texts, split_size=15, max_level=6, level=0
    ):
        logging.info(f"Making Topics {level + 1} of maximally {max_level + 1}")
        labels = self.cluster(embeddings=embeddings)
        topic_ids_2_doc_ids = self.labels2docs(texts=texts, labels=labels)
        keywords = self.make_keywords(
            topic_2_docids=topic_ids_2_doc_ids, texts=texts, lookup=meta
        )
        topics_titles = self.make_titles(keywords)

        topics = {}

        for i_group_label, i_group in topic_ids_2_doc_ids.items():
            try:
                group_embeddings = embeddings[i_group]
                group_meta = [meta[i] for i in i_group]
                group_texts = [texts[i] for i in i_group]
                if len(i_group) > split_size and level < max_level:

                    sub_topics = self.topicize_recursively(
                        group_embeddings,
                        group_meta,
                        group_texts,
                        split_size,
                        max_level=max_level,
                        level=level + 1,
                    )
                    topics[topics_titles[i_group_label]] = sub_topics
                else:
                    topics[topics_titles[i_group_label]] = group_meta
            except TypeError as e:
                logging.error(f"computing gaussian mixture {e}")
                raise e
            except IndexError as e:
                logging.error(f"computing subtopics with {e}")
                return topics
        return topics

    def cluster(self, embeddings):

        clusters = cluster(embeddings, _num_clusters=4)

        return clusters

    def labels2docs(self, texts, labels):
        topic_2_doc_ids = defaultdict(list)
        for i in range(len(texts)):
            topic_2_doc_ids[labels[i]].append(i)

        return topic_2_doc_ids

    def make_keywords(self, topic_2_docids, texts, lookup=None):
        from topics.TextRank4Keywords import TextRank4Keyword

        if not lookup:
            lookup = texts

        titled_clustered_documents = {}
        for topic_id, text_ids in topic_2_docids.items():
            constructed_doc = (
                " ".join(
                    [
                        w.strip()
                        for t in [texts[id] for id in text_ids]
                        for w in t.split()
                        if w.lower().strip() not in self.stop_words
                    ]
                )
                .replace(".", "")
                .replace(",", "")
            )

            tr4w = TextRank4Keyword()
            tr4w.analyze(constructed_doc, window_size=4, lower=True, stopwords=[])
            keywords = tr4w.get_keywords(5)

            title = titelize(constructed_doc).split()
            try:
                titled_clustered_documents[topic_id] = title
            except Exception as e:
                logging.error("Error making keywords", exc_info=True)
        return titled_clustered_documents

    def numpy_fillna(self, data, fill_value=0):
        lens = np.array([len(i) for i in data])
        max_len = max(lens)

        out = []
        for i, d in enumerate(data):
            out.append(d + (max_len - lens[i]) * [fill_value])
        return np.array(out)

    def make_titles(self, keywords_to_texts):
        return {k: " ".join(k[0] for k in v[:2]) for k, v in keywords_to_texts.items()}

    @staticmethod
    # @shelve_it("topic_maker_test_data")
    def test():
        TopicMaker.nlp = spacy.load("en_core_web_trf")

        logging.warning("Reading texts")

        # with open("/home/stefan/PycharmProjects/LayoutEagle/test/corpus/faust.txt") as f:
        #    text = " ".join([l for l in f.readlines() ])
        try:
            with open("./topics/faust.txt") as f:
                text = " ".join([l for l in f.readlines()])[0:15000]
        except:
            os.system(
                "wget https://raw.githubusercontent.com/martinth/mobverdb/master/faust.txt -P ./topics/"
            )
            with open("./topics/faust.txt") as f:
                text = " ".join([l for l in f.readlines()])[0:15000]

        doc = TopicMaker.nlp(text)

        logging.warning("Tokenizing texts")

        def paragraphs(document):
            length = 50
            start = 0
            try:
                for token in document:
                    if token.is_space and token.text.count("\n") > 1:
                        yield document[start : token.i][:length]
                        start = token.i
                yield document[start:][:length]
            except IndexError:
                logging.error("accessing doc after end")

        def nps(d):
            for t in d:
                try:
                    yield t.text
                except IndexError as e:
                    logging.error("token not found")
                continue

        texts = list(map(lambda d: list(nps(d)), paragraphs(doc)))
        texts = [" ".join(t) for t in texts]
        metas = [{"text": text} for text in texts]

        return list(zip(texts, metas))


if __name__ == "__main__":
    tm = TopicMaker
    test_data = tm.converter.test()
    print("calling topic maker")
    topics = tm(tm, test_data)
    d2g = Dict2Graph
    print(list(d2g([topics]))[0][0][0])
