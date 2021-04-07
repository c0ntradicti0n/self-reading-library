# This software is a free software. Thus, it is licensed under GNU General Public License.
# Python implementation to Smith-Waterman Algorithm for Homework 1 of Bioinformatics class.
# Forrest Bao, Sept. 26 <http://fsbao.net> <forrest.bao aT gmail.com>

from fastDamerauLevenshtein import damerauLevenshtein
from texttable import Texttable

damerauLevenshtein('car', 'cars', similarity=True)  # expected result: 0.75


# zeros() was origianlly from NumPy.
# This version is implemented by alevchuk 2011-04-10
def zeros(shape):
    retval = []
    for x in range(shape[0]):
        retval.append([])
        for y in range(shape[1]):
            retval[-1].append(0)
    return retval


gap_penalty = -1


def match_score(alpha, beta):
    sim = damerauLevenshtein(alpha, beta, similarity=True,
                             replaceWeight=1
                             )
    return (sim - 0.5)


def none_window(seq, i1):
    window = []
    for i in range(i1, 0, -1):
        if seq[i] == '-':
            window.append(i)
        else:
            window.append(i)
            break;
    for i in range(i1, len(seq)):
        if seq[i] == '-':
            window.append(i)
        else:
            window.append(i)
            break;

    return list(sorted(set(window)))


def rework_windows(align1, align2, ialign1, ialign2):
    for i in range(0, len(align1)):

        if align1[i] == '-':
            window = none_window(align1, i)
            i_start = window[0]
            i_end = window[-1]
            word_right = "".join(align2[j] for j in window[1:]).replace('-', '').replace(':', '')
            word_left = "".join(align2[j] for j in window[:-1]).replace('-', '').replace(':', '')

            if match_score(word_right, align1[i_end]) > match_score(word_left, align2[i_start]):
                i_real = i_end
            else:
                i_real = i_start
            ialign1[i] = ialign1[i_real]

        if align2[i] == '-':
            window = none_window(align2, i)
            i_start = window[0]
            i_end = window[-1]
            word_right = "".join(align1[j] for j in window[1:]).replace('-', '').replace(':', '')
            word_left = "".join(align1[j] for j in window[:-1]).replace('-', '').replace(':', '')

            if match_score(word_right, align2[i_end]) > match_score(word_left, align2[i_start]):
                i_real = i_end
            else:
                i_real = i_start
            ialign2[i] = ialign2[i_real]

    return align1, align2, ialign1, ialign2


