import React, { Component } from "react";

class HtmlRenderer extends Component {
  componentDidMount() {
    console.log("html", this);
  }


  render() {
    console.log("HtmlRenderer", this);
    return (
      <div dangerouslySetInnerHTML={{__html: this.props.data}}>
      </div>
    );
  }
}
export default HtmlRenderer;