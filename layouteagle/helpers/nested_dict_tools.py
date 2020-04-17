from collections import abc, Mapping, Collection
import numpy as np
from pip._vendor.pyparsing import basestring

def get_dict_wo_key(dictionary, key):
    """Returns a **shallow** copy of the dictionary without a key."""
    _dict = dictionary.copy()
    _dict.pop(key, None)
    return _dict

def flatten(*args):
    """
    Flatten a list.

        >>> from nltk.util import flatten
        >>> flatten(1, 2, ['b', 'a' , ['c', 'd']], 3)
        [1, 2, 'b', 'a', 'c', 'd', 3]

    :param args: items and lists to be combined into a single list
    :rtype: list
    """

    x = []
    for l in args:
        if not isinstance(l, (list, tuple)): l = [l]
        for item in l:
            if isinstance(item, (list, tuple)):
                x.extend(flatten(item))
            else:
                x.append(item)
    return x

def nested_dict_iter(nested):
    try:
        for key, value in nested.items():
            if isinstance(value, abc.Mapping):
                yield from nested_dict_iter(value)
            else:
                yield key, value
    except AttributeError:
        raise


def apply(data, f):
    stack = []
    stack.append(data)
    while stack:
        data = stack.pop()
        if isinstance(data, dict):
            for k,v in data.items():
                if isinstance(v, (dict,list,tuple)):
                    stack.append(v)
                else:
                    data[k] = f(v)
        if isinstance(data, list):
            for i,e in enumerate(data):
                if isinstance(e, (dict,list,tuple)):
                    stack.append(e)
                else:
                    data[i] = f(e)


import collections

def flattenDict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        try:
            new_key = parent_key + sep + k if parent_key else k
        except TypeError:
            new_key = str(k)
        if isinstance(v, collections.MutableMapping):
            items.extend(flattenDict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def reverseDict(dic, end_key, call=None, extra_keys=[], excluded_types=[str, int, float, np.array, np.float64]):
    """ Reverse nested dict, that the key and values are exchanged and non-uniqueness is replaced by lists

    >>> exampleset = { \
        'body': { \
            'abdomen': [{ \
                'arms': { \
                    'value': 2, \
                } \
            }, { \
                'legs': { \
                    'value': 2, \
                } \
            }], \
            'hands': { \
                'fingers': { \
                    'value': 5, \
                } \
            }, \
        } \
    }
    >>> import pprint
    >>> pprint.pprint(reverseDict(exampleset, end_key='value'))
    [{2: {'arms': {'abdomen': {'body': {}}}}},
     {2: {'legs': {'abdomen': {'body': {}}}}},
     {5: {'fingers': {'hands': {'body': {}}}}}]

    :param dic:
    :param condition:
    :return:
    """
    # https://stackoverflow.com/questions/35627441/using-recursion-to-reverse-a-dictionary-around-a-value-in-python

    if isinstance(end_key, str):
        def condition(x):
            return x == end_key
    if callable(end_key):
        def condition(x):
            return end_key(x)

    res = []


    def revnest(inp, keys=[]):
        res2 = res
        if type(inp) == list:
            #inp = {i: j[i] for j in inp for i in j}
            inp = {str(k):v for k,v in enumerate(inp)}
            register = False
        else:
            register = True

        if type(inp) in excluded_types or not inp:
            return

        if not isinstance(inp, (dict,list,tuple)):
            print ('non iterable type in dict, that is not ignored %s' % str(inp))
            return


        for x in inp:
            if condition(x):
                res2.append({tuple(inp[x]):{}})
                if call:
                    kwargs = {z: inp[z] for z in extra_keys}
                    call(inp[x], keys, **kwargs)
                else:
                    res2 = res2[-1][tuple(inp[x])]
                    for y in keys[::-1]:
                        res2[y] = {}
                        res2 = res2[y]
            else:
                try:
                    revnest(inp[x], keys + ([x] if register else []))
                except IndexError:
                    pass

    revnest(dic)
    return res


def recursive_map(something, func):
    if isinstance(something, dict):
        accumulator = {}
        for key, value in something.items():
            accumulator[key] = recursive_map(value, func)
        return accumulator
    elif isinstance(something, (list, tuple, set)):
        accumulator = []
        for item in something:
            accumulator.append(recursive_map(item, func))
        return type(something)(accumulator)
    else:
        return func(something)

