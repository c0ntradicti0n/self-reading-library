import base64
import hashlib
import json
import falcon
import nltk

from core import config
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.pathant.Converter import converter
from helpers.hash_tools import bas64encode, hashval
from helpers.list_tools import metaize
from helpers.model_tools import BEST_MODELS
from language.transformer.FilterAlignText import FilterAlignText

def bioul_pos(pos, tag):
    tag_splitters = tag.split("-")
    if len(tag_splitters) > 1:
        return tag_splitters[0] + "-" + pos
    else:
        return pos


def annotation2conll(annotation):
    nltk.download('punkt')
    # required for parts of speech tagging
    nltk.download('averaged_perceptron_tagger')

    tokens = [w for w, t in annotation]
    pos_tags = nltk.pos_tag(tokens)
    tab_lines = [
        "\t".join([word, pos, bioul_pos(pos, tag), tag])
        for (word, tag), (ww, pos) in zip(annotation, pos_tags)
    ]
    result = "\n".join(tab_lines)
    return "\n" + result + "\n"



@converter("reading_order.filter_align_text.difference", "rest")
class DifferenceAnnotationPublisher(RestPublisher):

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="difference_annotation",
            type="difference_annotation",
            path="difference_annotation",
            route="difference_annotation",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))
        self.dir = config.markup_dir
        self.kind = "difference_annotation"

    def on_post(self, req, resp, id=None):
        print(f"Annotating {self.kind}")
        id, text, pdf_path = req.media
        pipeline = self.ant(
            "feature", "reading_order.page.difference",
            via="reading_order.filter_align_text",
            from_function_only=True
        )
        result = list(
            pipeline(
                metaize([id]),
                filter_text=text,
                service_id=__file__,
                difference_model_path=BEST_MODELS["difference"]['best_model_path'],
                layout_model_path=config.layout_model_path
            )
        )[0]
        annotation = [(word, tag) for tag, word in result[1]['annotation']]
        resp.body = json.dumps(annotation)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id=None):
        print(f"Saving Annotation {self.kind}")
        print(req.media)
        id, annotation = req.media
        annotation_filename = bas64encode(id) + "--" + hashval(annotation)
        with open(config.ELMO_DIFFERENCE_COLLECTION_PATH
                  + "/"
                  + annotation_filename
                  + ".conll", "w") \
                as f:
            f.write(annotation2conll(annotation))

        resp.status = falcon.HTTP_OK


if __name__== "__main__":
    test_annotation = [['solitons', 'U-SUBJECT'], ['arise', 'B-CONTRAST'], ['as', 'I-CONTRAST'], ['nontrivial', 'I-CONTRAST'], ['solutions', 'I-CONTRAST'], ['in', 'I-CONTRAST'], ['field', 'I-CONTRAST'], ['theories', 'I-CONTRAST'], ['with', 'I-CONTRAST'], ['non', 'I-CONTRAST'], ['linear', 'I-CONTRAST'], ['interactions', 'I-CONTRAST'], ['.', 'I-CONTRAST'], ['These', 'I-CONTRAST'], ['solutions', 'I-CONTRAST'], ['are', 'I-CONTRAST'], ['stable', 'I-CONTRAST'], ['against', 'I-CONTRAST'], ['dispersion', 'L-CONTRAST'], ['.', 'null'], ['Topology', 'U-SUBJECT'], ['enters', 'B-CONTRAST'], ['through', 'I-CONTRAST'], ['the', 'I-CONTRAST'], ['absolute', 'I-CONTRAST'], ['conservation', 'I-CONTRAST'], ['of', 'I-CONTRAST'], ['topological', 'I-CONTRAST'], ['charge', 'I-CONTRAST'], [',', 'I-CONTRAST'], ['or', 'I-CONTRAST'], ['winding', 'I-CONTRAST'], ['number', 'I-CONTRAST'], ['.[1]', 'I-CONTRAST'], ['It', 'I-CONTRAST'], ['is', 'I-CONTRAST'], ['for', 'I-CONTRAST'], ['this', 'I-CONTRAST'], ['reason', 'I-CONTRAST'], ['they', 'I-CONTRAST'], ['become', 'I-CONTRAST'], ['so', 'I-CONTRAST'], ['important', 'I-CONTRAST'], ['in', 'I-CONTRAST'], ['the', 'I-CONTRAST'], ['description', 'I-CONTRAST'], ['of', 'I-CONTRAST'], ['phenomena', 'I-CONTRAST'], ['like', 'I-CONTRAST'], [',', 'I-CONTRAST'], ['optical', 'I-CONTRAST'], ['self-focusing', 'I-CONTRAST'], [',', 'I-CONTRAST'], ['magnetic', 'I-CONTRAST'], ['flux', 'I-CONTRAST'], ['in', 'I-CONTRAST'], ['Josephson', 'I-CONTRAST'], ['junctions[2]', 'I-CONTRAST'], ['or', 'I-CONTRAST'], ['even', 'I-CONTRAST'], ['the', 'I-CONTRAST'], ['very', 'I-CONTRAST'], ['existence', 'I-CONTRAST'], ['of', 'I-CONTRAST'], ['stable', 'I-CONTRAST'], ['elementary', 'I-CONTRAST'], ['particles', 'I-CONTRAST'], [',', 'I-CONTRAST'], ['such', 'I-CONTRAST'], ['as', 'I-CONTRAST'], ['the', 'I-CONTRAST'], ['skyrmion', 'I-CONTRAST'], ['[3,', 'L-CONTRAST']]
    print (annotation2conll(test_annotation))