def needle(seq1, seq2):
    """
    >>> a = ['Intro', 'duction', 'f', 'rom', ':', '', 'Distinction', ':', '', 'A', 'Social', 'Critique', 'of', 'the', 'J', 'udgement', 'of', 'Taste', '', 'by', 'Pierr', 'e', 'Bou', 'rdieu', '198', '4', 'Introduction',  'You', 'said', 'i', 't,', 'my', 'go', 'od', 'kn', 'ight', 'There', 'oug', 'ht', 'to', 'b', 'e', 'laws', 'to', '', 'protect', 'the', 'b', 'od', 'y', 'of', 'acquir', 'ed', 'know', 'ledg', 'e.', '', '', 'Take', 'one', 'of', 'our', 'g', 'ood', 'p', 'upils,', 'for', 'ex', 'ample:', 'mo', 'dest', '', 'and', 'd', 'iligent,', 'from', 'hi', 's', 'earl', 'iest', 'gramm', 'ar', 'c', 'lasse', 's', 'he', '\x19s', '', 'kept', 'a', 'lit']
    >>> b = ['Introduction', 'from', ':', 'Distinction', ':', 'A', 'Social', 'Critique', 'of', 'the', 'Judgement', 'of', 'Taste', 'by', 'Pierre', 'B', 'our', 'dieu', '1984', 'Introduction', 'You', 'said', 'it', ',', 'my', 'good', 'knight', 'There', 'ought', 'to', 'be', 'laws', 'to', 'protect', 'the', 'body', 'of', 'acquired', 'knowledge', '.', 'Take', 'one', 'of', 'our', 'good', 'pupils', ',', 'for', 'example', ':', 'modest', 'and', 'diligent', ',', 'from', 'his', 'earliest', 'grammar', 'classes', 'he', 's', 'kept', 'a', 'lit']
    >>> alignment = list(zip(*needle(a, b)))
    >>> print (alignment_table(alignment, a, b))
    ... # doctest: +NORMALIZE_WHITESPACE
    i         w1             w2        i1        ->        i2        ->
    ========================================================================
    0           Intro   -               0   Intro           0   Introduction
    1         duction   Introduction    1   duction         0   Introduction
    2               f   -               2   f               1   from
    3             rom   from            3   rom             1   from
    4               :   :               4   :               2   :
    5                   -               5                   3   Distinction
    6     Distinction   Distinction     6   Distinction     3   Distinction
    7               :   :               7   :               4   :
    8                   -               8                   5   A
    9               A   A               9   A               5   A
    10         Social   Social         10   Social          6   Social
    11       Critique   Critique       11   Critique        7   Critique
    12             of   of             12   of              8   of
    13            the   the            13   the             9   the
    14              J   -              14   J              10   Judgement
    15       udgement   Judgement      15   udgement       10   Judgement
    16             of   of             16   of             11   of
    17          Taste   Taste          17   Taste          12   Taste
    18                  -              18                  12   Taste
    19             by   by             19   by             13   by
    20          Pierr   Pierre         20   Pierr          14   Pierre
    21              e   -              21   e              14   Pierre
    22              -   B              22   Bou            15   B
    23            Bou   -              22   Bou            15   B
    24              -   our            23   rdieu          16   our
    25          rdieu   dieu           23   rdieu          17   dieu
    26            198   1984           24   198            18   1984
    27              4   -              25   4              18   1984
    28   Introduction   Introduction   26   Introduction   19   Introduction
    29            You   You            27   You            20   You
    30           said   said           28   said           21   said
    31              i   it             29   i              22   it
    32             t,   ,              30   t,             23   ,
    33             my   my             31   my             24   my
    34             go   -              32   go             25   good
    35             od   good           33   od             25   good
    36             kn   -              34   kn             26   knight
    37           ight   knight         35   ight           26   knight
    38          There   There          36   There          27   There
    39            oug   -              37   oug            28   ought
    40             ht   ought          38   ht             28   ought
    41             to   to             39   to             29   to
    42              b   -              40   b              30   be
    43              e   be             41   e              30   be
    44           laws   laws           42   laws           31   laws
    45             to   to             43   to             32   to
    46                  -              44                  32   to
    47        protect   protect        45   protect        33   protect
    48            the   the            46   the            34   the
    49              b   -              47   b              34   body
    50             od   body           48   od             35   body
    51              y   -              49   y              35   body
    52             of   of             50   of             36   of
    53         acquir   acquired       51   acquir         37   acquired
    54             ed   -              52   ed             38   acquired
    55           know   -              53   know           38   knowledge
    56           ledg   knowledge      54   ledg           38   knowledge
    57             e.   .              55   e.             39   .
    58                  -              56                  40   Take
    59                  -              57                  40   Take
    60           Take   Take           58   Take           40   Take
    61            one   one            59   one            41   one
    62             of   of             60   of             42   of
    63            our   our            61   our            43   our
    64              g   -              62   g              44   good
    65            ood   good           63   ood            44   good
    66              -   pupils         63   ood            45   pupils
    67              p   -              64   p              45   pupils
    68              -   ,              65   upils,         46   ,
    69         upils,   -              65   upils,         47   for
    70            for   for            66   for            47   for
    71             ex   -              67   ex             48   example
    72         ample:   example        68   ample:         48   example
    73              -   :              68   ample:         49   :
    74             mo   -              69   mo             50   modest
    75           dest   modest         70   dest           50   modest
    76                  -              71                  51   and
    77            and   and            72   and            51   and
    78              d   -              73   d              52   diligent
    79       iligent,   diligent       74   iligent,       52   diligent
    80              -   ,              74   iligent,       53   ,
    81           from   from           75   from           54   from
    82             hi   his            76   hi             55   his
    83              s   -              77   s              56   his
    84           earl   -              78   earl           56   earliest
    85           iest   earliest       79   iest           56   earliest
    86          gramm   grammar        80   gramm          57   grammar
    87             ar   -              81   ar             57   grammar
    88              c   -              82   c              57   classes
    89          lasse   classes        83   lasse          58   classes
    90              s   -              84   s              58   classes
    91             he   he             85   he             59   he
    92              s   s              86   s              60   s
    93                  -              87                  61   kept
    94           kept   kept           88   kept           61   kept
    95              a   a              89   a              62   a
    96            lit   lit            90   lit            63   lit

    """
    m, n = len(seq1), len(seq2)

    score = zeros((m + 1, n + 1))

    for i in range(0, m + 1):
        score[i][0] = gap_penalty * i
    for j in range(0, n + 1):
        score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(seq1[i - 1], seq2[j - 1])
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)

    align1, align2 = [], []
    ialign1, ialign2 = [], []

    i, j = m, n
    while i > 0 and j > 0:
        score_current = score[i][j]
        score_diagonal = score[i - 1][j - 1]
        score_up = score[i][j - 1]
        score_left = score[i - 1][j]
        if match_score(seq1[i - 1], seq2[j - 1]) > -0.1:
            align1.append(seq1[i - 1])
            align2.append(seq2[j - 1])

            ialign1.append(i - 1)
            ialign2.append(j - 1)

            i -= 1
            j -= 1
        elif score_up < score_left:
            align1.append(seq1[i - 1])
            align2.append('-')

            ialign1.append(i - 1)
            ialign2.append(None)

            i -= 1
        elif score_current < score_up:
            align1.append('-')
            align2.append(seq2[j - 1])

            ialign1.append(None)
            ialign2.append(j - 1)

            j -= 1
        else:
            if score_left <= score_up:
                align1.append(seq1[i - 1])
                align2.append('-')

                ialign1.append(i - 1)
                ialign2.append(None)

                i -= 1
            else:
                align1.append('-')
                align2.append(seq2[j - 1])

                ialign1.append(None)
                ialign2.append(j - 1)

                j -= 1
            align1.append(seq1[i - 1] + "?")
            align2.append(seq2[j - 1] + "?")

            ialign1.append(i - 1)
            ialign2.append(j - 1)

            i -= 1
            j -= 1

    # Finish tracing up to the top left cell
    while i > 0:
        align1.append(seq1[i - 1])
        align2.append('-')

        ialign1.append(i - 1)
        ialign2.append(None)

        i -= 1
    while j > 0:
        align1.append(seq2[i - 1] + "?")
        align2.append(seq2[j - 1] + "?")

        ialign1.append(None)
        ialign2.append(j - 1)

        j -= 1

    align1.reverse()
    align2.reverse()
    ialign1.reverse()
    ialign2.reverse()

    align1, align2, ialign1, ialign2 = rework_windows(align1, align2, ialign1, ialign2)
    return align1, align2, list(zip(ialign1, ialign2))


