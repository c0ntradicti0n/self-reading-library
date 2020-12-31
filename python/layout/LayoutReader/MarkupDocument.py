import json
import os
from pprint import pprint

from python.layouteagle import config
from python.layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from python.helpers.cache_tools import file_persistent_cached_generator
from python.layouteagle.pathant.Converter import converter

import wordninja


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

    @file_persistent_cached_generator(config.cache + 'markup_finished.json',
                                      if_cache_then_finished=True)
    def __call__(self, feature_meta, *args, **kwargs):
        for feature_df, meta in feature_meta:
            soup = meta['soup']
            #self.assign_labels_from_div_content(feature_df)
            self.label_lookup = meta['label_lookup']
            indexed_words = self.make_word_index(soup, feature_df)

            html_path = meta['pdf2htmlEX.html'] + outputs['html']
            with open(html_path, 'w') as f:
                f.write(str(soup))

            json_path = meta['pdf2htmlEX.html'] + outputs['json']
            with open(json_path, 'w') as f:
                json.dump(indexed_words, f, indent=4)

            txt_path = meta['pdf2htmlEX.html'] + outputs['txt']
            with open(meta['pdf2htmlEX.html'] + outputs['txt'], 'w') as f:
                string = "".join(list(indexed_words.values()))
                detokenized = " ".join(wordninja.split(string))
                f.write(detokenized)

            print ((html_path, json_path, txt_path))
            print (meta['label_lookup'].token_to_id)
            num_labels = len(meta['label_lookup'].token_to_id)
            col_dict = {v: f"hsl({int((u/num_labels) * 360)}, 100%, 50%)"
                        for v,u in meta['label_lookup'].token_to_id.items()}
            print (f"""pastel color "{'" "'.join(list(col_dict.values()))}" """)
            os.system(f"""pastel color "{'" "'.join(list(col_dict.values()))}" """)
            pprint (col_dict)
            del meta['soup']
            del meta['label_lookup']
            meta = {k:v for k,v in meta.items() if k not in ['soup', 'label_lookup']}

            yield (html_path, json_path, txt_path), meta
