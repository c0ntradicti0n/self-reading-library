import * as React from "react";
import AudiobookService from "../resources/AudiobookService";
import AudiobookPlayer from "../components/AudiobookPlayer";
import {Button} from "@mui/material";
import {Audio} from "react-loader-spinner";

export default class Audiobook extends React.Component {
    state = {
        exists: null,
        checked: null,
        id: null,
        audioPath: null,
    };

    componentDidUpdate() {
    }

    componentWillUnmount() {
        clearInterval(this.intervalId);
    }

    componentDidMount() {
        this.service = new AudiobookService();
        this.existsCall();
        this.intervalId = window.setInterval(this.existsCall, 20000);
    }

    existsCall = async () => {
        await this.service.exists(this.props.id, (res) => {
            console.log(res);

            this.setState({
                exists: true,
                id: this.props.id,
                audioPath: res.audio_path,
            });
            console.log(res);
            clearInterval(this.intervalId);
        });
        this.setState({checked: true});
    };

    load = async () => {
        console.log(this, this.props, this.props.id);
        if (this.props.id && this.state.id != this.props.id) {
            console.log("Request audiobook for", this.props.id);

            await this.service.fetch_one(this.props.id, (res) => {
                console.log(res);

                this.setState({exists: true, id: this.props.id, audioPath: res});
                console.log(res);
            });
        }
    };

    render() {
        console.log(this);
        return (
            <div>
                {this.state.checked === null ? (
                    <Audio height="80"/>
                ) : this.state.exists ? (
                    <AudiobookPlayer id={this.state.audioPath}></AudiobookPlayer>
                ) : (
                    <Button onClick={this.load}>Create (new) Audiobook</Button>
                )}
            </div>
        );
    }
}