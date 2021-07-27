import time
from heapq import heappop, heappush
from itertools import count
from pprint import pprint
from typing import List, Set, Tuple

import numpy
from Levenshtein._levenshtein import distance
from more_itertools import pairwise
from texttable import Texttable

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

import paired
from contextlib import contextmanager

import matplotlib.pyplot as plt

with open("/home/finn/PycharmProjects/LayoutEagle/test/faust.txt") as f:
    text = "".join(f.readlines()) [:10000].replace("", "")

words_a = text.replace("n", "n ").split(" ")
words_b = text.replace("m", "m ").split(" ")
m = numpy.zeros((len(words_b), len(words_a)))


def lcs(S: str, T: str) -> Set[Tuple[int, int, str]]:
    """
    finds a common substring, returning both indices of findings
    >>> lcs("blablublobleblib", "papalapapp")
    [((1, 3), (4, 6), 'la')]

    >>> lcs("blablublobleblibblablublobleblib", "papalapapp")
    [((1, 3), (4, 6), 'la'), ((17, 19), (4, 6), 'la')]


    """
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = []
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = list()
                    longest = c
                    lcs_set.append(((i-c+1, i+1), (j-c+1, j+1), S[i-c+1:i+1]))
                elif c == longest:
                    lcs_set.append(((i-c+1, i+1), (j-c+1, j+1), S[i-c+1:i+1]))

    return lcs_set

def alignment_table(alignment, a, b):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["c", "r", "l", "r", "l"])
    table.add_rows(
        [
            ['i', 'w1', 'w2', 'i', 'j']
        ] + [
            [ii, a[i] if i or i==0 else "xxx", b[j] if j or j==0 else "xxx", i, j
             ]
            for ii, (i, j)
            in enumerate(alignment)]
    )
    return table.draw()

def last_words(pos, seq, min_len=10):
    n = pos
    L = 0
    while True:
        L += len(seq[n])
        n -= 1

        if L > min_len or n+1 <= 0:
            return "".join(seq[n+1:pos+1])

def after_words(pos, seq, min_len=10):
    n = pos
    L = 0
    while True:
        L += len(seq[n -1])
        n += 1

        if L > min_len or n >= len(seq) :
            return "".join(seq[pos+1:n+1])


sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)


def str_in_list_at(sl :List[str], pos:int, pos_str_start: int = 0, pos_str_end: int = 0, span: int = 4) -> str:
    """
    From a list of strings return the string before or after, given the positions


    >>> str_in_list_at("abc def gef hij".split(), 1, pos_str_end = 2, span = 6)
    'gefhij'


    >>> str_in_list_at("abc def gef hij".split(), 2, pos_str_start = 2, span = -6)
    'cdefge'


    >>> str_in_list_at("abc def gef hij".split(), 1, pos_str_start = 2, span = 6)
    'fgefhi'

    >>> str_in_list_at("abc def gef hij".split(), 2, pos_str_end = 2, span = -6)
    'defgef'


    >>> str_in_list_at("abc def gef hij".split(), 2, span = -3)
    'def'

    >>> str_in_list_at("abc def gef hij".split(), 0, span = -3)
    ''

    >>> str_in_list_at("abc def gef hij".split(), 3, span = 3)
    ''

    >>> str_in_list_at("abc def gef hij".split(), 2, span = 3)
    'hij'

    >>> str_in_list_at("abc def gef hij".split(), 1, span = 6)
    'gefhij'




    if the requested range is shorter, the result is also shorter as with the "abc"[:10] syntax, that
    gives "abc"


    """
    fb = sign(span)
    if fb == 0:
        return ""

    if pos_str_start == 0 and pos_str_end == 0:
        r = ""
    if pos_str_start > 0:
        r = (sl[pos][:pos_str_start] if fb < 0 else sl[pos][pos_str_start:])
    if pos_str_end > 0:
        r = (sl[pos][:pos_str_end + 1] if fb < 0 else sl[pos][pos_str_end + 1:])


    pos_new = pos + (1 if fb > 0 else -1)
    span_len = abs(span)


    while True:
        if pos_new < 0 or pos_new >= len(sl):
            return r

        if fb > 0:
            r = r + sl[pos_new][:span]

            if len(r) >= span_len:
                return r[:span]
            else:
                pos_new += 1

        elif fb < 0:
            r = sl[pos_new][span:] + r

            if len(r) >= span_len:
                return r[span:]
            else:
                pos_new -= 1



def diff (pos_a, seq_a,  pos_b, seq_b, span_len=5):
    if pos_a >= len(seq_a):
        raise IndexError

    ma = seq_a[pos_a]
    if pos_b >= len(seq_b):
        raise IndexError

    mb = seq_b[pos_b]
    candidates = lcs(ma, mb)
    scores = {}

    if len(candidates) == 0:
        return 100

    for c, ((i1, i2), (j1, j2), substring) in enumerate(candidates):
        # grow the match in both directions
        front_str_a   = str_in_list_at(seq_a, pos_a, pos_str_start = i1)
        back_string_a = str_in_list_at(seq_a, pos_a, pos_str_end = i2)
        front_str_b   = str_in_list_at(seq_b, pos_b, pos_str_start = j1)
        back_string_b = str_in_list_at(seq_b, pos_b, pos_str_end = j2)

        # how big is the difference with 5 characters at both sides
        scores[c] = distance(
            front_str_a + substring + back_string_a, front_str_b + substring + back_string_b
        )

    return min(scores.values())




def neighbors(u,v, G):
    if v + 1 < G.shape[1]:
        yield u, v + 1
    if u + 1 < G.shape[0]:
        yield u + 1, v
    if  v + 1 < G.shape[1] and u + 1 < G.shape[0]:
        yield u + 1, v + 1


if __name__ == "__main__":

    with timeit_context('a-star-117'):
        print((join_divide_and_conquer_a_star(words_a[:117], words_b[:117])))


    with timeit_context('joins'):
        multiple_longest_common_sequence(words_a, words_b)

        print (multiple_longest_common_sequence(words_a, words_b))

    #with timeit_context('join a start'):
    #    print (join_a_star(words_a, words_b))

    #with PyCallGraph(output=GraphvizOutput()):
    #    print(join_a_star(words_a, words_b))

    with timeit_context('a-star-modification'):
        print(join_divide_and_conquer_a_star(words_a, words_b))

    print(alignment_table(join_divide_and_conquer_a_star(words_a, words_b), words_a, words_b))

    with timeit_context('a-star-116'):
        print(join_divide_and_conquer_a_star(words_a[:116], words_b[:116]))

    with timeit_context('a-star-117'):
        print(join_divide_and_conquer_a_star(words_a[:117], words_b[:117]))


    with timeit_context('a-star-1000'):
        print(join_divide_and_conquer_a_star(words_a[:1000], words_b[:1000]))

    with timeit_context('paired-1000'):
        print (paired.align(words_a[:1000], words_b[:1000]))


    with timeit_context('paired'):
        print (paired.align(words_a, words_b))

    perf_plot()


if __name__ == "__main__":
    import doctest

    doctest.NORMALIZE_WHITESPACE = True
    doctest.testmod()


