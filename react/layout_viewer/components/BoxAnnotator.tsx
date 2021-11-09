import React, {Component} from "react";
import {zip} from "../src/util/array";


export default class BoxAnnotator extends Component {
    LABEL_SWITCH = {NONE: "c1", c1: "NONE"}

    componentDidMount() {
        console.log("HtmlRenderer", this);
    }

    render() {
        console.log(this.props)
        if (this.props.superState.value) {
                    const cols = zip([this.props.superState.value.bbox, this.props.superState.value.labels])

            return <>
                <h4> {this.props.superState.meta.html_path}</h4>

                <img src={"data:image/jpeg;charset=utf-8;base64," + this.props.superState?.value?.human_image}>
                </img>

                <table>
                    <thead>
                    <tr>
                        <th>Box</th>
                        <th>Label</th>
                    </tr>
                    </thead>
                    <tbody>
                    {cols.map((row, i) => <tr onClick={() => {
                        console.log("row", i)
                        this.props.service.change(
                            "[0].labels.[" + i + "]", this.LABEL_SWITCH[row[1]],
                        this.props.setFullState)
                    }}>
                        <td>{JSON.stringify(row[0])}</td>
                        <td>{JSON.stringify(row[1])}</td>
                    </tr>)}
                    </tbody>
                </table>

                {JSON.stringify(cols)}

                <button onClick={() => this.props.service.ok ([this.props.superState.value, this.props.superState.meta])}>OK</button>
                <button onClick={this.props.service.discard}>Discard</button>


                <img src={"data:image/jpeg;charset=utf-8;base64," + this.props.superState?.value?.image}>
                </img>
            </>
        } else {
            return null
        }

    }
}