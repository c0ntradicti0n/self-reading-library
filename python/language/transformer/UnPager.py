import copy

from listalign.helpers import alignment_table

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from listalign.word_pyalign import align
import multiprocessing as mp


@converter("reading_order.page.*", 'reading_order.*')
class UnPager(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


    def __call__(self, feature_meta, *args, **kwargs):
        whole_doc_id = None
        whole_annotation = []
        whole_meta = None

        for _pdf_path, meta in feature_meta:
            annotation = meta['annotation']
            if not whole_doc_id:
                whole_doc_id = meta["doc_id"]
            if meta["doc_id"] != whole_doc_id :
                if "chars_and_char_boxes" in meta:
                    del meta['chars_and_char_boxes']

                if not "i_word" in whole_meta:
                    self.logger.warning(f"Finished prediction with {whole_meta}")
                    whole_doc_id = meta["doc_id"]
                    whole_meta={**meta}
                    continue
                l_a = [iw[1] if iw[1] else '*' for iw in whole_meta['i_word']]

                whole_meta["_i_to_i2"] = {}

                for i_annotation, part_annotation in enumerate(whole_annotation):
                    l_b = [jw[1] if jw[1] else '~' for jw in part_annotation]
                    try:
                        assert l_b and l_a

                        def foo(q, l_a, l_b):
                            q.put(align(l_a, l_b))

                        q = mp.Queue()
                        p = mp.Process(target=foo, args=(q,l_a, l_b))
                        p.start()
                        alignment, cigar = q.get()
                    except:
                        self.logger.error("alignment failed")
                        continue



                    print(alignment_table(alignment, l_a, l_b, info_b=lambda i_b: part_annotation[i_b]))

                    try:
                        for _i1, _i2 in alignment:
                            if _i1 and _i2:
                                whole_meta["_i_to_i2"][whole_meta["i_word"][_i1][0]] = (i_annotation, _i2)
                    except:
                        self.logger.error("Error using alignment", exc_info=True)
                whole_meta['whole_annotation'] = whole_annotation
                yield _pdf_path, whole_meta

                whole_annotation = []
                whole_meta = None

            if not whole_meta:
                whole_meta = copy.deepcopy(meta)
                consumed_until_now = 0


            try:
                consumed_until_now += meta['consumed_i2']
                whole_annotation.append(annotation[:meta['consumed_i2']])
            except:
                if not meta["doc_id"] == 'finito':
                    self.logger.error("There was no determined consumption", exc_info=True)
                whole_annotation.append(annotation)

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

