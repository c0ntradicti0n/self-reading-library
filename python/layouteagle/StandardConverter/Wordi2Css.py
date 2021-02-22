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

            i_to_tag = {}
            for _i1, _i2 in meta["_i_to_i2"]:
                if _i1 not in i_to_tag or i_to_tag[_i1] == "O":
                    if (_i2< len(tags)):
                        i_to_tag [ _i1] = annotation[_i2]

            scss =  self.parse_to_sass(i_to_tag, meta)
            yield scss, meta

    def parse_to_sass(self, css_obj, meta):
            return "\n".join([f""".z{hex(i)[2:]} {{
            {meta["CSS"][annotation[0]]}
            }}
""" for i, annotation in css_obj.items()])
