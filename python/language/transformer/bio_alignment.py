import numpy as np


def compare(m, n, match, n_match):
    if m == n:
        return match
    else:
        return n_match


def Smith_Waterman(seq1, seq2, mS, mmS, w1):
    path = {}
    S = np.zeros([len(seq1) + 1, len(seq2) + 1], int)

    for i in range(0, len(seq1) + 1):
        for j in range(0, len(seq2) + 1):
            if i == 0 or j == 0:
                path["[" + str(i) + ", " + str(j) + "]"] = []
            else:
                if seq1[i - 1] == seq2[j - 1]:
                    s = mS
                else:
                    s = mmS
                L = S[i - 1, j - 1] + s
                P = S[i - 1, j] - w1
                Q = S[i, j - 1] - w1
                S[i, j] = max(L, P, Q, 0)
                path["[" + str(i) + ", " + str(j) + "]"] = []
                if L == S[i, j]:
                    path["[" + str(i) + ", " + str(j) + "]"].append(
                        "[" + str(i - 1) + ", " + str(j - 1) + "]"
                    )
                if P == S[i, j]:
                    path["[" + str(i) + ", " + str(j) + "]"].append(
                        "[" + str(i - 1) + ", " + str(j) + "]"
                    )
                if Q == S[i, j]:
                    path["[" + str(i) + ", " + str(j) + "]"].append(
                        "[" + str(i) + ", " + str(j - 1) + "]"
                    )

    end = np.argwhere(S == S.max())
    for i in end:
        key = str(list(i))
        value = path[key]
        result = [key]
        traceback(path, S, value, result, seq1, seq2)


def Smith_Waterman_aff(seq1, seq2, match, n_match, u, v):
    a = len(seq1)
    b = len(seq2)
    path = {}
    S = np.zeros((a + 1, b + 1))
    L = np.zeros((a + 1, b + 1))
    P = np.zeros((a + 1, b + 1))
    Q = np.zeros((a + 1, b + 1))
    seq1 = " " + seq1[:]
    seq2 = " " + seq2[:]
    for r in range(1, b + 1 if a > b else a + 1):
        for c in range(r, b + 1):
            L[r, c] = S[r - 1, c - 1] + compare(seq1[r], seq2[c], match, n_match)
            P[r, c] = max(np.add(S[0:r, c], -(np.arange(r, 0, -1) * u + v)))
            Q[r, c] = max(np.add(S[r, 0:c], -(np.arange(c, 0, -1) * u + v)))
            S[r, c] = max([0, L[r, c], P[r, c], Q[r, c]])
        for c in range(r + 1, a + 1):
            L[c, r] = S[c - 1, r - 1] + compare(seq1[c], seq2[r], match, n_match)
            P[c, r] = max(np.add(S[0:c, r], -(np.arange(c, 0, -1) * u + v)))
            Q[c, r] = max(np.add(S[c, 0:r], -(np.arange(r, 0, -1) * u + v)))
            S[c, r] = max([0, L[c, r], P[c, r], Q[c, r]])
        for i in range(0, len(seq1)):
            for j in range(0, len(seq2)):
                if i == 0 or j == 0:
                    path["[" + str(i) + ", " + str(j) + "]"] = []
                else:
                    path["[" + str(i) + ", " + str(j) + "]"] = []
                    if L[i, j] == S[i, j]:
                        path["[" + str(i) + ", " + str(j) + "]"].append(
                            "[" + str(i - 1) + ", " + str(j - 1) + "]"
                        )
                    if P[i, j] == S[i, j]:
                        path["[" + str(i) + ", " + str(j) + "]"].append(
                            "[" + str(i - 1) + ", " + str(j) + "]"
                        )
                    if Q[i, j] == S[i, j]:
                        path["[" + str(i) + ", " + str(j) + "]"].append(
                            "[" + str(i) + ", " + str(j - 1) + "]"
                        )
    end = np.argwhere(S == S.max())
    for i in end:
        key = str(list(i))
        value = path[key]
        result = [key]
        traceback(path, S, value, result, seq1, seq2)


def traceback(path, S, value, result, seq1, seq2):
    i = 0
    j = 0
    if value != []:
        key = value[0]
        result.append(key)
        value = path[key]
        i = int((key.split(",")[0]).strip("["))
        j = int((key.split(",")[1]).strip("]"))
    if S[i, j] == 0:
        x = 0
        y = 0
        s1 = ""
        s2 = ""
        md = ""
        for n in range(len(result) - 2, -1, -1):
            point = result[n]
            i = int((point.split(",")[0]).strip("["))
            j = int((point.split(",")[1]).strip("]"))
            if i == x:
                s1 += "-"
                s2 += seq2[j - 1]
                md += " "
            elif j == y:
                s1 += seq1[i - 1]
                s2 += "-"
                md += " "
            else:
                s1 += seq1[i - 1]
                s2 += seq2[j - 1]
                md += "|"
            x = i
            y = j

    else:
        traceback(path, S, value, result, seq1, seq2)


if __name__ == "__main__":
    for i in range(500):

        fruits1 = ["orange", "jpear", "aphhple", "pear", "orange"] * i
        fruits2 = ["pearj", "applhe", "okrang"] * i
        print(Smith_Waterman(fruits1, fruits2, 1, -1 / 3, 1))
        print(i)
