import itertools
from collections import OrderedDict, Iterable
from functools import wraps

from nltk import flatten
from nltk.corpus import wordnet
from nltk.corpus.reader import Synset
from nltk.stem import PorterStemmer

from overrides import overrides

from xnym_embeddings.dict_tools import balance_complex_tuple_dict
from sklearn.preprocessing import Normalizer
from allennlp.modules.token_embedders.token_embedder import TokenEmbedder
from allennlp.data import Vocabulary
from xnym_embeddings.time_tools import timeit_context
import numpy as np
import torch
from multiprocessing import Pool


#Wordnet sense disambiguation

def rolling_window_lastaxis(a, window):
    """Directly taken from Erik Rigtorp's post to numpy-discussion.
    <http://www.mail-archive.com/numpy-discussion@scipy.org/msg29450.html>"""
    if window < 1:
       raise ValueError ("`window` must be at least 1.")
    if window > a.shape[-1]:
       raise ValueError ("`window` is too long.")
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def search_in_rowling(M, single_sequence):
    return np.where(
        np.all
            (np.logical_xor(
            M == single_sequence,
                np.isnan(single_sequence)),
            axis=2
    ))

def last_nonzero(arr, axis, invalid_val=-1):
    mask = arr!=0
    val = arr.shape[axis] - np.flip(mask, axis=axis).argmax(axis=axis) - 1
    return np.where(mask.any(axis=axis), val, invalid_val)

def search_sequence_numpy(arr,seq):
    """ Find arrays in arrays at arbitrary position on second axis

    Multiple occurrences in a sample are given with recurrent sample indices and other positions in the samples

    :param arr: 2d array to look in
    :param seq: 2d array to look from; padding with nan allows to compare sequences with minor length
    :return: list of tuples of arrays with shape: length of seq * shape[0] of arr * shape[1] of arr
                                                                  no. of sample     positions in samples

    """
    # compute strides from samples with length of seqs
    len_sequences = seq.shape[1]
    M = rolling_window_lastaxis(arr, len_sequences)

    # check if they match these smaller sequences
    matched_xnyms = list(search_in_rowling(M,s) for s in seq)

    # return the index of the matched word, the indices of the samples, where it was found and the positions within these samples
    for xnym_index, (sample_indices, position_indices) in enumerate(matched_xnyms):
        if len(sample_indices)>0:
            yield xnym_index, sample_indices, position_indices

def split_multi_word(word):
    return tuple(word.split('-') if '-' in word else word.split('_'))


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

wordnet_lookers = {}
@parametrized
def wordnet_looker(fun, kind):
    wordnet_lookers[kind] = fun
    @wraps(fun)
    def aux(*xs, **kws):
        return fun(*xs, **kws)
    return aux

@wordnet_looker('hyponyms')
def get_hyponyms(synset, depth=0, max_depth=0):
    if depth > max_depth:
        return set(synset.hyponyms())
    hyponyms = set()
    for hyponym in synset.hyponyms():
        hyponyms |= set(get_hyponyms(hyponym, depth=depth+1))
    return hyponyms | set(synset.hyponyms())

@wordnet_looker('cohyponyms')
def get_cohyponyms(synset):
    """ Cohyponyms are for exmaple:
    Dog, Fish, Insect, because all are animals, as red and blue, because they are colors.
    """
    cohyponyms = set()
    for hypernym in synset.hypernyms():
        cohyponyms |= set(hypernym.hyponyms())
    return cohyponyms - set([synset])

@wordnet_looker('cohypernyms')
def get_cohypernyms(synset):
    """ Cohypernyms are for exmaple:

    A Legal Document and a Testimony are cohypernyms, because what is a Legal Document is possibly not a Testimony and
    vice versa, but also that may possibly be the case.

    Dog, Fish, Insect are no cohypernyms, because there is no entity, that is at the same time a Dog and a Fisch or an
    Insect.
    """
    cohypernyms = set()
    for hyponym in synset.hyponyms():
        cohypernyms |= set(hyponym.hypernyms())
    return cohypernyms - set([synset])

@wordnet_looker('hypernyms')
def get_hypernyms(synset):
    hypernyms = set()
    for hyponym in synset.hypernyms():
        hypernyms |= set(get_hypernyms(hyponym))
    result_syns = hypernyms | set(synset.hypernyms())
    result = set(flatten([list(x.lemmas()) if isinstance(x, Synset) else x for x in result_syns]))
    return result


