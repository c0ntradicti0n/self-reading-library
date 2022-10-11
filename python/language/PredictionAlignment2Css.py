import logging
import os

import pandas as pd

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter("reading_order.*", "css.*")
class PredictionAlignment2Css(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def write_css(self, selector, data, output):
        children = []
        attributes = []

        for key, value in data.items():
            if hasattr(value, "items"):
                children.append((key, value))
            else:
                attributes.append((key, value))

        for key, value in children:
            self.write_css(selector + (key,), value, output)

    def window_overlap(self, i1, i2, j1, j2):
        if i1 >= j1 and i2 <= j2:
            return (i1, i2)
        else:
            return None

    def __call__(self, feature_meta, *args, **kwargs):
        for _pdf_path, meta in feature_meta:

            annotation = meta["whole_annotation"]
            i_to_tag = {}

            try:
                for _i1, (i_annotation, _i2) in meta["_i_to_i2"].items():
                    if _i1 not in i_to_tag or i_to_tag[_i1] == "O":
                        # if _i2 < len(tags):
                        i_to_tag[_i1] = annotation[i_annotation][_i2]
            except Exception as e:
                logging.error(e, exc_info=True)

            css = self.parse_to_css(i_to_tag, meta)

            nested_dict_list = []
            for _i, _i2 in meta["_i_to_i2"].items():
                try:
                    nested_dict_list.append(
                        {
                            "_i": _i,
                            "_i2": _i2,
                            "hex id": f""".z{hex(_i)[2:]}""",
                            "tags": i_to_tag[_i][0]
                            if _i in i_to_tag
                            else "no _i in _i_to_tag",
                            "text": i_to_tag[_i][1]
                            if _i in i_to_tag
                            else "no _i in _i_to_tag",
                        }
                    )
                except Exception as e:
                    self.logger.error(
                        f"did not find all original indices from all indice {e}"
                    )
                    break

            try:
                df = pd.DataFrame(nested_dict_list).sort_values(by="_i")
            except Exception as e:
                logging.error(e, exc_info=True)
                logging.error("Was unable to compose css")
                continue

            try:
                with open(
                    os.path.join(
                        config.hidden_folder + "log/",
                        meta["doc_id"].replace("/", "").replace(".", "") + ".txt",
                    ),
                    "w",
                ) as f:
                    df.to_string(f, index=False)
            except KeyError:
                self.logger.warning("set meta['doc_id'] for logs")

            meta["css"] = css
            yield _pdf_path, meta

    def parse_to_css(self, css_obj, meta):
        try:
            return "\n".join(
                [
                    f""".z{hex(i)[2:]} {{
    {meta["CSS"][annotation[0]]}
    }}
    
"""
                    for i, annotation in css_obj.items()
                ]
            )
        except KeyError:
            raise
