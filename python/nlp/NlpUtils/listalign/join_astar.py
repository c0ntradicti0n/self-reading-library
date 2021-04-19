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


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))


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

import ray

ray.shutdown()
ray.init(num_cpus=16) #, local_mode=True)
@ray.remote
def astar_path(a,b, G, source, target, ret = None):

    push = heappush
    pop = heappop

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guaranteed unique for all nodes in the graph.
    c = count()
    queue = [(0, next(c), source, 0, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}

    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent = pop(queue)

        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return ret, path

        if curnode in explored:
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost, h = enqueued[curnode]
            if qcost < dist:
                continue

        explored[curnode] = parent

        for neighbor in neighbors(*curnode, G):
            weight = diff(neighbor[0], a, neighbor[1], b)
            ncost = dist + weight

            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
                # if qcost <= ncost, a less costly path from the
                # neighbor to the source was already determined.
                # Therefore, we won't attempt to push this neighbor
                # to the queue
                if qcost <= ncost:
                    continue
            else:
                h = 0
            enqueued[neighbor] = ncost, h
            push(queue, (ncost + h, next(c), neighbor, ncost, curnode))

def index_finder(lst, item):
    """A generator function, if you might not need all the indices"""
    start = 0
    while True:
        try:
            start = lst.index(item, start)
            yield start
            start += 1
        except ValueError:
            break

def search_b(w, seq_a, seq_b, i, I, J, min_match_len):
    for j in index_finder(seq_b, w):
        n = 0
        candidate = None

        while True:
            if i + n >= I or j + n >= J:
                if candidate:
                    yield candidate
                break

            if seq_a[i + n] == seq_b[j + n]:
                if n >= min_match_len:
                    candidate = ((i, i + n), (j, j + n))
            else:
                if candidate:
                    yield candidate
                break
            n += 1


def r(gl):
    """ iterates generator to list """
    rl = []
    for l in gl:
        ll = list(l)
        if ll:
            rl.append(ll)
    return rl

def rg(gl):
    """ iterates generator to list """
    rl = []
    for l in gl:
        ll = list(l)
        if ll:
            yield rl.append(ll)
    return rl

def multiple_longest_common_sequence(seq_a, seq_b, min_match_len = 5):
    """

    >>> r(multiple_longest_common_sequence (['a','b','c','d'], ['aa','b','c','dd', 'b','c'], min_match_len = 1))
    [[((1, 2), (1, 2)), ((1, 2), (4, 5))]]

    >>> r(multiple_longest_common_sequence (['a','b','c','d'], ['aa','b','c','dd'], min_match_len = 1))
    [[((1, 2), (1, 2))]]


    """
    I = len(seq_a)
    J = len(seq_b)
    n = 0

    for i, w in enumerate(seq_a):
        if n:
            n -= 1
            continue

        r = list (search_b(w=w, seq_a=seq_a, seq_b=seq_b, i=i, I=I, J=J, min_match_len=min_match_len))


        if r:
            longest = max(r, key=lambda ab: ab[0][1]-ab[0][0])
            n = longest[0][1]-longest[0][0]

            yield r


def perf_plot():
    res = {}
    for i in range(100, 200):
        startTime = time.time()
        join_divide_and_conquer_a_star(words_a[:i], words_b[:i])
        res[i] = time.time() - startTime
        print (i)

    plt.plot(list(res.keys()), list(res.values()))
    plt.xlabel('length of lists', fontsize=18)
    plt.ylabel('s per run', fontsize=16)
    fig1 = plt.gcf()
    plt.show()
    plt.draw()
    fig1.savefig('join-a-star.png', dpi=100)


def join_divide_and_conquer_a_star(words_a: List[str], words_b: List[str]) -> List[Tuple[int, int]]:
    #print (list(pairwise(mlcs(words_a, words_b))))
    futures = []
    lens = []

    for i, (aws, bws) in enumerate(pairwise(multiple_longest_common_sequence(words_a, words_b))):
        for (a1, a2), (b1, b2) in aws:
            for (a1_, a2_), (b1_, b2_) in bws:

                    #with timeit_context('a-star-' + str(i)):

                    a = [w for w in words_a[a2:a1_] if w]
                    b = [w for w in words_b[b2:b1_] if w]
                    z = numpy.zeros((len(a), len(b)))

                    lens.append((len(a), len(b)))
                    if not a or not b:
                        print ("window before another" + str((aws, bws)) + "\n" + str((a, b)))
                        continue



                    futures.append(astar_path.remote(a, b, z, (0, 0), (z.shape[0] - 1,z.shape[1] - 1),
                                   ret = ((a1, a2), (b1, b2) , (a1_, a2_), (b1_, b2_))))
                    #path = astar_path(a, b, z, (0, 0), (z.shape[0] - 1,z.shape[1] - 1))

                    #pprint([(a[i], b[j]) for i, j in path])
                    #pa = paired.align(a,b)
                    #pprint(alignment_table(pa, a,b))
                    break
    res = (ray.get(futures))
    pairs = [(i + a1, j + b1) for ((a1, a2), (b1, b2) , (a1_, a2_), (b1_, b2_)), path in res for i, j in path ]
    print (max(lens, key=lambda t: t[0] + t[1]))
    return pairs


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


ray.shutdown()