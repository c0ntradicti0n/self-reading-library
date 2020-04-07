from scipy import signal
from helpers.time_tools import timeit_context

from bert_embedding import BertEmbedding
bert_embedding = BertEmbedding(model='bert_12_768_12', dataset_name='book_corpus_wiki_en_cased')

def pad_right (arr, should_len):
    return np.pad(arr, (0, should_len-len(arr)), 'constant')

def repeat_or(a, n=4):
    m = a
    k = m.copy()

    # lenM and lenK say for each mask how many
    # subsequent Trues there are at least
    lenM, lenK = 1, 1

    # we run until a combination of both masks will give us n or more
    # subsequent Trues
    while lenM+lenK < n:
        # append what we have in k to the end of what we have in m
        m[lenM:] |= k[:-lenM]

        # swap so that m is again the small one
        m, k = k, m

        # update the lengths
        lenM, lenK = lenK, lenM+lenK

    # see how much m has to be shifted in order to append the missing Trues
    k[n-lenM:] |= m[:-n+lenM]

    return k

def correlate_argmax_label (sheet, embeddings1, embeddings2, label, score_sheet):
    if not embeddings1.any() or not embeddings2.any():
        raise ValueError('Some embeddings empty')

    c = signal.correlate(embeddings1, embeddings2, 'valid')
    rc = signal.correlate(np.flip(embeddings1), np.flip(embeddings2), 'valid')

    #c = signal.fftconvolve(embeddings1, embeddings2, 'valid')
    peak_threshold = max (c[0,:,0]) * 0.93
    rpeak_threshold = max (rc[0,:,0]) * 0.93

    if embeddings2.shape[1] > 1:
        print ('hallo')
    padded_c = pad_right(c[0,:,0], len (sheet))
    rpadded_c = pad_right(rc[0,:,0], len (sheet))

    mask = (padded_c >= peak_threshold) #& (padded_c > score_sheet)
    rmask = (rpadded_c >= rpeak_threshold) #& (rpadded_c > score_sheet)

    mask = repeat_or(mask, n=embeddings2.shape[1]-1)
    rmask = repeat_or(rmask, n=embeddings2.shape[1]-1)[::-1]

    sheet[mask&rmask] = label
    score_sheet[mask&rmask] = padded_c[mask&rmask]
    return sheet, score_sheet

def l_border_from_correlate (embeddings1, embeddings2):
    len_phrase = embeddings2.shape[1]
    if len_phrase > 1:
       c = signal.correlate(embeddings1, embeddings2, 'valid')
       l = np.argmax(c, axis=0)[0]
    else:
       c = np.array([[cosine(e, embeddings2) for e in embeddings1]])
       l = np.argmin (c, axis=1)[0]
    conf = c[l][0]
    return l, conf

def r_border_from_correlate (embeddings1, embeddings2):
    rc = np.flip(signal.correlate(np.flip(embeddings1), np.flip(embeddings2), 'valid'))
    r = np.argmax(rc, axis=0)[0]
    conf = rc[r][0]
    return r  + 1, conf

def embed (tokens):
    return []
    with timeit_context('generating embeddings for "%s"' % (str(tokens))):
        if not tokens:
            return None
        ts = [t["text_tokenized"] for t in tokens]

        embeddings = [emb[0] if len(emb)>=1 else print (ts[i-1], ts[i+1], tok, emb) for i, (tok, emb) in enumerate(bert_embedding(ts))]
        embeddings = np.stack(embeddings, axis=0)
        return embeddings


from scipy.spatial.distance import  cosine
import numpy as np
def elmo_sim(embeddings1, embeddings2):
    res = -(elmo_sim +
            cosine(embeddings1[1, :], embeddings2[1, :]) +
            cosine(embeddings1[2, :], embeddings2[2, :])) / 3
    if np.isnan(res):
        res = -25
    return res