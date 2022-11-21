from more_itertools import pairwise
from config.ant_imports import *
import math
from functools import reduce

import matplotlib as matplotlib
import dashvis
from dash import html, dcc
from dash_extensions.enrich import (
    DashProxy as Dash,
    MultiplexerTransform,
    Input,
    Output,
)
from flask import Flask
from helpers.hash_tools import hashval
from helpers.span_tools import span_sets2kind_sets

server = Flask(__name__)

app = Dash(
    server=server,
    url_base_pathname=os.environ.get("BASE_URL", "/"),
    transforms=[MultiplexerTransform()],
)

time_range = [20, 500]

cmap = matplotlib.cm.get_cmap("plasma", 30)


app.layout = html.Div(
    [
        dashvis.DashNetwork(
            id="net",
            options=dict(
                height="800px",
                width="100%",
            ),
        ),
        dcc.Input(id="start", type="range", value=0),
        dcc.Input(id="end", type="range", value=200),
    ]
)


ant = PathAnt()


def node_id(kind, a_num, s_num, words):
    return f"{hashval(words)}"  # f"{kind}+{a_num}-{s_num}"


gold_span_annotation = ant(
    "span_annotation.collection.fix", "span_annotation.collection.analysed"
)


def generate_nodes_edges():

    gold_span_annotation = ant(
        "span_annotation.collection.fix",
        "span_annotation.collection.span_set",
        service_id="gold_span_annotation",
    )

    for i, (path, meta) in enumerate(gold_span_annotation([])):
        nodes = []
        edges = []

        span_sets = meta["span_set"]
        for j, (span_set) in span_sets.items():
            set_ids = []
            for kind, annotation_slice in span_set:
                words = tags2_words(annotation_slice)

                rgba = cmap(i)
                color = matplotlib.colors.rgb2hex(rgba)

                nodes.append(
                    {
                        "id": node_id(kind, i, j, words),
                        "label": " ".join(words),
                        "color": color,
                    }
                )
                set_ids.append(node_id(kind, i, j, words))

            for a, b in pairwise(sorted(set_ids)):
                edges.append({"id": f"arm-{a}-{b}", "from": a, "to": b})

        for group in span_sets2kind_sets(span_sets):
            for a, b in pairwise(group["value"]):
                id_a = node_id(a[0], 0, 0, tags2_words(a[1]))
                id_b = node_id(b[0], 0, 0, tags2_words(b[1]))
                edges.append({"id": f"arm-{id_a}-{id_b}", "from": id_a, "to": id_b})

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


@app.callback(Output("net", "options"), [Input("start", "value")])
def myfunc(x):
    time_range[0] = math.ceil(float(x))
    print(time_range)
    return {"nodes": {"color": x}}


@app.callback(Output("net", "options"), [Input("end", "value")])
def myfunc(x):
    time_range[1] = math.ceil(float(x))
    print(time_range)
    return {"nodes": {"color": x}}


@app.callback(Output("net", "data"), [Input("start", "value"), Input("end", "value")])
def myfun(start, end):
    print("hallo")
    data = merge_nested(generate_nodes_edges())

    return data


if __name__ == "__main__":
    server.run("0.0.0.0", 12345)
