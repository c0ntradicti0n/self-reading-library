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

          {this.props?.meta ?
              <style dangerouslySetInnerHTML={{
                __html: this.props.meta.css +
                    `\n\n#page-container { 
         background-color: transparent !important;
         background-image: none !important;
       }`
              }}/>
              : "no css found!"
          }
          {this.props.meta?.html ?
              <div dangerouslySetInnerHTML={{__html: this.props.meta.html}}/>
              : "no html found"
          }
      </>
    );
  }
}
export default HtmlRenderer;