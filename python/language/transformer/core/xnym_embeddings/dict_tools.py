def invert_dict(d):
    inverse = dict()
    for key in d:
        # Go through the list that is saved in the dict:
        for item in d[key]:
            # Check if in the inverted dict the key exists
            if item not in inverse:
                # If not create a new list
                inverse[item] = [key]
            else:
                inverse[item].append(key)
    return inverse


def balance_complex_tuple_dict(d):
    inverse = d.copy()
    for key in d:
        # Go through the list that is saved in the dict:
        for item in d[key]:
            # Check if in the inverted dict the key exists
            if item not in inverse:
                # If not create a new list
                inverse[item] = [key]
            else:
                if (item == key):
                    continue
                inverse[item].append(key)

    for key, val in inverse.items():
        inverse[key] = list(set(val))
    return inverse


def dict_compare(d1, d2, ignore_order=False):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    if ignore_order:
        modified = {o : (d1[o], d2[o]) for o in intersect_keys
                    if set(d1[o]) != set(d2[o])}

    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same

import collections

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


import unittest
class TestDicTools(unittest.TestCase):


    def test_balance_complex_tuple_dict(self):
        import pprint
        d = {
            ('differ'):['equal'],
            ('have','*','in', 'common'):[('differ','in'), 'differ', 'derive']
        }
        balanced = balance_complex_tuple_dict(dict(d))

        print (balanced)


if __name__ == '__main__':
    unittest.main()
