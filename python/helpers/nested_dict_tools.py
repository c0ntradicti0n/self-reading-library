try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
import numpy as np

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




# Note: Typing for elements of iterable types such as Set, List, or Dict
# use a variation of Run Length Encoding.

def type_spec_iterable(iterable, name="Types of it are "):
    def iterable_info(iterable):
        # With an iterable for it to be comparable
        # the identity must contain the name and length
        # and for the elements the type, order and count.
        length = 0
        types_list = []
        pervious_identity_type = None
        pervious_identity_type_count = 0
        first_item_done = False
        for e in iterable:
            item_type = type_spec(e)
            if (item_type != pervious_identity_type):
                if not first_item_done:
                    first_item_done = True
                else:
                    types_list.append((pervious_identity_type, pervious_identity_type_count))
                pervious_identity_type = item_type
                pervious_identity_type_count = 1
            else:
                pervious_identity_type_count += 1
            length += 1
        types_list.append((pervious_identity_type, pervious_identity_type_count))
        return (length, types_list)
    (length, identity_list) = iterable_info(iterable)
    element_types = ""
    for (identity_item_type, identity_item_count) in identity_list:
        if element_types == "":
            pass
        else:
            element_types += ","
        element_types += identity_item_type
        if (identity_item_count != length) and (identity_item_count != 1):
            element_types += "[" + str(identity_item_count) + "]"

    if name in ["list", "set", "dict"]:
        name = name.title()
    result = name + "=" + str(length) + "[" + element_types + "]"
    return result

def list2dict(d, key):
    try:
        if isinstance(d, dict):
            return {k: list2dict(v, key) for k, v in d.items()}
        elif isinstance(d, (set, list)):
            return {key(e): list2dict(e, key) if isinstance( e, dict) else list2dict(e, key)  for e in d}
        else:
            return d
    except:
        return d

def type_spec_dict(dict, name):
    def dict_info(dict):
        # With a dict for it to be comparable
        # the identity must contain the name and length
        # and for the key and value combinations the type, order and count.
        length = 0
        types_list = []
        pervious_identity_type = None
        pervious_identity_type_count = 0
        first_item_done = False
        for (k, v) in dict.items():
            key_type = type_spec(k)
            value_type = type_spec(v)
            item_type = (key_type, value_type)
            if (item_type != pervious_identity_type):
                if not first_item_done:
                    first_item_done = True
                else:
                    types_list.append((pervious_identity_type, pervious_identity_type_count))
                pervious_identity_type = item_type
                pervious_identity_type_count = 1
            else:
                pervious_identity_type_count += 1
            length += 1
        types_list.append((pervious_identity_type, pervious_identity_type_count))
        return (length, types_list)
    (length, identity_list) = dict_info(dict)
    element_types = ""
    for ((identity_key_type,identity_value_type), identity_item_count) in identity_list:
        if element_types == "":
            pass
        else:
            element_types += ","
        identity_item_type = "(" + identity_key_type + "," + identity_value_type + ")"
        element_types += identity_item_type
        if (identity_item_count != length) and (identity_item_count != 1):
            element_types += "[" + str(identity_item_count) + "]"
    result = name + "[" + str(length) + "]<" + element_types + ">"
    return result

def type_spec_tuple(tuple, name):
    return name + "<" + ", ".join(type_spec(e) for e in tuple) + ">"

def type_spec(obj):
    object_type = type(obj)
    name = object_type.__name__
    if (object_type is int) or (object_type is bytes) or (object_type is str) or (object_type is bool) or (object_type is float):
        result = name
    elif object_type is type(None):
        result = "(none)"
    elif (object_type is list) or (object_type is set):
        result = type_spec_iterable(obj, name)
    elif (object_type is dict):
        result = type_spec_dict(obj, name)
    elif (object_type is tuple):
        result = type_spec_tuple(obj, name)
    else:
        if name == 'ndarray':
            ndarray = obj
            ndarray_shape = "[" + str(ndarray.shape).replace("L","").replace(" ","").replace("(","").replace(")","") + "]"
            ndarray_data_type = str(ndarray.dtype).split("'")[1]
            result = name + ndarray_shape + "<" + ndarray_data_type + ">"
        else:
            result = "Unknown type: " , name
    return result