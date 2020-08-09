import glob
import logging
from collections import Callable
from typing import Dict, Tuple
import numpy as np
import lda
import lda.datasets
from gensim import models
from gensim.corpora import Dictionary
from gensim.models import Word2Vec, FastText
from gensim.test.test_hdpmodel import dictionary

from RestPublisher.Resource import Resource
from RestPublisher.RestPublisher import RestPublisher
from RestPublisher.react import react
from layouteagle.pathant.Converter import converter

@converter("layout.txt", "topics")
class Topics(RestPublisher, react) :
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Topics",
            path="topics",
            route="topics",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))

        self.topics = None



    def __call__(self, documents):
        if not self.topics:
            """documents = list(documents)

            print (len(list(zip(documents))))
            html_paths_json_paths_txt_paths, metas = list(zip(*documents))
            print (html_paths_json_paths_txt_paths)
            html_paths, json_paths, txt_paths = list(zip(*html_paths_json_paths_txt_paths))
            print (txt_paths)
            """
            texts = map(lambda x: x.split(" "),
                        "Converting the sentences to a vector space model would transform them in such a way that looks at the words in all sentences, and then represents the words in the sentence with a number. "
                        "2If the sentences were One-Hot encoded:".split("."))

            X = lda.datasets.load_reuters()
            vocab = lda.datasets.load_reuters_vocab()
            titles = lda.datasets.load_reuters_titles()

            logging.warning("Building corpus")
            dictionary = Dictionary(texts)
            logging.warning("Performing Hierarchical Dirichlet Process, HDP is a non-parametric bayesian method (note the missing number of requested topics)")
            model = models.HdpModel(
                corpus=dictionary.doc2bow(map(texts, lambda x: x.split(" "))),
                id2word=dictionary,
                max_time=10)


            print (model)
            print (dir(model))
            logging.warning("GENSIM")

            w2v = Word2Vec(texts, min_count=1, size=5)

            vocab = list(w2v.wv.vocab)


            # X.shape
            (395, 4258)
            X.sum()
            # 84010
            print(X)
            model = lda.LDA(n_topics=2, n_iter=1500, random_state=1)
            model.fit_transform(X)  # model.fit_transform(X) is also available
            topic_word = model.topic_word_  # model.components_ also works
            n_top_words = 8
            topics = []
            print(X)
            for i, topic_dist in enumerate(topic_word):
                topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
                topics.append(topics)
                print('Topic {}: {}'.format(i, ' '.join(topic_words)))


            doc_topic = model.doc_topic_
            text2topic = []
            for i in range(10):
                print("{} (top topic: {})".format(titles[i], ))
                text2topic.append([doc_topic[i].argmax(), texts[i], metas[i]])

            self.topics = text2topic

        return self.topics

    def on_get(self, *args, **kwargs): # get all
        #self.prediction_pipe = self.ant("pdf", "layout.html")
        pdfs = [file for file in glob.glob("layouteagle/test/*.pdf")]

        #result_paths = list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))
        return list(self.ant("pdf", "topics")([(pdf, {}) for pdf in pdfs]))


import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
