import * as React from "react";
import Button from "@mui/material/Button";
import {AppSettings} from "../config/connection";


export default class DownloadFile extends React.Component {
    render() {
        console.log(this.props)
        return (
            <form method="POST" action={AppSettings.BACKEND_HOST + "/" + this.props.kind}>
                <input value={this.props.id} id="id" name="id" type={"text"} hidden/>
                <Button type="submit">Download {this.props.children}</Button>
            </form>
        );
    }
}
