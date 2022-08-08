import * as React from "react";
import AudiobookService from "../resources/AudiobookService"
import AudiobookPlayer from "../components/AudiobookPlayer"
import {Button} from "@mui/material";

export default class Audiobook extends React.Component {
    state = {
        exists: null,
        id: null,
        audioPath: null
    }

    componentDidUpdate() {
    }

    componentDidMount() {
        this.service = new AudiobookService()

        ;(async () => {
            const exists = await this.service.exists(this.props.id,
                (res) => {
                    console.log(res)

                    this.setState({exists: true, id: this.props.id, audioPath: res})
                    console.log(res)
                })
            console.log(exists)
            this.setState({exists})
        })()
    }

    load = async () => {
        console.log(this, this.props, this.props.id)
        if (this.props.id && this.state.id != this.props.id) {
            console.log("Request audiobook for", this.props.id)

            await this.service.fetch_one(this.props.id,
                (res) => {
                    console.log(res)

                    this.setState({exists: true, id: this.props.id, audioPath: res})
                    console.log(res)
                })
        }


    }

    render() {
        console.log(this)
        return <>
            {
                this.state.exists
                    ? <AudiobookPlayer id={this.state.audioPath}></AudiobookPlayer>
                    : <Button onClick={this.load}>Create (new) Audiobook</Button>

            }</>
    }
}