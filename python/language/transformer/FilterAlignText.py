from listalign.helpers import alignment_table
from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from language.transformer.Pager import Pager
from listalign.word_pyalign import align


@converter("reading_order", 'reading_order.filter_align_text')
class FilterAlignTextPager(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, gen, *args, **kwargs):
        for k, meta in gen:
            texts = meta['enumerated_texts']
            filter_text = meta['filter_text']
            all_tokens = Pager.preprocess_text(texts)
            filter_text_tokens = filter_text.split()
            alignment = align(all_tokens, filter_text_tokens)
            print(alignment_table(alignment, all_tokens, filter_text_tokens))
            meta['text'] = [a for a, b in alignment if b]
            yield k, meta
