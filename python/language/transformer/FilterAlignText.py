from listalign.helpers import alignment_table
from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from helpers.str_tools import str_ascii
from language.nlp_helpers.split_interpunction import split_punctuation
from language.transformer.Pager import Pager, preprocess_text
from listalign.word_pyalign import align


@converter("reading_order", "reading_order.filter_align_text")
class FilterAlignText(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, gen, *args, **kwargs):
        for k, meta in gen:
            texts = meta["enumerated_texts"]
            filter_text = self.flags["filter_text"]
            filter_text = str_ascii(filter_text)
            all_tokens = preprocess_text(texts)
            filter_text_tokens = split_punctuation(filter_text)
            alignment = align(all_tokens, filter_text_tokens)[0]
            print(alignment_table(alignment, all_tokens, filter_text_tokens))
            meta["words"] = [
                all_tokens[a] for a, b in alignment if b is not None and a is not None
            ]
            yield k, meta