@wordnet_looker('antonyms')
def get_antonyms(synset):
    antonyms = set()
    new_antonyms = set()
    for lemma in synset.lemmas():
        new_antonyms |= set(lemma.antonyms())
        antonyms |= new_antonyms
        for antonym in new_antonyms:
            antonyms |= set(flatten([list(x.lemmas()) for x in antonym.synset().similar_tos()]))
    return antonyms

@wordnet_looker('synonyms')
def get_synonyms(synset):
    synonyms = set(synset.lemmas())
    return synonyms

porter = PorterStemmer()

def wordnet_lookup_xnyms (index_to_tokens, fun):
    xnym_dict = OrderedDict()
    lemma_vocab =  set (porter.stem(word) for word in index_to_tokens.values())

    for token in lemma_vocab:
        xnyms_syns = set()
        for syn in wordnet.synsets(token):
            xnyms_syns |= fun(syn)

        lemmas = set(flatten([list(x.lemmas()) if isinstance(x, Synset) else x for x in xnyms_syns]))

        strings = [split_multi_word(x.name()) for x in lemmas]

        xnym_dict[(token,)] = strings
    return xnym_dict

def numerize(d, token2index):
    number_dict = OrderedDict()
    for key, val in d.items():
        if isinstance(key, Iterable):
            new_key = type(key)([token2index[t] for t in key if t in token2index])
        else:
            new_key = type(key)(token2index[key])

        new_vals = []
        for var in val:
            if isinstance(var, Iterable):
                new_val = type(var)([token2index[t] for t in var if t in token2index])
                if not new_val:
                    continue
            else:
                new_val = type(var)(token2index[var])
            new_vals.append(new_val)

        if not new_vals or not new_key:
            continue

        number_dict[new_key] = new_vals
    return number_dict

