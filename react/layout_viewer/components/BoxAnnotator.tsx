import React, {Component} from "react";
import {pairwise, zip} from "../src/util/array";
import {Button} from "@mui/material";
import Nav from "./Nav";
import Router from "next/router";
import {Watch} from "react-loader-spinner";

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
    };

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
    };

    TAG_COLOR = {
        c1: "blue",
        c2: "green",
        c3: "orange",
        NONE: "violet",
        none: "violet",
        None: "violet",
        other: "yellow",
        null: "violet",
        pn: "yellow",
        h: "red",
        wh: "purple",
        fg: "brown",
        fn: "grey",
        tb: "beige",
    };

    state = {
        next_key: null,
        finished: false,
        imgOriginalSize: null,
        imgRenderSize: null,
        labels: null,
    };

    componentDidMount() {
        console.log("HtmlRenderer", this);
        document.addEventListener("keydown", this.key, true);
    }

    componentWillUnmount() {
        document.removeEventListener("keydown", this.key, true);
    }

    componentDidUpdate(
        prevProps: Readonly<any>,
        prevState: Readonly<{}>,
        snapshot?: any
    ) {
        console.log(this);
        if (
            this.props.superState?.meta?.image &&
            (!this.state.imgOriginalSize ||
                window.innerHeight != this.state.imgRenderSize?.height)
        ) {
            const width = window.innerWidth;
            const scaleW = width * 0.5;
            const height = window.innerHeight;
            const scaleH = height;

            let im = new Image();
            im.src =
                "data:image/jpeg;charset=utf-8;base64," +
                this.props.superState?.meta?.image;
            im.onload = () =>
                this.setState({
                    imgOriginalSize: {width: im.width, height: im.height},
                    imgRenderSize: {width: scaleW, height: scaleH},
                });
        }
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

        if (!next_key) {
            console.log("unknown keycode", event.code);
        }
        if (next_key) {
            this.setState({next_key});
            event.preventDefault();
        }
    };

    render() {
        let cols;
        if (this.props.superState.meta)
            cols = zip([
                this.props.superState.meta.bbox,
                this.state.labels ?? this.props.superState.meta.labels,
            ]);

        // @ts-ignore
        return (
            <div style={{fontSize: "1em !important", display: "flex"}}>
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
                    data={this.props.superState}
                />
                {this.state.finished ? (
                    <div>
                        <h2>
                            We have annotated the whole document!{" "}
                            <Button
                                onClick={(e) => {
                                    console.log(e);
                                    Router.push({
                                        pathname: "/difference/",
                                        query: {id: this.props.superState?.value},
                                    });
                                }}
                            >
                                Return to document!
                            </Button>
                        </h2>
                    </div>
                ) : (
                    <div className="container" style={{position: "absolute"}}>
                        {this.props.superState?.meta?.image ? (
                            <img
                                id="annotation_canvas"
                                src={
                                    "data:image/jpeg;charset=utf-8;base64," +
                                    this.props.superState?.meta?.image
                                }
                            />
                        ) : null}

                        {this.state.imgOriginalSize ? (
                            cols?.map((row, i) => (
                                <div
                                    style={{
                                        position: "absolute",
                                        left:
                                            (
                                                (row[0][0] / this.state.imgOriginalSize.width) *
                                                this.state.imgRenderSize.width
                                            ).toString() + "px",
                                        top:
                                            (
                                                (row[0][1] / this.state.imgOriginalSize.height) *
                                                this.state.imgRenderSize.height -
                                                this.state.imgRenderSize.height * 0.003
                                            ).toString() + "px",
                                        width:
                                            (
                                                ((row[0][2] - row[0][0]) /
                                                    this.state.imgOriginalSize.width) *
                                                this.state.imgRenderSize.width *
                                                1.02
                                            ).toString() + "px",
                                        height:
                                            (
                                                ((row[0][3] - row[0][1]) /
                                                    this.state.imgOriginalSize.height) *
                                                this.state.imgRenderSize.height +
                                                this.state.imgRenderSize.height * 0.003
                                            ).toString() + "px",
                                        //border: "1px solid black",
                                        zIndex: Math.ceil(
                                            9000000 -
                                            (row[0][2] - row[0][0]) * (row[0][3] - row[0][1])
                                        ),
                                        opacity: "0.5",
                                        background: this.TAG_COLOR[row[1]],
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
                                                (res) => {
                                                    console.log(res);
                                                    this.setState({labels: res[1].labels});
                                                }
                                            );
                                    }}
                                ></div>
                            ))
                        ) : (
                            <Watch ariaLabel="Waiting for image"/>
                        )}

                        {cols ? (
                            <>
                                <Button
                                    style={{backgroundColor: "#DEF"}}
                                    onClick={() => {
                                        (async () => {
                                            console.log("ok");
                                            await this.props.service.ok(
                                                [
                                                    this.props.superState.value,
                                                    this.props.superState.meta,
                                                ],
                                                "",
                                                {},
                                                async (val) => {
                                                    console.log(await val);
                                                    if (!Object.keys(val).length) {
                                                        this.setState({finished: true});
                                                    }

                                                    console.log("get new");

                                                    this.props.service.fetch_all((val) =>
                                                        this.props.setFullState(val)
                                                    );
                                                }
                                            );
                                        })();
                                    }}
                                >
                                    OK
                                </Button>
                                <Button
                                    style={{backgroundColor: "#FED"}}
                                    onClick={this.props.service.discard}
                                >
                                    Discard
                                </Button>
                            </>
                        ) : null}

                        <div>
                            <table style={{width: "10%"}}>
                                <tr>
                                    <td> KEY</td>
                                    <td>TAG</td>
                                </tr>
                                {Object.entries(this.KEYS).map(([k, v], i) => (
                                    <tr onClick={() => this.setState({next_key: this.KEYS[k]})}>
                                        <td
                                            key={i + "_1"}
                                            style={{
                                                border: "1px",
                                                fontFamily: "keys",
                                                fontSize: "4em",
                                                verticalAlign: "bottom",
                                            }}
                                        >
                                            {this.KEY_TRANSLATE[k]}
                                        </td>
                                        <td
                                            key={i + "_2"}
                                            style={{
                                                verticalAlign: "top",
                                            }}
                                        >
                                            <div
                                                style={{
                                                    backgroundColor: this.TAG_COLOR[v] as string,
                                                    border: "10px solid " + this.TAG_COLOR[v],
                                                    display: "block",
                                                    borderRadius: "7px",
                                                }}
                                            >
                                                {" "}
                                                {this.TAG_TRANSLATE[v]}{" "}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </table>
                        </div>
                    </div>
                )}
            </div>
        );
    }
}
