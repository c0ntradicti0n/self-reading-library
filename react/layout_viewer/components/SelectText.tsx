import {Component} from "react";
import Spannotator from "./Spannotator";

interface Props {

}

interface State {
    selected: string
}

class SelectText extends Component<Props, State> {
    state = {selected : null}
  handleMouseUp = () => {
      this.setState({selected:window.getSelection().toString()})
        console.log(`Selected text: ${window.getSelection().toString()}`);
    }
    render() {


    return (
        <div onMouseUp={this.handleMouseUp}>
            {this.state.selected && <Spannotator text={this.state.selected} onClose={() => this.setState({selected:null})}/>}
                {this.props.children}

            </div>)

    }
}

export default SelectText;