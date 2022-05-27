import {Component} from "react";
import Nav from "./Nav";
import ServerResource from "../resources/GeneralResource";
import {ThreeCircles, Triangle} from "react-loader-spinner";

interface Props {
    data: { value: any, meta: any }
    service: ServerResource<any>
}

class HtmlRenderer extends Component<Props> {
    componentDidMount() {
        console.log("HtmlRenderer", this);
    }

    render() {
        console.log("HtmlRenderer", this);
        return <>
            <Nav forward={() => this.props.service.ok(null, "", {}, () => window.location.reload())
            }/>
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
            }}>
                {this.props?.data.meta ?
                    <style dangerouslySetInnerHTML={{
                        __html: this.props.data.meta.css +
                            `\n\n#page-container { 
         background-color: transparent !important;
         background-image: none !important;
       }`
                    }}/>
                    : <ThreeCircles
                        color="red"
                        outerCircleColor="blue"
                        middleCircleColor="green"
                        innerCircleColor="grey"
                    />
                }
                {this.props.data.meta?.html ?
                    <div dangerouslySetInnerHTML={{__html: this.props.data.meta.html}}/>
                    : <Triangle ariaLabel="loading-indicator"/>
                }
            </div>
        </>
    }
}

export default HtmlRenderer;