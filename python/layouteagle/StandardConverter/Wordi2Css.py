import paired
from more_itertools import pairwise

from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec


@converter("wordi.*", 'css.*')
class Wordi2Css(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def write_css(self, selector, data, output):
        children = []
        attributes = []

        for key, value in data.items():
            if hasattr(value, 'items'):
                children.append((key, value))
            else:
                attributes.append((key, value))

        if attributes:
            print >> output, ' '.join(selector), "{"
            for key, value in attributes:
                print >> output, "\t", key + ":", value
            print >> output, "}"

        for key, value in children:
            self.write_css(selector + (key,), value, output)

    def window_overlap(self, i1, i2, j1, j2):
        if i1 >= j1 and i2 <= j2:
            return (i1,i2)
        else:
            return None


    def __call__(self, feature_meta, *args, **kwargs):
        for annotation, meta in feature_meta:
            tags, words = list(zip(*annotation))
            i, iwords = list(zip(*meta["i_word"]))

            alignment = paired.align(
                iwords, words,
                match_score=5,
                mismatch_score=-1,
                gap_score=-5
            )
            i_to_tag = \
                {i[_i1]: tags[_i2] for _i1, _i2 in alignment if _i2 and _i1}

            scss =  self.parse_to_sass(i_to_tag, meta)
            yield scss, meta

    def parse_to_sass(self, css_obj, meta):
            print (meta["CSS"])
            return "\n".join([f""".z{hex(i)[2:]} {{
            {meta["CSS"][tag]}
            }}
""" for i, tag in css_obj.items()])
