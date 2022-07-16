import React, { Component } from "react";
import { zip, pairwise } from "../src/util/array";

export default class BoxAnnotator extends Component<any> {
  LABELS = ["NONE", "c1", "c2", "c3", "wh", "h", "pn", "fn", "fg", "tb"];

  LABEL_SWITCH = Object.fromEntries(pairwise([...this.LABELS, this.LABELS[0]]));

  KEYS = {
    KeyF: "fn",
    KeyG: "fg",
    KeyT: "tb",
    Digit1: "c1",
    Digit2: "c2",
    Digit3: "c3",
    Digit0: "wh",
    KeyW: "wh",

    KeyN: "pn",
    KeyH: "h",
    Space: "NONE",
  };

  state = {
    next_key: null,
  };

  componentDidMount() {
    console.log("HtmlRenderer", this);
    document.addEventListener("keydown", this.key, false);
  }

  componentWillUnmount() {
    document.removeEventListener("keydown", this.key, false);
  }

  key = (event) => {
    console.log(
      event.keyCode,
      event.key,
      event.which,
      event.code,
      "a".charCodeAt(0)
    );

    var next_key = this.KEYS[event.code];

    if (!next_key) console.log("unknown keycode", event.code);

    if (next_key) this.setState({ next_key });
  };

  render() {
    console.log(this.props);

    let cols;
    if (this.props.superState.value)
      cols = zip([
        this.props.superState.value.bbox,
        this.props.superState.value.labels,
      ]);

    return (
      <div style={{ fontSize: "1em !important" }}>
        <div style={{ fontSize: "1em !important" }}>
          <form
            onSubmit={(e) => {
              console.log("submit", e, e.target);
              this.props.service.upload(e.target);
            }}
            style={{ fontSize: "1em" }}
          >
            <input
              type="file"
              name="file"
              multiple
              style={{ fontSize: "2em" }}
            />
            <button type="submit" style={{ fontSize: "1em" }}>
              Upload
            </button>
          </form>
        </div>
        <h4> {this.props.superState?.meta?.html_path}</h4>
        <div className="container" style={{ position: "absolute" }}>
          {this.props.superState?.value?.human_image ? (
            <img
              src={
                "data:image/jpeg;charset=utf-8;base64," +
                this.props.superState?.value?.human_image
              }
            />
          ) : null}

          {cols?.map((row, i) => (
            <div
              style={{
                position: "absolute",
                left: row[0][0].toString() + "px",
                top: row[0][1].toString() + "px",
                width: (row[0][2] - row[0][0]).toString() + "px",
                height: (row[0][3] - row[0][1]).toString() + "px",
                border: "1px solid black",
                zIndex: Math.ceil(
                  9000000 - (row[0][2] - row[0][0]) * (row[0][3] - row[0][1])
                ),
              }}
              onClick={() => {
                console.log("row", i);
                let label;
                if (this.state.next_key) {
                  label = this.state.next_key;
                } else {
                  label = this.LABEL_SWITCH[row[1]];
                }
                console.log({ label, ls: this.LABEL_SWITCH });
                if (label)
                  this.props.service.change(
                    "[0].labels.[" + i + "]",
                    label,
                    this.props.setFullState
                  );
              }}
            ></div>
          ))}

          {cols ? (
            <>
              <button
                onClick={() => {
                  this.props.service.ok([
                    this.props.superState.value,
                    this.props.superState.meta,
                  ]);
                  this.props.service.fetch_all(this.props.setFullState);
                }}
              >
                OK
              </button>
              <button onClick={this.props.service.discard}>Discard</button>
            </>
          ) : null}

          <h1>
            <pre> {JSON.stringify(this.KEYS, null, 2)} </pre>
          </h1>
        </div>
      </div>
    );
  }
}
