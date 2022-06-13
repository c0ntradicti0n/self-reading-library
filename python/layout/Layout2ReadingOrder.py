import copy
import logging
import os

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from core import config
from helpers.cache_tools import configurable_cache

@converter("prediction", 'reading_order')
class Layout2ReadingOrder(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, feature_meta, *args, **kwargs):
        for pdf_path, meta in feature_meta:
            annotation = meta['predictions_metas_per_document']
            try:
                title = [[(i,l) for i, l in enumerate(an[0]['labels']) if l in config.TITLE] for an in annotation]
                used_titles = [annotation[0][0]['df']['text'].tolist()[0][i] for i, h in title[0]]
                used_titles = used_titles[0] if len(used_titles)>1 else meta['html_path']
            except:
                logging.error("Failure setting title", exc_info=True)
                used_titles = meta["html_path"]
            meta['title'] = used_titles

            used_label_is = [self.sort_by_label([(i,l) for i, l in enumerate(an[0]['labels']) if l in config.TEXT_LABELS]) for an in annotation]
            used_texts = [[annotation[i][0]['df']['text'].tolist()[0][ull] for ull in ul] for i, ul in enumerate(used_label_is)]
            used_boxes = [[annotation[i][0]['bbox'][ull] for ull in ul] for i, ul in enumerate(used_label_is)]

            sorted_texts = self.sort_by_box(used_texts, used_boxes)

            meta['used_text_boxes'] = sorted_texts

            enumerated_texts = self.enumerate_words(sorted_texts)
            if 'df' in meta:
                del meta['df']
            del meta['chars_and_char_boxes']
            del meta['final_feature_df']
            del meta['predictions_metas_per_document']
            meta['enumerated_texts'] = enumerated_texts
            yield pdf_path, meta

    def sort_by_label(self, i_l):
        return [i for i, l in sorted(i_l, key=lambda x: config.TEXT_LABELS.index(x[1]))]

    def sort_by_box(self, all_texts, all_boxes):
        return list(sorted(zip(texts, boxes), key=lambda x: x[1][0] + x[1][1] ) for texts, boxes in zip(all_texts, all_boxes))

    def enumerate_words(self, all_texts):
        i = 0
        all_enumeration = []
        for texts in all_texts:
            enumeration = []
            for word in " ".join([text for text, box in texts]).split(" "):
                enumeration.append((i, word))
                i += 1
            enumeration.append((i, "\n    "))
            i += 1
            all_enumeration.append(enumeration)


        return all_enumeration