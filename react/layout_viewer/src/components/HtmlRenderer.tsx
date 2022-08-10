import React, { Component } from "react";
import Nav from "./Nav";
import ServerResource from "../resources/GeneralResource";
import { ThreeCircles, Triangle } from "react-loader-spinner";
import SelectText from "./SelectText";
import { AppSettings } from "../../config/connection";
import Difference_AnnotationService from "../resources/Difference_AnnotationService";

interface Props {
  data: { value: any; meta: any };
  service: ServerResource<any>;
}

function httpGet(theUrl) {
  let xmlhttp;

  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp = new XMLHttpRequest();
  }

  xmlhttp.onreadystatechange = function () {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      return xmlhttp.responseText;
    }
  };
  xmlhttp.open("GET", theUrl, false);
  xmlhttp.send();

  return xmlhttp.response;
}

class HtmlRenderer extends Component<Props> {
  state = {
    htmlContent: null,
    id: null,
  };

  componentDidMount() {
    console.log("HtmlRenderer", this);
  }

  componentDidUpdate(
    prevProps: Readonly<Props>,
    prevState: Readonly<{}>,
    snapshot?: any
  ) {
    if (this.props.data.value != this.state.id) {
      let htmlContent = httpGet(
        AppSettings.FRONTEND_HOST +
          "/" +
          this.props.data.value.replace(".layouteagle/", "") +
          ".html"
      );
      this.setState({ id: this.props.data.value, htmlContent });
    }
  }

  differenceService = new Difference_AnnotationService();

  render() {
    console.log("HtmlRenderer", this, this.props.data.value);
    console.log(this.state.htmlContent);
    return (
      <div>
        <Nav
          forward={() =>
            this.props.service.ok(null, "", {}, () => window.location.reload())
          }
          goto={(form_data) =>
            this.props.service.fetch_one(form_data, () =>
              console.log("will display content...")
            )
          }
          upload={(form_data) =>
            this.props.service.upload(new FormData(form_data), () =>
              console.log("will display content...")
            )
          }
          data={this.props.data}
        />
        <SelectText
          meta={this.props.data.meta}
          value={this.props.data.value}
          service={this.differenceService}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "9em",
            }}
          >
            {this.props?.data.meta ? (
              <style
                dangerouslySetInnerHTML={{
                  __html:
                    this.props.data.meta.css +
                    `\n\n#page-container { 
                                 background-color: transparent !important;
                                 background-image: none !important;
                               }`,
                }}
              />
            ) : (
              <ThreeCircles
                color="red"
                outerCircleColor="blue"
                middleCircleColor="green"
                innerCircleColor="grey"
              />
            )}
            {this.state.htmlContent ? (
              <div
                dangerouslySetInnerHTML={{ __html: this.state.htmlContent }}
              />
            ) : (
              <Triangle ariaLabel="loading-indicator" />
            )}
          </div>
        </SelectText>
      </div>
    );
  }
}

export default HtmlRenderer;
