import AudioPlayer from "react-h5-audio-player";
import "react-h5-audio-player/lib/styles.css";
import React from "react";

export default class AudiobookPlayer extends React.Component {
  render() {
    return (
      <AudioPlayer
        src={this.props.id?.replace(".layouteagle/", "")}
        onPlay={(e) => console.log("onPlay")}
      />
    );
  }
}
