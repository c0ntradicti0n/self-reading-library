import copy
import logging

from listalign.helpers import alignment_table

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from listalign.word_pyalign import align


@converter("reading_order.page.*", 'reading_order.*')
class UnPager(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


    def __call__(self, feature_meta, *args, **kwargs):
        whole_doc_id = None
        whole_annotation = []
        whole_meta = None
        all_annotations = []

        for annotation, meta in feature_meta:
            if not whole_doc_id:
                whole_doc_id = meta["doc_id"]
            if meta["doc_id"] != whole_doc_id:
                if "chars_and_char_boxes" in meta:
                    del meta['chars_and_char_boxes']

                l_a = [iw[1] for iw in whole_meta['i_word']]
                l_b = [jw[1] for jw in whole_annotation]
                alignment, cigar = align(l_a, l_b)

                print(alignment_table(alignment, l_a, l_b))

                try:
                    whole_meta["_i_to_i2"] = {}
                    for _i1, _i2 in alignment:
                        if _i1 and _i2:
                            whole_meta["_i_to_i2"][meta["i_word"][_i1][0]] = _i2
                except:
                    logging.error("Error using alignment", exc_info=True)

                yield whole_annotation, whole_meta

                whole_annotation = []
                whole_meta = None

            if not whole_meta:
                whole_meta = copy.deepcopy(meta)
                consumed_until_now = 0


            consumed_until_now += meta['consumed_i2']
            whole_annotation.extend(annotation[:meta['consumed_i2']])

            all_annotations.append(annotation)
            try:
                whole_doc_id = meta["doc_id"]
            except Exception as e:
                self.logger.error("No doc_id_given")
                whole_doc_id = "?"



    default_values = {
        str: "",
        list: [],
        dict: {}
    }

    def reduce_meta_list_prop(self, props, whole_meta, part_meta, consumed_tokens):
        for key in part_meta.keys():
            if key not in props:
                whole_meta[key] = part_meta[key]
        for prop in props:
            if not prop in whole_meta:
                whole_meta[prop] = self.default_values[type(part_meta[prop])]
            whole_meta[prop] = whole_meta[prop] + part_meta[prop][:consumed_tokens]

