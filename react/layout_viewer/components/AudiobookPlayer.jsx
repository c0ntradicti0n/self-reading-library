import AudioPlayer from 'react-h5-audio-player';
import 'react-h5-audio-player/lib/styles.css';
import React from "react";
import {AppSettings} from "../config/connection";

export default class AudiobookPlayer extends React.Component {
    render() {
        return <AudioPlayer
            autoPlay
            src={ this.props.id?.replace(".layouteagle/", "") + ".ogg"}
            onPlay={e => console.log("onPlay")}
        />
    }
}