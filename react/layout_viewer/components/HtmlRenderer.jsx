import React, { Component } from "react";


class HtmlRenderer extends Component {
  componentDidMount() {
    console.log("HtmlRenderer", this);
  }

  render() {
    console.log("HtmlRenderer", this);
    return (<>
      <style dangerouslySetInnerHTML={{__html: this.props.data.css +
      `\n\n#page-container { 
         background-color: transparent !important;
         background-image: none !important;
       }`}} />
      <div dangerouslySetInnerHTML={{__html: this.props.data.html}}/>
      </>
    );
  }
}
export default HtmlRenderer;