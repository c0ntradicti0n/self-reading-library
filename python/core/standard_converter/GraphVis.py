import json
import math
from functools import reduce
from queue import Queue

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

server = Flask(__name__)
app = Dash(server=server, transforms=[MultiplexerTransform()])

time_range = [20, 500]

cmap = matplotlib.cm.get_cmap("plasma", 30)


app.layout = html.Div(
    [
        dashvis.DashNetwork(
            id="net",
            options=dict(
                height="800px",
                width="100%",
                layout=dict(
                    hierarchical=dict(
                        enabled=True,
                        levelSeparation=850,
                        nodeSpacing=100,
                        treeSpacing=500,  # blockShifting=True,
                        # edgeMinimization=True, parentCentralization=True,
                        direction="LR",
                        sortMethod="directed",  # shakeTowards='leaves'
                    )
                ),
            ),
        ),
        dcc.Input(id="start", type="range", value=0),
        dcc.Input(id="end", type="range", value=200),
    ]
)


def read_data(start_ids):
    q = Queue()
    i = 0
    for id in start_ids:
        q.put(id)
    while e := q.get():
        i += 1
        with open(f"{DATA_DIR}/{e}.json") as f:
            result = json.load(f)
        new_edges = []

        for c in result["citations"]:
            c_paperId = c["paperId"]
            q.put(c_paperId)
            new_edges.append({"id": f"{e}-{c_paperId}", "from": e, "to": c_paperId})

        rgba = cmap(result["year"] - 2000)
        color = matplotlib.colors.rgb2hex(rgba)

        if i > time_range[0]:
            yield {
                "nodes": [
                    {
                        "id": e,
                        "label": str(result["year"]) + "\n" + result["title"],
                        "color": color,
                    }
                ],
                "edges": new_edges,
            }
        q.task_done()

        if i > time_range[0] + time_range[1]:
            break


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
    data = merge_nested(read_data([seed_id]))

    return data


server.run("0.0.0.0", 3467)
