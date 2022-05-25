import {Component} from "react";
import Nav from "./Nav";
import ServerResource from "../resources/GeneralResource";

interface Props {
  data: {value:any, meta:any}
  service: ServerResource<any>
}

class HtmlRenderer extends Component<Props> {
  componentDidMount() {
    console.log("HtmlRenderer", this);
  }

  render() {
    console.log("HtmlRenderer", this);
    return (<>
          <Nav forward={this.props.service.ok}/>

          {this.props?.data.meta ?
              <style dangerouslySetInnerHTML={{
                __html: this.props.data.meta.css +
                    `\n\n#page-container { 
         background-color: transparent !important;
         background-image: none !important;
       }`
              }}/>
              : "no css found!"
          }
          {this.props.data.meta?.html ?
              <div dangerouslySetInnerHTML={{__html: this.props.data.meta.html}}/>
              : "no html found"
          }
      </>
    );
  }
}
export default HtmlRenderer;