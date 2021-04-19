from itertools import groupby
from pprint import pprint

from Levenshtein._levenshtein import distance
from diff_match_patch import diff_match_patch

from python.listalign.helpers import alignment_table
from python.listalign.suffixtreealign import suffix_align

def equalize_seqs(seq_a, seq_b, s, moves):
    print(seq_a)
    print(seq_b)
    a_diff = "".join([d[1] for d in s if d[0] <= diff_match_patch.DIFF_EQUAL])
    b_diff = "".join([d[1] for d in s if d[0] >= diff_match_patch.DIFF_EQUAL])
    bt = suffix_align(seq_b, b_diff)

    # to make words in seq b we have to see, which blocks need to change with which
    # indices. Here {1:0} means, that all what is in block 1 needs to be transposed to
    # where block 0 is and all in block zero need to be transposed at the position of
    # block 1
    diff_transposition = {
        (a_diff.index(m[1]), a_diff.index(m[1]) + len(m[1])): (b_diff.index(m[1]), b_diff.index(m[1]) + len(m[1])) for m
        in moves}

    seq_b_mod = [c for c in "".join(seq_b.copy())]
    transpose_tokens(diff_transposition, seq_b_mod)

    mod_align = suffix_align(seq_b_mod, seq_a)

    # now undo edits by transposing the alignment back to original
    transpose_indices({v: k for k, v in diff_transposition.items()}, mod_align)

    db = dict((v, k) for k, v in bt)
    res = list(set(((a_i, db[mod_i]) for mod_i, a_i in mod_align)))

    res = list(sorted(res, key=lambda x: x[0] * 100 + x[1]))

    return res


def transpose_tokens(diff_transposition, seq_b_mod):
    for (j1, j2), (i1, i2) in reversed(diff_transposition.items()):

        moving_seq = seq_b_mod[i1:i2]
        seq_b_mod[i1:i2] = []
        for c in reversed(moving_seq):
            seq_b_mod.insert(j1, c)


def transpose_indices(diff_transposition, seq_b_mod):
    for (j1, j2), (i1, i2) in reversed(diff_transposition.items()):
        moving_seq1 = seq_b_mod[i1:i2]
        moving_seq2 = seq_b_mod[j1:j2]
        seq_b_mod[i1:i2] = [(t1[0], t2[1]) for t1, t2 in zip(moving_seq2, moving_seq1)]
        seq_b_mod[j1:j2] = [(t1[0], t2[1]) for t2, t1 in zip(moving_seq2, moving_seq1)]


def diff_move_alignment(seq_a, seq_b):
    a = seq_a
    b = seq_b
    s = diff_match_patch().diff_main("".join(a), "".join(b))
    dels = [d for d in s if d[0] == diff_match_patch.DIFF_DELETE]
    ins = [d for d in s if d[0] == diff_match_patch.DIFF_INSERT]
    move = [d for d in dels for i in ins if distance(i[1], d[1]) < 5]
    unequal_edits = [d for d in dels for i in ins if distance(i[1], d[1]) > 5]

    print(move)
    return equalize_seqs(seq_a, seq_b, s, move)


if __name__ == "__main__":
    import time
    from texttable import Texttable
    from contextlib import contextmanager

    with open("../../test/data/faust.txt") as f:
        text = "".join(f.readlines())[:100000000].replace("", "")

    words_a = text.replace("n", "n ").split(" ")
    words_b = text.replace("m", "m ").split(" ")


    @contextmanager
    def timeit_context(name):
        startTime = time.time()
        yield
        elapsedTime = time.time() - startTime
        print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))


    seq_1 = 'jumpedoverthelazydogThequickbrownfox'.replace('o', 'o ').split(' ')
    seq_2 = 'The quick brown fox jumped over the lazy dog '.replace('e', 'e ').split(' ')

    print(alignment_table(diff_move_alignment(seq_1, seq_2), seq_1, seq_2))

    seq_1 = 'cere frangit brum'.split(' ')
    seq_2 = 'frangit cerebrum'.split(' ')

    print(alignment_table(diff_move_alignment(seq_1, seq_2), seq_1, seq_2))

    seq_1 = 'umpedoverthelazydogThequickbrownfox'.replace('o', 'o ').split(' ')
    seq_2 = 'The quick brown fox umped o\'er the lazy dog '.replace('e', 'e ').split(' ')

    print(diff_move_alignment(seq_1, seq_2))
