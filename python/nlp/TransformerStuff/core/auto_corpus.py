import unittest
from pprint import pformat

from allennlp.common.checks import ConfigurationError
from helpers.color_logger import *
from regex import regex
from server.core.corpus import CONLL_LINE, CONLL_LINE_SANITIZE, START_LINE, ALLOWED_CHARS, conll_reader


class AutoCorpus:
    """ This class contains functions for automatic manipulation of the corpus.
    """
    def __init__(self, source_corpora=None, target_corpus=None):
        self.target_corpus = target_corpus
        instances = []
        for path in source_corpora:
            try:
                instances.extend(conll_reader.read("./" + path))
            except ConfigurationError as e:
                logging.info("nonexisting or empty conll file" + path)

        self.all_annotations = [list(zip(instance.fields['tokens'], instance.fields['tags'])) for instance in instances]
        logging.info(self.all_annotations[:3])

    def compare_and_notate(self, document_name, proposals):
        yet_seen = []
        for proposal in proposals:
            contained_proposals = [(proposal, annotation) for annotation in self.all_annotations if AutoCorpus.contains(proposal, annotation, yet_seen)]
            transposed_proposals = [self.transpose_annotation_to_proposal(*cp) for cp in contained_proposals]
            self.write(document_name, transposed_proposals)

    def contains(proposal, annotation, yet_seen):
       proposal_text = proposal['text']
       annotation_text = " ".join(an[0].text for an in annotation)
       res = annotation_text in proposal_text #fuzz.partial_ratio( annotation_text, proposal_text)>0.4
       if proposal['id'] not in yet_seen and res:
           yet_seen.append(proposal['id'])
           return res

    def write(self, document_name, contained_proposals):
        if contained_proposals:
            logging.info("found text annotated somewhere")
            for proposal in contained_proposals:
                self.target_corpus.write_annotation(proposal['annotation'])

    # functions to manipulate samples
    def zeroize(sample):
        return "\n".join([regex.sub(CONLL_LINE, r"\1  \2  O  O", line) for line in sample.split('\n')])

    def add_only_first_of_pair(samples, how_much):
        pairs = list(zip(samples, samples[1:] + samples[:1]))
        z_pairs = ["\n".join([s, AutoCorpus.zeroize(z)]) for s, z in pairs]
        return samples + z_pairs[:int(len(z_pairs) * how_much)]

    def limit_length(samples):
        return [s for s in samples if len(s.split('\n')) < 210]

    def sanitize_conll(path):
        with open(path, 'r+') as f1:
            with open(path[:-1], 'w+') as f2:
                for l in f1.readlines():
                    if l:
                        match = CONLL_LINE_SANITIZE.match(l)
                        if match:
                            token, pos, tag_wod, tag_annot = match.groups()

                            token = "".join([c for c in token if c in ALLOWED_CHARS])
                            if not token:
                                continue

                            l = "  ".join([token, pos, tag_wod, tag_annot]) + "\n"
                            f2.write(l)
                        else:
                            f2.write(l)

    def transpose_annotation_to_proposal(self, param):
        raise NotImplementedError


class TestStringMethods(unittest.TestCase):
    def test_transpose(self):

        raise NotImplementedError

if __name__ == '__main__':
    unittest.main()



