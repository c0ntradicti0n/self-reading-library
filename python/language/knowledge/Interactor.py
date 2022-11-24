import visdcc
from more_itertools import pairwise
from wasabi import wrap

from config.ant_imports import *
import math
from functools import reduce

import matplotlib as matplotlib

from dash import html, dcc
from dash_extensions.enrich import (
    DashProxy as Dash,
    MultiplexerTransform,
    Input,
    Output,
)
from flask import Flask

server = Flask(__name__)

app = Dash(
    server=server,
    url_base_pathname=os.environ.get("BASE_URL", "/"),
    transforms=[MultiplexerTransform()],
)

time_range = [20, 500]

COLOR_MAP_RANGE = 100
cmap = matplotlib.cm.get_cmap("plasma", COLOR_MAP_RANGE)

ant = PathAnt()


def generate_nodes_edges():
    gold_span_annotation = ant(
        "span_annotation.collection.fix",
        "span_annotation.collection.analysed",
        service_id="gold_span_annotation",
    )

    for i, (path, meta) in enumerate(gold_span_annotation([])):
        nodes = []
        edges = []

        span_sets = meta["span_set"]
        rgba = cmap(span_sets.subject_hash_int % COLOR_MAP_RANGE)
        rgba = [c / math.sin(c * math.pi / 2) for c in rgba]
        color = matplotlib.colors.rgb2hex(rgba)
        add_rgba = [abs(math.cos((c * math.pi))) for c in rgba]
        add_color = matplotlib.colors.rgb2hex(add_rgba)

        for j, (span_set) in enumerate(span_sets.side_sets):
            set_ids = []
            for span in span_set:
                nodes.append(
                    {
                        "id": span.nlp_id,
                        "label": wrap(span.text),
                        "color": color,
                    }
                )
                set_ids.append(span.nlp_id)

            for a, b in pairwise(sorted(set_ids)):
                edges.append({"id": f"arm-{a}-{b}", "from": a, "to": b, "label": "..."})

        for values in span_sets.kind_sets:
            for a, b in pairwise(values):
                id_a, id_b = a.nlp_id, b.nlp_id
                edges.append(
                    {
                        "id": f"arm-{id_a}-{id_b}",
                        "from": id_a,
                        "to": id_b,
                        "arrows": "to;from",
                    }
                )

        analysed_links = meta["analysed_links"]
        for a1, a2, c1, c2, l1, l2 in analysed_links:
            k1_id = c1.nlp_id + "krit"
            k2_id = c2.nlp_id + "krit"
            nodes.extend(
                [
                    {
                        "id": k1_id,
                        "label": a1,
                        "color": add_color,
                    },
                    {
                        "id": k2_id,
                        "label": a2,
                        "color": add_color,
                    },
                ]
            )
            edges.append(
                {
                    "id": f"arm-{k1_id}-{k2_id}-krit",
                    "from": k2_id,
                    "to": k1_id,
                    "label": "krit",
                }
            )

            edges.append(
                {"id": f"arm-{k1_id}-{k2_id}-k1", "from": k1_id, "to": c1.nlp_id}
            )
            edges.append(
                {"id": f"arm-{k1_id}-{k2_id}-k2", "from": k2_id, "to": c2.nlp_id}
            )

        yield {
            "nodes": nodes,
            "edges": edges,
        }


def tags2_words(annotation_slice):
    return [t[0] for t in annotation_slice]


def merge_nested(dicts):
    def merge(acc, d):
        return {k: v + (acc[k] if k in acc else []) for k, v in d.items()}

    return reduce(merge, dicts, {})


options = (
    dict(
        height="800px",
        width="100%",
        layout=dict(
            hierarchical=dict(
                sortMethod="directed",
            ),
        ),
    ),
)

data = merge_nested(generate_nodes_edges())


def search(text):
    return data


@app.callback(Output("net", "data"), [Input("search", "value")])
def search_callback(text):
    return search(text)


app.layout = html.Div(
    [
        visdcc.Network(
            id="net",
            options=dict(
                height="800px",
                width="100%",
                layout=dict(
                    randomSeed=0,
                    improvedLayout=False
                ),
            ),
        ),
        dcc.Input(id="search", type="text", value="hallo"),
    ]
)

if __name__ == "__main__":
    server.run("0.0.0.0", 12345)
