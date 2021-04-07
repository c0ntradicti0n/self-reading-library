from itertools import zip_longest

import logging

from fastDamerauLevenshtein import damerauLevenshtein

from python.layouteagle.pathant.logger import setup_logging

setup_logging(default_level=logging.DEBUG)
logger = logging.getLogger(__name__)


def alignment_table(alignment, a, b):
    from texttable import Texttable
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["c",  "r",  "l", 'r', 'l'])
    table.add_rows(
        [
            ['i',  'i1', "->", 'i2', '->']
        ] + [
            [i, x, a[x], y, b[y]
        ]
          for i, (x, y)
          in enumerate(alignment)]
    )
    return table.draw()

def better_now_than_later(s1, s2, m):
    if damerauLevenshtein(s1,m, similarity=True) > 0.01:
        return damerauLevenshtein(s1,m, similarity=True) > damerauLevenshtein(s2, m, similarity=True)
    else:
        return False

def align(a, b):
    """
    Is a zipper for crazy tokenized lists of strings

    >>> b = ['it,', 'my', 'good', 'knight', '!', 'There', 'ought', 'to', 'be', 'laws', 'to', 'protect', 'the', 'body', 'of', 'acquired', 'knowledge.', 'Take', 'one', 'of', 'our', 'good', 'pupils,', 'for', 'example', ':', 'modest', 'and', 'diligent,', 'from', 'his', 'earliest', 'grammar', 'classes', 'hes', 'kept', 'a', 'little', 'notebook', 'full', 'of', 'phrases.', 'After', 'hanging', 'on', 'the', 'lips', 'of', 'his', 'teachers', 'for', 'twenty', 'years,', 'hes', 'managed', 'to', 'build', 'up', 'an', 'intellectual', 'stock', 'in', 'trade', ';', 'doesnt', 'it', 'belong', 'to', 'him', 'as', 'if', 'it', 'were', 'a', 'house,', 'or', 'money', '?', 'Paul', 'Claudel,', 'Le', 'soulier', 'de', 'satin,', 'Day', 'III,', 'Scene', 'ii', 'There', 'is', 'an', 'economy', 'of', 'cultural', 'goods,', 'but', 'it', 'has', 'a', 'specific', 'logic.', 'Sociology', 'endeavours', 'to', 'establish', 'the', 'conditions', 'in', 'which', 'the', 'consumers', 'of', 'cultural', 'goods,', 'and', 'their', 'taste', 'for', 'them,', 'are', 'produced,', 'and', 'at', 'the', 'same', 'time', 'to', 'describe', 'the', 'different', 'ways', 'of', 'appropriating', 'such', 'of', 'these', 'objects', 'as', 'are', 'regarded', 'at', 'a', 'particular', 'moment', 'as', 'works', 'of', 'art,', 'and', 'the', 'social', 'conditions', 'of', 'the', 'constitution', 'of', 'the', 'mode', 'of', 'appropriation', 'that', 'is', 'considered', 'legitimate.']
    >>> a = ['i', 't,', 'my', 'go', 'od', 'kn', 'ight!', 'There', 'oug', 'ht', 'to', 'b', 'e', 'laws', 'to', '', 'protect', 'the', 'b', 'od', 'y', 'of', 'acquir', 'ed', 'know', 'ledg', 'e.', '', '', 'Take', 'one', 'of', 'our', 'g', 'ood', 'p', 'upils,', 'for', 'ex', 'ample:', 'mo', 'dest', '', 'and', 'd', 'iligent,', 'from', 'hi', 's', 'earl', 'iest', 'gramm', 'ar', 'c', 'lasse', 's', 'he', 's', '', 'kept', 'a', 'lit', 'tle', 'no', 'tebo', 'ok', 'full', 'o', 'f', 'ph', 'rases.', '', '', 'After', 'hanging', 'on', 'the', 'lips', 'o', 'f', 'h', 'is', 't', 'each', 'ers', 'for', 'twen', 'ty', '', 'years,', 'he', 's', 'manag', 'ed', 'to', 'bu', 'ild', 'up', 'an', 'in', 'tellec', 'tual', 'stock', 'in', '', 'trade;', 'doesn', 't', 'it', 'belong', 'to', 'him', 'a', 's', 'if', 'it', 'we', 're', 'a', 'house,', 'or', '', 'mon', 'ey?', '', '', '', 'Paul', 'Cl', 'aude', 'l,', 'L', 'e', 'soulier', 'd', 'e', 'satin,', 'D', 'ay', 'III,', 'S', 'cen', 'e', 'ii', '', '', '', 'There', 'is', 'an', 'eco', 'no', 'my', 'o', 'f', 'cu', 'ltu', 'ral', 'good', 's,', 'b', 'ut', 'i', 't', 'has', 'a', 'specifi', 'c', 'l', 'ogi', 'c.', 'Soci', 'olo', 'gy', '', 'endeav', 'ou', 'rs', 'to', 'establ', 'ish', 'th', 'e', 'con', 'ditio', 'ns', 'in', 'whi', 'ch', 't', 'he', 'consu', 'mers', 'o', 'f', 'cult', 'ural', 'g', 'oo', 'ds,', '', 'and', 't', 'hei', 'r', 'tast', 'e', 'for', 't', 'he', 'm,', 'are', 'p', 'ro', 'du', 'ced,', 'and', 'at', 'th', 'e', 's', 'ame', 'ti', 'me', 't', 'o', 'd', 'esc', 'ribe', 't', 'he', '', 'differen', 't', 'ways', 'of', 'ap', 'pro', 'priat', 'in', 'g', 'su', 'ch', 'o', 'f', 'thes', 'e', 'obj', 'ects', 'as', 'are', 'reg', 'ard', 'ed', 'at', 'a', '', 'parti', 'cul', 'ar', 'mo', 'ment', 'as', 'works', 'o', 'f', 'art', ',', 'an', 'd', 'th', 'e', 'so', 'cial', 'co', 'ndi', 'tio', 'ns', 'o', 'f', 'the', 'co', 'ns', 'tit', 'ution', 'o', 'f', '', 'the', 'mo', 'de', 'o', 'f', 'ap', 'pro', 'priat', 'ion']
    >>> alignment = align (a,b)
    >>> print (alignment_table(alignment, a, b))

    >>> a = ['Intro', 'duction', 'f', 'rom', ':', '', 'Distinction', ':', '', 'A', 'Social', 'Critique', 'of', 'the',
    ... 'J', 'udgement', 'of', 'Taste', '', 'by', 'Pierr', 'e', 'Bou', 'rdieu', '198', '4', 'Introduction',  'You',
    ... 'said', 'i', 't,', 'my', 'go', 'od', 'kn', 'ight', 'There', 'oug', 'ht', 'to', 'b', 'e', 'laws', 'to', '',
    ... 'protect', 'the', 'b', 'od', 'y', 'of', 'acquir', 'ed', 'know', 'ledg', 'e.', '', '', 'Take', 'one', 'of',
    ... 'our', 'g', 'ood', 'p', 'upils,', 'for', 'ex', 'ample:', 'mo', 'dest', '', 'and', 'd', 'iligent,', 'from',
    ... 'hi', 's', 'earl', 'iest', 'gramm', 'ar', 'c', 'lasse', 's', 'he', 's', '', 'kept', 'a', 'lit']
    >>> b = ['Introduction', 'from', ':', 'Distinction', ':', 'A', 'Social', 'Critique', 'of', 'the', 'Judgement', 'of',
    ... 'Taste', 'by', 'Pierre', 'B', 'our', 'dieu', '1984', 'Introduction', 'You', 'said', 'it', ',', 'my', 'good',
    ... 'knight', 'There', 'ought', 'to', 'be', 'laws', 'to', 'protect', 'the', 'body', 'of', 'acquired', 'knowledge',
    ... '.', 'Take', 'one', 'of', 'our', 'good', 'pupils', ',', 'for', 'example', ':', 'modest', 'and', 'diligent', ',',
    ... 'from', 'his', 'earliest', 'grammar', 'classes', 'he', 's', 'kept', 'a', 'lit']
    >>> alignment = align (a,b)
    >>> print (alignment_table(alignment, a, b))

    """
    if not "".join(a) == "".join(b):
        print([(i, t) for i, t in enumerate(list(zip_longest("".join(a), "".join(b))))
               if t[0] != t[1]])
        logger.error("window texts must be equal")

    i, j = 0, 0
    alignment = []
    s_all = "".join(a)
    s_b = "".join(b)
    s_add = ""
    s_add_next = ""


    while i < len(a) and j < len(b):
        ma = a[i]
        ma_next = a[i + 1] if i<len(a)-1 else ""

        mb = b[j]

        print(damerauLevenshtein(s_add,mb, similarity=True) , damerauLevenshtein(s_add_next, mb, similarity=True), better_now_than_later(s_add, s_add_next, mb), (s_add, s_add_next, mb, ))

        while better_now_than_later(s_add, s_add_next, mb) or not mb in s_b:
            if ma in mb or mb in ma:
                alignment.append((i, j))
            s_add = ""
            s_add_next = ""

            j += 1
            mb = b[j]
        else:
            alignment.append((i, j))

        if s_all.startswith(ma):
            i += 1
            s_all = s_all[len(ma):]

            s_add += ma
            s_add_next = s_add + ma_next


    return alignment

if __name__ == "__main__":
    import doctest

    doctest.NORMALIZE_WHITESPACE = True
    doctest.testmod()