def alignment_table(alignment, a, b):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["c", "r", "l", "r", "l", 'r', 'l'])
    table.add_rows(
        [
            ['i', 'w1', 'w2', 'i1', "->", 'i2', '->']
        ] + [
            [i, t, w, x, a[x], y, b[y]
             ]
            for i, (t, w, x, y)
            in enumerate(alignment)]
    )
    return table.draw()


if __name__ == "__main__":
    fruits1 = ['Intro', 'duction', 'f', 'rom', ':', '', 'Distinction', ':', '', 'A', 'Social', 'Critique', 'of', 'the',
               'J', 'udgement', 'of', 'Taste', '', 'by', 'Pierr', 'e', 'Bou', 'rdieu', '198', '4', 'Introduction',
               'You', 'said', 'i', 't,', 'my', 'go', 'od', 'kn', 'ight', 'There', 'oug', 'ht', 'to', 'b', 'e', 'laws',
               'to', '', 'protect', 'the', 'b', 'od', 'y', 'of', 'acquir', 'ed', 'know', 'ledg', 'e.', '', '', 'Take',
               'one', 'of', 'our', 'g', 'ood', 'p', 'upils,', 'for', 'ex', 'ample:', 'mo', 'dest', '', 'and', 'd',
               'iligent,', 'from', 'hi', 's', 'earl', 'iest', 'gramm', 'ar', 'c', 'lasse', 's', 'he', '\x19s', '',
               'kept', 'a', 'lit']
    fruits2 = ['Introduction', 'from', ':', 'Distinction', ':', 'A', 'Social', 'Critique', 'of', 'the', 'Judgement',
               'of', 'Taste', 'by', 'Pierre', 'B', 'our', 'dieu', '1984', 'Introduction', 'You', 'said', 'it', ',',
               'my', 'good', 'knight', 'There', 'ought', 'to', 'be', 'laws', 'to', 'protect', 'the', 'body', 'of',
               'acquired', 'knowledge', '.', 'Take', 'one', 'of', 'our', 'good', 'pupils', ',', 'for', 'example', ':',
               'modest', 'and', 'diligent', ',', 'from', 'his', 'earliest', 'grammar', 'classes', 'he', 's', 'kept',
               'a', 'lit']
    alignment = list(zip(*needle(fruits1, fruits2)))
    print(alignment_table(alignment, fruits1, fruits2))
    print(f"len 1 {len(fruits1)}  len 2 {len(fruits2)}")

    fruits1 = ["con", "sump", "t", "ion", "orange", "pear", "apple", "x,y,z", "pear", "orange", "consumption"]
    fruits2 = ["consumption", "pear", "apple", "x,", "y,", "z", "con", "sump", "t", "ion"]
    alignment = list(zip(*needle(fruits1, fruits2)))
    print()
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["c", "l", "r", "l", "r"])
    table.add_rows([['i', 'w1', 'w2', 'i1', 'i2']] + [[i, t, w, x, y] for i, (t, w, x, y)
                                                      in enumerate(alignment)])
    print(table.draw())
    print(f"len 1 {len(fruits1)}  len 2 {len(fruits2)}")

if __name__ == "__main__":
    import doctest

    doctest.NORMALIZE_WHITESPACE = True
    doctest.testmod()
