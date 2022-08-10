import { Component } from "react";
import SpanAnnotation from "./SpanAnnotation";
import ServerResource from "../resources/GeneralResource";

interface Props {
  service: ServerResource<any>;
  meta: any;
}

interface State {
  selected: string;
}

class SelectText extends Component<Props, State> {
  state = { selected: null };
  handleMouseUp = () => {
    this.setState({ selected: window.getSelection().toString() });
    console.log(`Selected text: ${window.getSelection().toString()}`);
  };

  render() {
    console.log("SelectText", this)
    return (
      <div onMouseUp={this.handleMouseUp}>
        {this.state.selected && (
          <SpanAnnotation
            text={this.state.selected}
            onClose={() => this.setState({ selected: null })}
            service={this.props.service}
            value={this.props.value}
            meta={this.props.meta}
          />
        )}
        {this.props.children}
      </div>
    );
  }
}

export default SelectText;
