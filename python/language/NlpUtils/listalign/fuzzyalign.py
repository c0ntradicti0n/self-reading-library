import difflib
import json

from diff_match_patch import diff_match_patch

from language.NlpUtils.listalign.helpers import preprocess, alignment_table, str_in_list_at, find_pos_at, AlignmentException
from language.NlpUtils.listalign.join_astar import lcs
from language.NlpUtils.listalign.suffixtreealign import suffix_align


def fuzzyalign(seq_a, seq_b):
    """

    :param seq_a:
    :param seq_b:
    :return:
    """

    seq_a, seq_b = preprocess([seq_a, seq_b])
    new_seq_a, new_seq_b, a_to_take, b_to_take = equalize_seq_b(seq_a, seq_b)

    s = diff_match_patch().diff_main("".join(new_seq_a), "".join(new_seq_b))

    s = [d for d in s if d[0] != 0]
    if not len(s) == 0:
        print("SEQUENCES DIFFER FOR ALIGNMENT " + str(s))

    diff = difflib.SequenceMatcher(a="".join(new_seq_a), b="".join(new_seq_b))
    print(diff.get_opcodes())

    r = suffix_align(new_seq_a, new_seq_b)

    print(alignment_table(r, new_seq_a, new_seq_b))
    r = [(a_to_take[i], b_to_take[j]) for i, j in r]
    return r


def do_op(param):
    pass


def equalize_ending(append_seq_a, append_seq_b, step):
    i = 5 * step
    while True:
        i += step * 5
        s_a = str_in_list_at(
            append_seq_a,
            pos=(0 if step > 0 else len(append_seq_a)),
            span=abs(i) * step
        )
        s_b = str_in_list_at(
            append_seq_b,
            pos=(0 if step > 0 else len(append_seq_b)),
            span=abs(i) * step
        )

        if (s_a[:i] == s_b[:i]) if step > 0 else (s_a[i:] == s_b[i:]):
            break
        else:
            sub = lcs(s_a, s_b)[0][2]

            print(sub, s_a, s_b)
            diff_a = s_a.split(sub)[0 if step > 0 else 1]
            diff_b = s_b.split(sub)[0 if step > 0 else 1]
            if diff_a and diff_b:
                continue

            if not diff_a and not diff_b:
                break
            if diff_b:
                append_seq_a[0 if step > 0 else -1] = \
                    (diff_b if step > 0 else '') + append_seq_a[0 if step > 0 else -1] + ('' if step > 0 else diff_b)
            if diff_a:
                append_seq_b[0 if step > 0 else -1] = \
                    (diff_a if step > 0 else '') + append_seq_b[0 if step > 0 else -1] + ('' if step > 0 else diff_a)
            if append_seq_a[step] == append_seq_b[step]:
                break

    sub = lcs("".join(append_seq_a), "".join(append_seq_b))[0][2]

    print([sub, "".join(append_seq_a), "".join(append_seq_b)])
    diff_a = "".join(append_seq_a).split(sub)[0 if step > 0 else 1]
    diff_b = "".join(append_seq_b).split(sub)[0 if step > 0 else 1]
    if not diff_a == diff_b:
        print("Equalizing error")

        from pprint import pprint

        diff = difflib.SequenceMatcher(a="".join(append_seq_a), b="".join(append_seq_b))
        pprint(diff.get_opcodes())
        print(append_seq_a)
        print(append_seq_b)
        equalize_ending(append_seq_a, append_seq_b, step)
        raise AlignmentException("after equalizing lists of strings, they are not equal!")


def strip_to_equal(append_seq_a, append_seq_b):
    diff = difflib.SequenceMatcher(a="".join(append_seq_a), b="".join(append_seq_b))
    print(diff.get_opcodes())
    equalize_ending(append_seq_a, append_seq_b, 1)
    equalize_ending(append_seq_a, append_seq_b, -1)

    return append_seq_a, append_seq_b


def equalize_seq_b(seq_a, seq_b, min_l=3):
    diff = difflib.SequenceMatcher(a="".join(seq_a), b="".join(seq_b))
    print(diff.get_opcodes())
    operations = diff.get_opcodes()
    operations = [o for o in operations if o[0] == 'equal']

    indices_transpose_a = {}
    indices_transpose_b = {}
    new_seq_a, new_seq_b = [], []

    for op in (operations):
        ia, cia = find_pos_at(seq_a, c_pos=op[1])
        ja, cja = find_pos_at(seq_a, c_pos=op[2])
        ib, cib = find_pos_at(seq_b, c_pos=op[3])
        jb, cjb = find_pos_at(seq_b, c_pos=op[4])
        ia = ia + (1 if cia != 0 else 0)
        ja = ja + (1 if cja != 0 else 0)
        ib = ib + (1 if cib != 0 else 0)
        jb = jb + (1 if cjb != 0 else 0)

        append_seq_a = seq_a[ia:ja]
        append_seq_b = seq_b[ib:jb]

        la = len(append_seq_a)
        lb = len(append_seq_b)

        if (la < min_l or lb < min_l):
            continue
        # we may have sliced some chars, that are in the word-string and we need to
        # trim them until they are equal.
        append_seq_a, append_seq_b = strip_to_equal(append_seq_a, append_seq_b)

        new_seq_a.extend(append_seq_a)
        new_seq_b.extend(append_seq_b)

        indices_transpose_a.update({len(indices_transpose_a) + i: i_a for i, i_a in enumerate(range(ia, ja))})
        indices_transpose_b.update({len(indices_transpose_b) + i: i_a for i, i_a in enumerate(range(ib, jb))})

    return new_seq_a, new_seq_b, indices_transpose_a, indices_transpose_b


if __name__ == "__main__":
    with open("../../test/data/pdfminer-vs-pdf2htmlex.json") as f:
        words_a, words_b = json.loads("".join(f.readlines()))

    print(alignment_table(fuzzyalign(words_a, words_b), words_a, words_b))

    print("does not work for shifts")
    seq_1 = 'cere frangit brum'.split(' ')
    seq_2 = 'frangit cerebrum'.split(' ')

    print(alignment_table(fuzzyalign(seq_1, seq_2), seq_1, seq_2))

    import doctest

    doctest.NORMALIZE_WHITESPACE = True
    doctest.testmod()
