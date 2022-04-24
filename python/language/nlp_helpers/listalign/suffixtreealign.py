from collections import defaultdict, deque
from typing import List, Tuple

from language.nlp_helpers.listalign.helpers import alignment_table
from python.helpers .time_tools import timeit_context


def suffix_align(*texts, _tree=None) -> List[Tuple[int, int]]:
    tree = build_suffix_tree(texts) if not _tree else _tree

    path_to_return = []
    w_pos_b = 0
    w_pos_a = 0
    z = 1

    for iw, word in enumerate(texts[0]):
        for ic, ch in enumerate(word):
            node = tree[ch]

            new_w_pos_a = iw

            try:
                c_pos_b, new_w_pos_b = find_position(node)
            except StopIteration:
                # continue

                print("not found")
                print(path_to_return)
                return path_to_return

            c_pos_b += 1

            w_pos_a, w_pos_b, z = update_variables(new_w_pos_a, new_w_pos_b, path_to_return, texts, w_pos_a, w_pos_b, z)

    return path_to_return


def find_position(node):
    t = node[1].popleft()
    new_w_pos_b, c_pos_b = t
    return c_pos_b, new_w_pos_b


def update_variables(new_w_pos_a, new_w_pos_b, path_to_return, texts, w_pos_a, w_pos_b, z):
    if new_w_pos_b != w_pos_b or new_w_pos_a != w_pos_a or len(path_to_return) == 0:
        w_pos_b = new_w_pos_b
        w_pos_a = new_w_pos_a
        z = find_following_zero_texts(texts, w_pos_b)
        path_to_return.append((w_pos_a, w_pos_b))
    return w_pos_a, w_pos_b, z


def build_suffix_tree(texts):
    tree = defaultdict(lambda: defaultdict(lambda: deque()))

    for it, t in enumerate(texts):
        for iw, word in enumerate(t):
            for ic, ch in enumerate(word):
                tree[ch][it].append((iw, ic))

    return tree


def find_following_zero_texts(texts, w_pos_b):
    for iz, t in enumerate(texts[1][w_pos_b + 1:w_pos_b + 10]):
        if t != "":
            return iz + 1

    return 1


if __name__ == "__main__":
    import time
    import paired
    import matplotlib.pyplot as plt

    with open("../../test/data/faust.txt") as f:
        text = "".join(f.readlines())[:100000000].replace("", "")

    words_a = text.replace("n", "n ").split(" ")
    words_b = text.replace("m", "m ").split(" ")

    print("does not work for shifts")
    seq_1 = 'cere frangit brum'.split(' ')
    seq_2 = 'frangit cerebrum'.split(' ')

    print(alignment_table(suffix_align(seq_1, seq_2), seq_1, seq_2))

    a = ['jumpedo', 'verthelazydo', 'gThequickbro', 'wnfo', 'x']
    b = ['jumpe', 'd', 'ove', 'r', 'the', '', 'lazy', 'dog', 'The', '', 'quick', 'brown', 'fox', '']
    print(alignment_table(suffix_align(a, b), a, b))
    a = ['jumpedo', 'verthelazydo', 'gThequickbro', 'wnfo', 'x']
    b = ['jump', 'd', 'ove', 'r', 'the', '', 'lazy', 'dog', 'The', '', 'quick', 'brown', 'fox', '']
    print(alignment_table(suffix_align(b, a), b, a))

    seq_1 = 'Thequickbrownfoxjumpedoverthelazydog'.replace('o', 'o ').split(' ')
    seq_2 = 'The quick brown fox jumped over the lazy dog'.replace('e', 'e ').split(' ')

    print(alignment_table(suffix_align(seq_1, seq_2), seq_1, seq_2))

    print(alignment_table(paired.align(seq_1, seq_2), seq_1, seq_2))

    with timeit_context('suffix-align-1000-1000'):
        path = (suffix_align(words_a[:1000], words_b[:1000]))
        print(alignment_table(path, words_a, words_b))

    with timeit_context('paired-1000-1000'):
        print(paired.align(words_a[:1000], words_b[:1000]))

    with timeit_context(f'full suffix-align on {len(words_a)}x{len(words_b)}'):
        x = suffix_align(words_a, words_b)


    def perf_plot():
        res = {}
        for i in range(100, 100000, 1000):
            start_time = time.time()
            suffix_align(words_a[:i], words_b[:i])
            res[i] = time.time() - start_time
            print(f'{i}.', end='')

        plt.plot(list(res.keys()), list(res.values()))
        plt.xlabel('length of lists', fontsize=18)
        plt.ylabel('s per run', fontsize=16)
        fig1 = plt.gcf()
        plt.show()
        plt.draw()
        fig1.savefig('../../suffix-align.png', dpi=100)


    with timeit_context('performance plot'):
        perf_plot()


    def perf_plot_paired():
        res = {}
        for i in range(100, 1000, 10):
            start_time = time.time()
            suffix_align(words_a[:i], words_b[:i])
            la = time.time() - start_time
            start_time = time.time()
            paired.align(words_a[:i], words_b[:i])
            pa = time.time() - start_time
            res[i] = (la, pa)
            print(f'{i}.', end='')

        plt.plot(list(res.keys()), list(x1[0] for x1 in res.values()), label='list align')
        plt.plot(list(res.keys()), list(x2[1] for x2 in res.values()), label='paired align')

        plt.xlabel('length of lists', fontsize=18)
        plt.ylabel('s per run', fontsize=16)
        plt.legend()
        fig1 = plt.gcf()
        plt.show()
        plt.draw()
        fig1.savefig('../../suffix-align_pa.png', dpi=100)


    with timeit_context('performance plot against paired'):
        perf_plot_paired()

    import doctest

    doctest.NORMALIZE_WHITESPACE = True
    doctest.testmod()
