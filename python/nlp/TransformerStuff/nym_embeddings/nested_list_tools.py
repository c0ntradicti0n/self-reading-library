from more_itertools import replace
import collections
import functools
import operator


def flatten(iterable):
    for el in iterable:
        if isinstance(el, collections.Iterable) and not isinstance(el, str):
            yield from flatten(el)
        else:
            yield el

def flatten_reduce(iterable):
    if not isinstance(iterable[0], dict):
        return functools.reduce(operator.add, iterable)
    else:
        return iterable


def curry(fun, *args, **kwargs):
    def fun_new(x):
        return fun (x, *args, **kwargs)
    return fun_new

def on_each_level (lol, fun, out = []):
    for x in lol:
        if not isinstance(x, list):
            out.append(fun(x))
        else:
            out.append(on_each_level(x, fun, []))
    return out


def gen_dict_extract(var, key):
    if isinstance(var, dict):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, (dict, list)):
                yield from gen_dict_extract(v, key)
    elif isinstance(var, list):
        for d in var:
            yield from gen_dict_extract(d, key)


def on_each_iterable (lol, fun):
    out = []
    if isinstance(lol, collections.Iterable) and not isinstance(lol, str):
        for x in lol:
            out.append(on_each_iterable(x, fun))
        out = fun(out)
    else:
        out = lol
    return out


def stack_matryoshka(nesting_list):
    nesting_list = sorted(nesting_list, key=lambda x: len(x))
    n = 0
    while n < (len(nesting_list) - 1):
        to_fit_there = nesting_list[n]
        flatted_to_fit_there = list(flatten(to_fit_there[:]))

        def is_fitting(*xs):
            flatted_compared = list(flatten(xs[:]))
            if type(flatted_compared[-1]) == object:
                return False
            try:
                decision = flatted_compared == list(flatted_to_fit_there)
            except TypeError:
                return False
            return decision

        for m in range(n + 1, len(nesting_list)):
            through = list(nesting_list[m])

            def replacing_fun(x):
                return list(replace(list(x), is_fitting, [to_fit_there], window_size=len(to_fit_there)))

            nesting_list[m] = on_each_iterable(through, replacing_fun)

        n = n + 1
    return (nesting_list[-1])

def replace_pattern(lst, pattern_sequence, replacement, expand=False):
    out = lst[:]
    len_difference = 0
    for i, e in enumerate(lst):

        if pattern_sequence[0](e):
            i1 = i
            f = 1
            if len(lst) - i < len(pattern_sequence):
                f = 0
            for fun_e1, e2 in zip(pattern_sequence, lst[i:]):
                if not fun_e1(e2):
                    f = 0
                    break
                i1 += 1
            if f == 1:
                del out[i+ +len_difference : i1  + len_difference]
                if expand:
                    for x in list(replacement):
                        out.insert(i + len_difference, x)
                else:
                    for j,x in enumerate(list(replacement)):
                        if '\\' in x:
                            n = int(x[1])
                            out.insert(i+j + len_difference, lst[i+n])
                        else:
                            out.insert(i+j + len_difference, x)
                    len_difference += len(replacement) - len(pattern_sequence)

    return out

def check_for_tuple_at_index(l, t, start, wildcard='*'):
    suspend = False

    i1 = start
    e1 = l[i1]
    i2 = 0
    try:
        e2 = t[i2]
    except IndexError:
        x=1
        raise

    # find_end
    while i1 <= len(l):
        found = False
        if e1 == e2:
            found = True
            i2 += 1
            if i2 == len(t):
                return True
            e2 = t[i2]
            i1 += 1
            if i1 == len(l):
                return False
            e1 = l[i1]
            continue
        elif e2 == wildcard:
            i2 += 1
            if i2 == len(t):
                return True
            e2 = t[i2]
            found = True
            suspend = True
            continue
        elif suspend:
            i1 += 1
            if i1 == len(l):
                return False
            e1 = l[i1]
        else:
            found = False
            break
    else:
        return False
    return found


import unittest


def check_for_tuple_in_list (l, t, wildcard='*'):
    found = False
    suspend = False
    for i1, e1 in enumerate(l):
        # find start
        i2 = 0
        if i2 == len(t):
            break
        e2 = t[i2]

        # find_end
        while i1 < len(l):
            found = False
            if e1 == e2:
                found = True
                i2+=1
                if i2 == len(t):
                    return True
                e2 = t[i2]
                i1+=1
                if i1 == len(l):
                    return False
                e1 = l[i1]
                continue
            elif e2 == wildcard:
                i2 += 1
                if i2 == len(t):
                    return True
                e2 = t[i2]
                found = True
                suspend = True
                continue
            elif suspend:
                i1 += 1
                if i1 == len(l):
                    return False
                e1 = l[i1]
            else:
                found = False
                break
        else:
            return False
    return found

import unittest

class TestNLT(unittest.TestCase):
    def test_check_for_tuple_at_index(self):
        l  = [1,2,3,4,5,6,7,8,9]
        t1 = (1,2,3)
        t2 = (4,5,6)
        t3 = (3,)
        t4 = (4,'*')
        t5 = (9,)

        self.assertTrue (check_for_tuple_at_index(l,t1, start=0))
        self.assertFalse (check_for_tuple_at_index(l,t1, start=1))
        self.assertTrue (check_for_tuple_at_index(l,t2, start=3))
        self.assertFalse (check_for_tuple_at_index(l,t2, start=8))
        self.assertTrue (check_for_tuple_at_index(l,t3, start=2))
        self.assertFalse (check_for_tuple_at_index(l,t3, start=8))
        self.assertTrue (check_for_tuple_at_index(l,t4, start=3))
        self.assertTrue (check_for_tuple_at_index(l,t5, start=8))


    def test_check_for_tuple_in_list(self):
        l  = [1,2,3,4,5,6,7,8,9]
        t1 = (1,2,3)
        t2 = (1,2,4)
        t3 = (8,9,10)
        t4 = (7,8,9)
        t5 = (1,2,3,4,5,6,7,8,9,0)

        t6 = (1,'*',3)
        t7 = (1,'*',4)
        t8 = (1,'*',9)
        t9 = (6,'*',9)
        t10= (6,'*',10)
        t11= (6,'*',7)
        t12 = (1,2)

        self.assertTrue (True  == check_for_tuple_in_list(l,t1))
        self.assertTrue (False == check_for_tuple_in_list(l,t2))
        self.assertTrue (False == check_for_tuple_in_list(l,t3))
        self.assertTrue (True  == check_for_tuple_in_list(l,t4))
        self.assertTrue (False == check_for_tuple_in_list(l,t5))
        self.assertTrue (True  == check_for_tuple_in_list(l,t6))
        self.assertTrue (True  == check_for_tuple_in_list(l,t7))
        self.assertTrue (True  == check_for_tuple_in_list(l,t8))
        self.assertTrue (True  == check_for_tuple_in_list(l,t9))
        self.assertTrue (False == check_for_tuple_in_list(l,t10))
        self.assertTrue (True  == check_for_tuple_in_list(l,t11))
        self.assertTrue (True  == check_for_tuple_in_list(l,t12))

        t12 = 'derive'
        l = ['have', 'both', 'the', 'name', 'the', 'definition', 'answer', 'to', 'the', 'name', 'in', 'common']
        self.assertTrue (False  == check_for_tuple_in_list(l,t12))

if __name__ == '__main__':
    unittest.main()