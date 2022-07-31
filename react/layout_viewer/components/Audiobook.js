import * as React from "react";
import AudiobookService from "../resources/AudiobookService"
import AudiobookPlayer from "../components/AudiobookPlayer"

export default class Audiobook extends React.Component {
    state = {
        exists: null,
        id: null,
        audioPath: null
    }

    componentDidUpdate() {
        this.service = new AudiobookService()
        this.load()
    }

    load = async () => {
        console.log(this, this.props, this.props.id)
        if (this.props.id && this.state.id != this.props.id) {
            console.log("Request audiobook")

            await this.service.fetch_one(this.props.id,
                (res) => this.setState({exists: true, id: this.props.id, audioPath: res})
            )
        }
    }

    render() {
        console.log(this)
        return <>{
            this.state.exists
                ? <AudiobookPlayer id={this.state.audioPath}></AudiobookPlayer>
                : <div>Creating your audiobook</div>
        }</>
    }
}