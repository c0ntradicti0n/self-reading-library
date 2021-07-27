from pprint import pprint

from listalign.suffixtreealign import suffix_align
from more_itertools import pairwise
from pdfminer.high_level import extract_text

from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter

import wordninja

outputs = {
    'html': 'layout.html',  # same looking html
    'txt': 'layout.txt',  # pure text from single-word text (with hyphens)
    'json': 'layout.json'  # json with indexed single words as they can be reapplied via css to the html-document
}


@converter('predicted.feature', "wordi.layout")
class MarkupDocument(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.css = {
            0: 'color: #123',
            1: 'background-color: #FFDC00 ',
            2: 'background-color: #A012BE ',
            3: 'background-color: #0152BE '
        }
        pass

    # @file_persistent_cached_generator(config.cache + 'markup_finished.json',
    #                                  if_cache_then_finished=True)
    def __call__(self, feature_meta, *args, **kwargs):
        for feature_df, meta in feature_meta:
            self.assign_labels_from_div_content(feature_df)
            self.label_lookup = meta['label_lookup']

            text = extract_text(meta['filename']).replace('', "")
            feature_df.word_num = feature_df.word_num.astype(int)
            ranges = [list(range(*r))
                      for r in list(pairwise([0] + list(feature_df.word_num)))]

            meta["_i_to_i2"] = {i: i for i in range(0, max(list(feature_df.word_num)))}

            annotation = [(self.label_lookup.token_to_id[l], feature_df.text[i]) for i, l in
                          enumerate(feature_df.layoutlabel)]
            meta['CSS'] = self.css
            meta['i_word'] = []
            yield annotation, meta
