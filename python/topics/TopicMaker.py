import collections
import logging
import os
from collections import defaultdict
import nltk
from sklearn import mixture
from sklearn.manifold import TSNE

from core import config
from nltk.corpus import wordnet as wn
import numpy as np
import spacy
from core.StandardConverter.Dict2Graph import Dict2Graph
from topics.TextRank4Keywords import TextRank4Keyword


class TopicMaker:
    options_file = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x1024_128_2048cnn_1xhighway/elmo_2x1024_128_2048cnn_1xhighway_options.json"
    weight_file = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x1024_128_2048cnn_1xhighway/elmo_2x1024_128_2048cnn_1xhighway_weights.hdf5"

    def __init__(self):
        self.alphabet = [f"{chr(value)}" for value in range(ord('a'), ord('a') + 26)]
        self.numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.stop_words = ['abstract', 'paper', *self.alphabet, *[str(i) for i in range(1000)]]

    def test(self):
        self.nlp = spacy.load("en_core_web_trf")

        logging.warning("Reading texts")

        # with open("/home/stefan/PycharmProjects/LayoutEagle/test/corpus/faust.txt") as f:
        #    text = " ".join([l for l in f.readlines() ])
        with open("/home/stefan/PycharmProjects/LayoutEagle/python/test/corpus/faust.txt") as f:
            text = " ".join([l for l in f.readlines()])[5000:15000]

        doc = self.nlp(text)

        logging.warning("Tokenizing texts")

        def paragraphs(document):
            length = 50
            start = 0
            try:
                for token in document:
                    if token.is_space and token.text.count("\n") > 1:
                        yield document[start:token.i][:length]
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

        print(texts[:3])
        return texts, [{"text": text} for text in texts]

    def __call__(self, texts, meta, *args, **kwargs):
        self.nlp = spacy.load("en_core_web_trf")

        embeddingl = []
        logging.info(f"Making embeedings")
        for text in texts:
            try:
                embedding = self.nlp(text[:config.TOPIC_TEXT_LENGTH])._.trf_data.tensors[1]
                shape = embedding.shape
            except Exception as e:
                logging.error(f"could not create embedding", exc_info=True)
                embedding = np.random.random(shape)
            embeddingl.append(embedding)

        embeddings = np.vstack(embeddingl)

        n_components = 50
        logging.info(f"Reducing from {embeddings.shape} to {n_components} dimensions")

        tsne = TSNE(n_components, method='exact')
        tsne_result = tsne.fit_transform(embeddings)
        logging.info(f"Reduced embeddings to {tsne_result.shape=}")

        del embeddingl

        topics = self.topicize_recursively(embeddings, meta, texts)

        return topics, meta

    def topicize_recursively(self, embeddings, meta, texts, split_size=10, max_level=5, level=0):
        print(f"Making Topics {level + 1} of maximally {max_level + 1}")
        labels = self.cluster(embeddings=embeddings)
        topic_ids_2_doc_ids = self.labels2docs(texts=texts, labels=labels)
        keywords = self.make_keywords(topic_2_docids=topic_ids_2_doc_ids, texts=texts, lookup=meta)
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
                        level=level + 1)
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
        X = embeddings

        g = mixture.GaussianMixture(
            n_components=min(int(X.shape[0] / 3 + 0.5), 10),
            covariance_type="tied",
            reg_covar=1e-1,
            n_init=20,
            max_iter=50
        )

        g.fit(X)

        labels = g.predict(X)

        return labels

    def labels2docs(self, texts, labels):
        topic_2_doc_ids = defaultdict(list)
        for i in range(len(texts)):
            topic_2_doc_ids[labels[i]].append(i)

        return topic_2_doc_ids

    def make_keywords(self, topic_2_docids, texts, lookup=None):
        if not lookup:
            lookup = texts

        titled_clustered_documents = {}
        for topic_id, text_ids in topic_2_docids.items():
            constructed_doc = " ".join([w for t in [texts[id] for id in text_ids] for w in t.split() if
                                        w.lower() not in self.stop_words]).replace(".", "").replace(",", "")

            tr4w = TextRank4Keyword()
            tr4w.analyze(constructed_doc, window_size=4, lower=True,
                         stopwords=[])
            keywords = tr4w.get_keywords(5)

            keywords = [k for k in keywords if len(k[0]) > 3]
            try:
                titled_clustered_documents[topic_id] = keywords
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
        return {k: " ".join(k[0] for k in v[:4]) for k, v in keywords_to_texts.items()}


if __name__ == "__main__":
    tm = TopicMaker()
    topics = tm(*tm.test())
    d2g = Dict2Graph
    print(list(d2g([topics]))[0][0][0])
