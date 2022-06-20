import {Component} from "react";
import Nav from "./Nav";
import ServerResource from "../resources/GeneralResource";
import {ThreeCircles, Triangle} from "react-loader-spinner";
import SelectText from "./SelectText";

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
        return <SelectText>
            <Nav
                forward={() => this.props.service.ok(null, "", {}, () => window.location.reload())}
                goto={(form_data) => this.props.service.fetch_one(form_data, () => console.log("will display content..."))}
                upload={(form_data) => this.props.service.upload(new FormData(form_data), () => console.log("will display content..."))}
            />

            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: "9em"
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
        </SelectText>
    }
}

export default HtmlRenderer;