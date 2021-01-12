import itertools
import logging
from pprint import pprint
from typing import List

import spacy
from more_itertools import pairwise, split_before
from nltk import flatten
import regex as re

from python.nlp.TransformerStuff.core import bio_annotation

nlp = spacy.load("en_core_sci_sm")



def next_natural_number():
    i = 0
    while True:
        yield i
        i += 1

def seq_split(lst, cond):
    sublst = [lst[0]]
    for item in lst[1:]:
        if cond(item):
            sublst.append(item)
        else:
            yield sublst
            sublst = [item]
    if sublst:
        yield sublst


def approx_unique(urn=[], choices=[], variance=0.005):
    d = round(max(flatten([urn]+choices)) * variance)
    for i, v in enumerate(urn):
        if any(vd in flatten(choices) for vd in range(v-d, v+d)):
            yield i, v


class TextSplitter:
    """ Splits texts based on the states of made annotations.

        Longer must be split into smaller annotable pieces. 

        It handles two models. It steps through the text and makes predictions, where it takes the first
        annotation. The corpus for this model must be trained to take the first possible annotation set. 
        If something ist found, then the text of the intermediate parts of the annotation is fed into
        the second model. The second model is to be trained to annotate the whole sample and this is done
        until nothing reasonable is found any more.
         
    """
    def __init__(self, model_first, model_over, multi_model=False,  max_len = 100):
        self.model_first = model_first
        #self.model_second = model_over
        self.max_len = max_len
        self.annotation_scheme = bio_annotation
        self.multi_model = multi_model
        self.id_source = next_natural_number()
        next(self.id_source)

    def make_proposals(self, tokens):
        sent_cuts = [i+1 for i, token in  enumerate(tokens)
                     if token=="." or token=="?" or token=="!"]
        start_i, end_i = self.next_proposal(tokens, sent_cuts, start_i=0)

        done = []
        while start_i != end_i:
            span = sent_cuts[start_i],sent_cuts[end_i]
            if span in done:
                logging.info("repeating work, why?")
                start_i =  end_i
                end_i = start_i + 5

            result = self.get_sample(
                    start=span[0],
                    end=span[1],
                    tokens=tokens[span[0]:span[1]],
                    sentence_cuts=sent_cuts)
            done.append(span)

            last_start_i, last_end_i = start_i, end_i
            yield result
            last_mark = sent_cuts[start_i] + result['mark_end']
            next_position = min(sent_cuts, key=lambda x: abs(last_mark - x))
            new_start_i = sent_cuts.index(next_position)
            start_i = start_i if new_start_i == start_i else new_start_i
            start_i, end_i = self.next_proposal(tokens, sent_cuts, start_i)
            if start_i < last_end_i:
                logging.info("starting at tokens before")

    def next_proposal (self, whole_doc, whole_sent_starts, start_i):
        """ Effectively this functions computes the new end of the span, that fits in the window of text to be analysed

        :param whole_doc:
        :param whole_sent_starts:
        :param start_i:
        :return:
        """
        next_i = start_i
        while next_i < len(whole_sent_starts)-1 and len(whole_doc[whole_sent_starts[start_i]:whole_sent_starts[next_i]])< self.max_len:
            next_i += 1
        return start_i, next_i

    def make_windwos(self, doc, text, cuts):
        numba, cut_i = zip(*cuts)
        groups       = list(zip(cuts, seq_split(doc, lambda t: t.i not in cut_i)))
        return groups

    def get_predicted_annotations (self, windows):
        reasonable_samples = (self.get_sample_if_reasonable(r) for r in windows)
        return [r for r in reasonable_samples if r]

    def get_sample(self, start, end, tokens, sentence_cuts, depth = 0, max_depth = 1, which='first'):
        """ make the prediction based on some parts of the text, optionally regarding also distinctions, that appear
        within the sides or arms of a found distinction

        :param start:
        :param end:
        :param tokens:
        :param sentence_cuts:
        :param depth:
        :param max_depth:
        :return:
        """
        indices = list(range(start, end))
        assert len (indices) == len(tokens)
        assert len(tokens) == end-start
        if not tokens:
            logging.error(ValueError("no text in given span").__repr__())
            return {'difference':False}

        if which == 'first':
            model = self.model_first
        else:
            model = self.model_second

        annotation = model.predict_tokens(tokens)

        tokens = [x[0] for x in annotation]
        tags = [x[1] for x in annotation]
        relevant_tags =  [x != "O" for x in tags]
        BIO_tokens = [t[0] for t in tags]

        number_of_annotations = BIO_tokens.count('B')
        number_of_subjects    = BIO_tokens.count('S')

        if True in relevant_tags:
            # global position of span end of annotation
            mark_end = len(relevant_tags) - relevant_tags[::-1].index(True)  # last tags (look backwards and index first True and thats the position from the end
        else:
            mark_end = len(tokens)

        privative = number_of_annotations>=2 and number_of_subjects >=2
        return {
            'annotation': annotation,
            'indices': indices,
            'tokens': tokens,
            'depth': depth,
            'start': start,
            'id': next(self.id_source),
            'mark_end': mark_end,
            'annotated': any(relevant_tags),
            'difference': number_of_annotations >=2 ,
            'privative': privative,
        }

    def change_proposals(self, cuts, indices):
        sentences = list(self.doc.sents)
        relevant_sentences = [sentences[s:e] for s, e in pairwise(cuts)]
        windows = list(zip(zip(cuts, indices), relevant_sentences))
        new_proposals = self.get_predicted_annotations(windows)
        return new_proposals

    def nearest(position:int, positions:List[int], before: bool = False, after: bool = False) -> int:
        """ Approximating the index, that is next to some value of a specified list, the index can be specified
        to be before or after this matched element.

        At beginning
        >>> TextSplitter.nearest (6, [3,8,12])
        1
        >>> TextSplitter.nearest (6, [3,8,12], before=True)
        0
        >>> TextSplitter.nearest (4, [3,8,12], after=True)
        1

        More at the end
        >>> TextSplitter.nearest (42, [3, 8, 12, 43, 100])
        3
        >>> TextSplitter.nearest (99, [3, 8, 12, 43, 100], before=True)
        3
        >>> TextSplitter.nearest (44, [3, 8, 12, 43, 100], after=True)
        4

        Borders of range
        >>> TextSplitter.nearest (100, [3, 8, 12, 43, 100])
        4
        >>> TextSplitter.nearest (3, [3, 8, 12, 43, 100])
        0
        >>> TextSplitter.nearest (100, [3, 8, 12, 43, 100], before=True)
        4
        >>> TextSplitter.nearest (3, [3, 8, 12, 43, 100], before=True)
        0
        >>> TextSplitter.nearest (100, [3, 8, 12, 43, 100], after=True)
        4
        >>> TextSplitter.nearest (3, [3, 8, 12, 43, 100], after=True)
        0

        Out out range

        >>> TextSplitter.nearest (300, [3, 8, 12, 43, 100])
        4
        >>> TextSplitter.nearest (2, [3, 8, 12, 43, 100])
        0
        >>> TextSplitter.nearest (500, [3, 8, 12, 43, 100], before=True)
        4
        >>> TextSplitter.nearest (1, [3, 8, 12, 43, 100], after=True)
        0


        :param position:
        :param positions:
        :param before:
        :param after:
        :return:
        """
        pos = positions.index(min(positions, key=lambda x: abs(position - x)))

        if before:
            if position < min(positions):
                raise ValueError("Before can't before all, if looking before")
            elif position < positions[pos]:
                return pos - 1
            else:
                return pos
        elif after:
            if position > max(positions):
                raise ValueError("After can't be after after all")
            elif position > positions[pos]:
                return pos + 1
            else:
                return pos
        else:
            return pos

