import glob
from collections import Callable
from typing import Dict, Tuple
import numpy as np
import lda
import lda.datasets

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
            print (list(zip(list(documents))))
            texts, metas = list(zip(list(documents)))

            X = lda.datasets.load_reuters()
            vocab = lda.datasets.load_reuters_vocab()
            titles = lda.datasets.load_reuters_titles()

            # X.shape
            (395, 4258)
            X.sum()
            # 84010
            model = lda.LDA(n_topics=20, n_iter=1500, random_state=1)
            model.fit(texts)  # model.fit_transform(X) is also available
            topic_word = model.topic_word_  # model.components_ also works
            n_top_words = 8
            topics = []
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
