import logging
from collections import defaultdict, OrderedDict
from typing import List

import numpy

from layouteagle.helpers.nested_dict_tools import recursive_map, flatten


def partition_iterable(to_split, indices):
    return [to_split[i:j] for i, j in zip([0]+indices, indices + [None])]


def sorted_by_zipped(x):
    return list(_x[0] for _x in sorted(zip(*x), key=lambda __x:__x[1]))


def find_repeating(lst, count=2):
    ret = []
    counts = [None] * len(lst)
    for i in lst:
        if counts[i] is None:
            counts[i] = i
        elif i == counts[i]:
            ret += [i]
            if len(ret) == count:
                return ret


def reverse_dict_of_lists(d):
    reversed_dict = defaultdict(list)
    for key, values in d.items():
        for value in values:
            reversed_dict[value].append(key)
    return reversed_dict

def threewise(iterable):
    "s -> (s0,s1,s2), (s1,s2, s3), (s2, s3, s4), ..."
    iterable = list(iterable)
    l = len(iterable)
    for i in range(1,l-1):
        yield iterable[i-1], iterable[i], iterable[i+1]


def nd_fractal(s_value, s_tuple, n=3, lense = 1):
    """   [10, 40, 70] ->

          10- >  [-10.  10.  30.]
          40 ->  [ 20. 40. 60.]
          70 ->  [ 50. 70. 90.]

    """
    mid = numpy.mean(s_tuple)
    new_range = s_value + lense * 2/n * (numpy.array(s_tuple) - mid )
    return new_range


class Lookup:
    token_to_id = OrderedDict()
    id_to_token = OrderedDict()

    def __init__(self, tokens: List):
        if all(isinstance(t, List) for t in tokens):
          tokens = flatten(tokens)
        self.id_to_token = OrderedDict(sorted((i, t) for i, t in list(enumerate(sorted(tokens)))))
        self.token_to_id = OrderedDict(sorted((k,v) for v,k in self.id_to_token.items()))

    def __call__(self, id_s=None, token_s=None):
        assert bool(id_s) ^ bool(token_s)
        if id_s:
            return list(recursive_map(id_s, lambda x: self.id_to_token[x]))
        if token_s:
            return list(recursive_map(token_s, lambda x: self.token_to_id[x]))

    def ids_to_tokens(self, ids):
        try:
            return [self.id_to_token[id] for id in ids]
        except:
            logging.error(f"{[id for id in ids if id not in self.id_to_token]} not in labels dict {self.id_to_token}")


def pad_along_axis(array: numpy.ndarray, target_length, axis=0):

    pad_size = target_length - array.shape[axis]
    axis_nb = len(array.shape)

    if pad_size < 0:
        return array

    npad = [(0, 0) for x in range(axis_nb)]
    npad[axis] = (0, pad_size)

    b = numpy.pad(array, pad_width=npad, mode='constant', constant_values=0)

    return b







import unittest

class ListToolsTest(unittest.TestCase):
    def test_third_fractal(self):
        s_tuple = (10,40,70)
        for s in s_tuple:
            new_range = nd_fractal(s, s_tuple)
            print (new_range)
            s1, s2, s3 = s_tuple
            ds = s3 - s1
            new_len = ds * 2 / 3
            logging.error(f" {s_tuple} is now {new_range}")
            #assert new_range.max() - new_range.min() == new_len
            #assert new_range[0] >= s1 and new_range[2] <= s3



if __name__ == '__main__':
    unittest.main()


