import copy
from collections import defaultdict

from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec


@converter("wordi.page.*", 'wordi.*')
class UnPager(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, feature_meta, *args, **kwargs):
        whole_doc_id = None
        whole_annotation = []
        whole_meta = None

        for annotation, meta in feature_meta:
            if whole_doc_id and meta["doc_id"]  != whole_doc_id:
                yield whole_annotation, whole_meta
                whole_annotation = []
                whole_meta = None
            if not whole_meta:
                whole_meta = copy.deepcopy(meta)
                whole_meta['_i_to_i2'] = {}
                consumed_until_now = 0

            whole_meta['_i_to_i2'].update(
                {_i: [_i2 + consumed_until_now for _i2 in _i2s] for _i, _i2s in meta['_i_to_i2'].items()}
            )

            consumed_until_now += meta['consumed_i2']
            whole_annotation.extend(annotation[:meta['consumed_i2']])

            try:
                whole_doc_id = meta["doc_id"]
            except Exception as e:
                self.logger.error("No doc_id_given")
                whole_doc_id = "?"
        yield whole_annotation, whole_meta

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