@TokenEmbedder.register("xnym_embedder")
class XnymEmbedder (TokenEmbedder):
    """
    Represents a sequence of tokens as a relation based embeddings.


    Each sequence gets a vector of length vocabulary size, where the i'th entry in the vector
    corresponds to number of times the i'th token in the vocabulary appears in the sequence.
    By default, we ignore padding tokens.
    Parameters
    ----------
    vocab: ``Vocabulary``
    projection_dim : ``int``, optional (default = ``None``)
        if specified, will project the resulting bag of positions representation
        to specified dimension.
    ignore_oov : ``bool``, optional (default = ``False``)
        If true, we ignore the OOV token.
    """
    def __init__(self,
                 vocab: Vocabulary,
                 projection_dim: int = 10,
                 xnyms:str='antonyms',
                 normalize=True,
                 sparse=True,
                 parallelize=False,
                 numerize_dict=True):
        super(XnymEmbedder, self).__init__()
        self.xnyms = xnyms
        self.S = None

        with timeit_context('creating %s-dict' % self.xnyms):
            self.vocab = vocab
            self.parallelize = parallelize

            xnyms_looker_fun = wordnet_lookers[xnyms]
            self.xnym_dict = wordnet_lookup_xnyms(vocab._index_to_token['tokens'], fun=xnyms_looker_fun)

            self.xnym_dict[('in', 'common',)] = [('differ',), ('differs',)]
            self.xnym_dict[('equivocally',)] = [('univocally',)]
            self.xnym_dict[('micronutrients',)] = [('macronutrients',)]

            self.xnym_dict = balance_complex_tuple_dict(self.xnym_dict)

            if numerize_dict:
                self.xnym_dict = numerize(self.xnym_dict, vocab.get_token_to_index_vocabulary())

            #pprint.pprint (dict(zip(list(self.xnym_dict.keys())[:take],list(self.xnym_dict.values())[:take])))


            self.normalize = normalize
            self.sparse = sparse
            self.output_dim = projection_dim

            xnym_keys = list(self.xnym_dict.keys())
            length = max(map(len, xnym_keys))

            self.xnyms_keys = np.array([list(xi) + [np.nan] * (length - len(xi)) for xi in xnym_keys])
            self.xnyms_counterparts = self.generate_xnym_counterparts(self.xnym_dict.values())

            self.xnyms_keys_len_groups = [(l, list(g)) for l, g in
                                          itertools.groupby(
                                              sorted(self.xnym_dict.items(),
                                                     key=lambda x:len(x[0])),
                                              key=lambda x:len(x[0]))]
            #self.xnyms_counterparts_len_groups = [self.generate_xnym_counterparts(group.values()) for group in self.xnyms_keys_len_groups]

    def generate_xnym_counterparts(self, values):
        xnyms_counterparts = []
        xnym_counterpars = list(values)
        for ac in xnym_counterpars:
            length = max(map(len, ac))
            counterparts = np.array([list(xi) + [np.nan] * (length - len(xi)) for xi in ac])
            xnyms_counterparts.append(counterparts)
        return np.array(xnyms_counterparts)

    def position_distance_embeddings(self, input_array):
        where_xnyms_match = list(search_sequence_numpy(input_array, self.xnyms_keys))

        for x1_index, s1_indices, p1_index in where_xnyms_match:
            where_counterpart_matches = list(search_sequence_numpy(input_array[s1_indices], self.xnyms_counterparts[x1_index]))

            for _, s2_indices, p2_index in where_counterpart_matches:
                both_containing_samples = s1_indices[s2_indices]
                both_containing_positions = p1_index[s2_indices]
                difference = np.fabs(both_containing_positions - p2_index)

                if difference.any():
                    index_sample_token1 = (both_containing_samples, both_containing_positions)
                    index_sample_token2 = (s1_indices[s2_indices], p2_index)
                    occurrences = np.column_stack(index_sample_token1 + index_sample_token2)

                    for i, instance in enumerate(occurrences):
                        ind = instance.reshape((2,2)).T

                        try:
                            samples = self.S[ind[0]]
                        except:
                            raise ValueError("Why is that None???")
                        tokens = samples[:,ind[1]]
                        min_dim = last_nonzero(tokens, axis=1, invalid_val=-1).max() + 1
                        self.S[tuple(instance[:2]) + (min_dim,)] = difference[i]
                        self.S[tuple(instance[2:]) + (min_dim,)] = difference[i]

    @overrides
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        inputs: ``torch.Tensor``
            Shape ``(batch_size, timesteps, sequence_length)`` of word ids
            representing the current batch.
        Returns
        -------
        The distance position representations for the input sequence, shape
        ``(batch_size, vocab_size)``
        """
        input_array = inputs.cpu().detach().numpy()
        self.S = np.zeros((*input_array.shape, self.output_dim), dtype=np.float32)

        if self.parallelize:
            array_slices = np.array_split(input_array, 4)
            with timeit_context('parallel %s-position calculation...' % self.xnyms):
                with Pool(processes=4) as pool:
                    results = pool.map(self.position_distance_embeddings, enumerate(array_slices))

            S = np.concatenate([x[1] for x in sorted(results, key=lambda x: x[0])])
        else:
            with timeit_context('%s-position calculation...' % self.xnyms):
                self.position_distance_embeddings(input_array)

        #print ( [self.vocab.get_index_to_token_vocabulary()[i] for i in input_array[0]])

        transformer = Normalizer(norm='l2').fit(self.S.reshape(-1, self.S.shape[-1]))  # fit does nothing.
        tS = transformer.transform(self.S.reshape(-1, self.S.shape[-1] )).reshape(*self.S.shape)
        tS = np.sort(tS, axis=0)
        #print ('%s-position calculation...' % self.xnyms, tS[0])
        tensor = torch.from_numpy(tS)

        #np.set_printoptions(threshold=sys.maxsize)
        #pprint.pprint (tS)
        return tensor

    @overrides
    def get_output_dim(self) -> int:
        return self.output_dim


import unittest

class TestingDistanceEmbeddings(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestingDistanceEmbeddings, self).__init__(*args, **kwargs)

    def test_setup(self):
        self.corpus = ['fine','honest', 'good', 'proficient', 'commodity', 'beneficial', 'skillful', 'soundly', 'respectable', 'skilful', 'near', 'practiced', 'sound', 'effective', 'expert', 'goodness', 'dear', 'in_effect', 'trade_good', 'well', 'serious', 'dependable', 'upright', 'thoroughly', 'salutary', 'ripe', 'unspoilt', 'honorable', 'full', 'estimable', 'in_force', 'secure', 'undecomposed', 'just', 'right', 'safe', 'adept', 'unspoiled', 'bad', 'unsound']
        self.xe = XnymEmbedder(vocab=self.corpus)

    def test_embed(self):
        self.test_setup()
        inputs = ['good', 'fine', 'bad', 'honest', 'dishonest', 'unsatisfactory', 'imprecise']
        Es = self.xe.forward(inputs)
        from sklearn.metrics.pairwise import cosine_similarity

        self.assertEqual (cosine_similarity(Es[0].reshape(1,-1), Es[2].reshape(1,-1))[0][0], -1)
        self.assertLess  (cosine_similarity(Es[1].reshape(1,-1), Es[0].reshape(1,-1)),       0)
        self.assertEqual (cosine_similarity(Es[1].reshape(1,-1), Es[3].reshape(1,-1))[0][0],  0)


if __name__ == "__main__":
    unittest.main()