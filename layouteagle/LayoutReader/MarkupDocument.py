import json
import logging

from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from pathant.Converter import converter

outputs = {
 'html':'layout.html', # same looking html
 'txt': 'layout.txt', # pure text from single-word text (with hyphens)
 'json': 'layout.json' # json with indexed single words as they can be reapplied via css to the html-document
}


@converter('predicted.feature', list(outputs.values()))
class MarkupDocument(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


    def __call__(self, feature_meta, *args, **kwargs):
        for feature_df, meta in feature_meta:
            soup = meta['soup'] #self.make_soup(meta['pdf2htmlEX.html'])
            self.assign_labels_from_div_content(feature_df)
            self.label_lookup = meta['label_lookup']
            indexed_words = self.make_word_index(soup, feature_df)
            print (indexed_words)

            html_path = meta['pdf2htmlEX.html'] + outputs['html']
            with open(html_path, 'w') as f:
                f.write(str(soup))

            json_path = meta['pdf2htmlEX.html'] + outputs['json']
            with open(json_path, 'w') as f:
                json.dump(indexed_words, f, indent=4)

            txt_path = meta['pdf2htmlEX.html'] + outputs['txt']
            with open(meta['pdf2htmlEX.html'] + outputs['txt'], 'w') as f:
                json.dump(indexed_words, f, indent=4)

            print ((html_path, json_path, txt_path))

            yield (html_path, json_path, txt_path), meta
