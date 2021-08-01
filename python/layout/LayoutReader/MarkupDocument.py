from pprint import pprint
from listalign.suffixtreealign import suffix_align
from more_itertools import pairwise
from pdfminer.high_level import extract_text
import logging
logging.getLogger('pdfminer').setLevel(logging.ERROR)
from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter


@converter('predicted.feature', "wordi.layout")
class MarkupDocument(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    css = {
        0: 'background-color: #ccc !important',
        1: 'background-color: #1ff !important',
        2: 'background-color: #f1f !important',
        3: 'background-color: #ff1 !important'
    }

    def __call__(self, feature_meta, *args, **kwargs):
        for feature_df, meta in feature_meta:

            #self.assign_labels_from_div_content(feature_df)

            feature_df.word_num = feature_df.word_num.astype(int)
            ranges = [list(range(*r))
                      for r in list(pairwise([0] + list(feature_df.word_num)))]
            meta["_i_to_i2"] = {i2: i1 for i1, r in enumerate(ranges) for i2 in r}

            annotation = [(
                meta['label_lookup'].token_to_id[l], feature_df.text[i]
            )   for i, l in enumerate(feature_df.layoutlabel)]

            meta['CSS'] = self.css
            yield annotation, meta
