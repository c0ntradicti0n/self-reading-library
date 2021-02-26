#This software is a free software. Thus, it is licensed under GNU General Public License.
#Python implementation to Smith-Waterman Algorithm for Homework 1 of Bioinformatics class.
#Forrest Bao, Sept. 26 <http://fsbao.net> <forrest.bao aT gmail.com>

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
                             replaceWeight = 1
                             )
    return (sim -0.5)

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

    return list(sorted(set(window)) )


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
        else:
            align1.append('-')
            align2.append(seq2[j - 1])

            ialign1.append(None)
            ialign2.append(j - 1)

            j -= 1
        """
        else:
             if score_left <= score_up:
                 align1.append(seq1[i - 1])
                 align2.append('-')

                 ialign1.append(i - 1)
                 ialign2.append(None)

                 i -= 1
             elif score_current <= score_up:
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
             j -= 1"""


    # Finish tracing up to the top left cell
    while i > 0:
        align1.append(seq1[i - 1])
        align2.append('-')

        ialign1.append(i -1 )
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
    return align1, align2, ialign1, ialign2




if __name__ == "__main__":

    fruits1 = ['Intro', 'duction', 'f', 'rom', ':', '', 'Distinction', ':', '', 'A', 'Social', 'Critique', 'of', 'the', 'J', 'udgement', 'of', 'Taste', '', 'by', 'Pierr', 'e', 'Bou', 'rdieu', '198', '4', 'Introduction',  'You', 'said', 'i', 't,', 'my', 'go', 'od', 'kn', 'ight', 'There', 'oug', 'ht', 'to', 'b', 'e', 'laws', 'to', '', 'protect', 'the', 'b', 'od', 'y', 'of', 'acquir', 'ed', 'know', 'ledg', 'e.', '', '', 'Take', 'one', 'of', 'our', 'g', 'ood', 'p', 'upils,', 'for', 'ex', 'ample:', 'mo', 'dest', '', 'and', 'd', 'iligent,', 'from', 'hi', 's', 'earl', 'iest', 'gramm', 'ar', 'c', 'lasse', 's', 'he', '\x19s', '', 'kept', 'a', 'lit']
    fruits2 = ['Introduction', 'from', ':', 'Distinction', ':', 'A', 'Social', 'Critique', 'of', 'the', 'Judgement', 'of', 'Taste', 'by', 'Pierre', 'B', 'our', 'dieu', '1984', 'Introduction', 'You', 'said', 'it', ',', 'my', 'good', 'knight', 'There', 'ought', 'to', 'be', 'laws', 'to', 'protect', 'the', 'body', 'of', 'acquired', 'knowledge', '.', 'Take', 'one', 'of', 'our', 'good', 'pupils', ',', 'for', 'example', ':', 'modest', 'and', 'diligent', ',', 'from', 'his', 'earliest', 'grammar', 'classes', 'he', 's', 'kept', 'a', 'lit']
    alignment = list(zip(*needle(fruits1, fruits2)))
    print()
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["c", "r", "l", "r",  "l", 'r', 'l'])
    table.add_rows([['i', 'w1', 'w2', 'i1', "->", 'i2', '->']] + [[i, t, w, x, fruits1[x], y, fruits2[y]] for i, (t, w, x, y)
                                                      in enumerate(alignment)])
    print(table.draw())
    print(f"len 1 {len(fruits1)}  len 2 {len(fruits2)}")



    fruits1 = ["con", "sump","t", "ion", "orange", "pear", "apple", "x,y,z", "pear", "orange", "consumption"]
    fruits2 = ["consumption", "pear", "apple", "x,", "y,", "z", "con", "sump","t", "ion"]
    alignment = list(zip(*needle(fruits1, fruits2)))
    print()
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["c", "l", "r", "l", "r"])
    table.add_rows([['i', 'w1', 'w2', 'i1', 'i2']] + [[i, t, w, x, y] for i, (t, w,x,y)
                                          in enumerate(alignment)])
    print(table.draw())
    print (f"len 1 {len(fruits1)}  len 2 {len(fruits2)}")
