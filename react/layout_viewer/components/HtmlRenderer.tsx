import {Component} from "react";

interface Props {
  value: any
  meta: any
}

class HtmlRenderer extends Component<Props> {
  componentDidMount() {
    console.log("HtmlRenderer", this);
  }

  render() {
    console.log("HtmlRenderer", this);
    return (<>

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