import React, {Component} from "react";
import {zip, pairwise} from "../src/util/array";
import {Button} from "@mui/material";
import Nav from "./Nav";

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

        KeyN: "pn",
        KeyH: "h",
        Space: "NONE",
    };

    KEY_TRANSLATE = {
        KeyF: "F",
        KeyG: "G",
        KeyT: "T",
        Digit1: "1",
        Digit2: "2",
        Digit3: "3",
        Digit0: "0",
        KeyW: "W",

        KeyN: "N",
        KeyH: "H",
        Space: "w",
    }

    TAG_TRANSLATE = {
        fn: "footnote",
        fg: "figure",
        tb: "table",
        c1: "column 1",
        c2: "column 2",
        c3: "column 3",
        wh: "single column",

        pn: "page number",
        h: "header",
        NONE: "out of scope",
    }

    state = {
        next_key: null,
    };

    componentDidMount() {
        console.log("HtmlRenderer", this);
        document.addEventListener("keydown", this.key, true);

    }

    componentWillUnmount() {
        document.removeEventListener("keydown", this.key, true);
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

        if (next_key) this.setState({next_key});
    };

    render() {
        console.log(this.props);
        const width = window.innerWidth
        const scale = width * 0.5 * 0.994


        let cols;
        if (this.props.superState.meta)
            cols = zip([
                this.props.superState.meta.bbox,
                this.props.superState.meta.labels,
            ]);

        return (
            <div style={{fontSize: "1em !important", display: "flex"}}>
                <h2>Improve Layout</h2>
                <Nav
                    forward={() =>
                        this.props.service.ok(null, "", {}, () => window.location.reload())
                    }
                    goto={(form_data) =>
                        this.props.service.fetch_one(form_data, () =>
                            console.log("will display content...")
                        )
                    }
                    upload={(form_data) =>
                        this.props.service.upload(new FormData(form_data), () =>
                            console.log("will display content...")
                        )
                    }
                    data={this.props.data}
                />
                <div className="container" style={{position: "absolute"}}>
                    {this.props.superState?.meta?.human_image ? (
                        <img
                            id="annotation_canvas"
                            src={
                                "data:image/jpeg;charset=utf-8;base64," +
                                this.props.superState?.meta?.human_image
                            }
                        />
                    ) : null}

                    {cols?.map((row, i) => (
                        <div
                            style={{
                                position: "absolute",
                                left: (row[0][0] / 2500 * scale).toString() + "px",
                                top: (row[0][1] / 2500 * scale).toString() + "px",
                                width: ((row[0][2] - row[0][0]) / 2500 * scale).toString() + "px",
                                height: ((row[0][3] - row[0][1]) / 2500 * scale).toString() + "px",
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
                                console.log({label, ls: this.LABEL_SWITCH});
                                if (label)
                                    this.props.service.change(
                                        "[1].labels.[" + i + "]",
                                        label,
                                        this.props.setFullState
                                    );
                            }}
                        ></div>
                    ))}

                    {cols ? (
                        <>
                            <Button
                                style={{backgroundColor: "#DEF"}}
                                onClick={() => {
                                    this.props.service.ok([
                                        this.props.superState.value,
                                        this.props.superState.meta,
                                    ]);
                                    this.props.service.fetch_all(this.props.setFullState);
                                }}
                            >
                                OK
                            </Button>
                            <Button
                                style={{backgroundColor: "#FED"}}

                                onClick={this.props.service.discard}>Discard</Button>
                        </>
                    ) : null}

                    <div>
                        <table style={{width: "10%"}}
                        >
                            <tr><td>KEY</td><td>TAG</td></tr>
                            {Object.entries(this.KEYS).map(([k, v], i) => <tr>
                                    <td key={i + "_1"}
                                        style={{
                                            border: "1px", fontFamily: "keys", fontSize: "4em"
                                        }}
                                        onClick={() => this.setState({next_key: this.KEYS[k]})}
                                    >{this.KEY_TRANSLATE[k]}</td>
                                    <td key={i + "_2"}>{this.TAG_TRANSLATE[v]} </td>

                                </tr>
                            )
                            }
                        </table>
                    </div>
                </div>
            </div>
        );
    }
}
