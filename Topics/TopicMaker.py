import logging
from collections import defaultdict
from pprint import pprint

import nltk
import scipy
import textacy
from gensim.parsing import remove_stopwords
from multi_rake import Rake
from numpy.lib.recfunctions import find_duplicates
from scipy.optimize import linear_sum_assignment
from sklearn import mixture, decomposition
from textacy.keyterms import sgrank, textrank

logging.warning("NLTK Download")
#nltk.download('stopwords')
#nltk.download('punkt')

import hdbscan
import numpy as np

import spacy


from allennlp.modules.elmo import Elmo, batch_to_ids

class TopicMaker:
    options_file = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x1024_128_2048cnn_1xhighway/elmo_2x1024_128_2048cnn_1xhighway_options.json"
    weight_file = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x1024_128_2048cnn_1xhighway/elmo_2x1024_128_2048cnn_1xhighway_weights.hdf5"

    def __init__(self):
        # Note the "1", since we want only 1 output representation for each token.
        self.elmo = Elmo(self.options_file, self.weight_file, 1, dropout=0)
        self.nlp = spacy.load("en_core_web_md")

    def test(self):
        logging.warning("Reading texts")

        #with open("/home/stefan/PycharmProjects/LayoutEagle/test/corpus/faust.txt") as f:
        #    text = " ".join([l for l in f.readlines() ])
        with open("/home/stefan/PycharmProjects/LayoutEagle/test/corpus/faust.txt") as f:
            text = " ".join([l  for l in f.readlines() ])[:50000]

        doc = self.nlp(text)

        logging.warning("Tokenizing texts")

        def paragraphs(document):
            length = 20
            start = 0
            try:
                for token in document:
                    if token.is_space and token.text.count("\n") > 1:
                        yield document[start:token.i][:length]
                        start = token.i
                yield document[start:][:length]
            except IndexError:
                logging.error("accessing doc after end")

        def nps (d):
            for t in d:
                    try:
                        yield t.text
                    except IndexError as e:
                        logging.error("token not found")
                    continue

        texts = list(map(lambda d: list(nps(d)), paragraphs(doc)))

        print (texts[:3])
        return texts, {}

    def __call__(self, texts, meta, *args, **kwargs):
        texts = list(texts)
        embeddings = self.embed(texts=texts)
        labels = self.cluster(embeddings=embeddings)
        topic_ids_2_doc_ids = self.labels2docs(texts=texts, labels=labels)
        keywords = self.make_keywords(topic_2_docids=topic_ids_2_doc_ids, texts=texts)
        topics = self.make_titles(keywords)
        return topics, meta

    def embed(self, texts):
        logging.info("Topic modelling")

        logging.warning("- getting embeddings")

        character_ids = batch_to_ids(texts)

        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        Xs = []
        chunks_ = list(chunks(character_ids, 30))

        for n, chunk in enumerate(chunks_):
            print (f" · {n+1} of {len(chunks_)}")
            embeddings = self.elmo(chunk)
            X = embeddings['elmo_representations'][0].detach().numpy()
            X = X.reshape(X.shape[0], -1)

            Xs.append(X)

            del embeddings
            del X

        X = np.vstack(Xs)
        print(X.shape)
        logging.warning("sizing embeddings")

        pca = decomposition.PCA(n_components=100)
        pca.fit(X)
        X = pca.transform(X)

        logging.warning("- cluster embeddings")
        return X

    def cluster(self, embeddings):
        X = embeddings
        g = mixture.GaussianMixture(n_components=10, covariance_type="spherical")
        g.fit(X)

        labels = g.predict(X)
        return labels

    def labels2docs(self, texts, labels):
        topic_2_docids = defaultdict(list)
        for i in range(len(texts)):
            topic_2_docids[labels[i]].append(i)

        print (topic_2_docids)
        return topic_2_docids

    def make_keywords(self, topic_2_docids, texts):
        from nltk.corpus import stopwords

        stop_words = stopwords.words()

        def stop_word_removal(x):
            token = x.split()
            return ' '.join([w for w in token if not w in stop_words])

        titled_clustered_documents = []
        for topic_id, text_ids in topic_2_docids.items():
            constructed_doc = " ".join([w.title() for id in text_ids for w in texts[id]] )
            constructed_doc = remove_stopwords(stop_word_removal(constructed_doc.lower()))
            doc = textacy.make_spacy_doc(constructed_doc, lang="en_core_web_md")
            keywords = textrank(doc, normalize="lemma", n_keyterms=15)

            print (keywords)
            print(constructed_doc[:2000])

            titled_clustered_documents.append(
                ([keywords if keywords else []] ,
                 [texts[id] for id in text_ids]))

        return titled_clustered_documents

    def numpy_fillna(self, data):
        # Get lengths of each row of data
        lens = np.array([len(i) for i in data])

        # Mask of valid places in each row
        mask = np.arange(lens.max()) < lens[:, None]

        # Setup output array and put elements from data into masked positions
        out = np.zeros(mask.shape, dtype=np.float64)
        out[mask] = np.concatenate(data)
        return out

    def make_titles(self, keywords_to_texts):
        words = np.array([[kw[0] for kw in keys[0]] for keys, values in list(keywords_to_texts)])
        scores = self.numpy_fillna([[kw[1] for kw in keys[0]] for keys, values in list(keywords_to_texts)])

        scores = -scores
        unq, count = np.unique(words, return_counts=True)
        dups = unq[count > 1]
        vec_in_fun = np.vectorize(lambda w: w in dups)
        mask = vec_in_fun(words)
        scores[mask] = 1
        print(scores)

        row_ids, col_ids = linear_sum_assignment(scores)
        titles_to_texts =  {keywords_to_texts[row][0][0][col][0]:keywords_to_texts[row][1]
                           for col, row in zip(col_ids, row_ids)}
        pprint({k: " ".join(u for w in v[:10] for u in w) for k, v in titles_to_texts.items()})

        return  titles_to_texts






if __name__=="__main__":
    tm = TopicMaker()
    tm(*tm.test())