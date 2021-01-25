import React, { Component } from "react";
import {createUseStyles} from 'react-jss';


class HtmlRenderer extends Component {
  componentDidMount() {
    console.log("HtmlRenderer", this);

    //const useStyle = createUseStyles(JSON.parse(this.props.data.css));
    //console.log(useStyle);
    //this.setState({style: useStyle});
  }

  render() {
    console.log("HtmlRenderer", this);
    return (<>
      <style dangerouslySetInnerHTML={{__html: this.props.data.css}} />
      <div dangerouslySetInnerHTML={{__html: this.props.data.html}} />
      </>
    );
  }
}
export default HtmlRenderer;